import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import pandas as pd
from entidades.estrategias_descritivas.base import BaseEstrategiaDescritiva
from indicadores.bandas_bollinger import bandas_bollinger, sinal_fffd
import numpy as np
from vectorbt import nb

# ==========================================
# Versão completa com Numba (sem vetorização)
# Entrada na superação da máxima da vela referência, saída no preço de stop ou alvo
# ==========================================
@nb.njit
def bollinger_bands_long_nb(close, high, low, fffd, q_stop, banda_superior):
    entries = np.full(close.shape, np.nan)  # Inicializar com NaN para preços
    exits = np.full(close.shape, np.nan)    # Inicializar com NaN para preços
    stop_price = np.full(close.shape, np.nan)
    target_price = np.full(close.shape, np.nan)

    in_trade = False
    entry_price = 0.0
    stop_value = 0.0
    target_value = 0.0

    for i in range(999, len(close)):
        cond1 = fffd[i - 1] == 1
        cond2 = high[i] > high[i - 1]

        if not in_trade and cond1 and cond2:
            entry_price = high[i - 1]  # Preço de entrada
            min_stop = low[i - q_stop + 1:i + 1]
            if len(min_stop) == q_stop:
                stop_value = np.min(min_stop)
                target_value = banda_superior[i]

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

            else:
                target_value = banda_superior[i]
                target_price[i] = target_value

    return entries, exits, stop_price, target_price

# ===========================================================
# Versão procedural para utilização com Numba
# ===========================================================
def gerar_estrategia(df: pd.DataFrame, estrategia: BaseEstrategiaDescritiva):
    close = df['fechamento'].values
    high = df['maxima'].values
    low = df['minima'].values

    periodo_bb = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    desvios_bb = int(estrategia.condicoes_entrada[1].parametros['desvios'])

    # Calcular Bandas de Bollinger
    df = bandas_bollinger(df, periodo_bb, desvios_bb)
    df, _, _ = sinal_fffd(df)

    fffd = df['fffd'].values
    banda_superior = df['banda_superior'].values

    # Extrair parâmetros (para bollinger bands: periodo e nro de desvios padrão)
    q_stop = int(estrategia.stop.parametros['quantidade'])

    # Chamar a função com Numba
    entries, exits, stop_price, target_price = bollinger_bands_long_nb(
        close, high, low, fffd, q_stop, banda_superior
    )

    index = df.index
    return (
        pd.Series(entries, index=index),
        pd.Series(exits, index=index),
        pd.Series(stop_price, index=index),
        pd.Series(target_price, index=index),
    )