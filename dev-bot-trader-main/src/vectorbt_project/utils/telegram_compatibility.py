"""
Utilitário para compatibilidade entre VectorBT e python-telegram-bot.

Este módulo resolve conflitos de versão entre VectorBT 0.27.2 e 
python-telegram-bot 22.x, permitindo usar a versão moderna do 
telegram-bot para notificações enquanto executa backtests.
"""

import sys
import types
from unittest.mock import MagicMock

def disable_vectorbt_messaging():
    """
    Desabilita o módulo messaging do VectorBT para evitar conflitos 
    com python-telegram-bot 22.x.
    
    Este patch deve ser chamado ANTES de importar vectorbt.
    
    Returns:
        bool: True se o patch foi aplicado com sucesso
    """
    try:
        # Verificar se já foi aplicado
        if 'vectorbt.messaging' in sys.modules:
            print("⚠️ Patch já aplicado anteriormente")
            return True
        
        # Criar módulo messaging falso com todos os atributos necessários
        messaging_module = types.ModuleType("vectorbt.messaging")
        
        # Adicionar __path__ para que pkgutil.walk_packages funcione
        messaging_module.__path__ = []  # Lista vazia indica que é um pacote sem subpacotes
        messaging_module.__package__ = "vectorbt.messaging"
        messaging_module.__spec__ = None
        messaging_module.__file__ = "<mock>"
        
        # Adicionar classes/funções vazias que o VectorBT pode esperar
        messaging_module.TelegramBot = MagicMock
        messaging_module.Telegram = MagicMock
        
        # Criar submódulo telegram também
        telegram_module = types.ModuleType("vectorbt.messaging.telegram")
        telegram_module.__package__ = "vectorbt.messaging.telegram"
        telegram_module.__spec__ = None
        telegram_module.__file__ = "<mock>"
        telegram_module.TelegramBot = MagicMock
        
        # Registrar os módulos no sys.modules ANTES do VectorBT tentar importá-los
        sys.modules['vectorbt.messaging'] = messaging_module
        sys.modules['vectorbt.messaging.telegram'] = telegram_module
        
        print("✅ Compatibilidade VectorBT x python-telegram-bot aplicada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar patch de compatibilidade: {str(e)}")
        return False

def apply_vectorbt_telegram_patch():
    """
    Alias para disable_vectorbt_messaging() com nome mais descritivo.
    """
    return disable_vectorbt_messaging()

# Para compatibilidade, aplicar automaticamente se importado diretamente
if __name__ != "__main__":
    # Só aplica se não estiver sendo executado como script principal
    pass