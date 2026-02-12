import pandas as pd

def engolfo_alta(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df['fechamento'].shift(1) < df['abertura'].shift(1)) &
        (df['fechamento'] > df['abertura'].shift(1)) &
        (df['abertura'] <= df['fechamento'].shift(1))
    )

def engolfo_baixa(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df['fechamento'].shift(1) > df['abertura'].shift(1)) &
        (df['fechamento'] < df['abertura'].shift(1)) &
        (df['abertura'] >= df['fechamento'].shift(1))
    )

def piercing_line_alta(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df['fechamento'].shift(1) < df['abertura'].shift(1)) &
        (df['fechamento'] > (df['abertura'].shift(1) + df['fechamento'].shift(1)) / 2) &
        (df['abertura'] <= df['fechamento'].shift(1))
    )

def piercing_line_baixa(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df['fechamento'].shift(1) > df['abertura'].shift(1)) &
        (df['fechamento'] < (df['abertura'].shift(1) + df['fechamento'].shift(1)) / 2) &
        (df['abertura'] >= df['fechamento'].shift(1))
    )

def harami_alta(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df['fechamento'].shift(1) < df['abertura'].shift(1)) &
        (df['fechamento'] < (df['abertura'].shift(1) + df['fechamento'].shift(1)) / 2) &
        (df['fechamento'] > ((df['abertura'].shift(1) - df['fechamento'].shift(1) / 4) + df['fechamento'].shift(1))) &
        (df['abertura'] <= df['fechamento'].shift(1))
    )

def harami_baixa(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df['fechamento'].shift(1) > df['abertura'].shift(1)) &
        (df['fechamento'] > (df['abertura'].shift(1) + df['fechamento'].shift(1)) / 2) &
        (df['fechamento'] < ((df['fechamento'].shift(1) - df['abertura'].shift(1) / 4) - df['fechamento'].shift(1))) &
        (df['abertura'] >= df['fechamento'].shift(1))
    )

# Estrela da manha e da noite para os casos onde a vela seguinte possui fechamento contràrio à anterior e tamanho menor do que 1/4 do corpo da vela anterior 
def estrela_manha(df: pd.DataFrame) -> pd.DataFrame:
    pass

def estrela_noite(df: pd.DataFrame) -> pd.DataFrame:
    pass