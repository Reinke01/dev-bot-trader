from agno.agent import Agent
from agno.models.groq import Groq
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Read Groq API key from environment to avoid hardcoding secrets in source code.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Configure it in your environment or create a local .env file from dev-bot-trader-main/.env.example"
    )

agent = Agent(
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
    ),
    instructions=[
        "Você é um especialista em análise gráfica de criptomoedas. ",
        "Realize análises técnicas detalhadas, identifique padrões gráficos, ",
        "suportes, resistências e sugira possíveis trades com base nos dados apresentados. ",
        "Use tabelas e gráficos sempre que possível.",
        "Analisar tendencia atual do mercado. Se é de baixa, alta ou lateral.",
        "Quando sugerir trades, informe no formato de dicionario com as seguintes chaves:",
        "trade_long, trade_short, entry_price, stop_loss, take_profit",
    ],
    markdown=True,
)

agent.print_response(f"""
Qual o preço do Bitcoin nesse momento?
""")