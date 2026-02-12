import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import importlib
from typing import Any
from entidades.estrategias_descritivas.base import BaseEstrategiaDescritiva

def carregar_classe_descritiva_por_nome(nome: str) -> Any:
    try:
        modulo = importlib.import_module(f"entidades.estrategias_descritivas.{nome}")
        classe = getattr(modulo, nome_to_class(nome))
        if not issubclass(classe, BaseEstrategiaDescritiva):
            raise TypeError(f"{classe.__name__} não herda de BaseEstrategiaDescritiva")
        return classe
    except ModuleNotFoundError:
        raise ValueError(f"Arquivo '{nome}.py' não encontrado em estrategias_descritivas/")
    except AttributeError:
        raise ValueError(f"Classe '{nome_to_class(nome)}' não encontrada no módulo.")

def nome_to_class(nome: str) -> str:
    # Ex: 'double_ema_breakout' → 'DoubleEmaBreakout'
    return ''.join(word.capitalize() for word in nome.split('_'))
