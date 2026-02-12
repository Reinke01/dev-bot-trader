import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import pandas as pd
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout
import numpy as np
import vectorbt as vbt
from vectorbt import nb

# ==========================================
# Versão completa com Numba (sem vetorização), entrada e saída após fechamento da vela que ativou o sinal
# ==========================================
@nb.njit
def double_ema_breakout_nb(close, high, low, ema1, ema2, q_stop, rr):
    entries = np.full(close.shape, False)
    exits = np.full(close.shape, False)
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
            entry_price = high[i - 1]
            min_stop = low[i - q_stop + 1:i + 1]
            if len(min_stop) == q_stop:
                stop_value = np.min(min_stop)
                target_value = entry_price + (entry_price - stop_value) * rr

                entries[i] = True
                stop_price[i] = stop_value
                target_price[i] = target_value
                in_trade = True

        elif in_trade:
            current_low = low[i]
            current_high = high[i]

            stop_price[i] = stop_value
            target_price[i] = target_value

            if current_high >= target_value or current_low <= stop_value:
                exits[i] = True
                in_trade = False

    return entries, exits, stop_price, target_price

# ===========================================================
# Versão procedural completa, para utilização com Numba, entrada e saída após fechamento da vela que ativou o sinal
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

# ===========================================================
# Versão procedural completa, para referência (não otimizada)
# ===========================================================
def gerar_estrategia_procedural(df: pd.DataFrame, estrategia: DoubleEmaBreakout):
    close = df['fechamento']
    high = df['maxima']

    # Extrair parâmetros
    p1 = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2 = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop = int(estrategia.stop.parametros['quantidade'])
    rr = float(estrategia.alvo.parametros['multiplicador'])

    # Indicadores
    ema1 = close.ewm(span=p1).mean()
    ema2 = close.ewm(span=p2).mean()

    cond1 = close.shift(1) > ema1.shift(1)
    cond2 = close.shift(1) > ema2.shift(1)
    cond3 = high > high.shift(1)

    entries_signal = cond1 & cond2 & cond3

    # Inicializar vetores de saída
    entries = pd.Series(False, index=df.index)
    exits = pd.Series(False, index=df.index)
    stop_price = pd.Series(index=df.index, dtype='float64')
    target_price = pd.Series(index=df.index, dtype='float64')

    in_trade = False
    entry_price = None
    stop_value = None
    target_value = None

    for i in range(999, len(df)):
        if not in_trade and entries_signal.iloc[i]:
            entry_price = df['maxima'].iloc[i-1]
            stop_value = df['minima'].iloc[i - q_stop + 1:i + 1].min()
            target_value = entry_price + (entry_price - stop_value) * rr

            entries.iloc[i] = True
            stop_price.iloc[i] = stop_value
            target_price.iloc[i] = target_value
            in_trade = True

        elif in_trade:
            current_low = df['minima'].iloc[i]
            current_high = df['maxima'].iloc[i]

            stop_price.iloc[i] = stop_value
            target_price.iloc[i] = target_value

            if current_high >= target_value or current_low <= stop_value:
                exits.iloc[i] = True
                in_trade = False                

    return entries, exits, stop_price, target_price

# ==========================================
# Versão vetorizada completa para avaliação (está incorreta por enquanto)
# ==========================================
def gerar_estrategia_vetorizada(df: pd.DataFrame, estrategia: DoubleEmaBreakout):
    close = df['fechamento']
    high = df['maxima']
    low = df['minima']

    # Parâmetros da estratégia
    p1 = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2 = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop = int(estrategia.stop.parametros['quantidade'])
    rr = float(estrategia.alvo.parametros['multiplicador'])

    # Indicadores
    ema1 = close.ewm(span=p1).mean()
    ema2 = close.ewm(span=p2).mean()

    # Sinal de entrada (vela anterior fecha acima das EMAs e máxima atual > máxima anterior)
    cond1 = close.vbt.crossed_above(ema1)
    cond2 = close.vbt.crossed_above(ema2)
    cond3 = high > high.shift(1)
    entries_signal = cond1 & cond2 & cond3

    # Preço de entrada: máxima da vela anterior
    entry_price = high.shift(1)

    # Stop dinâmico: mínima das últimas N velas
    stop_price = low.rolling(window=q_stop).min()

    # Alvo baseado em RR
    target_price = entry_price + (entry_price - stop_price) * rr

    # Condições de saída
    stop_hit = low <= stop_price
    target_hit = high >= target_price
    exits = stop_hit | target_hit

    # Filtrar múltiplas entradas simultâneas
    # Comportamento da estratégia está diferente da procedural
    entries_cumsum = entries_signal.cumsum()
    exits_cumsum = exits.cumsum().shift(1).fillna(0)
    entries_final = exits_cumsum < entries_cumsum

    # Aplica o filtro final às entradas
    entries = entries_signal & entries_final

    return entries, exits, stop_price, target_price