from textwrap import dedent
from .market_context import format_market_context
from .trades_pnl import format_trades_pnl
from .sentiment_context import format_sentiment_context
from datetime import datetime

def prompt_trade_entry_evaluator(
    saldo,
    tempo_grafico,
    ema_rapida_compra,
    ema_lenta_compra,
    cripto,
    qtd_min_para_operar,
    subconta,
    lado,
    df, 
    df_1w,
    df_1d,
    df_1h,
):
    df = df.reset_index()
    df_1w = df_1w.reset_index()
    df_1d = df_1d.reset_index()
    df_1h = df_1h.reset_index()

    # Define os detalhes específicos baseados no lado da operação
    if lado.lower() == "compra":
        direcao = "Compra"
        detalhes = f"Vela anterior fechou acima das emas e a atual superou a máxima da anterior, no tempo gráfico {tempo_grafico}."
    else:  # venda
        direcao = "Venda"
        detalhes = f"Vela anterior fechou abaixo das emas e a atual perdeu a mínima da anterior, no tempo gráfico {tempo_grafico}."
    
    return dedent(f"""
Sinal de entrada identificado.

# Valor da minha carteira: {saldo} USDT

# Detalhes do sinal:
- Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Tempo gráfico: {tempo_grafico}
- EMA curta: {ema_rapida_compra}
- EMA longa: {ema_lenta_compra}
- Símbolo: {cripto}
- Casas decimais (qty_step): {qtd_min_para_operar}
- Direção: {direcao}
- Subconta: {subconta}
- Detalhes: {detalhes}

{format_market_context(tempo_grafico, df, df_1w, df_1d, df_1h)}

{format_sentiment_context(cripto, tempo_grafico)}

{format_trades_pnl(subconta)}
""")