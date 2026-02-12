from agno.agent import Agent

from .configs.agent_configs import AgentConfigs

AGENT_VERSION = "v2"
MODEL_TYPE = "sonnet-4-5" # sonnet-4-5, gemini-flash, gemini-pro

config = AgentConfigs.get_trade_conductor_config(AGENT_VERSION, MODEL_TYPE)

trade_conductor = Agent(
    name="Condutor de trades",
    model=config["model"],
    description="Agente especializado em gestão de trades abertos em cripto. Avalia se a operação deve ser mantida, ajustada ou encerrada com base no risco, alvo e contexto técnico do mercado.",
    instructions=config["instructions"],
    debug_mode=False,
)