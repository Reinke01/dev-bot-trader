import pandas as pd
import numpy as np

def bandas_bollinger(df: pd.DataFrame, periodo: int = 20, desvios: int = 2) -> pd.DataFrame:
    df['media_movel'] = df['fechamento'].rolling(window=periodo).mean()
    df['desvio_padrao'] = df['fechamento'].rolling(window=periodo).std()
    df['banda_superior'] = df['media_movel'] + desvios * df['desvio_padrao']
    df['banda_inferior'] = df['media_movel'] - desvios * df['desvio_padrao']
    return df

def sinal_fffd(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    fffd_long = (df['fechamento'] > df['banda_inferior']) & (df['fechamento'].shift(1) < df['banda_inferior'].shift(1))

    fffd_short = (df['fechamento'] < df['banda_superior']) & (df['fechamento'].shift(1) > df['banda_superior'].shift(1))

    df['fffd'] = 0
    df.loc[fffd_long, 'fffd'] = 1
    df.loc[fffd_short, 'fffd'] = -1

    return df, fffd_long, fffd_short