from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

from dotenv import load_dotenv
load_dotenv()

def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Converte a temperatura de Celsius para Fahrenheit.
    Args:
        celsius: Temperatura em Celsius.
    Returns:
        Temperatura em Fahrenheit.
    """
    return (celsius * 9/5) + 32

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    tools=[
        DuckDuckGoTools(),
        celsius_to_fahrenheit
    ],
    debug_mode=False
)

agent.print_response("Use o DuckDuckGo para pesquisar notícias sobre a temperatura em Foz do Iguaçu")

