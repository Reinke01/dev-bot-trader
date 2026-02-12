from agno.agent import Agent

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agentes.toolkits.bybit import BybitTools
from agentes.configs.agent_configs import AgentConfigs

AGENT_VERSION = "v2"
MODEL_TYPE = "sonnet-4-5" # sonnet-4-5, gemini-flash, gemini-pro

config = AgentConfigs.get_trade_entry_evaluator_config(AGENT_VERSION, MODEL_TYPE)

trade_entry_evaluator = Agent(
    name="Avaliador de entrada de trade",
    model=config["model"],
    description="Agente especializado em avaliar se um trade deve ser realizado com base no contexto técnico do mercado.",
    instructions=config["instructions"],
    # tools=[
    #     BybitTools(
    #         # buscar_contexto=True,
    #         abrir_compra=False,
    #         abrir_venda=False
    #     )
    # ],
    debug_mode=False,
)