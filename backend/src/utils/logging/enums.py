"""
Enums para o sistema de logging.

Define níveis e categorias de log de forma type-safe.
"""

import logging
from enum import Enum
from typing import Set


class LogLevel(int, Enum):
    """
    Níveis de log type-safe.
    
    Compatível com logging.LEVEL padrão + níveis customizados.
    """
    CRITICAL = logging.CRITICAL  # 50
    ERROR = logging.ERROR        # 40
    WARNING = logging.WARNING    # 30
    INFO = logging.INFO          # 20
    DEBUG = logging.DEBUG        # 10
    NOTSET = logging.NOTSET      # 0
    
    # Níveis customizados
    TRADING = 25  # Entre INFO e WARNING
    PERFORMANCE = 22  # Entre INFO e WARNING


class LogCategory(str, Enum):
    """
    Categorias de log para classificar mensagens.
    
    Usado para rotear logs para handlers especializados.
    """
    # Sistema
    BOT_START = "BOT_START"
    BOT_STOP = "BOT_STOP"
    SYSTEM_INIT = "SYSTEM_INIT"
    CONFIGURATION = "CONFIGURATION"
    INITIALIZATION = "INITIALIZATION"
    SHUTDOWN = "SHUTDOWN"
    RESTART = "RESTART"
    
    # Erros
    EXCEPTION = "EXCEPTION"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    API_ERROR = "API_ERROR"
    CRITICAL_ERROR = "CRITICAL_ERROR"
    PARSING_ERROR = "PARSING_ERROR"
    VALUE_ERROR = "VALUE_ERROR"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    TRADE_OPEN_ERROR = "TRADE_OPEN_ERROR"  # Erro ao abrir posição
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    
    # Trading
    POSITION_OPEN = "POSITION_OPEN"
    POSITION_UPDATE = "POSITION_UPDATE"
    POSITION_CLOSE = "POSITION_CLOSE"
    TRADE_SIGNAL = "TRADE_SIGNAL"
    POSITION_STATUS = "POSITION_STATUS"
    TARGET_HIT = "TARGET_HIT"
    STOP_HIT = "STOP_HIT"
    MANUAL_CLOSE = "MANUAL_CLOSE"
    
    # Agentes
    AGENT_EXECUTION = "AGENT_EXECUTION"
    AGENT_RESPONSE = "AGENT_RESPONSE"
    AGENT_DECISION = "AGENT_DECISION"
    AGENT_ACTION = "AGENT_ACTION"
    AGENT_SCHEDULE = "AGENT_SCHEDULE"
    
    # Performance
    CPU_USAGE = "CPU_USAGE"
    MEMORY_USAGE = "MEMORY_USAGE"
    NETWORK_USAGE = "NETWORK_USAGE"
    EXECUTION_TIME = "EXECUTION_TIME"
    PERFORMANCE_METRIC = "PERFORMANCE_METRIC"
    
    # Otimização
    OPTIMIZATION = "OPTIMIZATION"
    GRID_SEARCH_START = "GRID_SEARCH_START"
    GRID_SEARCH_PROGRESS = "GRID_SEARCH_PROGRESS"
    GRID_SEARCH_RESULT = "GRID_SEARCH_RESULT"
    GRID_SEARCH_FINISH = "GRID_SEARCH_FINISH"
    EVOLUTION_START = "EVOLUTION_START"
    EVOLUTION_GENERATION = "EVOLUTION_GENERATION"
    EVOLUTION_RESULT = "EVOLUTION_RESULT"
    EVOLUTION_FINISH = "EVOLUTION_FINISH"
    BACKTEST_START = "BACKTEST_START"
    BACKTEST_RESULT = "BACKTEST_RESULT"
    BACKTEST_FINISH = "BACKTEST_FINISH"
    
    # Categorias gerais
    SYSTEM = "SYSTEM"
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    ERROR = "ERROR"
    RETRY_ATTEMPT = "RETRY_ATTEMPT"
    FATAL_ERROR = "FATAL_ERROR"
    TRADE_STATUS_ERROR = "TRADE_STATUS_ERROR"
    TRADE_SEARCH = "TRADE_SEARCH"
    EMPTY_DATA = "EMPTY_DATA"
    INVALID_PRICES = "INVALID_PRICES"
    INVALID_ORDER_QTY = "INVALID_ORDER_QTY"
    LOW_RISK_REWARD = "LOW_RISK_REWARD"
    
    @classmethod
    def get_trading_categories(cls) -> Set['LogCategory']:
        """Retorna categorias relacionadas a trading."""
        return {
            cls.POSITION_OPEN, cls.POSITION_UPDATE, cls.POSITION_CLOSE,
            cls.TRADE_SIGNAL, cls.POSITION_STATUS, cls.TARGET_HIT,
            cls.STOP_HIT, cls.MANUAL_CLOSE
        }
    
    @classmethod
    def get_agent_categories(cls) -> Set['LogCategory']:
        """Retorna categorias relacionadas a agentes."""
        return {
            cls.AGENT_EXECUTION, cls.AGENT_RESPONSE, cls.AGENT_DECISION,
            cls.AGENT_ACTION, cls.AGENT_SCHEDULE
        }
    
    @classmethod
    def get_error_categories(cls) -> Set['LogCategory']:
        """Retorna categorias relacionadas a erros."""
        return {
            cls.EXCEPTION, cls.CONNECTION_ERROR, cls.API_ERROR,
            cls.CRITICAL_ERROR, cls.PARSING_ERROR, cls.VALUE_ERROR,
            cls.EXECUTION_ERROR, cls.TRADE_OPEN_ERROR, cls.UNKNOWN_ERROR
        }
    
    @classmethod
    def get_system_categories(cls) -> Set['LogCategory']:
        """Retorna categorias relacionadas a sistema."""
        return {
            cls.BOT_START, cls.BOT_STOP, cls.SYSTEM_INIT,
            cls.CONFIGURATION, cls.INITIALIZATION, cls.SHUTDOWN, cls.RESTART
        }
    
    @classmethod
    def is_trading_category(cls, category: 'LogCategory') -> bool:
        """Verifica se categoria é de trading."""
        return category in cls.get_trading_categories()
    
    @classmethod
    def is_agent_category(cls, category: 'LogCategory') -> bool:
        """Verifica se categoria é de agente."""
        return category in cls.get_agent_categories()
    
    @classmethod
    def is_error_category(cls, category: 'LogCategory') -> bool:
        """Verifica se categoria é de erro."""
        return category in cls.get_error_categories()
    
    @classmethod
    def is_system_category(cls, category: 'LogCategory') -> bool:
        """Verifica se categoria é de sistema."""
        return category in cls.get_system_categories()

