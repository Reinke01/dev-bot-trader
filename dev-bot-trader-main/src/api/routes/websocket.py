"""
Rotas WebSocket - Usa LogStreamManager para streaming de logs.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.services.log_stream_manager import get_log_stream_manager
from api.services.bot_manager import get_bot_manager

router = APIRouter()

# Instâncias singleton globais
log_manager = get_log_stream_manager()
bot_manager = get_bot_manager()


@router.websocket("/ws/logs")
async def websocket_logs_all(websocket: WebSocket):
    """
    WebSocket para receber logs de todos os bots.
    
    Envia buffer de logs recentes ao conectar.
    """
    await websocket.accept()
    
    # Callback para enviar via WebSocket
    async def send_log(message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    # Enviar buffer de logs recentes
    for log in log_manager.get_buffer():
        await websocket.send_json(log)
    
    # Registrar subscriber para novos logs
    log_manager.subscribe_global(send_log)
    
    try:
        while True:
            # Manter conexão viva
            data = await websocket.receive_text()
            # Pode processar comandos do cliente aqui (filtros, etc)
    except WebSocketDisconnect:
        log_manager.unsubscribe_global(send_log)


@router.websocket("/ws/logs/{bot_id}")
async def websocket_logs_bot(websocket: WebSocket, bot_id: str):
    """
    WebSocket para receber logs de um bot específico.
    
    Filtra logs pelo bot_id.
    """
    # Validar se o bot existe antes de aceitar conexão
    bot_status = bot_manager.get_bot_status(bot_id)
    if not bot_status:
        await websocket.close(code=1008, reason=f"Bot '{bot_id}' não encontrado")
        return
    
    await websocket.accept()
    
    # Callback para enviar via WebSocket
    async def send_log(message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    # Enviar buffer específico desse bot (eficiente - O(1))
    for log in log_manager.get_buffer(bot_id=bot_id):
        await websocket.send_json(log)
    
    # Registrar subscriber para novos logs desse bot
    log_manager.subscribe_to_bot(bot_id, send_log)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Pode processar comandos do cliente aqui
    except WebSocketDisconnect:
        log_manager.unsubscribe_from_bot(bot_id, send_log)


@router.get("/ws/connections")
async def get_connections_info():
    """
    Retorna informações sobre conexões WebSocket ativas e estatísticas do streaming.
    """
    bot_statuses = bot_manager.get_all_bots_status()
    log_stats = log_manager.get_stats()
    bot_subscribers = log_manager.get_all_bot_subscribers()
    
    return {
        "global_connections": log_stats['total_global_subscribers'],
        "bot_connections": bot_subscribers,
        "total_bots": len(bot_statuses),
        "active_bots": len([b for b in bot_statuses if b['status'] == 'running']),
        "log_stats": {
            "buffer_size": log_stats['buffer_size'],
            "buffer_max": log_stats['buffer_max'],
            "total_bot_subscribers": log_stats['total_bot_subscribers'],
            "bots_with_subscribers": log_stats['bots_with_subscribers']
        }
    }