"""
Rotas REST para gerenciar bots.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import APIRouter, HTTPException
from api.schemas import StartBotRequest, StartBotResponse, BotStatusResponse
from api.services.bot_manager import get_bot_manager
from typing import List

router = APIRouter()
bot_manager = get_bot_manager()


@router.post("/bot/start", response_model=StartBotResponse)
async def start_bot(config: StartBotRequest):
    """Inicia um bot de trading com as configurações fornecidas."""
    try:
        bot_id = bot_manager.start_bot(config)
        return StartBotResponse(
            success=True,
            message=f"Bot iniciado com sucesso. Acesse o seguinte link para acompanhar o log do bot: http://localhost:8000/api/v1/ws/logs/{bot_id}",
            bot_id=bot_id,
            details=config.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot/status", response_model=List[BotStatusResponse])
async def get_all_bots_status():
    """Retorna o status de todos os bots em execução."""
    return bot_manager.get_all_bots_status()


@router.get("/bot/status/{bot_id}", response_model=BotStatusResponse)
async def get_bot_status(bot_id: str):
    """Retorna o status de um bot específico."""
    status = bot_manager.get_bot_status(bot_id)
    if not status:
        raise HTTPException(status_code=404, detail="Bot não encontrado")
    return status


@router.post("/bot/stop/{bot_id}")
async def stop_bot(bot_id: str):
    """Para um bot específico."""
    success = bot_manager.stop_bot(bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bot não encontrado ou já parado")
    return {"success": True, "message": f"Bot {bot_id} parado com sucesso"}


@router.post("/bot/stop-all")
async def stop_all_bots():
    """Para todos os bots em execução."""
    count = bot_manager.stop_all_bots()
    return {"success": True, "message": f"{count} bot(s) parado(s)"}