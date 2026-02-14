"""
Bot Telegram via Webhook/Polling Simplificado
Analisa moedas quando você enviar o nome pelo Telegram!
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import time
import requests
from dotenv import load_dotenv
from corretoras.funcoes_bybit import cliente
import pandas as pd
import pandas_ta as ta

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("🤖 Bot Telegram Interativo (Polling)")
print(f"📱 Autorizado para: {CHAT_ID}\n")

def send_message(text):
    """Envia mensagem para o Telegram"""
    try:
        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })
        return True
    except Exception as e:
        print(f"Erro ao enviar: {e}")
        return False

def analisar_moeda(symbol):
    """Analisa moeda"""
    try:
        if not symbol.endswith('USDT'):
            symbol = symbol.upper() + 'USDT'
        else:
            symbol = symbol.upper()
        
        resp = cliente.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        
        if not resp or 'result' not in resp or not resp['result']['list']:
            return f"❌ Símbolo {symbol} não encontrado."
        
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
            rec = "🔥 FORTE"
        elif score >= 3:
            rec = "✨ BOA"
        elif score >= 2:
            rec = "⚠️ MODERADA"
        else:
            rec = "❌ EVITAR"
        
        price = f"${last_close:,.2f}" if last_close >= 1 else f"${last_close:.6f}"
        
        return f"""<b>🔍 ANÁLISE: {symbol}</b>

<b>📊 SCORE: {score}/5</b>
{rec}

<b>💰 Preço:</b> {price}
<b>📈 Tendência:</b> {trend}
<b>📊 RSI:</b> {last_rsi:.1f}
<b>📈 Volume:</b> {(last_vol/avg_vol*100):.0f}%

<b>Detalhes:</b>
{chr(10).join(details)}

<b>EMAs:</b>
• 20: ${ema20.iloc[-1]:,.2f}
• 50: ${ema50.iloc[-1]:,.2f}
• 200: ${ema200.iloc[-1]:,.2f}

💡 <b>Para tradear:</b>
<code>--cripto {symbol} --is_simulator</code>

#{symbol.replace('USDT', '')} #TradingBot
"""
    except Exception as e:
        return f"❌ Erro: {str(e)}"

def get_updates(offset=None):
    """Busca atualizações do Telegram"""
    try:
        params = {"timeout": 30, "offset": offset}
        resp = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar updates: {e}")
        return {"ok": False}

def process_message(message):
    """Processa mensagem recebida"""
    chat_id = str(message['chat']['id'])
    
    if chat_id != CHAT_ID:
        send_message("❌ Não autorizado.")
        return
    
    text = message.get('text', '').strip()
    
    if text == '/start' or text == '/ajuda':
        send_message("""🤖 <b>BOT ATIVO!</b>

📊 <b>Como usar:</b>
• Envie: BTC, ETH, SOL
• /status - Ver status

💡 <b>Exemplo:</b>
Envie: BTC""")
    
    elif text == '/status':
        send_message("""✅ <b>OPERACIONAL</b>

🤖 Sistema ativo
📊 Scanner OK
📱 Telegram OK

<i>Envie uma moeda!</i>""")
    
    elif len(text) >= 2 and len(text) <= 10 and not text.startswith('/'):
        send_message("🔄 Analisando...")
        print(f"📊 Analisando {text}...")
        resultado = analisar_moeda(text)
        send_message(resultado)
    
    elif text and not text.startswith('/'):
        send_message("💡 Envie: BTC, ETH, SOL\nOu /ajuda")

def main():
    """Loop principal"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Configure .env")
        return
    
    # Enviar mensagem de início
    send_message("""🤖 <b>Bot Interativo Ativo!</b>

Envie o nome de uma moeda para análise completa!

<b>Exemplos:</b> BTC, ETH, SOL""")
    
    print("✅ Bot rodando!")
    print("💡 Envie uma moeda no Telegram")
    print("⏸️  Ctrl+C para parar\n")
    
    offset = None
    
    try:
        while True:
            updates = get_updates(offset)
            
            if not updates.get('ok'):
                time.sleep(5)
                continue
            
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                
                if 'message' in update:
                    message = update['message']
                    print(f"📨 Mensagem recebida: {message.get('text', '')}")
                    process_message(message)
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n⏸️  Bot parado!")
        send_message("⏸️ Bot pausado.")

if __name__ == '__main__':
    main()
