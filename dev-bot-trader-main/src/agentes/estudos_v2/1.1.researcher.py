from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

from dotenv import load_dotenv
load_dotenv()

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    tools=[
        DuckDuckGoTools()
    ],
    debug_mode=False
)

agent.print_response("Use o DuckDuckGo para pesquisar notícias sobre a temperatura em Foz do Iguaçu")

