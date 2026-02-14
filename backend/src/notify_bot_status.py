"""
Enviar notificação de status do bot pelo Telegram
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv
from utils.notifications.telegram_client import get_telegram_client
from datetime import datetime

load_dotenv()

client = get_telegram_client()

if client:
    message = f"""
🤖 <b>BOT DE TRADING ATIVO</b>

✅ <b>Status:</b> Operacional
📊 <b>Modo:</b> Simulação
⏰ <b>Iniciado:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

<b>📈 Configuração:</b>
• <b>Par:</b> BTCUSDT
• <b>Timeframe:</b> 15 minutos
• <b>Estratégia:</b> Double EMA Breakout
• <b>EMAs Compra:</b> 5 / 15
• <b>EMAs Venda:</b> 21 / 125
• <b>Risco:</b> 1% por operação
• <b>Operações:</b> Long & Short (ambos)

<b>🔍 Estado Atual:</b>
🔵 Sem posição aberta
🔎 Procurando oportunidades de trade

<b>🤖 Agente IA:</b> Google Gemini Flash
<b>📱 Notificações:</b> Ativas

<i>Bot monitorando mercado em tempo real...</i>
    """
    
    success = client.send(message)
    if success:
        print("✅ Notificação de status enviada para o Telegram!")
    else:
        print("❌ Falha ao enviar notificação")
else:
    print("❌ Cliente Telegram não disponível")
