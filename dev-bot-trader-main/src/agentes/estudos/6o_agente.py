from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from corretoras.funcoes_bybit import busca_velas

def busca_velas_bybit(simbolo, intervalo, emas):
    """
    Busca velas (candles) do mercado de criptomoedas na corretora Bybit.

    Parâmetros:
        simbolo (str): O símbolo do ativo (ex: 'BTCUSDT').
        intervalo (str): O intervalo de tempo das velas (ex: '15' para 15 minutos).
        emas (list): Lista de períodos (com duas posições) para cálculo das médias móveis exponenciais (EMAs).

    Retorna:
        DataFrame: Um DataFrame contendo os dados das velas e as EMAs calculadas.
    """
    return busca_velas(simbolo, intervalo, emas)

# Create agent with Groq model and financial tools
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        DuckDuckGoTools(),
        YFinanceTools(),
        busca_velas_bybit
    ],
    instructions=[
        "Você é um especialista em análise gráfica de criptomoedas. ",
        "Realize análises técnicas detalhadas, identifique padrões gráficos, ",
        "suportes, resistências e sugira possíveis trades com base nos dados apresentados. ",
        "Use tabelas e gráficos sempre que possível.",
        "Analisar tendencia atual do mercado. Se é de baixa, alta ou lateral.",
        "Quando sugerir trades, informe no formato de dicionario com as seguintes chaves:",
        "trade_long, trade_short, entry_price, stop_loss, take_profit"
    ],
    markdown=True,
    debug_mode=True
)

# Get BTC analysis across timeframes
agent.print_response(f"""
Busque as velas da SOLUSDT com intervalo de 15 minutos e EMAs de 9 e 21.
Em seguida, me informe o contexto do mercado para as velas.
""")