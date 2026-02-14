from agno.agent import Agent
from agno.models.groq import Groq
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from corretoras.funcoes_bybit import busca_velas

# Create agent with Groq model and financial tools
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions=[
        "Você é um especialista em análise gráfica de criptomoedas. ",
        "Realize análises técnicas detalhadas, identifique padrões gráficos, ",
        "suportes, resistências e sugira possíveis trades com base nos dados apresentados. ",
        "Use tabelas e gráficos sempre que possível.",
        "Analisar tendencia atual do mercado. Se é de baixa, alta ou lateral.",
        "Quando sugerir trades, informe no formato de dicionario com as seguintes chaves:",
        "trade_long, trade_short, entry_price, stop_loss, take_profit"
    ],
    markdown=True
)

df_velas = busca_velas("SOLUSDT", "15", [5, 15])

response = agent.run(f"""
Analise o gráfico da criptomoeda Solana do seguinte periodo:
{df_velas}

mostre o valor atual e sugira possíveis trades. E explicar os motivos e indicadores tecnicos utilizados nos trades.
Me fale também sobre as condições de mercado para manter uma posição de vendas aberta ou realizar lucros.
""")

print(response.content)