"""
Bot Telegram Interativo Simplificado
Envia o nome da moeda e recebe análise completa!
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from corretoras.funcoes_bybit import cliente
import pandas as pd
import pandas_ta as ta

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print("🤖 Bot Telegram Interativo Iniciando...")
print(f"📱 Chat ID autorizado: {CHAT_ID}\n")

def analisar_moeda(symbol: str) -> str:
    """Analisa uma moeda e retorna relatório"""
    try:
        if not symbol.endswith('USDT'):
            symbol = symbol.upper() + 'USDT'
        else:
            symbol = symbol.upper()
        
        print(f"📊 Analisando {symbol}...")
        
        resp = cliente.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        
        if not resp or 'result' not in resp or not resp['result']['list']:
            return f"❌ Erro: Símbolo {symbol} não encontrado."
        
        klines = resp['result']['list'][::-1]
        df = pd.DataFrame(klines, columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'turnover'])
        df[['open', 'high', 'low', 'close', 'vol']] = df[['open', 'high', 'low', 'close', 'vol']].astype(float)
        
        # Indicadores
        ema20 = ta.ema(df['close'], length=20)
        ema50 = ta.ema(df['close'], length=50)
        ema200 = ta.ema(df['close'], length=200)
        rsi = ta.rsi(df['close'], length=14)
        
        last_close = df['close'].iloc[-1]
        last_vol = df['vol'].iloc[-1]
        avg_vol = df['vol'].tail(20).mean()
        last_rsi = rsi.iloc[-1]
        
        # Pontuação
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
        
        # Tendência
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
        
        # Recomendação
        if score >= 4:
            rec = "🔥 FORTE"
        elif score >= 3:
            rec = "✨ BOA"
        elif score >= 2:
            rec = "⚠️ MODERADA"
        else:
            rec = "❌ EVITAR"
        
        price = f"${last_close:,.2f}" if last_close >= 1 else f"${last_close:.6f}"
        
        return f"""🔍 ANÁLISE: {symbol}

📊 SCORE: {score}/5
{rec}

💰 Preço: {price}
{trend}
📊 RSI: {last_rsi:.1f}
📈 Vol: {(last_vol/avg_vol*100):.0f}%

{chr(10).join(details)}

EMAs:
20: ${ema20.iloc[-1]:,.2f}
50: ${ema50.iloc[-1]:,.2f}
200: ${ema200.iloc[-1]:,.2f}

💡 Comando:
python src/live_trading/...evaluator.py --cripto {symbol} --is_simulator
"""
    except Exception as e:
        return f"❌ Erro: {str(e)}"

def start(update, context):
    """Comando /start"""
    user_id = str(update.effective_chat.id)
    if user_id != CHAT_ID:
        update.message.reply_text("❌ Não autorizado.")
        return
    
    update.message.reply_text("""🤖 BOT ATIVO!

📊 COMANDOS:
• Envie: BTC, ETH, SOL
• /analise BTC
• /status
• /ajuda

💡 Exemplo: BTC""")

def status(update, context):
    """Comando /status"""
    user_id = str(update.effective_chat.id)
    if user_id != CHAT_ID:
        return
    
    update.message.reply_text("""✅ OPERACIONAL

🤖 Sistema ativo
📊 Scanner OK
📱 Telegram OK
🔐 Bybit OK

Envie uma moeda!""")

def analise(update, context):
    """Comando /analise"""
    user_id = str(update.effective_chat.id)
    if user_id != CHAT_ID:
        return
    
    if not context.args:
        update.message.reply_text("❌ Use: /analise BTC")
        return
    
    symbol = context.args[0]
    update.message.reply_text("🔄 Analisando...")
    resultado = analisar_moeda(symbol)
    update.message.reply_text(resultado)

def handle_text(update, context):
    """Mensagens de texto"""
    user_id = str(update.effective_chat.id)
    if user_id != CHAT_ID:
        return
    
    text = update.message.text.strip().upper()
    
    if 2 <= len(text) <= 10:
        update.message.reply_text("🔄 Analisando...")
        resultado = analisar_moeda(text)
        update.message.reply_text(resultado)
    else:
        update.message.reply_text("💡 Envie: BTC, ETH, SOL\nOu /ajuda")

def main():
    """Inicia bot"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Configure .env com TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")
        return
    
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ajuda", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("analise", analise))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Bot rodando!")
    print("💡 Envie uma moeda no Telegram (ex: BTC)")
    print("⏸️  Ctrl+C para parar\n")
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
