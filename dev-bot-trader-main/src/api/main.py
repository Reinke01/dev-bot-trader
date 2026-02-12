import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trading, websocket
from api.services.log_stream_manager import get_log_stream_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da API (startup e shutdown).
    """
    # Startup: Configurar LogStreamManager com event loop
    loop = asyncio.get_running_loop()
    log_manager = get_log_stream_manager()
    log_manager.set_event_loop(loop)
    # print("✅ API iniciada - LogStreamManager configurado para streaming em tempo real")
    
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