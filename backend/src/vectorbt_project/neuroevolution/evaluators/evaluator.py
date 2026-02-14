from vectorbt_project.generator_vectorbt import gerar_por_nome
from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()
import vectorbt as vbt
import pandas as pd
from ..individual import Individual

def evaluate_individual(ind: Individual, df: pd.DataFrame, estrategia_cls):
    estrategia = estrategia_cls.from_genome(ind.genome)
    entries, exits, *_ = gerar_por_nome("double_ema_breakout", df, estrategia)
    pf = vbt.Portfolio.from_signals(df['close'], entries, exits, direction='longonly')
    stats = pf.stats()
    ind.fitness = stats['Total Return [%]']  # ou outro critério
    ind.metadata = {
        'max_drawdown': stats['Max Drawdown [%]'],
        'trades': stats['Total Trades']
    }
    return ind