"""
TradingLogger refatorado - core do sistema de logging.

Mais simples, type-safe e extensível através de eventos.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .models import LogEvent, LogConfig
from .enums import LogLevel, LogCategory
from .formatters import get_formatter
from .handlers import FileHandlerFactory, CategoryFilterHandler, ConditionalHandler
from .config import ConfigManager
from ..notifications.events import get_event_emitter


class TradingLogger:
    """
    Logger principal do sistema de trading.
    
    Características:
    - Type-safe com Enums
    - Emite eventos para notificadores
    - Configuração simplificada
    - Handlers especializados por categoria
    """
    
    def __init__(self, name: str = "TradingBot", config: Optional[LogConfig] = None):
        """
        Inicializa o logger.
        
        Args:
            name: Nome do logger
            config: Configuração (usa padrão se None)
        """
        self.name = name
        self.config = config or LogConfig.default()
        self.event_emitter = get_event_emitter()
        
        # Logger interno do Python
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)  # Captura tudo, filtra nos handlers
        
        # Prevenir propagação para evitar duplicatas
        self._logger.propagate = False
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Configura handlers de log."""
        # Limpar handlers existentes
        self._logger.handlers.clear()
        
        # Console handler
        if self.config.console_enabled:
            self._add_console_handler()
        
        # Master file handler
        if self.config.master_file_enabled:
            self._add_master_file_handler()
        
        # Handlers especializados
        self._add_specialized_handlers()
    
    def _add_console_handler(self) -> None:
        """Adiciona handler de console."""
        console_handler = logging.StreamHandler()
        
        # Nível
        level = self._get_level_value(self.config.console_level)
        console_handler.setLevel(level)
        
        # Formatador (sem módulo para console)
        formatter = get_formatter('simple', use_colors=True, show_module=False)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_handler)
    
    def _add_master_file_handler(self) -> None:
        """Adiciona handler de arquivo master com rotação diária correta."""
        level = self._get_level_value(self.config.master_file_level)
        formatter = get_formatter('simple')
        
        # Usar DailyDateFileHandler para garantir nome correto do arquivo
        # mesmo quando bot roda 24/7 (resolve problema de data desatualizada)
        handler = FileHandlerFactory.create_daily_date_handler(
            filepath_pattern=self.config.master_file_path,  # Já tem {date}
            level=level,
            formatter=formatter,
            backup_count=90
        )
        
        self._logger.addHandler(handler)
    
    def _add_specialized_handlers(self) -> None:
        """Adiciona handlers especializados por categoria."""
        for handler_name, handler_config in self.config.handlers.items():
            if not handler_config.enabled:
                continue
            
            try:
                # Criar handler de arquivo
                level = self._get_level_value(handler_config.level)
                
                # Escolher formatador baseado no tipo
                if 'error' in handler_name or handler_config.format_type == 'error':
                    formatter = get_formatter('error')
                elif handler_config.format_type == 'detailed':
                    formatter = get_formatter('detailed')
                else:
                    formatter = get_formatter('simple')
                
                # Usar handler condicional (só cria arquivo quando necessário)
                file_handler = ConditionalHandler(
                    filepath=handler_config.path,
                    level=level,
                    formatter=formatter,
                    when='midnight',
                    backup_count=handler_config.keep_days
                )
                
                # Filtrar por categorias se especificadas
                if handler_config.categories:
                    categories = {LogCategory(cat) for cat in handler_config.categories}
                    filtered_handler = CategoryFilterHandler(
                        base_handler=file_handler,
                        categories=categories
                    )
                    self._logger.addHandler(filtered_handler)
                else:
                    self._logger.addHandler(file_handler)
                    
            except Exception as e:
                print(f"⚠️ Erro ao criar handler '{handler_name}': {e}")
    
    def _get_level_value(self, level_name: str) -> int:
        """Converte nome de nível para valor inteiro."""
        try:
            return LogLevel[level_name.upper()].value
        except KeyError:
            return LogLevel.INFO.value
    
    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        agent_name: Optional[str] = None,
        exception: Optional[Exception] = None,
        **context
    ) -> None:
        """
        Log principal - type-safe e emite eventos.
        
        Args:
            level: Nível do log (Enum)
            category: Categoria do log (Enum)
            message: Mensagem
            module: Módulo de origem
            agent_name: Nome do agente (se aplicável)
            exception: Exceção (se aplicável)
            **context: Contexto adicional como kwargs
        """
        # Criar LogEvent
        log_event = LogEvent(
            level=level,
            category=category,
            message=message,
            module=module,
            agent_name=agent_name,
            bot_id=self.name,
            exception=exception,
            context=context
        )
        
        # Criar LogRecord do Python logging
        record = self._logger.makeRecord(
            name=self._logger.name,
            level=level.value,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        # Anexar LogEvent ao record
        record.log_event = log_event
        
        # Log através do Python logging
        self._logger.handle(record)
        
        # Emitir evento para subscribers (Telegram, etc)
        self.event_emitter.emit('log_event', log_event)
    
    # Métodos de conveniência
    
    def debug(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        **context
    ) -> None:
        """Log de debug."""
        self.log(LogLevel.DEBUG, category, message, module=module, **context)
    
    def info(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        **context
    ) -> None:
        """Log informativo."""
        self.log(LogLevel.INFO, category, message, module=module, **context)
    
    def warning(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        **context
    ) -> None:
        """Log de aviso."""
        self.log(LogLevel.WARNING, category, message, module=module, **context)
    
    def error(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        exception: Optional[Exception] = None,
        **context
    ) -> None:
        """Log de erro."""
        self.log(LogLevel.ERROR, category, message, module=module, exception=exception, **context)
    
    def critical(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        exception: Optional[Exception] = None,
        **context
    ) -> None:
        """Log crítico."""
        self.log(LogLevel.CRITICAL, category, message, module=module, exception=exception, **context)
    
    def agent(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        agent_name: str = "Trade Conductor",
        **context
    ) -> None:
        """
        Log de agente.
        
        Args:
            category: Categoria (deve ser uma categoria de agente)
            message: Mensagem
            module: Módulo
            agent_name: Nome do agente
            **context: Contexto adicional
        """
        self.log(LogLevel.INFO, category, message, module=module, agent_name=agent_name, **context)
    
    def trading(
        self,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        **context
    ) -> None:
        """
        Log de operações de trading.
        
        Args:
            category: Categoria (deve ser uma categoria de trading)
            message: Mensagem
            module: Módulo
            **context: Contexto adicional (symbol, prices, etc)
        """
        self.log(LogLevel.TRADING, category, message, module=module, **context)


# Singleton pattern
_loggers: Dict[str, TradingLogger] = {}
_telegram_initialized: bool = False


def get_logger(name: str = "TradingBot", config: Optional[LogConfig] = None) -> TradingLogger:
    """
    Retorna logger (singleton por nome).
    
    Args:
        name: Nome do logger
        config: Configuração (opcional)
        
    Returns:
        TradingLogger
    """
    global _telegram_initialized
    
    if name not in _loggers:
        _loggers[name] = TradingLogger(name, config)
        
        # Inicializar Telegram automaticamente no primeiro logger (se configurado)
        if not _telegram_initialized:
            _telegram_initialized = True
            _try_initialize_telegram()
    
    return _loggers[name]


def _try_initialize_telegram():
    """
    Tenta inicializar notificações Telegram automaticamente.
    Só inicializa se as variáveis de ambiente estiverem configuradas.
    """
    import os
    
    # Verificar se Telegram está configurado
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        return  # Telegram não configurado, não inicializar
    
    try:
        from ..notifications.telegram import setup_telegram_notifications
        from ..notifications.events import get_event_emitter
        from .enums import LogCategory
        
        setup_telegram_notifications(
            event_emitter=get_event_emitter(),
            enabled=True,
            categories=None,
            rate_limit=0.1
        )
        
        # Substituir print por logger para escrita em master/ e specialized/system
        # print("✅ Notificações Telegram inicializadas automaticamente")
    except Exception as e:
        print(f"⚠️ Não foi possível inicializar notificações Telegram: {e}")


def setup_logger(name: str = "TradingBot", config: Optional[LogConfig] = None) -> TradingLogger:
    """
    Cria novo logger (substitui se já existir).
    
    Args:
        name: Nome do logger
        config: Configuração (opcional)
        
    Returns:
        TradingLogger
    """
    _loggers[name] = TradingLogger(name, config)
    return _loggers[name]

