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
from corretoras.funcoes_bybit import busca_velas
from fastapi import Query
import pandas as pd

router = APIRouter()
bot_manager = get_bot_manager()


@router.post("/bot/start", response_model=StartBotResponse)
async def start_bot(config: StartBotRequest):
    """Inicia um bot de trading com as configurações fornecidas."""
    try:
        bot_id = bot_manager.start_bot(config)
        ws_path = f"/api/v1/ws/logs/{bot_id}"
        return StartBotResponse(
            success=True,
            message=f"Bot iniciado com sucesso.",
            bot_id=bot_id,
            ws_url=ws_path,
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


@router.get("/candles")
async def get_candles(symbol: str = Query(..., description="Símbolo ex: SOLUSDT"), tf: str = Query('15', description="Timeframe ex: 1,3,5,15,60,240,1D"), limit: int = Query(500, description="Número máximo de velas")):
    """Retorna velas históricas usando a integração Bybit (padronizado: [{t,o,h,l,c,v}] com t em ms)."""
    # Validar símbolo simples
    if not symbol or not isinstance(symbol, str):
        raise HTTPException(status_code=400, detail="Par inválido")

    # Mapear timeframes aceitos para o formato da corretora
    tf_map = {
        '1': '1', '3': '3', '5': '5', '15': '15', '30': '30', '60': '60', '240': '240',
        '1D': 'D', '1d': 'D', 'D': 'D'
    }
    tf_mapped = tf_map.get(tf, tf)

    try:
        df = busca_velas(symbol, tf_mapped, [5, 15])
        if df is None or df.empty:
            return {"symbol": symbol, "tf": tf_mapped, "candles": []}

        df = df.tail(limit)
        records = []
        for idx, row in df.reset_index().iterrows():
            ts = int(pd.to_datetime(row['tempo_abertura']).timestamp() * 1000) if row['tempo_abertura'] is not None else None
            records.append({
                "t": ts,
                "o": float(row['abertura']),
                "h": float(row['maxima']),
                "l": float(row['minima']),
                "c": float(row['fechamento']),
                "v": float(row['volume'])
            })

        return {"symbol": symbol, "tf": tf_mapped, "candles": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))