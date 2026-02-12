from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

from dotenv import load_dotenv
load_dotenv()

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    tools=[
        YFinanceTools()
    ],
    instructions="Apresente a resposta em tabelas.",
    debug_mode=False
)

response = agent.run("Qual é a cotação da Nvidia?")
print(response.content)

