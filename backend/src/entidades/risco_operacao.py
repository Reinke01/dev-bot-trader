from enum import Enum

class RiscoOperacao(Enum):
    MUITO_BAIXO = 0.005
    BAIXO = 0.01  
    MEDIO = 0.02
    ALTO = 0.05
    MUITO_ALTO = 0.08