"""
Interfaces base para notificadores.

Define contratos que notificadores devem implementar.
"""

from abc import ABC, abstractmethod
from typing import Protocol
import sys

# Importar LogEvent
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    # Fallback para Python < 3.8
    Protocol = object


class LogEventSubscriber(ABC):
    """
    Interface abstrata para subscribers de eventos de log.
    
    Implementadores devem processar LogEvents e decidir se/como notificar.
    """
    
    @abstractmethod
    def handle_log_event(self, log_event) -> None:
        """
        Processa um evento de log.
        
        Args:
            log_event: LogEvent a processar
        """
        pass
    
    @abstractmethod
    def should_notify(self, log_event) -> bool:
        """
        Determina se deve notificar sobre este evento.
        
        Args:
            log_event: LogEvent a avaliar
            
        Returns:
            True se deve notificar
        """
        pass


class NotifierProtocol(Protocol):
    """
    Protocol (structural typing) para notificadores.
    
    Alternativa ao ABC que não requer herança explícita.
    Qualquer classe que implemente estes métodos é compatível.
    """
    
    def notify(self, message: str, **kwargs) -> bool:
        """
        Envia notificação.
        
        Args:
            message: Mensagem a notificar
            **kwargs: Parâmetros adicionais específicos do notificador
            
        Returns:
            True se enviado com sucesso
        """
        ...
    
    def is_enabled(self) -> bool:
        """
        Verifica se o notificador está habilitado.
        
        Returns:
            True se habilitado
        """
        ...


class BaseNotifier(LogEventSubscriber):
    """
    Classe base para notificadores com funcionalidades comuns.
    
    Fornece estrutura padrão para rate limiting, filtros, etc.
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
    
    def is_enabled(self) -> bool:
        """Verifica se o notificador está habilitado."""
        return self.enabled
    
    def handle_log_event(self, log_event) -> None:
        """
        Processa evento de log (template method).
        
        Args:
            log_event: LogEvent a processar
        """
        if not self.is_enabled():
            return
        
        if not self.should_notify(log_event):
            return
        
        try:
            self._send_notification(log_event)
        except Exception as e:
            # Log silencioso para não criar loops
            print(f"⚠️ Erro ao enviar notificação: {e}")
    
    @abstractmethod
    def should_notify(self, log_event) -> bool:
        """
        Determina se deve notificar (implementado por subclasses).
        
        Args:
            log_event: LogEvent a avaliar
            
        Returns:
            True se deve notificar
        """
        pass
    
    @abstractmethod
    def _send_notification(self, log_event) -> None:
        """
        Envia a notificação (implementado por subclasses).
        
        Args:
            log_event: LogEvent a notificar
        """
        pass

