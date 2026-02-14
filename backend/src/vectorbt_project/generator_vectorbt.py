import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import importlib
import pandas as pd
from entidades.estrategias_descritivas.base import BaseEstrategiaDescritiva

def gerar_por_nome(nome: str, df: pd.DataFrame, estrategia: BaseEstrategiaDescritiva):
    """
    Carrega dinamicamente a estratégia com base no nome e executa gerar_estrategia(df, estrategia).
    O nome deve corresponder ao nome do arquivo .py em strategies/ (sem .py)
    """
    try:
        modulo = importlib.import_module(f'vectorbt_project.strategies.{nome}')
        return modulo.gerar_estrategia(df, estrategia)
    except ModuleNotFoundError:
        raise ValueError(f"Estratégia '{nome}' não encontrada em vectorbt_project.strategies/")
    except AttributeError:
        raise ValueError(f"Arquivo '{nome}.py' encontrado, mas não possui a função gerar_estrategia.")