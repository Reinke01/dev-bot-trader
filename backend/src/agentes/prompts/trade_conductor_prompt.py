from textwrap import dedent
from .market_context import format_market_context
from .trades_pnl import format_trades_pnl
from .sentiment_context import format_sentiment_context

def prompt_trade_conductor(
    subconta,
    tempo_grafico,
    cripto,
    estado_de_trade,
    preco_entrada,
    preco_alvo,
    preco_stop,
    tamanho_posicao,
    trailing_stop,
    df,
    df_1w,
    df_1d,
    df_1h,
    vela_abertura_trade,
):
    df = df.reset_index()
    df_1w = df_1w.reset_index()
    df_1d = df_1d.reset_index()
    df_1h = df_1h.reset_index()

    return dedent(f"""Trade em aberto detectado.

# Detalhes da operação:
- Subconta: {subconta}
- Tempo gráfico utilizado: {tempo_grafico}
- Símbolo: {cripto}
- Direção: {estado_de_trade}
- Preço de entrada: {preco_entrada}
- Alvo: {preco_alvo}
- Stop: {preco_stop}
- Tamanho da posição: {tamanho_posicao}
- Trailing stop ativado (em dólares): {trailing_stop}
- Preço atual: {df['fechamento'].iloc[-1]}
- Tempo de abertura: {vela_abertura_trade if vela_abertura_trade is not None else "Não tenho essa informação"}

{format_market_context(tempo_grafico, df, df_1w, df_1d, df_1h)}

{format_sentiment_context(cripto, tempo_grafico)}

{format_trades_pnl(subconta)}

Analise se o trade deve ser mantido, ajustado ou encerrado.
""")

def prompt_trade_conductor_leader(
    subconta,
    tempo_grafico,
    cripto,
    estado_de_trade,
    preco_entrada,
    preco_alvo,
    preco_stop,
    df,
    df_1w,
    df_1d,
    df_1h,
    vela_abertura_trade,
):
    df = df.reset_index()
    df_1w = df_1w.reset_index()
    df_1d = df_1d.reset_index()
    df_1h = df_1h.reset_index()

    return dedent(f"""Trade em aberto detectado.

# Detalhes da operação:
- Subconta: {subconta}
- Tempo gráfico utilizado: {tempo_grafico}
- Símbolo: {cripto}
- Direção: {estado_de_trade}
- Preço de entrada: {preco_entrada}
- Alvo: {preco_alvo}
- Stop: {preco_stop}
- Preço atual: {df['fechamento'].iloc[-1]}
- Tempo de abertura: {vela_abertura_trade if vela_abertura_trade is not None else "Não tenho essa informação"}

{format_market_context(tempo_grafico, df, df_1w, df_1d, df_1h)}

{format_sentiment_context(cripto, tempo_grafico)}

# Listas de máximas e minimas:
##MAXIMAS: {df.tail(10)['maxima'].to_list()}
##MINIMAS: {df.tail(10)['minima'].to_list()}

{format_trades_pnl(subconta)}

Analise se o trade deve ser mantido, ajustado ou encerrado.""")