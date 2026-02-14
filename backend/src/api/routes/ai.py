from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import random
from datetime import datetime

router = APIRouter()

class AnalyzeRequest(BaseModel):
    symbol: str
    side: Optional[str] = None  # 'buy' or 'sell', if None IA decides


def generate_trade_plan_mock(symbol: str, side: Optional[str] = None) -> Dict[str, Any]:
    """Generate a mock AI trade plan"""
    
    # Decide side if not provided
    if side is None:
        side = random.choice(['buy', 'sell'])
    
    # Mock current price
    base_prices = {
        'BTCUSDT': 95000,
        'ETHUSDT': 2800,
        'SOLUSDT': 87,
        'BNBUSDT': 580,
        'XRPUSDT': 2.1,
        'ADAUSDT': 0.95,
        'DOGEUSDT': 0.28,
        'DOTUSDT': 6.5,
        'AVAXUSDT': 35,
        'LINKUSDT': 18,
    }
    
    price = base_prices.get(symbol, 100)
    is_buy = side == 'buy'
    
    # Generate entry, SL, TP
    entry_price = price
    stop_loss_price = entry_price * (0.97 if is_buy else 1.03)
    take_profit_price = entry_price * (1.05 if is_buy else 0.95)
    
    risk_reward = abs(take_profit_price - entry_price) / abs(entry_price - stop_loss_price)
    confidence = random.uniform(60, 90)
    
    plan = {
        'symbol': symbol,
        'direction': side,
        'confidence': round(confidence, 1),
        'entry': {
            'price': round(entry_price, 2),
            'reason': (
                'Retração em suporte chave + divergência RSI positiva'
                if is_buy else
                'Rejeição em resistência + padrão de reversão confirmado'
            )
        },
        'stopLoss': {
            'price': round(stop_loss_price, 2),
            'reason': (
                'Abaixo do swing low recente e suporte de Fibonacci 50%'
                if is_buy else
                'Acima do swing high recente e resistência psicológica'
            )
        },
        'takeProfit': {
            'price': round(take_profit_price, 2),
            'reason': (
                'Próxima resistência em Fibonacci 61.8% com confluência de EMA 200'
                if is_buy else
                'Próximo suporte em Fibonacci 38.2% com confluência de EMA 50'
            )
        },
        'riskReward': round(risk_reward, 2),
        'analysis': {
            'trend': (
                'Tendência de alta no timeframe diário com Higher Highs confirmados'
                if is_buy else
                'Tendência de baixa no timeframe diário com Lower Lows confirmados'
            ),
            'structure': (
                'Formando Higher Lows indicando força compradora'
                if is_buy else
                'Formando Lower Highs indicando pressão vendedora'
            ),
            'momentum': (
                'RSI saindo de zona de sobrevenda (35 → 48) com divergência positiva'
                if is_buy else
                'RSI entrando em zona de sobrevenda após rejeição em sobrecompra'
            ),
            'volume': 'Volume acima da média nas últimas 3 candles confirmando movimento',
            'summary': (
                f'Setup de compra com boa relação risco/retorno ({risk_reward:.2f}). '
                'Confluência de múltiplos indicadores técnicos. '
                'Aguardar confirmação de entrada com candle de alta. '
                'Gerenciar posição com trailing stop após atingir 2R.'
                if is_buy else
                f'Setup de venda com relação risco/retorno favorável ({risk_reward:.2f}). '
                'Sinais técnicos confluentes indicando reversão. '
                'Considerar entrada em duas parcelas. '
                'Gerenciar risco com stop loss ajustado conforme mercado.'
            )
        },
        'warnings': [
            '⚠️ Esta é uma análise simulada para demonstração',
            '⚠️ Sempre faça sua própria análise antes de operar',
            '⚠️ Gerencie seu risco adequadamente',
            '⚠️ Não opere com mais do que pode perder',
        ],
        'timestamp': int(datetime.now().timestamp() * 1000),
    }
    
    return plan


@router.post('/ai/analyze')
async def analyze_with_ai(request: AnalyzeRequest):
    """
    Analyze a symbol with AI and generate a trade plan.
    
    Returns a structured trade plan with entry, stop loss, take profit,
    risk/reward ratio, and detailed analysis.
    
    To integrate with real AI:
    - Import your AI agent (TradeEntryEvaluator or similar)
    - Call agent.analyze(symbol, timeframe, side)
    - Format response to match this structure
    - Include actual technical analysis
    """
    try:
        plan = generate_trade_plan_mock(request.symbol, request.side)
        return plan
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.post('/ai/analyze-batch')
async def analyze_batch(symbols: List[str]):
    """
    Analyze multiple symbols in batch.
    
    Returns a list of trade plans for each symbol.
    """
    try:
        plans = []
        for symbol in symbols:
            plan = generate_trade_plan_mock(symbol)
            plans.append(plan)
        
        return {
            'timestamp': int(datetime.now().timestamp() * 1000),
            'count': len(plans),
            'plans': plans,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
