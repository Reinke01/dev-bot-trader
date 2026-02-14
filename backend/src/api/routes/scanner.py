from fastapi import APIRouter
from api.services.scanner_service import get_scanner_service
from api.services.signal_service import get_signal_service
from api.services.bot_manager import get_bot_manager
from api.schemas import StartBotRequest, StartBotResponse

router = APIRouter()
scanner_service = get_scanner_service()
signal_service = get_signal_service()
bot_manager = get_bot_manager()

@router.get("/scanner/results")
async def get_scanner_results():
    """
    Retorna os resultados mais recentes do scan de moedas.
    """
    return scanner_service.get_results()

@router.post("/scanner/config")
async def update_scanner_config(limit: int):
    """
    Configura a quantidade de moedas a serem escaneadas.
    """
    scanner_service.set_limit(limit)
    return {"message": f"Limite atualizado para {limit}", "current_limit": scanner_service.scan_limit}

@router.get("/scanner/signals")
async def get_pending_signals():
    """
    Retorna os sinais/oportunidades identificados pelo scanner.
    """
    return signal_service.get_signals()

@router.post("/scanner/signals/approve", response_model=StartBotResponse)
async def approve_signal(symbol: str, config: StartBotRequest):
    """
    Aprova um sinal e inicia o bot correspondente.
    """
    # Force the symbol from the approval request
    config.cripto = symbol
    
    try:
        bot_id = bot_manager.start_bot(config)
        return StartBotResponse(
            success=True,
            message=f"Sinal aprovado! Bot para {symbol} iniciado.",
            bot_id=bot_id,
            details=config.model_dump()
        )
    except Exception as e:
        return StartBotResponse(
            success=False,
            message=f"Erro ao iniciar bot após aprovação: {str(e)}",
            bot_id=None
        )
