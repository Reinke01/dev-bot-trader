import json
import requests
from typing import Optional
from .base import BaseNotifier

try:
    from ..logging.enums import LogCategory
    from ..logging.models import LogEvent
except ImportError:
    LogEvent = None
    LogCategory = None

class WebhookNotifier(BaseNotifier):
    """
    Generic Webhook Notifier (compatible with Zapier, Make, Discord, etc).
    Use this to bridge notifications to Instagram.
    """
    
    def __init__(self, url: str, enabled: bool = True):
        super().__init__(enabled)
        self.url = url

    def should_notify(self, log_event: 'LogEvent') -> bool:
        if not self.url or not self.enabled:
            return False
        # Notify only important events by default
        important = {
            LogCategory.POSITION_OPEN,
            LogCategory.EXECUTION_ERROR,
            LogCategory.AGENT_DECISION
        }
        return log_event.category in important

    def _send_notification(self, log_event: 'LogEvent') -> None:
        try:
            payload = {
                "event": log_event.category.value if log_event.category else "unknown",
                "message": log_event.message,
                "symbol": log_event.context.get('symbol', 'N/A'),
                "timestamp": log_event.timestamp.isoformat(),
                "details": log_event.context
            }
            requests.post(self.url, json=payload, timeout=5)
        except Exception as e:
            print(f"⚠️ Webhook Error: {e}")
