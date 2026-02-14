from fastapi import APIRouter, HTTPException, Query
from api.services.optimization_service import get_optimization_service
from typing import List, Dict, Any

router = APIRouter()
opt_service = get_optimization_service()

@router.get("/optimization/top/{symbol}")
async def get_top_parameters(
    symbol: str, 
    interval: str = "15", 
    days: int = Query(7, gt=0, le=30)
):
    """Retorna os melhores parâmetros encontrados para um símbolo."""
    try:
        results = opt_service.optimize_symbol(symbol, interval, days)
        if not results:
            return {"success": False, "message": "Nenhum resultado encontrado ou falha na otimização."}
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimization/run/{symbol}")
async def run_optimization(
    symbol: str, 
    interval: str = "15", 
    days: int = 7
):
    """Inicia uma otimização sob demanda (útil para limpar cache ou forçar atualização)."""
    try:
        # Força limpeza de cache para este par
        cache_key = f"{symbol}_{interval}_{days}"
        if cache_key in opt_service.cache:
            del opt_service.cache[cache_key]
            
        results = opt_service.optimize_symbol(symbol, interval, days)
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
