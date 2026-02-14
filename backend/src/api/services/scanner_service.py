import time
import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import threading
from corretoras.funcoes_bybit import cliente
from scanner.symbols import SYMBOLS
from utils.logging import get_logger, LogCategory
from api.services.notification_service import notify_high_score_signal
from api.services.config_manager import get_config_manager
from api.services.signal_service import get_signal_service
import asyncio

class ScannerService:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self.is_running = False
        self.scan_limit = 20
        self.logger = get_logger("ScannerService")
        self._thread = None
        self.notified_signals = set() # Track already notified symbols for current score 5
        self.config_manager = get_config_manager()
        self.signal_service = get_signal_service()

    def start_scanning(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.logger.info(LogCategory.SYSTEM, f"🚀 Scanner Service iniciado em Thread dedicada (Limite: {self.scan_limit})")

    def stop_scanning(self):
        self.is_running = False

    def _run_loop(self):
        while self.is_running:
            try:
                self._scan_all_symbols_sync()
            except Exception as e:
                self.logger.error(LogCategory.EXECUTION_ERROR, f"❌ Erro no loop do scanner: {e}")
            time.sleep(60)

    def _scan_all_symbols_sync(self):
        new_results = []
        active_symbols = SYMBOLS[:self.scan_limit]
        
        for symbol in active_symbols:
            if not self.is_running:
                break
            result = self._scan_symbol_sync(symbol)
            if result:
                new_results.append(result)
            time.sleep(0.5) # Rate limit protection (2 requests per second)

        with self._lock:
            if new_results:
                self.results = sorted(new_results, key=lambda x: x['score'], reverse=True)
                self.logger.info(LogCategory.SYSTEM, f"✅ Scan completo: {len(self.results)} símbolos processados")
                
                # Verificar sinais para notificação
                self._check_for_notifications(self.results)
                
                # Atualizar Feed de Sinais / Oportunidades
                self.signal_service.update_signals(self.results)
            else:
                # Caso a varredura falhe e retorne vazio, mantenha resultados anteriores e registre aviso
                self.logger.warning(LogCategory.SYSTEM, f"⚠️ Scan retornou vazio; mantendo resultados anteriores ({len(self.results)} ativos)")

    def _scan_symbol_sync(self, symbol: str) -> Dict[str, Any]:
        try:
            resp = cliente.get_kline(
                category="linear", symbol=symbol, interval="60", limit=200
            )
            
            if not resp or 'result' not in resp or not resp['result']['list']:
                return None

            klines = resp['result']['list'][::-1]
            df = pd.DataFrame(klines, columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'turnover'])
            df[['open', 'high', 'low', 'close', 'vol']] = df[['open', 'high', 'low', 'close', 'vol']].astype(float)

            ema20 = ta.ema(df['close'], length=20)
            ema50 = ta.ema(df['close'], length=50)
            ema200 = ta.ema(df['close'], length=200)
            rsi = ta.rsi(df['close'], length=14)
            
            last_close = df['close'].iloc[-1]
            last_vol = df['vol'].iloc[-1]
            avg_vol = df['vol'].tail(20).mean()
            
            s1 = 1 if last_close > ema200.iloc[-1] else 0 
            s2 = 1 if ema20.iloc[-1] > ema50.iloc[-1] else 0 
            s3 = 1 if 45 <= rsi.iloc[-1] <= 65 else 0 
            s4 = 1 if last_vol > (avg_vol * 1.2) else 0 
            
            prev_high = df['high'].iloc[-2]
            proximity = abs(last_close - prev_high) / prev_high
            s5 = 1 if proximity <= 0.003 else 0 

            score = s1 + s2 + s3 + s4 + s5
            
            return {
                "symbol": symbol,
                "price": last_close,
                "score": score,
                "factors": {
                    "trend_htf": bool(s1),
                    "trend_mtf": bool(s2),
                    "rsi_zone": bool(s3),
                    "vol_surge": bool(s4),
                    "setup_prox": bool(s5)
                },
                "rsi": round(rsi.iloc[-1], 2),
                "last_update": datetime.now().isoformat()
            }
        except Exception as e:
            # Log de erro detalhado para facilitar diagnóstico (rede, rate limit, parsing)
            self.logger.error(LogCategory.EXECUTION_ERROR, f"❌ Erro ao scanear {symbol}: {e}")
            return None

    def _check_for_notifications(self, results):
        webhook_url = self.config_manager.get("webhook_url")
        if not webhook_url:
            return

        current_signals = set()
        for res in results:
            if res['score'] >= 5:
                current_signals.add(res['symbol'])
                if res['symbol'] not in self.notified_signals:
                    # Rodar notificação em background (async)
                    asyncio.run_coroutine_threadsafe(
                        notify_high_score_signal(webhook_url, res),
                        asyncio.get_event_loop()
                    )
                    self.notified_signals.add(res['symbol'])
        
        # Limpar símbolos que não estão mais com score 5 para permitir futura re-notificação
        self.notified_signals = self.notified_signals.intersection(current_signals)

    def get_results(self):
        with self._lock:
            return self.results

    def set_limit(self, limit: int):
        self.scan_limit = max(1, min(limit, len(SYMBOLS)))
        self.logger.info(LogCategory.SYSTEM, f"⚙️ Limite do scanner atualizado para {self.scan_limit}")

_scanner_instance = None

def get_scanner_service() -> ScannerService:
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = ScannerService()
    return _scanner_instance
