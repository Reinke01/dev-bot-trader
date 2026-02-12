"""
Notificador Telegram como subscriber de eventos de log.

Desacoplado do sistema de logging, mais robusto e simples.
"""

import html
import time
from typing import Set, Optional
from collections import deque
from datetime import datetime
import threading

from .base import BaseNotifier
from .events import Event

# Importar enums do logging sem criar dependência circular
try:
    from ..logging.enums import LogLevel, LogCategory
    from ..logging.models import LogEvent
except ImportError:
    # Fallback se imports falharem
    LogEvent = None
    LogCategory = None
    LogLevel = None
    print("⚠️ Não foi possível importar LogEvent, LogCategory, LogLevel")

# Importar TelegramClient
try:
    from .telegram_client import get_telegram_client
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ telegram_client não disponível")


class TelegramLogNotifier(BaseNotifier):
    """
    Notificador Telegram que recebe LogEvents e envia notificações seletivas.
    
    Características:
    - Rate limiting para evitar spam
    - Filtragem por categoria
    - Formatação específica para Telegram
    - Não quebra o logging se falhar
    """
    
    def __init__(
        self,
        enabled: bool = True,
        categories: Optional[Set[LogCategory]] = None,
        rate_limit: float = 0.1,  # segundos entre mensagens
        dedup_seconds: int = 60
    ):
        """
        Inicializa notificador Telegram.
        
        Args:
            enabled: Se notificador está habilitado
            categories: Categorias a notificar (None = todas de agente)
            rate_limit: Intervalo mínimo entre mensagens em segundos
        """
        super().__init__(enabled)
        
        if not TELEGRAM_AVAILABLE:
            self.enabled = False
            print("⚠️ Telegram desabilitado - módulo não disponível")
            return
        
        # Obter cliente
        self.client = get_telegram_client()
        if not self.client:
            self.enabled = False
            print("⚠️ Telegram desabilitado - cliente não disponível")
            return
        
        # Categorias padrão se não especificadas
        if categories is None and LogCategory:
            categories = {
                LogCategory.AGENT_RESPONSE,
                LogCategory.AGENT_ACTION,
                LogCategory.AGENT_DECISION,
                LogCategory.POSITION_OPEN,  # Abertura de posição (Entry Evaluator)
                LogCategory.LOW_RISK_REWARD,  # Warnings de risco/retorno
                LogCategory.INVALID_PRICES,  # Warnings de preços inválidos
                LogCategory.INVALID_ORDER_QTY,  # Warnings de quantidade inválida
                LogCategory.EXECUTION_ERROR,  # Erros de execução gerais
                LogCategory.TRADE_OPEN_ERROR,  # Erros ao abrir posição
                # LogCategory.API_ERROR,  # Erros de API
                # LogCategory.CRITICAL_ERROR,  # Erros críticos
                # LogCategory.UNKNOWN_ERROR  # Erros desconhecidos
            }
        
        self.categories = categories or set()
        self.rate_limit = rate_limit
        self.dedup_seconds = dedup_seconds
        
        # Rate limiting
        self._last_sent = 0.0
        self._lock = threading.Lock()
        # Deduplication map: (category, symbol, tf) -> last_ts
        self._last_sent_map = {}
    
    def should_notify(self, log_event: LogEvent) -> bool:
        """
        Determina se deve notificar sobre este evento.
        
        Args:
            log_event: LogEvent a avaliar
            
        Returns:
            True se deve notificar
        """
        if not log_event:
            return False
        
        # Verificar se categoria está na lista
        if self.categories and log_event.category not in self.categories:
            return False
        
        # Verificar rate limit
        with self._lock:
            now = time.time()
            if now - self._last_sent < self.rate_limit:
                return False
            self._last_sent = now

        # Deduplication: não reenviar o mesmo evento (categoria+symbol+tf) em menos de dedup_seconds
        symbol = log_event.context.get('symbol') if log_event and getattr(log_event, 'context', None) else None
        tf = log_event.context.get('tempo_grafico') or log_event.context.get('tf') or ''
        key = (str(log_event.category.value) if hasattr(log_event.category, 'value') else str(log_event.category), str(symbol), str(tf))
        last = self._last_sent_map.get(key, 0)
        if time.time() - last < self.dedup_seconds:
            return False

        # Register send time for dedup
        self._last_sent_map[key] = time.time()
        
        return True
    
    def _send_notification(self, log_event: LogEvent) -> None:
        """
        Envia notificação via Telegram.
        
        Args:
            log_event: LogEvent a notificar
        """
        if not self.client or not LogCategory:
            return
        
        try:
            # Formatar mensagem baseado na categoria
            message = self._format_message(log_event)
            
            # Enviar via cliente
            self.client.send(message)
        
        except Exception as e:
            # Log silencioso para não criar loops
            print(f"⚠️ Erro ao enviar notificação Telegram: {e}")
    
    def _format_message(self, log_event: LogEvent) -> str:
        """
        Formata mensagem baseado na categoria.
        Toda lógica de formatação fica aqui.
        
        Args:
            log_event: Evento a formatar
            
        Returns:
            String formatada para Telegram
        """
        category = log_event.category
        symbol = log_event.context.get('symbol', '')
        agent_name = log_event.agent_name or "Trade Bot"
        timestamp = log_event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        # Formatação específica por tipo
        if category == LogCategory.AGENT_RESPONSE:
            return self._format_agent_response(log_event, symbol, agent_name, timestamp)
        
        elif category in [LogCategory.AGENT_ACTION, LogCategory.AGENT_DECISION]:
            return self._format_agent_action(log_event, symbol, timestamp)
        
        elif category == LogCategory.POSITION_OPEN:
            return self._format_position_open(log_event, symbol, timestamp)
        
        elif category in [LogCategory.LOW_RISK_REWARD, LogCategory.INVALID_PRICES, LogCategory.INVALID_ORDER_QTY]:
            return self._format_warning(log_event, symbol, timestamp)
        
        elif category in [LogCategory.EXECUTION_ERROR, LogCategory.TRADE_OPEN_ERROR, LogCategory.API_ERROR, LogCategory.CRITICAL_ERROR, LogCategory.UNKNOWN_ERROR]:
            return self._format_error(log_event, symbol, timestamp)
        
        else:
            return self._format_generic(log_event, symbol, timestamp)
    
    def _format_agent_response(self, event: LogEvent, symbol: str, agent_name: str, timestamp: str) -> str:
        """
        Formata resposta de agente.
        
        Limite Telegram: 4096 caracteres TOTAL (texto + tags HTML)
        Template HTML: ~250 caracteres
        Limite seguro para content: 3700 caracteres
        """
        content = event.context.get('response_content', event.message)
        
        # Limite seguro: 4096 (Telegram) - ~400 (template + margem)
        MAX_CONTENT_LENGTH = 3700
        
        json_marker = '```json'
        json_start = content.find(json_marker)
        
        # Só processar JSON se existir E o conteúdo exceder o limite
        if json_start != -1 and len(content) > MAX_CONTENT_LENGTH:
            # Separar análise textual do JSON
            text_part = content[:json_start].strip()
            
            # Se parte textual ainda é grande, truncar
            if len(text_part) > MAX_CONTENT_LENGTH:
                # Truncar no último parágrafo completo
                truncate_at = text_part.rfind('\n\n', 0, MAX_CONTENT_LENGTH)
                if truncate_at == -1:
                    truncate_at = text_part.rfind('. ', 0, MAX_CONTENT_LENGTH)
                if truncate_at == -1:
                    truncate_at = MAX_CONTENT_LENGTH
                
                text_part = text_part[:truncate_at].rstrip() + "\n\n[...análise resumida devido ao tamanho...]"
            
            # Usar apenas a análise textual (decisão já está no sistema)
            content = text_part + "\n\n📊 Decisão registrada no sistema"
        
        elif len(content) > MAX_CONTENT_LENGTH:
            # Se não tem JSON OU tem JSON mas cabe no limite, truncar normalmente
            truncate_at = content.rfind('\n\n', 0, MAX_CONTENT_LENGTH)
            if truncate_at == -1:
                truncate_at = content.rfind('. ', 0, MAX_CONTENT_LENGTH)
            if truncate_at == -1:
                truncate_at = MAX_CONTENT_LENGTH
            
            content = content[:truncate_at].rstrip() + "\n\n[...análise truncada...]"
        
        # Escapar caracteres HTML para evitar erros de parsing (<, >, &)
        content = html.escape(content)
        
        return f"""🤖 <b>Análise {agent_name}</b>

📊 <b>Par:</b> {symbol}
🕐 <b>Horário:</b> {timestamp}

📋 <b>Análise:</b>
<pre>{content}</pre>

#TradingBot #CryptoAnalysis #{symbol.replace('USDT', '')}"""
    
    def _format_agent_action(self, event: LogEvent, symbol: str, timestamp: str) -> str:
        """Formata ação de agente."""
        action = event.context.get('action', 'unknown')
        details = event.context.get('details', event.message)
        decision = event.context.get('decision', '')
        
        # Mapear emojis
        emoji_map = {
            'comprar': '📈', 'vender': '📉', 'manter': '💎',
            'ignorar': '🚫', 'ajustar_stop': '🛡️', 'ajustar_alvo': '🎯',
            'fechar_compra': '📈', 'fechar_venda': '📉',
            'acionar_trailing_stop_imediato': '🔄',
            'acionar_trailing_stop_preço': '🔄',
            'realizar_parcial': '💰'
        }
        emoji = emoji_map.get(action, '⚡')
        
        # Determinar se é ação executada ou não
        no_action_cases = ['confiança_baixa', 'trailing_stop_ja_existe', 'manter', 'ignorar']
        is_no_action = action in no_action_cases or decision == 'NO_ACTION'
        
        title = 'Nenhuma Ação Executada' if is_no_action else 'Ação Executada'
        
        message = f"""{emoji} <b>{title}</b>

📊 <b>Par:</b> {symbol}
🕐 <b>Horário:</b> {timestamp}"""
        
        if is_no_action:
            if action == 'confiança_baixa':
                message += "\n⚠️ <b>Motivo:</b> Confiança baixa"
            elif action == 'trailing_stop_ja_existe':
                message += "\n⚠️ <b>Motivo:</b> Trailing stop já existe"
            elif action == 'manter':
                message += "\n⚠️ <b>Ação:</b> Manter posição"
            elif action == 'ignorar':
                message += "\n⚠️ <b>Ação:</b> Ignorar trade"
        else:
            message += f"\n🎬 <b>Ação:</b> {action.replace('_', ' ').title()}"
        
        if details:
            message += f"\n📝 <b>Detalhes:</b> {details}"
        
        message += f"\n\n#TradingBot #Action #{symbol.replace('USDT', '')}"
        return message
    
    def _format_position_open(self, event: LogEvent, symbol: str, timestamp: str) -> str:
        """
        Formata abertura de posição (Entry Evaluator).
        
        Context esperado:
        - operation: 'compra' ou 'venda'
        - entry_price: float
        - stop_price: float
        - target_price: float
        - position_size: float
        - risk_reward: float
        """
        operation = event.context.get('operation', 'unknown')
        entry_price = event.context.get('entry_price', 'N/A')
        stop_price = event.context.get('stop_price', 'N/A')
        target_price = event.context.get('target_price', 'N/A')
        position_size = event.context.get('position_size', 'N/A')
        risk_reward = event.context.get('risk_reward', 'N/A')
        
        # Formatar preços com separador de milhares
        def format_price(price):
            if price == 'N/A':
                return 'N/A'
            try:
                return f"${float(price):,.2f}"
            except (ValueError, TypeError):
                return str(price)
        
        # Formatar risk/reward como razão
        def format_rr(rr):
            if rr == 'N/A':
                return 'N/A'
            try:
                return f"{float(rr):.2f}:1"
            except (ValueError, TypeError):
                return str(rr)
        
        # Emoji e direção baseados em operação
        if operation == 'compra':
            emoji = '📈'
            direction = 'LONG'
            color_emoji = '🟢'
        else:
            emoji = '📉'
            direction = 'SHORT'
            color_emoji = '🔴'
        
        message = f"""{emoji} <b>Posição {direction} Aberta</b>

📊 <b>Par:</b> {symbol}
🕐 <b>Horário:</b> {timestamp}

{color_emoji} <b>Operação:</b> {operation.upper()}
💰 <b>Entrada:</b> {format_price(entry_price)}
🛡️ <b>Stop Loss:</b> {format_price(stop_price)}
🎯 <b>Take Profit:</b> {format_price(target_price)}
📦 <b>Tamanho:</b> {position_size}
📊 <b>Risco/Retorno:</b> {format_rr(risk_reward)}

#TradingBot #PositionOpen #{symbol.replace('USDT', '')} #{direction}"""
        
        return message
    
    def _format_warning(self, event: LogEvent, symbol: str, timestamp: str) -> str:
        """Formata warnings (LOW_RISK_REWARD, INVALID_PRICES, etc)."""
        category = event.category
        
        message = f"""⚠️ <b>Operação Ignorada</b>

📊 <b>Par:</b> {symbol}
🕐 <b>Horário:</b> {timestamp}

📉 <b>Motivo:</b> {event.message}"""
        
        # Detalhes específicos por tipo de warning
        if category == LogCategory.LOW_RISK_REWARD:
            risk_reward = event.context.get('risk_reward', 'N/A')
            threshold = event.context.get('threshold', 'N/A')
            action = event.context.get('action', 'ignorar')
            
            message += f"""

<b>Detalhes:</b>
• Risco/Retorno: {risk_reward}
• Threshold Mínimo: {threshold}
• Ação: {action.replace('_', ' ').title()}"""
        
        elif category == LogCategory.INVALID_PRICES:
            current_price = event.context.get('current_price', 'N/A')
            stop_price = event.context.get('stop_price', 'N/A')
            target_price = event.context.get('target_price', 'N/A')
            
            message += f"""

<b>Preços Detectados:</b>
• Preço Atual: {current_price}"""
            
            if stop_price != 'N/A':
                message += f"\n• Stop: {stop_price}"
            if target_price != 'N/A':
                message += f"\n• Alvo: {target_price}"
        
        elif category == LogCategory.INVALID_ORDER_QTY:
            calculated_qty = event.context.get('calculated_quantity', 'N/A')
            min_qty = event.context.get('min_quantity', 'N/A')
            current_price = event.context.get('current_price', 'N/A')
            stop_price = event.context.get('stop_price', 'N/A')
            target_price = event.context.get('target_price', 'N/A')
            
            message += f"""

<b>Detalhes da Ordem:</b>
• Quantidade Calculada: {calculated_qty}
• Quantidade Mínima: {min_qty}
• Preço Atual: {current_price}"""
            
            if stop_price != 'N/A':
                message += f"\n• Stop: {stop_price}"
            if target_price != 'N/A':
                message += f"\n• Alvo: {target_price}"
        
        message += f"\n\n#TradingBot #Warning #{symbol.replace('USDT', '')}"
        return message
    
    def _format_error(self, event: LogEvent, symbol: str, timestamp: str) -> str:
        """Formata erros (EXECUTION_ERROR, TRADE_OPEN_ERROR, API_ERROR, etc)."""
        error_type = event.category.value.replace('_', ' ').title()
        details = event.context.get('details', '')
        exception_msg = str(event.exception) if event.exception else ''
        
        # Informações específicas de erro de abertura de trade
        error_message = event.context.get('error_message', '')
        error_code = event.context.get('error_code', '')
        
        message = f"""🚨 <b>{error_type}</b>

📊 <b>Par:</b> {symbol}
🕐 <b>Horário:</b> {timestamp}

❌ <b>Erro:</b> {event.message}"""
        
        # Detalhes específicos de TRADE_OPEN_ERROR
        if error_message or error_code:
            message += "\n\n<b>Detalhes da API:</b>"
            if error_code:
                message += f"\n• Código: {error_code}"
            if error_message:
                message += f"\n• Mensagem: {error_message}"
        elif details:
            message += f"\n\n<b>Detalhes:</b> {details}"
        
        if exception_msg:
            # Truncar exceção se muito longa
            if len(exception_msg) > 500:
                exception_msg = exception_msg[:500] + "..."
            message += f"\n\n<b>Exception:</b>\n<pre>{exception_msg}</pre>"
        
        message += f"\n\n#TradingBot #Error #{symbol.replace('USDT', '')}"
        return message
    
    def _format_generic(self, event: LogEvent, symbol: str, timestamp: str) -> str:
        """Formatação genérica."""
        return f"""[{event.level.name}] [{event.category.value}]
{timestamp}

{event.message}

Par: {symbol}"""
    


