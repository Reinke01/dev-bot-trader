"""
Analisa mercado (scanner) + moeda específica e envia para Telegram
Uso: python analise_completa_telegram.py BTC
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv
from utils.notifications.telegram_client import get_telegram_client
from corretoras.funcoes_bybit import cliente
import pandas as pd
import pandas_ta as ta
from scanner.symbols import SYMBOLS

load_dotenv()

def analyze_symbol(symbol):
    """Analisa um símbolo e retorna os dados"""
    try:
        resp = cliente.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        
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
        last_rsi = rsi.iloc[-1]
        
        score = 0
        details = []
        
        if last_close > ema200.iloc[-1]:
            score += 1
            details.append("Acima EMA 200")
        else:
            details.append("Abaixo EMA 200")
        
        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 1
            details.append("EMA 20 maior que 50")
        else:
            details.append("EMA 20 menor que 50")
        
        if 45 <= last_rsi <= 65:
            score += 1
            details.append("RSI neutro")
        elif last_rsi > 65:
            details.append("RSI alto")
        else:
            details.append("RSI baixo")
        
        if last_vol > (avg_vol * 1.2):
            score += 1
            details.append("Volume alto")
        else:
            details.append("Volume normal")
        
        if last_close > df['high'].iloc[-2]:
            score += 1
            details.append("Breakout")
        else:
            details.append("Sem breakout")
        
        if last_close > ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
            trend = "Alta Forte"
        elif last_close > ema20.iloc[-1] > ema50.iloc[-1]:
            trend = "Alta"
        elif last_close < ema20.iloc[-1] < ema50.iloc[-1] < ema200.iloc[-1]:
            trend = "Baixa Forte"
        elif last_close < ema20.iloc[-1] < ema50.iloc[-1]:
            trend = "Baixa"
        else:
            trend = "Lateral"
        
        return {
            'symbol': symbol,
            'score': score,
            'price': last_close,
            'rsi': last_rsi,
            'trend': trend,
            'volume_ratio': last_vol / avg_vol,
            'ema20': ema20.iloc[-1],
            'ema50': ema50.iloc[-1],
            'ema200': ema200.iloc[-1],
            'details': details
        }
    except Exception as e:
        print(f"Erro ao analisar {symbol}: {e}")
        return None

# Scanner
print("🔍 SCANNER DE OPORTUNIDADES")
print("="*60)
print("📊 Analisando Top 30 moedas...")
print("="*60 + "\n")

results = []
symbols_to_scan = SYMBOLS[:30]

for i, symbol in enumerate(symbols_to_scan, 1):
    print(f"⏳ [{i}/30] Analisando {symbol}...", end='\r')
    data = analyze_symbol(symbol)
    if data:
        results.append(data)

print(" " * 80)
results.sort(key=lambda x: x['score'], reverse=True)

# Preparar mensagem do scanner
scanner_msg = f"<b>VARREDURA DE MERCADO</b>\n\n"
scanner_msg += f"<b>{len(results)} moedas analisadas</b>\n\n"
scanner_msg += f"<b>TOP 5 OPORTUNIDADES:</b>\n\n"

for idx, r in enumerate(results[:5], 1):
    emoji = "🔥" if r['score'] >= 4 else "✨" if r['score'] >= 3 else "📊"
    price = f"${r['price']:,.4f}" if r['price'] < 1 else f"${r['price']:,.2f}"
    scanner_msg += f"{idx}. {emoji} <b>{r['symbol']}</b>\n"
    scanner_msg += f"   Score: {r['score']}/5\n"
    scanner_msg += f"   Preco: {price}\n"
    scanner_msg += f"   RSI: {r['rsi']:.1f}\n"
    scanner_msg += f"   Tendencia: {r['trend']}\n\n"

# Análise específica da moeda solicitada
if len(sys.argv) >= 2:
    target_symbol = sys.argv[1].upper()
    if not target_symbol.endswith('USDT'):
        target_symbol += 'USDT'
    
    print(f"\n🔍 Analisando {target_symbol} em detalhes...")
    
    data = analyze_symbol(target_symbol)
    
    if data:
        if data['score'] >= 4:
            rec = "FORTE OPORTUNIDADE"
        elif data['score'] >= 3:
            rec = "BOA OPORTUNIDADE"
        elif data['score'] >= 2:
            rec = "OPORTUNIDADE MODERADA"
        else:
            rec = "EVITAR NO MOMENTO"
        
        price = f"${data['price']:,.4f}" if data['price'] < 1 else f"${data['price']:,.2f}"
        
        detail_msg = f"\n<b>{'='*40}</b>\n\n"
        detail_msg += f"<b>ANALISE DETALHADA: {target_symbol}</b>\n\n"
        detail_msg += f"<b>PONTUACAO: {data['score']}/5</b>\n"
        detail_msg += f"<b>Recomendacao:</b> {rec}\n\n"
        detail_msg += f"<b>Preco Atual:</b> {price}\n"
        detail_msg += f"<b>Tendencia:</b> {data['trend']}\n"
        detail_msg += f"<b>RSI (14):</b> {data['rsi']:.1f}\n"
        detail_msg += f"<b>Volume vs Media:</b> {(data['volume_ratio']*100):.0f}%\n\n"
        detail_msg += f"<b>Analise:</b>\n"
        for detail in data['details']:
            detail_msg += f"- {detail}\n"
        detail_msg += f"\n<b>EMAs:</b>\n"
        detail_msg += f"EMA 20: ${data['ema20']:,.2f}\n"
        detail_msg += f"EMA 50: ${data['ema50']:,.2f}\n"
        detail_msg += f"EMA 200: ${data['ema200']:,.2f}\n"
        
        scanner_msg += detail_msg

scanner_msg += f"\n#{target_symbol.replace('USDT', '')} #TradingBot"

print("\n" + scanner_msg.replace('<b>', '').replace('</b>', ''))

# Enviar para Telegram
print("\n📤 Enviando para Telegram...")
client = get_telegram_client()
if client:
    success = client.send(scanner_msg)
    if success:
        print("✅ Análise completa enviada para o Telegram!")
    else:
        print("❌ Falha ao enviar para o Telegram")
else:
    print("⚠️ Cliente Telegram não disponível")
