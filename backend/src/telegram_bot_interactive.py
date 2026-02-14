"""
Bot Telegram Interativo - Recebe comandos e retorna análises
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from corretoras.funcoes_bybit import cliente, busca_velas
from managers.data_manager import prepare_market_data
import pandas_ta as ta

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print("🤖 Bot Telegram Interativo Iniciando...")
print(f"📱 Chat ID autorizado: {CHAT_ID}")

# Função para analisar uma moeda
def analisar_moeda(symbol: str) -> str:
    """Analisa uma moeda e retorna relatório detalhado"""
    try:
        # Garantir formato correto
        if not symbol.endswith('USDT'):
            symbol = symbol.upper() + 'USDT'
        else:
            symbol = symbol.upper()
        
        print(f"📊 Analisando {symbol}...")
        
        # Buscar dados
        resp = cliente.get_kline(
            category="linear",
            symbol=symbol,
            interval="60",
            limit=200
        )
        
        if not resp or 'result' not in resp or not resp['result']['list']:
            return f"❌ Erro ao buscar dados para {symbol}. Verifique se o símbolo está correto."
        
        klines = resp['result']['list'][::-1]
        df = pd.DataFrame(klines, columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'turnover'])
        df[['open', 'high', 'low', 'close', 'vol']] = df[['open', 'high', 'low', 'close', 'vol']].astype(float)
        
        # Calcular indicadores
        ema20 = ta.ema(df['close'], length=20)
        ema50 = ta.ema(df['close'], length=50)
        ema200 = ta.ema(df['close'], length=200)
        rsi = ta.rsi(df['close'], length=14)
        
        last_close = df['close'].iloc[-1]
        last_vol = df['vol'].iloc[-1]
        avg_vol = df['vol'].tail(20).mean()
        last_rsi = rsi.iloc[-1]
        
        # Sistema de pontuação
        score = 0
        score_details = []
        
        if last_close > ema200.iloc[-1]:
            score += 1
            score_details.append("✅ Preço acima EMA 200")
        else:
            score_details.append("❌ Preço abaixo EMA 200")
        
        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 1
            score_details.append("✅ EMA 20 > EMA 50")
        else:
            score_details.append("❌ EMA 20 < EMA 50")
        
        if 45 <= last_rsi <= 65:
            score += 1
            score_details.append("✅ RSI em zona neutra")
        elif last_rsi > 65:
            score_details.append("⚠️ RSI sobrecomprado")
        else:
            score_details.append("⚠️ RSI sobrevendido")
        
        if last_vol > (avg_vol * 1.2):
            score += 1
            score_details.append("✅ Volume acima da média")
        else:
            score_details.append("❌ Volume normal/baixo")
        
        prev_high = df['high'].iloc[-2]
        if last_close > prev_high:
            score += 1
            score_details.append("✅ Breakout de alta")
        else:
            score_details.append("❌ Sem breakout")
        
        # Determinar tendência
        if last_close > ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
            trend = "🟢 Alta Forte"
            trend_emoji = "🚀"
        elif last_close > ema20.iloc[-1] > ema50.iloc[-1]:
            trend = "🟢 Alta"
            trend_emoji = "📈"
        elif last_close < ema20.iloc[-1] < ema50.iloc[-1] < ema200.iloc[-1]:
            trend = "🔴 Baixa Forte"
            trend_emoji = "📉"
        elif last_close < ema20.iloc[-1] < ema50.iloc[-1]:
            trend = "🔴 Baixa"
            trend_emoji = "📉"
        else:
            trend = "⚪ Lateral"
            trend_emoji = "➡️"
        
        # Recomendação
        if score >= 4:
            recomendacao = "🔥 FORTE OPORTUNIDADE"
            recom_emoji = "💎"
        elif score >= 3:
            recomendacao = "✨ BOA OPORTUNIDADE"
            recom_emoji = "👍"
        elif score >= 2:
            recomendacao = "⚠️ OPORTUNIDADE MODERADA"
            recom_emoji = "⚖️"
        else:
            recomendacao = "❌ EVITAR NO MOMENTO"
            recom_emoji = "🛑"
        
        # Formatar preço
        price_str = f"${last_close:,.2f}" if last_close >= 1 else f"${last_close:.6f}"
        
        # Montar relatório
        report = f"""
{trend_emoji} <b>ANÁLISE: {symbol}</b>

