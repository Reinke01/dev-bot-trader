"""
Teste de integração com Telegram
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv

print("📱 Testando integração com Telegram...\n")

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print(f"✅ Bot Token: {bot_token[:10]}...{bot_token[-10:]}")
print(f"✅ Chat ID: {chat_id}")

# Testar envio de mensagem
print("\n📤 Enviando mensagem de teste...\n")

try:
    from utils.notifications.telegram_client import get_telegram_client
    
    client = get_telegram_client()
    
    if client:
        message = """
🤖 <b>Bot de Trading - Teste de Comunicação</b>

✅ Conexão com Telegram estabelecida!
📊 Bot operacional
⏰ Data/Hora: {datetime}

🎯 <b>Configuração Atual:</b>
• Modo: Simulação
• Cripto: BTCUSDT
• Timeframe: 15 minutos
• Estratégia: Double EMA Breakout

<i>Sistema de notificações funcionando!</i>
        """.format(datetime=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        success = client.send(message)
        
        if success:
            print("✅ Mensagem enviada com sucesso!")
            print("\n📱 Verifique seu Telegram!")
        else:
            print("❌ Falha ao enviar mensagem")
    else:
        print("❌ Não foi possível criar cliente Telegram")
        
except Exception as e:
    print(f"❌ Erro ao enviar mensagem: {e}")
    import traceback
    traceback.print_exc()
