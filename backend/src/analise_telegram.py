"""
Analisa moeda e envia resultado para o Telegram
Uso: python analise_telegram.py BTC
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv
from utils.notifications.telegram_client import get_telegram_client
from corretoras.funcoes_bybit import cliente
import pandas as pd
import pandas_ta as ta

load_dotenv()

if len(sys.argv) < 2:
    print("❌ Uso: python analise_telegram.py BTC")
    sys.exit(1)

symbol = sys.argv[1].upper()
if not symbol.endswith('USDT'):
    symbol += 'USDT'

print(f"🔍 Analisando {symbol}...")

try:
    resp = cliente.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
    
    if not resp or 'result' not in resp or not resp['result']['list']:
        print(f"❌ Símbolo {symbol} não encontrado.")
        sys.exit(1)
    
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
        details.append("✅ Acima EMA 200")
    else:
        details.append("❌ Abaixo EMA 200")
    
    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 1
        details.append("✅ EMA 20 > 50")
    else:
        details.append("❌ EMA 20 < 50")
    
    if 45 <= last_rsi <= 65:
        score += 1
        details.append("✅ RSI neutro")
    elif last_rsi > 65:
        details.append("⚠️ RSI alto")
    else:
        details.append("⚠️ RSI baixo")
    
    if last_vol > (avg_vol * 1.2):
        score += 1
        details.append("✅ Volume alto")
    else:
        details.append("❌ Volume normal")
    
    if last_close > df['high'].iloc[-2]:
        score += 1
        details.append("✅ Breakout")
    else:
        details.append("❌ Sem breakout")
    
    if last_close > ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
        trend = "🚀 Alta Forte"
    elif last_close > ema20.iloc[-1] > ema50.iloc[-1]:
        trend = "📈 Alta"
    elif last_close < ema20.iloc[-1] < ema50.iloc[-1] < ema200.iloc[-1]:
        trend = "📉 Baixa Forte"
    elif last_close < ema20.iloc[-1] < ema50.iloc[-1]:
        trend = "📉 Baixa"
    else:
        trend = "➡️ Lateral"
    
    if score >= 4:
        rec = "🔥 FORTE OPORTUNIDADE"
    elif score >= 3:
        rec = "✨ BOA OPORTUNIDADE"
    elif score >= 2:
        rec = "⚠️ OPORTUNIDADE MODERADA"
    else:
        rec = "❌ EVITAR NO MOMENTO"
    
    price = f"${last_close:,.2f}" if last_close >= 1 else f"${last_close:.6f}"
    
    message = f"""<b>🔍 ANÁLISE SOLICITADA: {symbol}</b>

<b>📊 PONTUAÇÃO: {score}/5</b>
<b>Recomendação:</b> {rec}

<b>💰 Preço Atual:</b> {price}
<b>📈 Tendência:</b> {trend}
<b>📊 RSI (14):</b> {last_rsi:.1f}
<b>📈 Volume vs Média:</b> {(last_vol/avg_vol*100):.0f}%

<b>🔍 Análise Detalhada:</b>
{chr(10).join(details)}

<b>📉 EMAs:</b>
• EMA 20: ${ema20.iloc[-1]:,.2f}
• EMA 50: ${ema50.iloc[-1]:,.2f}
• EMA 200: ${ema200.iloc[-1]:,.2f}

💡 <b>Para tradear este ativo:</b>
<code>python src/live_trading/...evaluator.py --cripto {symbol} --is_simulator</code>

#{symbol.replace('USDT', '')} #TradingBot #Análise
"""
    
    print(message.replace('<b>', '').replace('</b>', '').replace('<code>', '').replace('</code>', ''))
    
    # Enviar para Telegram
    print("\n📤 Enviando para Telegram...")
    client = get_telegram_client()
    if client:
        client.send(message)
        print("✅ Análise enviada para o Telegram!")
    else:
        print("⚠️ Cliente Telegram não disponível")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
