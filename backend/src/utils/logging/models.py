"""
Modelos de dados para o sistema de logging.

Usa dataclasses para objetos de domínio e Pydantic para configuração.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from pydantic import BaseModel, Field, field_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback para dataclasses se Pydantic não estiver disponível
    PYDANTIC_AVAILABLE = False
    BaseModel = object

from .enums import LogLevel, LogCategory


@dataclass
class LogEvent:
    """
    Evento de log imutável que representa uma mensagem de log.
    
    Substitui o uso de strings + dicionários por um objeto tipado.
    """
    level: LogLevel
    category: LogCategory
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    module: Optional[str] = None
    agent_name: Optional[str] = None
    bot_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[Exception] = None
    
    def __post_init__(self):
        """Validação após inicialização."""
        # Garantir que level é LogLevel
        if isinstance(self.level, str):
            self.level = LogLevel[self.level.upper()]
        elif isinstance(self.level, int):
            self.level = LogLevel(self.level)
        
        # Garantir que category é LogCategory
        if isinstance(self.category, str):
            try:
                self.category = LogCategory(self.category)
            except ValueError:
                # Se não for uma categoria válida, usar genérica
                self.category = LogCategory.INFO
    
    @property
    def is_error(self) -> bool:
        """Verifica se é um evento de erro."""
        return self.level >= LogLevel.ERROR or LogCategory.is_error_category(self.category)
    
    @property
    def is_agent_event(self) -> bool:
        """Verifica se é um evento de agente."""
        return LogCategory.is_agent_category(self.category)
    
    @property
    def is_trading_event(self) -> bool:
        """Verifica se é um evento de trading."""
        return LogCategory.is_trading_category(self.category)
    
    @property
    def is_system_event(self) -> bool:
        """Verifica se é um evento de sistema."""
        return LogCategory.is_system_category(self.category)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'category': self.category.value,
            'message': self.message,
            'module': self.module,
            'agent_name': self.agent_name,
            'bot_id': self.bot_id,
            'context': self.context,
            'exception': str(self.exception) if self.exception else None
        }
    
    def format_for_display(self) -> str:
        """Formata evento para exibição simples."""
        parts = [
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            f"[{self.level.name}]",
            f"[{self.category.value}]"
        ]
        
        if self.agent_name:
            parts.append(f"[{self.agent_name}]")
        
        if self.module:
            parts.append(f"[{self.module}]")
        
        parts.append(self.message)
        
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"| {context_str}")
        
        return " ".join(parts)


# Modelos de configuração
if PYDANTIC_AVAILABLE:
    class HandlerConfig(BaseModel):
        """Configuração de um handler de log."""
        enabled: bool = True
        level: str = "DEBUG"
        path: Optional[str] = None
        format_type: str = "simple"
        categories: List[str] = Field(default_factory=list)
        rotation: str = "daily"
        keep_days: int = 30
        
        @field_validator('level')
        @classmethod
        def validate_level(cls, v: str) -> str:
            """Valida que o nível existe."""
            try:
                LogLevel[v.upper()]
            except KeyError:
                raise ValueError(f"Nível de log inválido: {v}")
            return v.upper()
    
    class LogConfig(BaseModel):
        """
        Configuração do sistema de logging.
        
        Type-safe com validação automática via Pydantic.
        """
        log_level: str = "DEBUG"
        console_enabled: bool = True
        console_level: str = "DEBUG"
        master_file_enabled: bool = True
        master_file_path: str = "logs/master/trading_bot_{date}.log"
        master_file_level: str = "DEBUG"
        telegram_enabled: bool = False
        telegram_categories: List[str] = Field(
            default_factory=lambda: ["AGENT_RESPONSE", "AGENT_ACTION", "AGENT_DECISION"]
        )
        handlers: Dict[str, HandlerConfig] = Field(default_factory=dict)
        
        @field_validator('log_level', 'console_level', 'master_file_level')
        @classmethod
        def validate_levels(cls, v: str) -> str:
            """Valida níveis de log."""
            try:
                LogLevel[v.upper()]
            except KeyError:
                raise ValueError(f"Nível de log inválido: {v}")
            return v.upper()
        
        @classmethod
        def from_dict(cls, config_dict: Dict[str, Any]) -> "LogConfig":
            """Cria configuração a partir de dicionário."""
            return cls(**config_dict)
        
        @classmethod
        def default(cls) -> "LogConfig":
            """Retorna configuração padrão."""
            return cls(
                log_level="DEBUG",
                console_enabled=True,
                console_level="DEBUG",
                master_file_enabled=True,
                master_file_level="DEBUG",
                telegram_enabled=False,
                handlers={
                    "errors": HandlerConfig(
                        enabled=True,
                        level="ERROR",
                        path="logs/specialized/errors/exceptions_{date}.log",
                        format_type="detailed",
                        categories=[
                            "EXCEPTION", "CONNECTION_ERROR", "API_ERROR",
                            "CRITICAL_ERROR", "PARSING_ERROR", "VALUE_ERROR",
                            "EXECUTION_ERROR"
                        ]
                    ),
                    "agents": HandlerConfig(
                        enabled=True,
                        level="INFO",
                        path="logs/specialized/agents/decisions_{date}.log",
                        format_type="simple",
                        categories=[
                            "AGENT_RESPONSE", "AGENT_DECISION", "AGENT_ACTION",
                            "AGENT_EXECUTION", "AGENT_SCHEDULE"
                        ]
                    ),
                    "system": HandlerConfig(
                        enabled=True,
                        level="INFO",
                        path="logs/specialized/system/system_{date}.log",
                        format_type="simple",
                        categories=[
                            "BOT_START", "BOT_STOP", "SYSTEM_INIT",
                            "CONFIGURATION", "INITIALIZATION", "SHUTDOWN", "RESTART"
                        ]
                    ),
                    "trading": HandlerConfig(
                        enabled=True,
                        level="INFO",
                        path="logs/specialized/trading/operations_{date}.log",
                        format_type="simple",
                        categories=[
                            "POSITION_OPEN", "POSITION_UPDATE", "POSITION_CLOSE",
                            "POSITION_STATUS", "TARGET_HIT", "STOP_HIT",
                            "MANUAL_CLOSE", "TRADE_SEARCH"
                        ]
                    )
                }
            )

else:
    # Fallback para dataclasses se Pydantic não disponível
    @dataclass
    class HandlerConfig:
        """Configuração de um handler de log."""
        enabled: bool = True
        level: str = "DEBUG"
        path: Optional[str] = None
        format_type: str = "simple"
        categories: List[str] = field(default_factory=list)
        rotation: str = "daily"
        keep_days: int = 30
    
    @dataclass
    class LogConfig:
        """Configuração do sistema de logging."""
        log_level: str = "DEBUG"
        console_enabled: bool = True
        console_level: str = "DEBUG"
        master_file_enabled: bool = True
        master_file_path: str = "logs/master/trading_bot_{date}.log"
        master_file_level: str = "DEBUG"
        telegram_enabled: bool = False
        telegram_categories: List[str] = field(
            default_factory=lambda: ["AGENT_RESPONSE", "AGENT_ACTION", "AGENT_DECISION"]
        )
        handlers: Dict[str, HandlerConfig] = field(default_factory=dict)
        
        @classmethod
        def default(cls) -> "LogConfig":
            """Retorna configuração padrão."""
            return cls(
                log_level="DEBUG",
                console_enabled=True,
                console_level="DEBUG",
                master_file_enabled=True,
                master_file_level="DEBUG",
                telegram_enabled=False,
                handlers={
                    "errors": HandlerConfig(
                        enabled=True,
                        level="ERROR",
                        path="logs/specialized/errors/exceptions_{date}.log",
                        format_type="detailed",
                        categories=[
                            "EXCEPTION", "CONNECTION_ERROR", "API_ERROR",
                            "CRITICAL_ERROR", "PARSING_ERROR", "VALUE_ERROR",
                            "EXECUTION_ERROR"
                        ]
                    ),
                    "agents": HandlerConfig(
                        enabled=True,
                        level="INFO",
                        path="logs/specialized/agents/decisions_{date}.log",
                        format_type="simple",
                        categories=[
                            "AGENT_RESPONSE", "AGENT_DECISION", "AGENT_ACTION",
                            "AGENT_EXECUTION", "AGENT_SCHEDULE"
                        ]
                    ),
                    "system": HandlerConfig(
                        enabled=True,
                        level="INFO",
                        path="logs/specialized/system/system_{date}.log",
                        format_type="simple",
                        categories=[
                            "BOT_START", "BOT_STOP", "SYSTEM_INIT",
                            "CONFIGURATION", "INITIALIZATION", "SHUTDOWN", "RESTART"
                        ]
                    ),
                    "trading": HandlerConfig(
                        enabled=True,
                        level="INFO",
                        path="logs/specialized/trading/operations_{date}.log",
                        format_type="simple",
                        categories=[
                            "POSITION_OPEN", "POSITION_UPDATE", "POSITION_CLOSE",
                            "TRADE_SIGNAL", "POSITION_STATUS", "TARGET_HIT",
                            "STOP_HIT", "MANUAL_CLOSE"
                        ]
                    )
                }
            )

