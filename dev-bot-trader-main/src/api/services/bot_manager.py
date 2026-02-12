"""
Bot Manager para API - Gerencia lifecycle de bots.

Focado apenas em:
- Iniciar/parar bots
- Gerenciar threads
- Status dos bots

Logs são automaticamente capturados pelo LogStreamManager via Event Emitter.
"""

import uuid
import threading
from datetime import datetime
from typing import Dict, Optional
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from live_trading.double_ema_breakout_orders_long_short_dual_params_agent_evaluator import start_live_trading_bot
from entidades.lado_operacao import LadoOperacao
from entidades.risco_operacao import RiscoOperacao
from utils.logging import get_logger, LogCategory


class BotManager:
    """
    Gerenciador de bots - focado em lifecycle.
    
    - Inicia/para bots em threads separadas
    - Rastreia status e configurações
    - Logs são automáticos via sistema de logging existente
    """
    
    def __init__(self):
        self.bots: Dict[str, dict] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
    
    def start_bot(self, config) -> str:
        """
        Inicia um bot em uma thread separada.
        
        O bot usa o sistema de logging existente (sem modificações).
        LogStreamManager captura automaticamente todos os logs.
        """
        bot_id = str(uuid.uuid4())  # UUID da API para controle
        
        # Converter enums
        lado_op = LadoOperacao(config.lado_operacao.value)
        risco_op = RiscoOperacao(config.risco_por_operacao.value)
        
        # Criar flag de parada
        stop_flag = threading.Event()
        self.stop_flags[bot_id] = stop_flag
        
        # Criar thread para executar o bot
        thread = threading.Thread(
            target=self._run_bot_safely,
            kwargs={
                'stop_flag': stop_flag,
                'bot_id': bot_id,
                'subconta': config.subconta,
                'cripto': config.cripto,
                'tempo_grafico': config.tempo_grafico,
                'lado_operacao': lado_op,
                'frequencia_agente_horas': config.frequencia_agente_horas,
                'executar_agente_no_start': config.executar_agente_no_start,
                'ema_rapida_compra': config.ema_rapida_compra,
                'ema_lenta_compra': config.ema_lenta_compra,
                'ema_rapida_venda': config.ema_rapida_venda,
                'ema_lenta_venda': config.ema_lenta_venda,
                'risco_por_operacao': risco_op,
            },
            daemon=True,
            name=f"Bot_{config.cripto}_{config.tempo_grafico}"
        )
        
        self.bots[bot_id] = {
            'config': config.model_dump(),
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'thread_id': thread.ident,
            'thread_name': thread.name,
        }
        
        self.threads[bot_id] = thread
        thread.start()
        
        # Log de sistema (da API, não do bot)
        logger = get_logger("BotManagerAPI")
        logger.info(
            LogCategory.BOT_START,
            f"🚀 Bot iniciado via API",
            "bot_manager",
            api_bot_id=bot_id,
            cripto=config.cripto,
            tempo_grafico=config.tempo_grafico,
            subconta=config.subconta,
        )
        
        return bot_id
    
    def _run_bot_safely(self, bot_id: str, stop_flag: threading.Event, **kwargs):
        """
        Executa o bot com tratamento de erro.
        
        Passa stop_flag para o bot permitir parada graciosa.
        """
        try:
            start_live_trading_bot(bot_id=bot_id, stop_flag=stop_flag, **kwargs)
        except Exception as e:
            logger = get_logger("BotManagerAPI")
            logger.error(
                LogCategory.EXECUTION_ERROR,
                f"❌ Erro ao executar bot",
                "bot_manager",
                exception=e,
                api_bot_id=bot_id
            )
    
    def stop_bot(self, bot_id: str, timeout: int = 10) -> bool:
        """Para um bot específico com timeout."""
        if bot_id not in self.bots:
            return False
        
        bot_info = self.bots[bot_id]
        
        # Sinalizar parada
        if bot_id in self.stop_flags:
            self.stop_flags[bot_id].set()
        
        # Aguardar thread parar graciosamente
        thread = self.threads.get(bot_id)
        if thread and thread.is_alive():
            thread.join(timeout=timeout)
        
        # Verificar se parou
        stopped = not (thread and thread.is_alive())
        
        # Log de sistema
        logger = get_logger("BotManagerAPI")
        
        if stopped:
            self.bots[bot_id]['status'] = 'stopped'
            self.bots[bot_id]['stopped_at'] = datetime.now().isoformat()
            logger.info(
                LogCategory.BOT_STOP,
                "✅ Bot parado com sucesso",
                "bot_manager",
                api_bot_id=bot_id,
                cripto=bot_info['config']['cripto'],
                tempo_grafico=bot_info['config']['tempo_grafico']
            )
        else:
            self.bots[bot_id]['status'] = 'error'
            self.bots[bot_id]['stopped_at'] = datetime.now().isoformat()
            logger.warning(
                LogCategory.BOT_STOP,
                "⚠️ Bot não respondeu ao sinal de parada no timeout",
                "bot_manager",
                api_bot_id=bot_id,
                cripto=bot_info['config']['cripto'],
                tempo_grafico=bot_info['config']['tempo_grafico'],
                timeout=timeout
            )
        
        return stopped
    
    def get_bot_status(self, bot_id: str) -> Optional[dict]:
        """Retorna o status de um bot específico."""
        if bot_id not in self.bots:
            return None
        
        bot_info = self.bots[bot_id]
        thread = self.threads.get(bot_id)
        
        return {
            'bot_id': bot_id,
            'status': 'running' if (thread and thread.is_alive()) else 'stopped',
            'subconta': bot_info['config']['subconta'],
            'cripto': bot_info['config']['cripto'],
            'tempo_grafico': bot_info['config']['tempo_grafico'],
            'lado_operacao': bot_info['config']['lado_operacao'],
            'risco_por_operacao': bot_info['config']['risco_por_operacao'],
            'frequencia_agente_horas': bot_info['config']['frequencia_agente_horas'],
            'executar_agente_no_start': bot_info['config']['executar_agente_no_start'],
            'ema_rapida_compra': bot_info['config']['ema_rapida_compra'],
            'ema_lenta_compra': bot_info['config']['ema_lenta_compra'],
            'ema_rapida_venda': bot_info['config']['ema_rapida_venda'],
            'ema_lenta_venda': bot_info['config']['ema_lenta_venda'],
            'started_at': bot_info['started_at'],
            'stopped_at': bot_info.get('stopped_at'),
        }
    
    def get_all_bots_status(self):
        """Retorna o status de todos os bots."""
        return [self.get_bot_status(bot_id) for bot_id in self.bots.keys()]
    
    def stop_all_bots(self) -> int:
        """Para todos os bots."""
        count = 0
        for bot_id in list(self.bots.keys()):
            if self.stop_bot(bot_id):
                count += 1
        return count


# ============= Singleton =============

_bot_manager_instance: Optional['BotManager'] = None

def get_bot_manager() -> 'BotManager':
    """Retorna instância singleton do BotManager."""
    global _bot_manager_instance
    if _bot_manager_instance is None:
        _bot_manager_instance = BotManager()
    return _bot_manager_instance