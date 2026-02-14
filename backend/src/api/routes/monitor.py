"""
Rotas REST para monitoria do estado dos bots (agregado via LogEvents).
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException
from api.services.monitor_state import get_monitor_state
from api.services.bot_manager import get_bot_manager

router = APIRouter()
monitor_state = get_monitor_state()
bot_manager = get_bot_manager()


@router.get("/monitor/bots")
async def get_monitor_bots():
    """
    Retorna resumo do estado monitorado de todos os bots.
    """
    summaries = monitor_state.get_summary()

    bot_status_map = {b["bot_id"]: b for b in bot_manager.get_all_bots_status()}
    for item in summaries:
        status = bot_status_map.get(item["bot_id"])
        if status:
            item["status"] = status["status"]
            item["cripto"] = status["cripto"]
            item["tempo_grafico"] = status["tempo_grafico"]
            item["subconta"] = status["subconta"]
    return summaries


@router.get("/monitor/bots/{bot_id}")
async def get_monitor_bot(bot_id: str):
    """
    Retorna o estado monitorado detalhado de um bot.
    """
    state = monitor_state.get_bot(bot_id)
    if not state:
        raise HTTPException(status_code=404, detail="Bot nao encontrado no monitor")

    status = bot_manager.get_bot_status(bot_id)
    if status:
        state["status"] = status["status"]
        state["meta"]["cripto"] = status["cripto"]
        state["meta"]["tempo_grafico"] = status["tempo_grafico"]
        state["meta"]["subconta"] = status["subconta"]

    return state
