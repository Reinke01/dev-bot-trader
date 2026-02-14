"""
Rota para análises Didi + Bollinger
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

router = APIRouter(prefix="/analise", tags=["analise"])

# Cache de resultados
_cache_varredura = {
    'timestamp': None,
    'dados': None
}

@router.get("/varredura")
async def get_varredura() -> List[Dict]:
    """
    Retorna varredura completa Didi + Bollinger
    """
    try:
        import time
        from varredura_didi_bollinger import analisar_moeda, MOEDAS
        
        # Verificar cache (válido por 5 minutos)
        agora = time.time()
        if _cache_varredura['timestamp'] and (agora - _cache_varredura['timestamp']) < 300:
            return _cache_varredura['dados']
        
        # Executar varredura
        resultados = []
        for moeda in MOEDAS:
            resultado = analisar_moeda(moeda)
            if resultado:
                resultados.append(resultado)
        
        # Ordenar por score
        resultados.sort(key=lambda x: x['score'], reverse=True)
        
        # Atualizar cache
        _cache_varredura['timestamp'] = agora
        _cache_varredura['dados'] = resultados
        
        return resultados
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/moeda/{simbolo}")
async def get_analise_moeda(simbolo: str) -> Dict:
    """
    Retorna análise detalhada de uma moeda
    """
    try:
        from varredura_didi_bollinger import analisar_moeda
        
        if not simbolo.endswith('USDT'):
            simbolo += 'USDT'
        
        resultado = analisar_moeda(simbolo.upper())
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Moeda não encontrada")
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
