import pandas as pd
import pandas_ta as ta
from scipy.signal import find_peaks

def calcula_rsi(df: pd.DataFrame, periodo=14):
    return ta.rsi(df['fechamento'], length=periodo)

def encontra_topos_e_fundos(df: pd.DataFrame, dinstance: int=7, prominence: float=0.75) -> tuple:
    """Encontra topos e fundos em uma série temporal.

    Args:
        df (pd.DataFrame): DataFrame com os dados.
        column (str): Nome da coluna a ser analisada.
        dinstance (int): Distância mínima entre os picos.
        prominence (float): Proeminência mínima dos picos.

    Returns:
        tuple: Índices dos topos e fundos por máximas, maiores fechamentos, mínimas e menores fechamentos.
    """
    # Encontrar topos
    topos_maxima, _ = find_peaks(df['maxima'], distance=dinstance, prominence=prominence)
    # topos_maxima = pd.Series(np.where(df.index.isin(topos_maxima), 1, 0), index=df.index)
    topos_fechamento, _ = find_peaks(df['fechamento'], distance=dinstance, prominence=prominence)
    
    # Encontrar fundos
    fundos_minima, _ = find_peaks(-df['minima'], distance=dinstance, prominence=prominence)
    fundos_fechamento, _ = find_peaks(-df['fechamento'], distance=dinstance, prominence=prominence)
    
    return topos_maxima, topos_fechamento, fundos_minima, fundos_fechamento