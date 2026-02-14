from agno.agent import Agent
from agno.models.groq import Groq
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

agent = Agent(
    model=Groq(
        id="llama-3.3-70b-versatile",  # Using Groq's free model
        api_key=os.getenv("GROQ_API_KEY")
    ),
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

agent.print_response(f"""
Qual o preço do Bitcoin nesse momento?
""")