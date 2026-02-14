"""
Formatadores simplificados para logs.

Trabalha com LogEvent em vez de strings, reduzindo parsing.
"""

import logging
from datetime import datetime
from typing import Optional

from .models import LogEvent
from .enums import LogLevel, LogCategory


class LogEventFormatter(logging.Formatter):
    """
    Formatador base que trabalha com LogEvent.
    
    Extrai informações do LogEvent de forma type-safe.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata LogRecord que contém LogEvent.
        
        Args:
            record: LogRecord do Python logging
            
        Returns:
            String formatada
        """
        # Se o record tem um LogEvent anexado, usar ele
        if hasattr(record, 'log_event'):
            return self._format_log_event(record.log_event)
        
        # Fallback para formatação padrão
        return super().format(record)
    
    def _format_log_event(self, event: LogEvent) -> str:
        """
        Formata LogEvent (implementado por subclasses).
        
        Args:
            event: LogEvent a formatar
            
        Returns:
            String formatada
        """
        return event.format_for_display()


class SimpleFormatter(LogEventFormatter):
    """
    Formatador simples para console.
    
    Formato: [HH:MM:SS] [LEVEL] [CATEGORY] message
    """
    
    def __init__(self, use_colors: bool = False, show_module: bool = True):
        super().__init__()
        self.use_colors = use_colors
        self.show_module = show_module  # Controla se exibe o nome do módulo
        
        # Códigos de cor ANSI
        self.colors = {
            'DEBUG': '\033[36m',      # Ciano
            'INFO': '\033[32m',       # Verde
            'WARNING': '\033[33m',    # Amarelo
            'TRADING': '\033[94m',    # Azul claro
            'ERROR': '\033[31m',      # Vermelho
            'CRITICAL': '\033[35m',   # Magenta
            'RESET': '\033[0m'        # Reset
        }
    
    def _format_log_event(self, event: LogEvent) -> str:
        """Formato simples e legível."""
        timestamp = event.timestamp.strftime('%H:%M:%S')
        
        # Cor do nível
        level_str = event.level.name
        if self.use_colors and level_str in self.colors:
            level_str = f"{self.colors[level_str]}{level_str}{self.colors['RESET']}"
        
        # Construir mensagem
        parts = [f"[{timestamp}]", f"[{level_str}]", f"[{event.category.value}]"]
        
        if event.agent_name:
            parts.append(f"[{event.agent_name}]")
        
        # Incluir módulo apenas se show_module=True (padrão para arquivos, False para console)
        if self.show_module and event.module:
            parts.append(f"[{event.module}]")
        
        parts.append(event.message)
        
        # Contexto adicional
        if event.context:
            context_items = [f"{k}={v}" for k, v in event.context.items()]
            parts.append(f"| {', '.join(context_items)}")
        
        return " ".join(parts)


class DetailedFormatter(LogEventFormatter):
    """
    Formatador detalhado para arquivos master.
    
    Inclui timestamp completo e todas as informações.
    """
    
    def _format_log_event(self, event: LogEvent) -> str:
        """Formato detalhado com todas as informações."""
        timestamp = event.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        parts = [
            timestamp,
            f"[{event.level.name}]",
            f"[{event.category.value}]"
        ]
        
        if event.agent_name:
            parts.append(f"[Agent:{event.agent_name}]")
        
        if event.module:
            parts.append(f"[Module:{event.module}]")
        
        parts.append(event.message)
        
        # Contexto em formato detalhado
        if event.context:
            context_str = " | ".join(f"{k}={v}" for k, v in event.context.items())
            parts.append(f"| Context: {context_str}")
        
        # Exceção se presente
        if event.exception:
            parts.append(f"\n  Exception: {event.exception}")
        
        return " ".join(parts)


class ErrorFormatter(LogEventFormatter):
    """
    Formatador especializado para erros com stack traces.
    """
    
    def _format_log_event(self, event: LogEvent) -> str:
        """Formato detalhado para erros."""
        timestamp = event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [
            "=" * 80,
            f"{timestamp} [{event.level.name}] [{event.category.value}]",
            f"MESSAGE: {event.message}"
        ]
        
        if event.module:
            lines.append(f"MODULE: {event.module}")
        
        if event.context:
            lines.append(f"CONTEXT: {event.context}")
        
        if event.exception:
            import traceback
            lines.append(f"EXCEPTION: {type(event.exception).__name__}: {event.exception}")
            if hasattr(event.exception, '__traceback__'):
                tb_lines = traceback.format_tb(event.exception.__traceback__)
                lines.append("TRACEBACK:")
                lines.extend(tb_lines)
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


def get_formatter(format_type: str, **kwargs) -> LogEventFormatter:
    """
    Factory function para criar formatadores.
    
    Args:
        format_type: Tipo do formatador ('simple', 'detailed', 'error')
        **kwargs: Argumentos para o formatador
        
    Returns:
        Instância do formatador
    """
    formatters = {
        'simple': SimpleFormatter,
        'detailed': DetailedFormatter,
        'error': ErrorFormatter
    }
    
    formatter_class = formatters.get(format_type, SimpleFormatter)
    return formatter_class(**kwargs)

