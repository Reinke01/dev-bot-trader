"""
Sistema de notificações desacoplado do logging.

Usa Observer Pattern para receber eventos de log e notificar canais externos.
"""

from .events import EventEmitter, Event, get_event_emitter
from .base import LogEventSubscriber, NotifierProtocol, BaseNotifier

__all__ = [
    'EventEmitter',
    'Event',
    'get_event_emitter',
    'LogEventSubscriber',
    'NotifierProtocol',
    'BaseNotifier'
]

