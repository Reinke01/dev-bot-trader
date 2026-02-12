"""
Módulos utilitários para o projeto VectorBT.

Este pacote contém funções comuns reutilizáveis para:
- Relatórios e exibição de resultados
- Plotagem e visualização
- Gerenciamento de resultados
- Configurações de plotagem
- Compatibilidade com python-telegram-bot
"""

from .telegram_compatibility import disable_vectorbt_messaging, apply_vectorbt_telegram_patch

__all__ = [
    'disable_vectorbt_messaging',
    'apply_vectorbt_telegram_patch'
]