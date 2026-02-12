"""
Sistema de logging refatorado para trading bot.

API pública e retrocompatibilidade com código existente.

Migration Guide:
--------------
Antes:
    from utils.logger import get_logger, log_error, log_agent
    
Depois:
    from utils.logging import get_logger, log_error, log_agent

O uso permanece idêntico:
    logger = get_logger("TradingBot")
    logger.agent("AGENT_EXECUTION", "mensagem", "module", 
                 agent_name="Trade Conductor", symbol=cripto)
                 
Novidades:
    - Categorias e níveis são Enums (type-safe)
    - Suporte a sistema de eventos para extensibilidade
    - Telegram desacoplado do logging core
"""

from typing import Optional, Any

from .enums import LogLevel, LogCategory
from .models import LogEvent, LogConfig
from .logger import TradingLogger, get_logger, setup_logger
from .config import ConfigManager, load_config
from ..notifications.events import get_event_emitter
from ..notifications.telegram import setup_telegram_notifications


# API principal
__all__ = [
    # Enums
    'LogLevel',
    'LogCategory',
    # Models
    'LogEvent',
    'LogConfig',
    # Logger
    'TradingLogger',
    'get_logger',
    'setup_logger',
    # Config
    'ConfigManager',
    'load_config',
    # Notifications
    'setup_telegram_notifications',
    # Funções de conveniência (retrocompatibilidade)
    'log_debug',
    'log_info',
    'log_warning',
    'log_error',
    'log_critical',
    'log_agent',
]


# ============================================================================
# Funções de conveniência para retrocompatibilidade
# ============================================================================

def _ensure_category(category: Any) -> LogCategory:
    """Garante que categoria é LogCategory (aceita string para compatibilidade)."""
    if isinstance(category, str):
        try:
            return LogCategory(category)
        except ValueError:
            # Se não for categoria válida, usar genérica
            return LogCategory.INFO
    return category


def log_debug(message: str, category: Any = "DEBUG", module: Optional[str] = None, **kwargs) -> None:
    """
    Função de conveniência para logs de debug.
    
    Compatível com API antiga que aceita strings como categoria.
    """
    logger = get_logger("TradingBot")
    cat = _ensure_category(category)
    logger.debug(cat, message, module, **kwargs)


def log_info(message: str, category: Any = "SYSTEM", module: Optional[str] = None, **kwargs) -> None:
    """
    Função de conveniência para logs informativos.
    
    Compatível com API antiga que aceita strings como categoria.
    """
    logger = get_logger("TradingBot")
    cat = _ensure_category(category)
    logger.info(cat, message, module, **kwargs)


def log_warning(message: str, category: Any = "WARNING", module: Optional[str] = None, **kwargs) -> None:
    """
    Função de conveniência para logs de aviso.
    
    Compatível com API antiga que aceita strings como categoria.
    """
    logger = get_logger("TradingBot")
    cat = _ensure_category(category)
    logger.warning(cat, message, module, **kwargs)


def log_error(
    message: str,
    category: Any = "ERROR",
    module: Optional[str] = None,
    exception: Optional[Exception] = None,
    **kwargs
) -> None:
    """
    Função de conveniência para logs de erro.
    
    Compatível com API antiga que aceita strings como categoria.
    """
    logger = get_logger("TradingBot")
    cat = _ensure_category(category)
    logger.error(cat, message, module, exception, **kwargs)


def log_critical(
    message: str,
    category: Any = "CRITICAL_ERROR",
    module: Optional[str] = None,
    exception: Optional[Exception] = None,
    **kwargs
) -> None:
    """
    Função de conveniência para logs críticos.
    
    Compatível com API antiga que aceita strings como categoria.
    """
    logger = get_logger("TradingBot")
    cat = _ensure_category(category)
    logger.critical(cat, message, module, exception, **kwargs)


def log_agent(
    message: str,
    category: Any = "AGENT_ACTION",
    module: Optional[str] = None,
    agent_name: str = "Trade Conductor",
    **kwargs
) -> None:
    """
    Função de conveniência para logs de agentes.
    
    Compatível com API antiga que aceita strings como categoria.
    """
    logger = get_logger("TradingBot")
    cat = _ensure_category(category)
    logger.agent(cat, message, module, agent_name, **kwargs)


# ============================================================================
# Setup e inicialização
# ============================================================================

def initialize_logging(
    config: Optional[LogConfig] = None,
    enable_telegram: bool = False,
    telegram_categories: Optional[list] = None
) -> TradingLogger:
    """
    Inicializa sistema de logging completo.
    
    Args:
        config: Configuração personalizada (usa padrão se None)
        enable_telegram: Se deve habilitar notificações Telegram
        telegram_categories: Categorias para notificar no Telegram
        
    Returns:
        TradingLogger configurado
    """
    # Criar logger
    logger = setup_logger("TradingBot", config)
    
    # Configurar Telegram se solicitado
    if enable_telegram:
        categories = None
        if telegram_categories:
            categories = {LogCategory(cat) for cat in telegram_categories}
        
        setup_telegram_notifications(
            event_emitter=get_event_emitter(),
            enabled=True,
            categories=categories,
            rate_limit=1.0
        )
    
    return logger

