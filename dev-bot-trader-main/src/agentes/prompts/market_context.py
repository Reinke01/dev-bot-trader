from textwrap import dedent

def format_market_context(tempo_grafico, df, df_1w, df_1d, df_1h):
    """
    Formata o contexto técnico do mercado com dados de diferentes timeframes.
    
    Args:
        tempo_grafico (str): Timeframe do gráfico principal (ex: "5", "15", "60")
        df: DataFrame com dados do timeframe principal
        df_1w: DataFrame com dados semanais
        df_1d: DataFrame com dados diários
        df_1h: DataFrame com dados horários
    
    Returns:
        str: Contexto técnico formatado
    """
    return dedent(f"""# Contexto técnico (últimas velas e indicadores):
## Semanal:
{df_1w.drop(columns=['abertura', 'turnover']).tail(12).to_string(index=False)}

## Diário:
{df_1d.drop(columns=['abertura', 'turnover']).tail(30).to_string(index=False)}

## 60 minutos:
{df_1h.drop(columns=['abertura', 'turnover', 'top_high', 'top_close', 'bottom_low', 'bottom_close', 'peaks']).tail(15).to_string(index=False)}

### Últimos 10 topos:
{df_1h[['tempo_abertura', 'top_high']].dropna()[-11:-1].to_string(index=False)}

### Últimos 10 fundos:
{df_1h[['tempo_abertura', 'bottom_low']].dropna()[-11:-1].to_string(index=False)}

## {tempo_grafico} minutos:
{df.drop(columns=['abertura', 'turnover']).tail(30).to_string(index=False)}""")
