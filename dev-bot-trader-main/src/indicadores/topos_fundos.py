import pandas as pd
import numpy as np
from .padroes_velas import engolfo_alta, piercing_line_alta, harami_alta, engolfo_baixa, piercing_line_baixa, harami_baixa

# Confirmação na superação ou perda de máxima ou mínima do padrão de velas (entrada na superação ou perda de máxima ou mínima)
def topos_fundos_duas_velas(df: pd.DataFrame) -> pd.DataFrame:
    fundos = (
        engolfo_alta(df.shift(1)) |
        piercing_line_alta(df.shift(1)) |
        harami_alta(df.shift(1))
    ) & (
        df['maxima'] > df['maxima'].shift(1)
    )

    topos = (
        engolfo_baixa(df.shift(1)) |
        piercing_line_baixa(df.shift(1)) |
        harami_baixa(df.shift(1))
    ) & (
        df['minima'] < df['minima'].shift(1)
    )

    df['last_peak_type'] = 0
    df.loc[fundos, 'last_peak_type'] = 1 
    df.loc[topos, 'last_peak_type'] = -1
    
    return df, fundos, topos

# Confirmação no fechamento acima de máxima ou abaixo de mínima do padrão de velas (entrada na abertura da próxima vela)
def topos_fundos_tres_velas(df: pd.DataFrame) -> pd.DataFrame:
    fundos = (
        engolfo_alta(df.shift(1)) |
        piercing_line_alta(df.shift(1)) |
        harami_alta(df.shift(1))
    ) & (
        df['fechamento'] > df['maxima'].shift(1)
    )

    topos = (
        engolfo_baixa(df.shift(1)) |
        piercing_line_baixa(df.shift(1)) |
        harami_baixa(df.shift(1))
    ) & (
        df['fechamento'] < df['minima'].shift(1)
    )

    df['last_peak_type'] = 0
    df.loc[fundos, 'last_peak_type'] = 1 
    df.loc[topos, 'last_peak_type'] = -1
    
    return df, fundos, topos

# Confirmação no fechamento acima de máxima ou abaixo de mínima do padrão de velas (entrada na abertura da próxima vela)
def topos_fundos_quatro_velas(df: pd.DataFrame) -> pd.DataFrame:
    fundos = (
        engolfo_alta(df.shift(2)) |
        piercing_line_alta(df.shift(2)) |
        harami_alta(df.shift(2))
    ) & (
        (df['fechamento'].shift(1) > df['maxima'].shift(2)) &
        (df['maxima'] > df['maxima'].shift(1))
    )

    topos = (
        engolfo_baixa(df.shift(2)) |
        piercing_line_baixa(df.shift(2)) |
        harami_baixa(df.shift(2))
    ) & (
        (df['fechamento'].shift(1) < df['minima'].shift(2)) &
        (df['minima'] < df['minima'].shift(1))
    )

    df['last_peak_type'] = 0
    df.loc[fundos, 'last_peak_type'] = 1 
    df.loc[topos, 'last_peak_type'] = -1
    
    return df, fundos, topos

def topos_fundos_quatro_velas_v2(df: pd.DataFrame) -> pd.DataFrame:
    fundos = (
        df['fechamento'].shift(3) < df['abertura'].shift(3)
    ) & (
        engolfo_alta(df.shift(1)) |
        piercing_line_alta(df.shift(1)) |
        harami_alta(df.shift(1))
    ) & (
        (df['maxima'] > df['maxima'].shift(1))
    )

    topos = (
        df['fechamento'].shift(3) > df['abertura'].shift(3)
    ) & (
        engolfo_baixa(df.shift(1)) |
        piercing_line_baixa(df.shift(1)) |
        harami_baixa(df.shift(1))
    ) & (
        (df['minima'] < df['minima'].shift(1))
    )

    df['last_peak_type'] = 0
    df.loc[fundos, 'last_peak_type'] = 1 
    df.loc[topos, 'last_peak_type'] = -1
    
    return df, fundos, topos

def topos_fundos_cinco_velas(df: pd.DataFrame) -> pd.DataFrame:
    fundos = (
        df['fechamento'].shift(4) < df['abertura'].shift(4)
    ) & (
        engolfo_alta(df.shift(2)) |
        piercing_line_alta(df.shift(2)) |
        harami_alta(df.shift(2))
    ) & (
        (df['fechamento'].shift(1) > df['maxima'].shift(2)) &
        (df['maxima'] > df['maxima'].shift(1))
    )

    topos = (
        df['fechamento'].shift(4) > df['abertura'].shift(4)
    ) & (
        engolfo_baixa(df.shift(2)) |
        piercing_line_baixa(df.shift(2)) |
        harami_baixa(df.shift(2))
    ) & (
        (df['fechamento'].shift(1) < df['minima'].shift(2)) &
        (df['minima'] < df['minima'].shift(1))
    )

    df['last_peak_type'] = 0
    df.loc[fundos, 'last_peak_type'] = 1 
    df.loc[topos, 'last_peak_type'] = -1
    
    return df, fundos, topos

#recebe como parâmetro um list de dtype: bool e retorno em array dtype int64 com o índice da posição
def topos_fundos_toNDArray(fundos: list[bool], topos: list[bool]) -> tuple[np.ndarray, np.ndarray]:
    fundos = np.array(fundos, dtype=np.int64)   
    topos = np.array(topos, dtype=np.int64)

    fundos = np.where(fundos == 1)[0]
    topos = np.where(topos == 1)[0]
    return fundos, topos