"""
Cliente Telegram simplificado - APENAS envia mensagens.

Responsabilidades:
- Gerenciar conexão com Bot API
- Enviar mensagens com retry/backoff
- Rate limiting básico
- NADA de lógica de negócio ou formatação

Suporte cross-platform:
- macOS: usa queue.Queue síncrona para evitar problemas conhecidos do asyncio
- Windows/Linux: usa asyncio.Queue com loop dedicado
"""

import os
import asyncio
import time
import platform
from typing import Optional, Tuple, Any
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import queue
from datetime import datetime

try:
    from telegram import Bot
    from telegram.constants import ParseMode
    from telegram.error import RetryAfter, TimedOut, NetworkError
    from telegram.request import HTTPXRequest
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot não disponível")


class TelegramClient:
    """
    Cliente Telegram minimalista - APENAS envia.
    
    Suporta macOS, Windows e Linux com estratégias otimizadas.
    macOS usa queue.Queue síncrona para evitar problemas conhecidos do asyncio.
    """
    
    def __init__(
        self, 
        bot_token: Optional[str] = None, 
        chat_id: Optional[str] = None,
        rate_limit: float = 1.0
    ):
        if not TELEGRAM_AVAILABLE:
            raise RuntimeError("python-telegram-bot não instalado")
        
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Token e Chat ID do Telegram são obrigatórios")
        
        # Request configurado para redes domésticas
        request = HTTPXRequest(
            connect_timeout=12.0,
            read_timeout=15.0,
            write_timeout=15.0,
            pool_timeout=8.0
        )
        
        self.bot = Bot(token=self.bot_token, request=request)
        
        # Rate limit simples por chat
        self._min_interval = rate_limit
        self._last_sent_ts_per_chat = {}
        
        # Detectar SO e escolher estratégia
        self._is_macos = platform.system() == 'Darwin'
        
        if self._is_macos:
            self._setup_macos_mode()
        else:
            self._setup_async_mode()
    
    def _setup_macos_mode(self):
        """Configuração específica para macOS usando queue síncrona."""
        print("🍎 Telegram: Modo macOS ativado (queue síncrona)")
        
        self._queue = queue.Queue()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="telegram")
        self._running = True
        
        # Criar e iniciar loop persistente para envios
        self._macos_loop = asyncio.new_event_loop()
        self._loop_thread = Thread(target=self._run_macos_loop, daemon=True)
        self._loop_thread.start()
        
        # Iniciar worker em thread separada
        self._worker_thread = Thread(target=self._macos_worker, daemon=True)
        self._worker_thread.start()
    
    def _run_macos_loop(self):
        """Executa o loop asyncio persistente para macOS."""
        asyncio.set_event_loop(self._macos_loop)
        self._macos_loop.run_forever()
    
    def _setup_async_mode(self):
        """Configuração original com asyncio para Windows/Linux."""
        # print("🪟 Telegram: Modo padrão ativado")
        
        # Fila e loop dedicados
        self._queue: asyncio.Queue[Tuple[str, ParseMode, asyncio.Future]] = asyncio.Queue()
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        # Inicia o worker dentro do loop dedicado
        def _start_worker():
            asyncio.ensure_future(self._worker(), loop=self._loop)
        self._loop.call_soon_threadsafe(_start_worker)
    
    def _run_loop(self):
        """Thread dedicada para asyncio (Windows/Linux)."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _macos_worker(self):
        """Worker para macOS usando queue síncrona."""
        while self._running:
            try:
                # Timeout para evitar bloqueio infinito
                message, parse_mode, result_queue = self._queue.get(timeout=1.0)
                
                # Enviar mensagem de forma síncrona
                success = self._send_sync_with_retry(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode
                )
                
                # Retornar resultado
                result_queue.put(success)
                self._queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Erro no worker do Telegram (macOS): {e}")
    
    def _send_sync_with_retry(self, chat_id: str, text: str, parse_mode: ParseMode) -> bool:
        """Envio síncrono com retry para macOS."""
        # Throttle por chat
        now = time.time()
        last = self._last_sent_ts_per_chat.get(chat_id, 0.0)
        delta = now - last
        if delta < self._min_interval:
            time.sleep(self._min_interval - delta)
        
        # Backoff: tenta algumas vezes (otimizado para não travar muito tempo)
        max_attempts = 3
        attempt = 0
        backoff = 2.0  # segundos
        
        while attempt < max_attempts:
            attempt += 1
            try:
                async def _send():
                    await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
                
                # Executar no loop persistente que está rodando
                future = asyncio.run_coroutine_threadsafe(_send(), self._macos_loop)
                future.result(timeout=30)  # Timeout para evitar bloqueio
                
                self._last_sent_ts_per_chat[chat_id] = time.time()
                print(f"✅ Mensagem enviada para o telegram: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            
            except RetryAfter as e:
                # Flood control do Telegram
                wait_s = max(float(getattr(e, "retry_after", backoff)), backoff)
                print(f"⚠️ RetryAfter: aguardando {wait_s:.2f}s")
                time.sleep(wait_s)
                backoff = min(backoff * 1.5, 10.0)
            
            except (TimedOut, NetworkError) as e:
                print(f"⚠️ {e.__class__.__name__}: {e.message} - tentativa {attempt}/{max_attempts}; backoff {backoff:.1f}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, 15.0)
            
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem ao Telegram: {e}")
                return False
        
        return False
    
    async def _worker(self):
        """Consome a fila e envia mensagens em ordem (Windows/Linux)."""
        while True:
            message, parse_mode, result_future = await self._queue.get()
            try:
                ok = await self._send_with_throttle_and_retry(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode
                )
                if not result_future.done():
                    result_future.set_result(ok)
            except Exception as e:
                if not result_future.done():
                    result_future.set_result(False)
                print(f"❌ Erro no worker do Telegram: {e}")
            finally:
                self._queue.task_done()
    
    async def _send_with_throttle_and_retry(self, chat_id: str, text: str, parse_mode: ParseMode) -> bool:
        """Envio assíncrono com throttle e retry (Windows/Linux)."""
        # Throttle por chat
        now = time.time()
        last = self._last_sent_ts_per_chat.get(chat_id, 0.0)
        delta = now - last
        if delta < self._min_interval:
            await asyncio.sleep(self._min_interval - delta)
        
        # Backoff: tenta algumas vezes (otimizado para não travar muito tempo)
        max_attempts = 3
        attempt = 0
        backoff = 2.0  # segundos
        
        while attempt < max_attempts:
            attempt += 1
            try:
                await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
                self._last_sent_ts_per_chat[chat_id] = time.time()
                print(f"✅ Mensagem enviada para o telegram: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            
            except RetryAfter as e:
                # Flood control do Telegram
                wait_s = max(float(getattr(e, "retry_after", backoff)), backoff)
                print(f"⚠️ RetryAfter: aguardando {wait_s:.2f}s")
                await asyncio.sleep(wait_s)
                backoff = min(backoff * 1.5, 10.0)
            
            except (TimedOut, NetworkError) as e:
                print(f"⚠️ {e.__class__.__name__}: {e.message} - tentativa {attempt}/{max_attempts}; backoff {backoff:.1f}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 15.0)
            
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem ao Telegram: {e}")
                return False
        
        return False
    
    async def _send_message_async(self, message: str, parse_mode: ParseMode = ParseMode.HTML) -> bool:
        """Enfileira a mensagem e aguarda o resultado dentro do loop dedicado (Windows/Linux)."""
        fut: asyncio.Future[Any] = asyncio.Future()
        await self._queue.put((message, parse_mode, fut))
        ok = await fut
        return bool(ok)
    
    def send(
        self, 
        message: str, 
        parse_mode: ParseMode = ParseMode.HTML,
        timeout: float = 60.0
    ) -> bool:
        """
        API síncrona (thread-safe): enfileira no loop dedicado e espera o resultado.
        Usa estratégia apropriada para o sistema operacional.
        
        Args:
            message: Mensagem a enviar
            parse_mode: Modo de parse (HTML, Markdown)
            timeout: Timeout total
            
        Returns:
            True se enviou com sucesso
        """
        try:
            if self._is_macos:
                # No macOS, usar queue síncrona
                result_queue = queue.Queue()
                self._queue.put((message, parse_mode, result_queue))
                try:
                    return result_queue.get(timeout=timeout)
                except queue.Empty:
                    print("❌ Timeout ao enviar mensagem no macOS")
                    return False
            else:
                # No Windows/Linux, usar asyncio
                coro = self._send_message_async(message, parse_mode)
                return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=timeout)
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem ao Telegram: {e}")
            return False
    
    def __del__(self):
        """Cleanup ao destruir a instância."""
        if hasattr(self, '_is_macos') and self._is_macos:
            if hasattr(self, '_running'):
                self._running = False
            if hasattr(self, '_executor'):
                self._executor.shutdown(wait=False)


# Singleton
_telegram_client: Optional[TelegramClient] = None

def get_telegram_client() -> Optional[TelegramClient]:
    """Retorna instância singleton do cliente."""
    global _telegram_client
    if _telegram_client is None:
        try:
            _telegram_client = TelegramClient()
        except Exception as e:
            print(f"⚠️ Telegram não disponível: {e}")
            return None
    return _telegram_client

