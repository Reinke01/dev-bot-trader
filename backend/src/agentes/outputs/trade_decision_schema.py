from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class TradeAction(BaseModel):
    acao: Literal[
        "manter", "fechar_compra", "fechar_venda", 
        "ajustar_stop", "ajustar_alvo", 
        "acionar_trailing_stop_imediato", "acionar_trailing_stop_preco"
    ]
    preco_stop: Optional[float] = None
    preco_alvo: Optional[float] = None
    preco_trailing: Optional[float] = None
    preco_acionamento: Optional[float] = None

class TradeDecisionOutput(BaseModel):
    acoes: List[TradeAction]
    confianca: float = Field(ge=0.0, le=1.0)
    justificativa: str