📊 <b>PONTUAÇÃO: {score}/5</b>
{recom_emoji} <b>Recomendação:</b> {recomendacao}

💰 <b>Preço Atual:</b> {price_str}
📈 <b>Tendência:</b> {trend}
📊 <b>RSI (14):</b> {last_rsi:.1f}
📉 <b>Vol vs Média:</b> {(last_vol/avg_vol*100):.0f}%

<b>🔍 Análise Detalhada:</b>
{chr(10).join(score_details)}

<b>📉 EMAs:</b>
• EMA 20: ${ema20.iloc[-1]:,.2f}
• EMA 50: ${ema50.iloc[-1]:,.2f}
• EMA 200: ${ema200.iloc[-1]:,.2f}

💡 <b>Para tradear este ativo:</b>
<code>python src/live_trading/double_ema_breakout_orders_long_short_dual_params_agent_evaluator.py --cripto {symbol} --is_simulator</code>

#TradingBot #{symbol.replace('USDT', '')}
        """
        
        return report.strip()
        
    except Exception as e:
        return f"❌ Erro ao analisar {symbol}: {str(e)}"

# Comandos do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user_id = str(update.effective_chat.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Usuário não autorizado.")
        return
    
    await update.message.reply_text(
        """🤖 <b>Bot de Trading Ativo!</b>

📊 <b>Comandos disponíveis:</b>

🔍 <b>Análise de Moedas:</b>
• Envie o nome da moeda (ex: BTC, ETH, SOL)
• /analise BTC - Análise detalhada

📈 <b>Scanner:</b>
• /top10 - Top 10 melhores oportunidades
• /scan - Última varredura do scanner

ℹ️ <b>Informações:</b>
• /status - Status do bot
• /ajuda - Lista de comandos

💡 <b>Exemplo:</b>
Envie: <code>BTC</code> ou <code>/analise ETH</code>
""", parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda"""
    await start(update, context)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    user_id = str(update.effective_chat.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Usuário não autorizado.")
        return
    
    await update.message.reply_text(
        """✅ <b>Bot Operacional</b>

🤖 Sistema de análise ativo
📊 Scanner monitorando mercado
📱 Telegram conectado
🔐 API Bybit OK

💡 Envie o nome de uma moeda para análise!
""", parse_mode='HTML')

async def analise_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /analise SÍMBOLO"""
    user_id = str(update.effective_chat.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Usuário não autorizado.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /analise BTC")
        return
    
    symbol = context.args[0]
    await update.message.reply_text("🔄 Analisando... aguarde.")
    
    resultado = analisar_moeda(symbol)
    await update.message.reply_text(resultado, parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto (nome da moeda)"""
    user_id = str(update.effective_chat.id)
    
    if user_id != CHAT_ID:
        await update.message.reply_text("❌ Usuário não autorizado.")
        return
    
    text = update.message.text.strip().upper()
    
    # Verificar se é um símbolo de moeda
    if len(text) >= 2 and len(text) <= 10:
        await update.message.reply_text("🔄 Analisando... aguarde.")
        resultado = analisar_moeda(text)
        await update.message.reply_text(resultado, parse_mode='HTML')
    else:
        await update.message.reply_text(
            "💡 Envie o nome da moeda (ex: BTC, ETH, SOL)\n"
            "Ou use /ajuda para ver comandos."
        )

# Função principal
async def main():
    """Inicia o bot"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env")
        return
    
    # Criar aplicação
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Adicionar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("analise", analise_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot Telegram Interativo rodando!")
    print("💡 Envie uma mensagem com o nome de uma moeda (ex: BTC)")
    print("⏸️  Pressione Ctrl+C para parar\n")
    
    # Iniciar bot
    await app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import pandas as pd
    asyncio.run(main())
