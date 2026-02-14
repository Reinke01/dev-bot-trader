"""
LogStreamManager - Gerencia streaming de logs via WebSocket.

Responsabilidades:
- Escuta LogEvents do sistema de logging
- Mantém buffer de logs recentes
- Broadcasting assíncrono para WebSocket subscribers
- Independente do BotManager (reutilizável)
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
from typing import Dict, List, Optional, Callable, Awaitable
from collections import deque
from utils.logging import LogEvent
from utils.notifications.events import get_event_emitter

class LogStreamManager:
    """
    Gerencia streaming de logs via WebSocket.
    
    - Escuta TODOS os LogEvents do sistema
    - Mantém buffer de logs recentes
    - Broadcasting assíncrono para WebSocket
    """
    
    def __init__(self, buffer_size: int = 500):
        # Subscribers por bot_id (para /ws/logs/{bot_id})
        self._bot_subscribers: Dict[str, List[Callable[[dict], Awaitable[None]]]] = {}
        
        # Subscribers globais (para /ws/logs)
        self._global_subscribers: List[Callable[[dict], Awaitable[None]]] = []
        
        # Buffers organizados por bot_id (mais eficiente)
        self._buffers_by_bot: Dict[str, deque] = {}
        self._buffer_size = buffer_size
        
        # Buffer global (compatibilidade + logs sem bot_id específico)
        self.log_buffer: deque = deque(maxlen=buffer_size)
        
        # Event loop principal do FastAPI (para broadcast thread-safe)
        self._main_loop = None
        
        # Conectar ao Event Emitter do sistema de logging
        get_event_emitter().subscribe('log_event', self._on_log_event)
    
    def set_event_loop(self, loop):
        """
        Define o event loop principal para broadcast thread-safe.
        
        Deve ser chamado no startup da API com o event loop do FastAPI.
        """
        self._main_loop = loop
    
    def _on_log_event(self, event):
        """
        Callback quando um LogEvent é emitido (síncrono).
        Converte para dict e agenda broadcast assíncrono.
        """
        log_event = event.data  # Extrair LogEvent do Event
        message = self._log_event_to_dict(log_event)
        
        # Adicionar ao buffer global
        self.log_buffer.append(message)
        
        # Adicionar ao buffer específico do bot
        bot_id = message.get('bot_id')
        if bot_id:
            if bot_id not in self._buffers_by_bot:
                self._buffers_by_bot[bot_id] = deque(maxlen=self._buffer_size)
            self._buffers_by_bot[bot_id].append(message)
        
        # Broadcast via WebSocket (thread-safe)
        if self._main_loop and not self._main_loop.is_closed():
            try:
                # Agendar corrotina no loop principal de forma thread-safe
                # Funciona mesmo quando chamado de threads diferentes (bots)
                asyncio.run_coroutine_threadsafe(
                    self._broadcast_async(message),
                    self._main_loop
                )
            except Exception:
                # Silenciosamente ignora se não conseguir agendar
                # (ex: loop fechado, erro de thread)
                pass
    
    def _log_event_to_dict(self, log_event: LogEvent) -> dict:
        """Converte LogEvent para dict para WebSocket."""
        return {
            'timestamp': log_event.timestamp.isoformat(),
            'level': log_event.level.name,
            'category': log_event.category.value,
            'message': log_event.message,
            'module': log_event.module,
            'agent_name': log_event.agent_name,
            'bot_id': log_event.bot_id,
            # Extrair informações úteis do context
            'cripto': log_event.context.get('symbol') or log_event.context.get('cripto'),
            'tempo_grafico': log_event.context.get('tempo_grafico'),
            'subconta': log_event.context.get('subconta'),
            'context': log_event.context,
            'exception': str(log_event.exception) if log_event.exception else None,
        }
    
    async def _broadcast_async(self, message: dict):
        """Envia mensagem para todos os subscribers apropriados."""
        bot_id = message.get('bot_id')
        
        # Broadcast para subscribers específicos do bot
        if bot_id and bot_id in self._bot_subscribers:
            await self._send_to_subscribers(self._bot_subscribers[bot_id], message)
        
        # Broadcast para subscribers globais
        await self._send_to_subscribers(self._global_subscribers, message)
    
    async def _send_to_subscribers(self, subscribers: List, message: dict):
        """Envia mensagem para lista de subscribers e remove os mortos."""
        dead_subscribers = []
        
        for subscriber in subscribers:
            try:
                await subscriber(message)
            except Exception as e:
                print(f"Erro ao enviar log via WebSocket: {e}")
                dead_subscribers.append(subscriber)
        
        # Remover subscribers mortos
        for subscriber in dead_subscribers:
            try:
                subscribers.remove(subscriber)
            except ValueError:
                pass
    
    # ============= Métodos públicos para gerenciar subscribers =============
    
    def subscribe_to_bot(self, bot_id: str, callback: Callable[[dict], Awaitable[None]]):
        """Registra callback para receber logs de um bot específico."""
        if bot_id not in self._bot_subscribers:
            self._bot_subscribers[bot_id] = []
        self._bot_subscribers[bot_id].append(callback)
    
    def unsubscribe_from_bot(self, bot_id: str, callback: Callable[[dict], Awaitable[None]]):
        """Remove callback de um bot específico."""
        if bot_id in self._bot_subscribers:
            try:
                self._bot_subscribers[bot_id].remove(callback)
            except ValueError:
                pass  # Callback já foi removido
    
    def subscribe_global(self, callback: Callable[[dict], Awaitable[None]]):
        """Registra callback para receber logs de todos os bots."""
        self._global_subscribers.append(callback)
    
    def unsubscribe_global(self, callback: Callable[[dict], Awaitable[None]]):
        """Remove callback global."""
        try:
            self._global_subscribers.remove(callback)
        except ValueError:
            pass  # Callback já foi removido
    
    # ============= Métodos de consulta =============
    
    def get_buffer(
        self, 
        max_items: Optional[int] = None, 
        bot_id: Optional[str] = None
    ) -> list:
        """
        Retorna buffer de logs em ordem cronológica (mais antigo primeiro).
        
        Args:
            max_items: Número máximo de logs a retornar (pega os últimos N logs)
            bot_id: Se fornecido, retorna buffer específico desse bot 
                    Se None, retorna buffer global
        
        Returns:
            Lista de logs em ordem cronológica (do mais antigo para o mais recente)
        """
        # Buscar por bot_id
        if bot_id:
            buffer = list(self._buffers_by_bot.get(bot_id, []))
        else:
            # Buffer global
            buffer = list(self.log_buffer)
        
        # Limitar quantidade se especificado
        if max_items:
            return buffer[-max_items:]
        
        # Retornar em ordem cronológica (mais antigo primeiro)
        return buffer
    
    def get_subscribers_count(self, bot_id: Optional[str] = None) -> int:
        """Retorna número de subscribers."""
        if bot_id:
            return len(self._bot_subscribers.get(bot_id, []))
        return len(self._global_subscribers)
    
    def get_all_bot_subscribers(self) -> Dict[str, int]:
        """Retorna contagem de subscribers por bot_id."""
        return {
            bot_id: len(subscribers)
            for bot_id, subscribers in self._bot_subscribers.items()
        }
    
    def get_bot_ids(self) -> list:
        """Retorna lista de bot_ids com buffers ativos."""
        return list(self._buffers_by_bot.keys())
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do sistema de streaming."""
        return {
            'total_global_subscribers': len(self._global_subscribers),
            'total_bot_subscribers': sum(len(subs) for subs in self._bot_subscribers.values()),
            'bots_with_subscribers': len(self._bot_subscribers),
            'buffer_size': len(self.log_buffer),
            'buffer_max': self.log_buffer.maxlen,
            # Estatísticas por bot
            'total_bots_with_buffer': len(self._buffers_by_bot),
            'bot_ids': list(self._buffers_by_bot.keys()),
        }


# ============= Singleton =============

_log_stream_manager_instance: Optional[LogStreamManager] = None

def get_log_stream_manager() -> LogStreamManager:
    """Retorna instância singleton do LogStreamManager."""
    global _log_stream_manager_instance
    if _log_stream_manager_instance is None:
        _log_stream_manager_instance = LogStreamManager()
    return _log_stream_manager_instance

