import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import pandas as pd
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout
import numpy as np
import vectorbt as vbt
from vectorbt import nb

# ==========================================
# Versão completa com Numba (sem vetorização)
# Entrada na superação da máxima da vela referência, saída no preço de stop ou alvo
# ==========================================
@nb.njit
def double_ema_breakout_nb(close, high, low, ema1, ema2, q_stop, rr):
    entries = np.full(close.shape, np.nan)  # Inicializar com NaN para preços
    exits = np.full(close.shape, np.nan)    # Inicializar com NaN para preços
    stop_price = np.full(close.shape, np.nan)
    target_price = np.full(close.shape, np.nan)

    in_trade = False
    entry_price = 0.0
    stop_value = 0.0
    target_value = 0.0

    for i in range(999, len(close)):
        cond1 = close[i - 1] > ema1[i - 1]
        cond2 = close[i - 1] > ema2[i - 1]
        cond3 = high[i] > high[i - 1]

        if not in_trade and cond1 and cond2 and cond3:
            entry_price = high[i - 1]  # Preço de entrada
            min_stop = low[i - q_stop + 1:i + 1]
            if len(min_stop) == q_stop:
                stop_value = np.min(min_stop)
                target_value = entry_price + (entry_price - stop_value) * rr

                entries[i] = entry_price  # Registrar preço de entrada
                stop_price[i] = stop_value
                target_price[i] = target_value
                in_trade = True

        elif in_trade:
            current_low = low[i]
            current_high = high[i]

            stop_price[i] = stop_value
            target_price[i] = target_value

            if current_high >= target_value or current_low <= stop_value:
                exits[i] = target_value if current_high >= target_value else stop_value  # Registrar preço de saída
                in_trade = False

    return entries, exits, stop_price, target_price

# ===========================================================
# Versão procedural para utilização com Numba
# ===========================================================
def gerar_estrategia(df: pd.DataFrame, estrategia: DoubleEmaBreakout):
    close = df['fechamento'].values
    high = df['maxima'].values
    low = df['minima'].values

    # Extrair parâmetros
    p1 = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2 = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop = int(estrategia.stop.parametros['quantidade'])
    rr = float(estrategia.alvo.parametros['multiplicador'])

    # Indicadores
    ema1 = pd.Series(close).ewm(span=p1).mean().values
    ema2 = pd.Series(close).ewm(span=p2).mean().values

    # Chamar a função com Numba
    entries, exits, stop_price, target_price = double_ema_breakout_nb(
        close, high, low, ema1, ema2, q_stop, rr
    )

    index = df.index
    return (
        pd.Series(entries, index=index),
        pd.Series(exits, index=index),
        pd.Series(stop_price, index=index),
        pd.Series(target_price, index=index),
    )