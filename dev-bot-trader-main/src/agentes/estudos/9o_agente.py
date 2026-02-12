from agno.agent import Agent
# from agno.models.groq import Groq
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb

from agno.playground import Playground, serve_playground_app

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from corretoras.funcoes_bybit import busca_velas

db = SqliteStorage(table_name="agent_history", db_file="tmp/agent_history.db")

memory = Memory(
    # model=Groq(id="llama-3.3-70b-versatile"),
    model=Claude(id="claude-sonnet-4-20250514"),
    db=SqliteMemoryDb(table_name="agent_memory", db_file="tmp/agent_memory.db")
)

# Create agent with Groq model and financial tools
agent = Agent(
    name="Analista de criptomoedas",
    # model=Groq(id="llama-3.3-70b-versatile"),
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[
        DuckDuckGoTools(),
        YFinanceTools()
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
    debug_mode=True,
    storage=db,
    add_history_to_messages=True,
    num_history_runs=3,
    memory=memory,
    enable_agentic_memory=True
)

app = Playground(agents=[
    agent
]).get_app()

if __name__ == "__main__":
    serve_playground_app("9o_agente:app", reload=True)

# df_velas = busca_velas("SOLUSDT", "15", [5, 15])

# # Get BTC analysis across timeframes
# agent.print_response(f"""
# Analise o gráfico da criptomoeda Solana do seguinte periodo:
# {df_velas}

# mostre o valor atual e sugira possíveis trades. E explicar os motivos e indicadores tecnicos utilizados nos trades.
# Me fale também sobre as condições de mercado para manter uma posição de vendas aberta ou realizar lucros.
# Para avaliar as condições de mercado, confira o movimento pelo dataframe apresentado e busque informações sobre as velas diárias no Yahoo Finance.
# Faça uma busca na internet para avaliar o sentimento do mercado e as noticias mais recentes sobre a criptomoeda.
# """)