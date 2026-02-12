"""
Sistema de eventos usando Observer Pattern.

Permite desacoplar o logging das notificações através de eventos.
"""

from typing import Callable, List, Dict, Any
from dataclasses import dataclass
import threading


@dataclass
class Event:
    """Evento genérico que pode ser emitido."""
    name: str
    data: Any


EventHandler = Callable[[Event], None]


class EventEmitter:
    """
    Emissor de eventos simples usando Observer Pattern.
    
    Permite registrar subscribers que serão notificados quando eventos ocorrerem.
    Thread-safe para uso em ambientes multi-threaded.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._lock = threading.Lock()
    
    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """
        Registra um handler para um tipo de evento.
        
        Args:
            event_name: Nome do evento (ex: 'log_event', 'notification')
            handler: Função que será chamada quando o evento ocorrer
        """
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            if handler not in self._subscribers[event_name]:
                self._subscribers[event_name].append(handler)
    
    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """
        Remove um handler de um tipo de evento.
        
        Args:
            event_name: Nome do evento
            handler: Função a ser removida
        """
        with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(handler)
                except ValueError:
                    pass  # Handler não estava registrado
    
    def emit(self, event_name: str, data: Any = None) -> None:
        """
        Emite um evento, notificando todos os subscribers.
        
        Args:
            event_name: Nome do evento a emitir
            data: Dados do evento (geralmente LogEvent)
        """
        # Criar evento
        event = Event(name=event_name, data=data)
        
        # Obter lista de handlers (com lock)
        with self._lock:
            handlers = self._subscribers.get(event_name, []).copy()
        
        # Executar handlers (sem lock para não bloquear)
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log silencioso para não criar loop
                print(f"⚠️ Erro ao executar handler de evento '{event_name}': {e}")
    
    def clear(self, event_name: str = None) -> None:
        """
        Remove todos os subscribers de um evento ou de todos os eventos.
        
        Args:
            event_name: Nome do evento (None = todos)
        """
        with self._lock:
            if event_name:
                self._subscribers.pop(event_name, None)
            else:
                self._subscribers.clear()
    
    def has_subscribers(self, event_name: str) -> bool:
        """
        Verifica se há subscribers para um evento.
        
        Args:
            event_name: Nome do evento
            
        Returns:
            True se há pelo menos um subscriber
        """
        with self._lock:
            return event_name in self._subscribers and len(self._subscribers[event_name]) > 0
    
    def subscriber_count(self, event_name: str) -> int:
        """
        Retorna o número de subscribers para um evento.
        
        Args:
            event_name: Nome do evento
            
        Returns:
            Número de subscribers
        """
        with self._lock:
            return len(self._subscribers.get(event_name, []))


# Instância global (singleton pattern)
_global_emitter = None


def get_event_emitter() -> EventEmitter:
    """
    Retorna instância global do event emitter (singleton).
    
    Returns:
        EventEmitter global
    """
    global _global_emitter
    if _global_emitter is None:
        _global_emitter = EventEmitter()
    return _global_emitter

