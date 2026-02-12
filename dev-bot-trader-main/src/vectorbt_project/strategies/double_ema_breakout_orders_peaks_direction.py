# estratégia para decidir entre compra e venda com base no último pico, se é topo ou fundo
# se é fundo, comprar até aparecer um topo
# se é topo, vender até aparecer um fundo
# criar a coluna last_peak_type, 1 para fundo e -1 para topo (gera derivação com info de último pico do gráfico diário)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import pandas as pd
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout
import numpy as np
from vectorbt import nb

# ==========================================
# Versão completa com Numba (sem vetorização)
# Entrada no preço de máxima ou mínima da vela referência, saída no preço de stop ou alvo
# Combina estratégias long e short em uma única função
# ==========================================
@nb.njit
def double_ema_breakout_long_short_nb(close, high, low, ema1, ema2, q_stop, rr, last_peak_type):
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
    last_peak = 0         # 0 = sem pico, 1 = fundo, -1 = topo

    for i in range(999, len(close)):
        if last_peak_type[i-5] == 1:
            last_peak = 1
        elif last_peak_type[i-5] == -1:
            last_peak = -1

        # Condições para long
        long_cond1 = close[i - 1] > ema1[i - 1]
        long_cond2 = close[i - 1] > ema2[i - 1]
        long_cond3 = high[i] > high[i - 1]
        long_cond4 = last_peak == 1

        # Condições para short
        short_cond1 = close[i - 1] < ema1[i - 1]
        short_cond2 = close[i - 1] < ema2[i - 1]
        short_cond3 = low[i] < low[i - 1]
        short_cond4 = last_peak == -1

        if not in_trade:
            # Verificar entrada long
            if long_cond1 and long_cond2 and long_cond3 and long_cond4:
                entry_price = high[i - 1]
                min_stop = low[i - q_stop + 1:i + 1]
                if len(min_stop) == q_stop:
                    stop_value = np.min(min_stop)
                    target_value = entry_price + (entry_price - stop_value) * rr

                    entries[i] = entry_price
                    stop_price[i] = stop_value
                    target_price[i] = target_value
                    size[i] = 1.0  # Entrada long (compra)
                    in_trade = True
                    current_position = 1

            # Verificar entrada short
            elif short_cond1 and short_cond2 and short_cond3 and short_cond4:
                entry_price = low[i - 1]
                max_stop = high[i - q_stop + 1:i + 1]
                if len(max_stop) == q_stop:
                    stop_value = np.max(max_stop)
                    target_value = entry_price - (stop_value - entry_price) * rr

                    entries[i] = entry_price
                    stop_price[i] = stop_value
                    target_price[i] = target_value
                    size[i] = -1.0  # Entrada short (venda)
                    in_trade = True
                    current_position = -1

        elif in_trade:
            stop_price[i] = stop_value
            target_price[i] = target_value
            current_high = high[i]
            current_low = low[i]

            # Saída por topo/fundo
            if current_position == 1:  # Em posição long
                if current_high >= target_value or current_low <= stop_value:
                    exits[i] = target_value if current_high >= target_value else stop_value
                    size[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0
                
                elif last_peak_type[i-5] == -1:  # topo
                    exits[i] = close[i-1]
                    size[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0
            else:  # Em posição short
                if current_low <= target_value or current_high >= stop_value:
                    exits[i] = target_value if current_low <= target_value else stop_value
                    size[i] = 0.0  # Saída short (compra)
                    in_trade = False
                    current_position = 0

                elif last_peak_type[i-5] == 1:  # fundo
                    exits[i] = close[i-1]
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
    p1 = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2 = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop = int(estrategia.stop.parametros['quantidade'])
    rr = float(estrategia.alvo.parametros['multiplicador'])

    # Indicadores
    ema1 = pd.Series(close).ewm(span=p1).mean().values
    ema2 = pd.Series(close).ewm(span=p2).mean().values

    # last_peak_type deve estar no DataFrame
    last_peak_type = df['last_peak_type'].values

    # Chamar a função com Numba
    entries, exits, stop_price, target_price, size = double_ema_breakout_long_short_nb(
        close, high, low, ema1, ema2, q_stop, rr, last_peak_type
    )

    index = df.index
    return (
        pd.Series(entries, index=index),
        pd.Series(exits, index=index),
        pd.Series(stop_price, index=index),
        pd.Series(target_price, index=index),
        pd.Series(size, index=index)
    )