def setup_telegram_notifications(
    event_emitter,
    enabled: bool = True,
    categories: Optional[Set] = None,
    rate_limit: float = 0.1,
    dedup_seconds: int = 60
) -> Optional[TelegramLogNotifier]:
    """
    Configura notificações Telegram como subscriber de eventos.
    
    Args:
        event_emitter: EventEmitter para registrar subscriber
        enabled: Se deve habilitar notificações
        categories: Categorias a notificar
        rate_limit: Intervalo entre mensagens
        
    Returns:
        TelegramLogNotifier se criado, None se desabilitado
    """
    if not enabled or not TELEGRAM_AVAILABLE:
        print("📱 Notificações Telegram desabilitadas")
        return None
    
    # Criar notificador
    notifier = TelegramLogNotifier(
        enabled=enabled,
        categories=categories,
        rate_limit=rate_limit,
        dedup_seconds=dedup_seconds
    )
    
    # Registrar como subscriber de log_event
    def handle_log_event(event: Event) -> None:
        """Handler para eventos de log."""
        if event.data:
            notifier.handle_log_event(event.data)
    
    event_emitter.subscribe('log_event', handle_log_event)
    
    # Substituir print por logger para escrita em master/ e specialized/system
    # print("✅ Notificações Telegram configuradas")
    return notifier

