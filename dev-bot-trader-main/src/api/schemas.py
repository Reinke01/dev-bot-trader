from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict
from enum import Enum

# ============= Trading Bot Schemas =============
class LadoOperacaoEnum(str, Enum):
    APENAS_COMPRA = "compra"
    APENAS_VENDA = "venda"  
    AMBOS = "ambos"

class RiscoOperacaoEnum(float, Enum):
    MUITO_BAIXO = 0.005
    BAIXO = 0.01
    MEDIO = 0.02
    ALTO = 0.05
    MUITO_ALTO = 0.08

class StartBotRequest(BaseModel):
    subconta: int = Field(default=1, ge=1, description="Número da subconta")
    cripto: str = Field(default="SOLUSDT", description="Par de criptomoeda")
    tempo_grafico: str = Field(default="15", description="Timeframe em minutos")
    lado_operacao: LadoOperacaoEnum = Field(default=LadoOperacaoEnum.AMBOS, description="Lado da operação: compra, venda ou ambos")
    frequencia_agente_horas: float = Field(default=4, gt=0, description="Frequência do agente em horas")
    executar_agente_no_start: bool = Field(default=False, description="Executar agente condutor no start em caso de trade aberto")
    ema_rapida_compra: int = Field(default=5, gt=0, description="EMA rápida para compra")
    ema_lenta_compra: int = Field(default=15, gt=0, description="EMA lenta para compra")
    ema_rapida_venda: int = Field(default=21, gt=0, description="EMA rápida para venda")
    ema_lenta_venda: int = Field(default=125, gt=0, description="EMA lenta para venda")
    risco_por_operacao: RiscoOperacaoEnum = Field(default=RiscoOperacaoEnum.BAIXO,
        description="Risco por operação: muito baixo (0.005 = 0.5%), baixo (0.01 = 1%), médio (0.02 = 2%), alto (0.05 = 5%), muito alto (0.08 = 8%)")

class BotStatusResponse(BaseModel):
    bot_id: str
    status: Literal["running", "stopped", "error"] = Field(description="Status atual do bot")
    subconta: int
    cripto: str
    tempo_grafico: str
    lado_operacao: LadoOperacaoEnum = Field(description="Lado da operação: compra, venda ou ambos")
    risco_por_operacao: RiscoOperacaoEnum = Field(description="Risco por operação")
    frequencia_agente_horas: float = Field(description="Frequência do agente em horas")
    executar_agente_no_start: bool = Field(description="Executar agente condutor no start em caso de trade aberto")
    ema_rapida_compra: int = Field(description="EMA rápida para compra")
    ema_lenta_compra: int = Field(description="EMA lenta para compra")
    ema_rapida_venda: int = Field(description="EMA rápida para venda")
    ema_lenta_venda: int = Field(description="EMA lenta para venda")
    started_at: Optional[str]

class StartBotResponse(BaseModel):
    success: bool
    message: str
    bot_id: Optional[str]
    details: Optional[dict]
    ws_url: Optional[str] = None

# ============= WebSocket Schemas =============
class LogTypeEnum(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"
    LOG = "log"
    PRINT = "print"
    SYSTEM = "system"

class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogMessage(BaseModel):
    type: LogTypeEnum = Field(description="Tipo da mensagem de log")
    message: str = Field(description="Conteúdo da mensagem")
    timestamp: str = Field(description="Timestamp ISO 8601")
    bot_id: str = Field(description="ID do bot que gerou o log")
    level: Optional[LogLevelEnum] = Field(None, description="Nível do log (apenas para type='log')")
    config: Optional[dict] = Field(None, description="Configuração do bot (apenas para type='system' no start)")