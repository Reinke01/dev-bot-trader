import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trading, websocket, monitor, scanner, config, optimization, analise, market, ai, trade, bot
from api.services.log_stream_manager import get_log_stream_manager
from api.services.scanner_service import get_scanner_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da API (startup e shutdown).
    """
    # Startup: Configurar LogStreamManager com event loop
    loop = asyncio.get_running_loop()
    log_manager = get_log_stream_manager()
    log_manager.set_event_loop(loop)
    
    # Iniciar Scanner Service em background (Thread)
    scanner_service = get_scanner_service()
    scanner_service.start_scanning()
    
    # print("✅ API iniciada - LogStreamManager e Scanner configuradoss")
    
    yield  # API está rodando
    
    # Shutdown: Limpeza se necessário
    # print("🛑 API encerrando...")

app = FastAPI(
    title="Trading Bot API",
    description="API para controle do bot de trading com WebSocket para logs",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "trading",
            "description": "Operações para gerenciar bots de trading: iniciar, parar e monitorar status.",
        },
        {
            "name": "websocket",
            "description": "Conexões WebSocket para streaming de logs em tempo real.",
        },
    ]
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(trading.router, prefix="/api/v1", tags=["trading"])
app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
app.include_router(monitor.router, prefix="/api/v1", tags=["monitor"])
app.include_router(scanner.router, prefix="/api/v1", tags=["scanner"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(optimization.router, prefix="/api/v1", tags=["optimization"])
app.include_router(analise.router, prefix="/api/v1", tags=["analise"])
# Web Terminal routes
app.include_router(market.router, prefix="/api/v1", tags=["market"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])
app.include_router(trade.router, prefix="/api/v1", tags=["trade"])
app.include_router(bot.router, prefix="/api/v1", tags=["bot"])

# Standardized endpoints (Passo 5)
@app.get("/api/v1/opportunities", tags=["standard"])
async def get_opportunities(tf: str = "15", limit: int = 10, universe: str = "top20"):
    """
    Retorna oportunidades de trading (Fallback/Dev).
    """
    try:
        from api.services.scanner_service import get_scanner_service
        service = get_scanner_service()
        results = service.get_results()
        if results:
            return results[:limit]
        
        # Mock responses if no results
        return [
            {"symbol": "BTCUSDT", "tf": tf, "score": 4.5, "signal": "BUY", "reason": "RSI Oversold + Support"},
            {"symbol": "ETHUSDT", "tf": tf, "score": 4.2, "signal": "BUY", "reason": "EMA Crossover"},
            {"symbol": "SOLUSDT", "tf": tf, "score": 3.8, "signal": "NEUTRAL", "reason": "Consolidation"}
        ]
    except Exception:
        return [
            {"symbol": "BTCUSDT", "tf": tf, "score": 4.5, "signal": "BUY", "reason": "Fallback Data"}
        ]

from pydantic import BaseModel
class AnalyzeRequest(BaseModel):
    symbol: str
    tf: str = "15"

@app.post("/api/v1/analyze", tags=["standard"])
async def analyze_crypto(request: AnalyzeRequest):
    """
    Analisa uma moeda específica (Fallback/Dev).
    """
    try:
        from varredura_didi_bollinger import analisar_moeda
        res = analisar_moeda(request.symbol)
        if res:
            return {
                "symbol": request.symbol,
                "score": res.get('score', 0),
                "confidence": 0.85,
                "narrative": f"Análise técnica para {request.symbol} no timeframe {request.tf}.",
                "plan": "Aguardar confirmação de rompimento"
            }
    except Exception:
        pass

    return {
        "symbol": request.symbol,
        "score": 4.2,
        "confidence": 0.8,
        "narrative": f"Fallback: {request.symbol} apresenta tendência de alta no {request.tf}m.",
        "plan": "Entrada sugerida em 0.5% acima do preço atual"
    }

@app.get("/")
async def root():
    return {"message": "Trading Bot API está online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

"""
Exemplo de como conectar ao WebSocket via console do navegador:
const botId = "SEU_BOT_ID_REAL";  // Pegue da resposta do start
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/logs/${botId}`);

ws.onopen = () => console.log("✅ Conectado!");
ws.onmessage = (event) => {
    const log = JSON.parse(event.data);
    console.log(`[${log.timestamp}] [${log.level}] ${log.message}`);
};
ws.onerror = (error) => console.error("❌ Erro:", error);
ws.onclose = () => console.log("❌ Desconectado");
"""