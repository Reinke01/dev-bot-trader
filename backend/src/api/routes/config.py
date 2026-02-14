from fastapi import APIRouter, Body
from api.services.config_manager import get_config_manager
from typing import Dict, Any

router = APIRouter()
config_manager = get_config_manager()

@router.get("/settings")
async def get_settings():
    """
    Retorna as configurações globais do bot.
    """
    return config_manager.get_config()

@router.post("/settings")
async def update_settings(settings: Dict[str, Any] = Body(...)):
    """
    Atualiza as configurações globais do bot.
    """
    config_manager.save_config(settings)
    return {"message": "Configurações atualizadas com sucesso", "config": config_manager.get_config()}
