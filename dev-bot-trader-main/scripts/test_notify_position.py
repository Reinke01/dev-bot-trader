#!/usr/bin/env python3
"""
Envia um log de posição aberta para testar notificações Telegram via sistema de logging.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT, 'src'))

from utils.logging import get_logger, LogCategory

logger = get_logger('test-notify')

logger.trading(LogCategory.POSITION_OPEN, "Teste: posição aberta", "test_notify", symbol='SOLUSDT', operation='compra', entry_price=100.0, stop_price=95.0, target_price=110.0, position_size=0.1, risk_reward=1.5)
print('Log enviado')
