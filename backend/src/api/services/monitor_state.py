"""
MonitorState - Agrega estado dos bots a partir de LogEvents.

Responsabilidades:
- Escutar eventos do logging (log_event)
- Consolidar estado por bot (trade, sinais, decisao de agentes)
- Expor dados para endpoints REST do monitor
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Dict, Optional

from utils.notifications.events import get_event_emitter
from utils.logging import LogCategory
from utils.logging.models import LogEvent
from agentes.parsers.trade_entry_evaluator_parser import TradeEntryEvaluatorParser
from agentes.parsers.trade_conductor_parser import TradeConductorParser


def _to_iso(ts: Optional[datetime]) -> Optional[str]:
    if not ts:
        return None
    return ts.isoformat()


def _safe_value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value


class MonitorState:
    """
    Agregador de estado em memoria para monitoria.

    Observacao: mantem apenas ultimo estado relevante por bot.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._bots: Dict[str, Dict[str, Any]] = {}
        self._entry_parser = TradeEntryEvaluatorParser()
        self._conductor_parser = TradeConductorParser()

        get_event_emitter().subscribe("log_event", self._on_log_event)

    def _default_state(self, bot_id: str) -> Dict[str, Any]:
        return {
            "bot_id": bot_id,
            "status": "unknown",
            "meta": {
                "subconta": None,
                "cripto": None,
                "tempo_grafico": None,
                "lado_operacao": None,
                "risco_por_operacao": None,
            },
            "last_log": {
                "timestamp": None,
                "category": None,
                "level": None,
                "message": None,
            },
            "trade": {
                "estado": None,
                "side": None,
                "entry_price": None,
                "stop_price": None,
                "target_price": None,
                "position_size": None,
                "trailing_stop": None,
                "risk_reward": None,
                "updated_at": None,
            },
            "signal": {
                "side": None,
                "tempo_grafico": None,
                "detected_at": None,
            },
            "entry_evaluator": {
                "last_response": None,
                "last_decision": None,
                "received_at": None,
                "parse_ok": None,
            },
            "trade_conductor": {
                "last_response": None,
                "last_decision": None,
                "received_at": None,
                "parse_ok": None,
            },
            "last_action": None,
            "last_blocker": None,
            "errors": {
                "count": 0,
                "last": None,
            },
            "warnings": {
                "count": 0,
                "last": None,
            },
            "stats": {
                "trading_events": 0,
                "agent_events": 0,
                "error_events": 0,
                "system_events": 0,
            },
        }

    def _resolve_target_bot_id(self, log_event: LogEvent) -> Optional[str]:
        if log_event.bot_id and log_event.bot_id != "BotManagerAPI":
            return log_event.bot_id
        api_bot_id = log_event.context.get("api_bot_id")
        if api_bot_id:
            return api_bot_id
        return log_event.bot_id

    def _on_log_event(self, event) -> None:
        log_event = event.data
        if not isinstance(log_event, LogEvent):
            return

        bot_id = self._resolve_target_bot_id(log_event)
        if not bot_id:
            return

        with self._lock:
            state = self._bots.setdefault(bot_id, self._default_state(bot_id))
            self._apply_log_event(state, log_event)

    def _apply_log_event(self, state: Dict[str, Any], log_event: LogEvent) -> None:
        category = log_event.category
        context = log_event.context or {}

        state["last_log"] = {
            "timestamp": _to_iso(log_event.timestamp),
            "category": category.value,
            "level": log_event.level.name,
            "message": log_event.message,
        }

        if log_event.is_error:
            state["errors"]["count"] += 1
            state["errors"]["last"] = {
                "timestamp": _to_iso(log_event.timestamp),
                "category": category.value,
                "message": log_event.message,
            }

        if log_event.level.name == "WARNING":
            state["warnings"]["count"] += 1
            state["warnings"]["last"] = {
                "timestamp": _to_iso(log_event.timestamp),
                "category": category.value,
                "message": log_event.message,
            }

        if log_event.is_trading_event:
            state["stats"]["trading_events"] += 1
        if log_event.is_agent_event:
            state["stats"]["agent_events"] += 1
        if log_event.is_error:
            state["stats"]["error_events"] += 1
        if log_event.is_system_event:
            state["stats"]["system_events"] += 1

        if category == LogCategory.BOT_START:
            state["status"] = "running"
            state["meta"]["subconta"] = context.get("subconta")
            state["meta"]["cripto"] = context.get("symbol") or context.get("cripto")
            state["meta"]["tempo_grafico"] = context.get("tempo_grafico")
            state["meta"]["lado_operacao"] = _safe_value(context.get("lado_operacao"))
            state["meta"]["risco_por_operacao"] = _safe_value(context.get("risco_por_operacao"))

        if category == LogCategory.BOT_STOP:
            state["status"] = "stopped"

        if category == LogCategory.POSITION_STATUS:
            state["trade"].update({
                "estado": _safe_value(context.get("estado_de_trade")),
                "entry_price": context.get("preco_entrada"),
                "stop_price": context.get("preco_stop"),
                "target_price": context.get("preco_alvo"),
                "position_size": context.get("tamanho_posicao"),
                "trailing_stop": context.get("trailing_stop"),
                "updated_at": _to_iso(log_event.timestamp),
            })

        if category == LogCategory.POSITION_OPEN:
            state["trade"].update({
                "estado": "aberto",
                "side": context.get("operation"),
                "entry_price": context.get("entry_price"),
                "stop_price": context.get("stop_price"),
                "target_price": context.get("target_price"),
                "position_size": context.get("position_size"),
                "risk_reward": context.get("risk_reward"),
                "updated_at": _to_iso(log_event.timestamp),
            })

        if category in {LogCategory.TARGET_HIT, LogCategory.STOP_HIT, LogCategory.MANUAL_CLOSE}:
            state["trade"].update({
                "estado": "de fora",
                "updated_at": _to_iso(log_event.timestamp),
            })

        if category == LogCategory.AGENT_EXECUTION and log_event.agent_name == "Entry Evaluator":
            state["signal"].update({
                "side": context.get("lado_operacao"),
                "tempo_grafico": context.get("tempo_grafico"),
                "detected_at": _to_iso(log_event.timestamp),
            })

        if category == LogCategory.AGENT_RESPONSE:
            response_content = context.get("response_content") or ""
            if log_event.agent_name == "Entry Evaluator":
                parsed = self._entry_parser.parse_response(response_content)
                state["entry_evaluator"].update({
                    "last_response": response_content,
                    "last_decision": parsed,
                    "received_at": _to_iso(log_event.timestamp),
                    "parse_ok": parsed is not None,
                })
            elif log_event.agent_name == "Trade Conductor":
                parsed = self._conductor_parser.parse_response(response_content)
                state["trade_conductor"].update({
                    "last_response": response_content,
                    "last_decision": parsed,
                    "received_at": _to_iso(log_event.timestamp),
                    "parse_ok": parsed is not None,
                })

        if category == LogCategory.AGENT_DECISION:
            state["last_action"] = {
                "timestamp": _to_iso(log_event.timestamp),
                "agent_name": log_event.agent_name,
                "action": context.get("action"),
                "decision": context.get("decision"),
                "confidence": context.get("confidence"),
            }

        if category == LogCategory.AGENT_ACTION:
            state["last_action"] = {
                "timestamp": _to_iso(log_event.timestamp),
                "agent_name": log_event.agent_name,
                "action": context.get("action"),
                "details": context,
            }

        if category in {
            LogCategory.INVALID_PRICES,
            LogCategory.INVALID_ORDER_QTY,
            LogCategory.LOW_RISK_REWARD,
            LogCategory.PARSING_ERROR,
            LogCategory.TRADE_OPEN_ERROR,
        }:
            state["last_blocker"] = {
                "timestamp": _to_iso(log_event.timestamp),
                "category": category.value,
                "message": log_event.message,
                "details": context,
            }

    def get_summary(self) -> list:
        with self._lock:
            return [
                {
                    "bot_id": bot_id,
                    "status": data["status"],
                    "cripto": data["meta"]["cripto"],
                    "tempo_grafico": data["meta"]["tempo_grafico"],
                    "subconta": data["meta"]["subconta"],
                    "last_log": data["last_log"],
                    "trade": data["trade"],
                    "entry_evaluator": {
                        "received_at": data["entry_evaluator"]["received_at"],
                        "last_decision": data["entry_evaluator"]["last_decision"],
                    },
                    "trade_conductor": {
                        "received_at": data["trade_conductor"]["received_at"],
                        "last_decision": data["trade_conductor"]["last_decision"],
                    },
                }
                for bot_id, data in self._bots.items()
            ]

    def get_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._bots.get(bot_id)


_monitor_state_instance: Optional[MonitorState] = None


def get_monitor_state() -> MonitorState:
    global _monitor_state_instance
    if _monitor_state_instance is None:
        _monitor_state_instance = MonitorState()
    return _monitor_state_instance
