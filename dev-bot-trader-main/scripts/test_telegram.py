#!/usr/bin/env python3
"""
scripts/test_telegram.py
Envia uma mensagem de teste usando o cliente Telegram do projeto.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Garantir que o pacote `src` esteja no PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT, 'src'))

try:
    from utils.notifications.telegram_client import get_telegram_client
except Exception as e:
    print("Erro ao importar o cliente do projeto:", e)
    sys.exit(1)


def main():
    client = get_telegram_client()
    if client is None:
        print("Telegram client não disponível. Verifique se 'python-telegram-bot' está instalado e as variáveis de ambiente.")
        return

    message = "🤖 Mensagem de teste: verificação do bot do projeto. ✅"
    ok = client.send(message)
    if ok:
        print("✅ Mensagem enviada com sucesso")
    else:
        print("❌ Falha ao enviar mensagem")


if __name__ == '__main__':
    main()
