"""
Script para testar as credenciais configuradas
"""
import os
from dotenv import load_dotenv

print("🔍 Verificando configuração de credenciais...\n")

# Carregar variáveis de ambiente
load_dotenv()

# Verificar Bybit
bybit_key = os.getenv('BYBIT_API_KEY')
bybit_secret = os.getenv('BYBIT_API_SECRET')

print("📊 BYBIT:")
if bybit_key and len(bybit_key) > 10:
    print(f"  ✅ API Key: {bybit_key[:8]}...{bybit_key[-4:]}")
else:
    print("  ❌ API Key não configurada")

if bybit_secret and len(bybit_secret) > 10:
    print(f"  ✅ API Secret: {bybit_secret[:8]}...{bybit_secret[-4:]}")
else:
    print("  ❌ API Secret não configurado")

# Verificar Google Gemini
google_key = os.getenv('GOOGLE_API_KEY')
print("\n🤖 GOOGLE GEMINI:")
if google_key and len(google_key) > 10:
    print(f"  ✅ API Key: {google_key[:8]}...{google_key[-4:]}")
else:
    print("  ❌ API Key não configurada (OBRIGATÓRIA)")

# Verificar Anthropic
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
print("\n🧠 ANTHROPIC CLAUDE:")
if anthropic_key and len(anthropic_key) > 10:
    print(f"  ✅ API Key: {anthropic_key[:8]}...{anthropic_key[-4:]}")
else:
    print("  ⚠️  API Key não configurada (opcional)")

# Verificar Telegram
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
print("\n📱 TELEGRAM:")
if telegram_token:
    print(f"  ✅ Bot Token configurado")
else:
    print("  ⚠️  Bot Token não configurado (opcional)")
if telegram_chat:
    print(f"  ✅ Chat ID: {telegram_chat}")
else:
    print("  ⚠️  Chat ID não configurado (opcional)")

# Testar conexão com Bybit
print("\n\n🔌 Testando conexão com Bybit...")
try:
    from pybit.unified_trading import HTTP
    
    if bybit_key and bybit_secret:
        client = HTTP(api_key=bybit_key, api_secret=bybit_secret, testnet=False)
        result = client.get_wallet_balance(accountType="UNIFIED")
        
        if result['retCode'] == 0:
            print("  ✅ Conexão com Bybit estabelecida!")
            print(f"  📈 Tipo de conta: {result.get('result', {}).get('accountType', 'N/A')}")
        else:
            print(f"  ❌ Erro na conexão: {result.get('retMsg', 'Desconhecido')}")
    else:
        print("  ⏭️  Pulando teste (credenciais não configuradas)")
except Exception as e:
    print(f"  ❌ Erro ao conectar: {str(e)}")

# Testar Google Gemini
print("\n🔌 Testando conexão com Google Gemini...")
try:
    if google_key:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Responda apenas 'OK'")
        print(f"  ✅ Google Gemini funcionando! Resposta: {response.text.strip()}")
    else:
        print("  ⏭️  Pulando teste (API Key não configurada)")
except Exception as e:
    print(f"  ❌ Erro ao conectar: {str(e)}")

print("\n" + "="*50)
print("\n💡 RESUMO:")
can_trade = bybit_key and bybit_secret and google_key
if can_trade:
    print("  ✅ Tudo pronto para executar o bot!")
else:
    print("  ❌ Configure as credenciais obrigatórias:")
    if not (bybit_key and bybit_secret):
        print("     - BYBIT_API_KEY e BYBIT_API_SECRET")
    if not google_key:
        print("     - GOOGLE_API_KEY (obrigatória)")
print("\n" + "="*50)
