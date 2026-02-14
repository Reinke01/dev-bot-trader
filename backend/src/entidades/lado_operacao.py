from enum import Enum

class LadoOperacao(Enum):
    APENAS_COMPRA = "compra"
    APENAS_VENDA = "venda"  
    AMBOS = "ambos"