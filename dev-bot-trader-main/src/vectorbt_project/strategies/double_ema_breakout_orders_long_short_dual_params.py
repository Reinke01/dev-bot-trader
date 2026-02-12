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
# Entrada no preço de máxima ou mínima da vela referência, saída no preço de stop ou alvo
# Combina estratégias long e short em uma única função
# ==========================================
@nb.njit
def double_ema_breakout_long_short_nb(close, high, low, ema1_long, ema2_long, ema1_short, ema2_short, q_stop_long, q_stop_short, rr_long, rr_short):
    entries = np.full(close.shape, np.nan)
    exits = np.full(close.shape, np.nan)
    stop_price = np.full(close.shape, np.nan)
    target_price = np.full(close.shape, np.nan)
    size = np.full(close.shape, np.nan)

    in_trade = False
    entry_price = 0.0
    stop_value = 0.0
    target_value = 0.0
    current_position = 0  # 0 = sem posição, 1 = long, -1 = short

    for i in range(999, len(close)):
        # Condições para long
        long_cond1 = close[i - 1] > ema1_long[i - 1]
        long_cond2 = close[i - 1] > ema2_long[i - 1]
        long_cond3 = high[i] > high[i - 1]

        # Condições para short
        short_cond1 = close[i - 1] < ema1_short[i - 1]
        short_cond2 = close[i - 1] < ema2_short[i - 1]
        short_cond3 = low[i] < low[i - 1]

        if not in_trade:
            # Verificar entrada long
            if long_cond1 and long_cond2 and long_cond3:
                entry_price = high[i - 1]
                min_stop = low[i - q_stop_long + 1:i + 1]
                if len(min_stop) == q_stop_long:
                    stop_value = np.min(min_stop)
                    target_value = entry_price + (entry_price - stop_value) * rr_long

                    entries[i] = entry_price
                    stop_price[i] = stop_value
                    target_price[i] = target_value
                    size[i] = 1.0  # Entrada long (compra)
                    in_trade = True
                    current_position = 1

            # Verificar entrada short
            elif short_cond1 and short_cond2 and short_cond3:
                entry_price = low[i - 1]
                max_stop = high[i - q_stop_short + 1:i + 1]
                if len(max_stop) == q_stop_short:
                    stop_value = np.max(max_stop)
                    target_value = entry_price - (stop_value - entry_price) * rr_short

                    entries[i] = entry_price
                    stop_price[i] = stop_value
                    target_price[i] = target_value
                    size[i] = -1.0  # Entrada short (venda)
                    in_trade = True
                    current_position = -1

        elif in_trade:
            current_low = low[i]
            current_high = high[i]

            stop_price[i] = stop_value
            target_price[i] = target_value

            if current_position == 1:  # Em posição long
                if current_high >= target_value or current_low <= stop_value:
                    exits[i] = target_value if current_high >= target_value else stop_value
                    size[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0

            else:  # Em posição short
                if current_low <= target_value or current_high >= stop_value:
                    exits[i] = target_value if current_low <= target_value else stop_value
                    size[i] = 0.0  # Saída short (compra)
                    in_trade = False
                    current_position = 0

    return entries, exits, stop_price, target_price, size

# ===========================================================
# Versão procedural para utilização com Numba
# ===========================================================
def gerar_estrategia(df: pd.DataFrame, estrategia: DoubleEmaBreakout):
    close = df['fechamento'].values
    high = df['maxima'].values
    low = df['minima'].values

    # Extrair parâmetros
    p1_long = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2_long = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop_long = int(estrategia.stop.parametros['quantidade'][0])
    rr_long = float(estrategia.alvo.parametros['multiplicador'][0])

    p1_short = int(estrategia.condicoes_entrada[3].parametros['periodo'])
    p2_short = int(estrategia.condicoes_entrada[4].parametros['periodo'])
    q_stop_short = int(estrategia.stop.parametros['quantidade'][1])
    rr_short = float(estrategia.alvo.parametros['multiplicador'][1])

    # Indicadores
    ema1_long = pd.Series(close).ewm(span=p1_long).mean().values
    ema2_long = pd.Series(close).ewm(span=p2_long).mean().values
    ema1_short = pd.Series(close).ewm(span=p1_short).mean().values
    ema2_short = pd.Series(close).ewm(span=p2_short).mean().values

    # Chamar a função com Numba
    entries, exits, stop_price, target_price, size = double_ema_breakout_long_short_nb(
        close, high, low, ema1_long, ema2_long, ema1_short, ema2_short, q_stop_long, q_stop_short, rr_long, rr_short
    )

    index = df.index
    return (
        pd.Series(entries, index=index),
        pd.Series(exits, index=index),
        pd.Series(stop_price, index=index),
        pd.Series(target_price, index=index),
        pd.Series(size, index=index)
    ) 