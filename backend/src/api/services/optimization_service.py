import pandas as pd
import numpy as np
import sys
import os

# Adicionando patch de compatibilidade para o VectorBT
# Isso deve ser feito ANTES de importar vectorbt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
try:
    from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
    apply_vectorbt_telegram_patch()
except ImportError:
    pass

import vectorbt as vbt
from vectorbt import nb
from datetime import datetime, timedelta
import threading
from typing import List, Dict, Any
import os

from corretoras.funcoes_bybit import carregar_dados_historicos
from utils.logging import get_logger, LogCategory

# Reutilizando o core Numba acelerado
@nb.njit
def double_ema_breakout_long_short_nb(close, high, low, ema1_long, ema2_long, ema1_short, ema2_short, q_stop_long, q_stop_short, rr_long, rr_short):
    entries = np.full(close.shape, np.nan)
    exits = np.full(close.shape, np.nan)
    size = np.full(close.shape, np.nan)

    in_trade = False
    entry_price = 0.0
    stop_value = 0.0
    target_value = 0.0
    current_position = 0  # 0 = sem posição, 1 = long, -1 = short

    for i in range(999, len(close)):
        # Condições para long
        long_cond1 = close[i - 1] > ema1_long[i - 1]
        long_cond2 = close[i - 1] > ema2_long[i - 1]
        long_cond3 = high[i] > high[i - 1]

        # Condições para short
        short_cond1 = close[i - 1] < ema1_short[i - 1]
        short_cond2 = close[i - 1] < ema2_short[i - 1]
        short_cond3 = low[i] < low[i - 1]

        if not in_trade:
            if long_cond1 and long_cond2 and long_cond3:
                entry_price = high[i - 1]
                min_stop = low[i - q_stop_long + 1:i + 1]
                if len(min_stop) == q_stop_long:
                    stop_value = np.min(min_stop)
                    target_value = entry_price + (entry_price - stop_value) * rr_long
                    entries[i] = entry_price
                    size[i] = 1.0
                    in_trade = True
                    current_position = 1

            elif short_cond1 and short_cond2 and short_cond3:
                entry_price = low[i - 1]
                max_stop = high[i - q_stop_short + 1:i + 1]
                if len(max_stop) == q_stop_short:
                    stop_value = np.max(max_stop)
                    target_value = entry_price - (stop_value - entry_price) * rr_short
                    entries[i] = entry_price
                    size[i] = -1.0
                    in_trade = True
                    current_position = -1

        elif in_trade:
            if current_position == 1:
                if high[i] >= target_value or low[i] <= stop_value:
                    exits[i] = target_value if high[i] >= target_value else stop_value
                    size[i] = 0.0
                    in_trade = False
                    current_position = 0
            else:
                if low[i] <= target_value or high[i] >= stop_value:
                    exits[i] = target_value if low[i] <= target_value else stop_value
                    size[i] = 0.0
                    in_trade = False
                    current_position = 0

    return entries, exits, size

class OptimizationService:
    def __init__(self):
        self.logger = get_logger("OptimizationService")
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def optimize_symbol(self, symbol: str, interval: str = '15', days: int = 7) -> List[Dict[str, Any]]:
        cache_key = f"{symbol}_{interval}_{days}"
        
        # Check cache (1 hour validity)
        with self._lock:
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(hours=1):
                    return cached_data['results']

        self.logger.info(LogCategory.SYSTEM, f"🔍 Iniciando otimização para {symbol} ({days} dias)...")
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Carregar dados (necessário pular velas o suficiente para as EMAs estabilizarem)
            df = carregar_dados_historicos(
                symbol, interval, [20, 200], 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d'),
                pular_velas=500
            )
            df.columns = df.columns.str.lower()
            
            close = df['fechamento'].values
            high = df['maxima'].values
            low = df['minima'].values
            
            # Espaço de busca otimizado para velocidade
            ema_short_range = [9, 12, 15, 21]
            ema_long_range = [34, 50, 89, 100]
            stop_range = [10, 15, 20]
            rr_range = [2.0, 3.0, 4.0]
            
            results = []
            
            # Grid Search
            for es in ema_short_range:
                for el in ema_long_range:
                    if el <= es: continue
                    
                    # Calcular EMAs uma vez por combinação
                    e_s = pd.Series(close).ewm(span=es).mean().values
                    e_l = pd.Series(close).ewm(span=el).mean().values
                    
                    for s in stop_range:
                        for r in rr_range:
                            entries, exits, sizes = double_ema_breakout_long_short_nb(
                                close, high, low, e_s, e_l, e_s, e_l, s, s, r, r
                            )
                            
                            # Avaliar performance usando vectorbt
                            order_price = pd.Series(entries).combine_first(pd.Series(exits))
                            pf = vbt.Portfolio.from_orders(
                                close=pd.Series(close),
                                price=order_price,
                                size=pd.Series(sizes),
                                size_type='targetpercent',
                                init_cash=1000,
                                fees=0.00055,
                                direction='both'
                            )
                            
                            stats = pf.stats()
                            total_return = stats['Total Return [%]']
                            drawdown = stats['Max Drawdown [%]']
                            win_rate = stats['Win Rate [%]']
                            
                            # Métrica de "Fitness" equilibrada
                            fitness = total_return * (1 - abs(drawdown)/100) if total_return > 0 else total_return
                            
                            results.append({
                                "parameters": {
                                    "ema_short": es,
                                    "ema_long": el,
                                    "stop_candles": s,
                                    "risk_reward": r
                                },
                                "metrics": {
                                    "return": round(total_return, 2),
                                    "drawdown": round(drawdown, 2),
                                    "win_rate": round(win_rate, 2),
                                    "trades": int(stats['Total Trades']),
                                    "fitness": round(fitness, 2)
                                }
                            })
            
            # Ordenar por fitness e pegar os top 5
            top_results = sorted(results, key=lambda x: x['metrics']['fitness'], reverse=True)[:5]
            
            with self._lock:
                self.cache[cache_key] = {
                    'timestamp': datetime.now(),
                    'results': top_results
                }
                
            self.logger.info(LogCategory.SYSTEM, f"✅ Otimização concluída para {symbol}. Top Fitness: {top_results[0]['metrics']['fitness'] if top_results else 0}")
            return top_results
            
        except Exception as e:
            self.logger.error(LogCategory.EXECUTION_ERROR, f"❌ Falha ao otimizar {symbol}: {e}")
            return []

_instance = None
def get_optimization_service():
    global _instance
    if _instance is None:
        _instance = OptimizationService()
    return _instance
