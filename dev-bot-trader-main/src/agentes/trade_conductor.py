"""
Agente Condutor de Trades

Este módulo implementa um agente especializado em gestão de trades abertos
no mercado de criptomoedas. O agente avalia continuamente posições ativas
para determinar se devem ser mantidas, ajustadas ou encerradas.

Funcionalidades principais:
- Análise técnica multi-timeframe (semanal, diário, intraday)
- Gestão de risco baseada em contexto técnico
- Avaliação de stop loss e take profit
- Proteção de lucros com ajuste de stop, alvo e acionamento de trailing stop

O agente utiliza análise clássica de movimento de preços combinada
com indicadores técnicos para tomada de decisões de gestão de trades.
"""

from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
from agno.models.groq import Groq
from agno.playground import Playground, serve_playground_app

from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb

from textwrap import dedent

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agentes.toolkits.bybit import BybitTools
from agentes.toolkits.team_session import TeamSessionTools
from agentes.configs.agent_configs import AgentConfigs

AGENT_VERSION = "v1"
MODEL_TYPE = "sonnet"

config = AgentConfigs.get_trade_conductor_config(AGENT_VERSION, MODEL_TYPE)

db = SqliteStorage(table_name="agent_history", db_file="tmp/agent_history.db")

# memory = Memory(
#     model=Claude(id="claude-sonnet-4-20250514"),
#     db=SqliteMemoryDb(table_name="agent_memory", db_file="tmp/agent_memory.db")
# )

trade_conductor = Agent(
    name="Condutor de trades",
    model=config["model"],
    tools=[
        BybitTools(
            buscar_contexto=False,
            fechar_compra=False,
            fechar_venda=False,
            ajustar_stop=False,
            ajustar_alvo=False,
            trailing_imediato=False,
            trailing_preco=False,
            enable_all=False,
        ),
        TeamSessionTools(
            salvar_state=False,
            limpar_state=False,
            ler_state=False,
            ler_state_team=False,
            enable_all=False,
        ),
    ],
    description="Agente especializado em gestão de trades abertos em cripto. Avalia se a operação deve ser mantida, ajustada ou encerrada com base no risco, alvo e contexto técnico do mercado.",
    instructions=config["instructions"],
    debug_mode=True,
    show_tool_calls=True,
    storage=db,
    add_history_to_messages=False,
    # num_history_runs=0,
    # memory=memory,
    # enable_agentic_memory=True,
)

# TODO:
# tools: executar_análise_completa, obter_delta, armazenar_delta
# objetivo: descobrir informações relevantes para armazenar em campo 'delta' no team_session_state
#   - na instrução do agente, avaliar se existe o delta gerado pela análise completa (com ampla quantidade de dados)
#   - se não existir ou estiver expirado, executar análise completa para gerar o delta
#   - se existir e não estiver expirado, executar a análise com dados resumidos (menos velas) e delta

# ALTERNATIVAS PARA O CÓDIGO ABAIXO:
# 1. Criar uma agente monitor de preços com formato específico de resposta e fazer o parse do resultado para saber quando resetar o tempo de execução do trade_conductor no live_trading
#   - Vantagem: posso usar outras variáveis para resetar o tempo de execução do trade_conductor, como quando o volume estiver x% acima da média, quando confirmar engolfo, etc
price_monitor = Agent(
    name="Monitor de preço",
    model=Claude(id="claude-3-5-haiku-20241022"),
    # model=Claude(id="claude-3-haiku-20240307"),
    # model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        TeamSessionTools(
            ler_state=True,
            limpar_state=True,
            enable_all=False,
        ),
    ],
    description="Agente especializado em monitorar a lista de máximas e de mínimas em relação ao suporte e resistência, registrados pelo trade_conductor no team_session_state.",
    instructions=dedent("""
        Você é um agente especializado em monitorar a lista de máximas e de mínimas em relação a resistência e suporte.
        
        ENTRADA: Listas ##MAXIMAS e ##MINIMAS no formato:
        ##MAXIMAS: [valor1, valor2, valor3, ...]
        ##MINIMAS: [valor1, valor2, valor3, ...]
        
        PROCESSO:
        1. Execute a tool ler_team_session_state para obter os preços de suporte e resistência
        2. Extraia os valores das listas ##MAXIMAS e ##MINIMAS do texto
        3. Compare cada valor das máximas com a resistência e cada valor das mínimas com o suporte
        
        REGRAS:
        - Se algum valor em ##MAXIMAS > resistência → {"status": "acima_resistencia", "acao": "limpar_team_session_state"} e execute limpar_team_session_state
        - Se algum valor em ##MINIMAS < suporte → {"status": "abaixo_suporte", "acao": "limpar_team_session_state"} e execute limpar_team_session_state
        - Se todas as máximas e mínimas estiverem entre suporte e resistência → {"status": "entre_niveis", "acao": "nenhuma"} e não execute limpar_team_session_state    

        SAÍDA: JSON no formato:
        {
            "status": "acima_resistencia" | "abaixo_suporte" | "entre_niveis",
            "acao": "limpar_team_session_state" | "nenhuma",
            "suporte": number|null,
            "resistencia": number|null,
            "maximas": number[]|null,
            "minimas": number[]|null
        }

        Sua resposta deve conter APENAS o JSON, sem texto adicional.
    """),
    debug_mode=True,
)

# Sugestão de instrução para o price_monitor:
# Você é um verificador binário de preço vs níveis.

# ENTRADA: JSON no formato:
# {
#   "preco_atual": number|null,
#   "levels": {"suporte": number|null, "resistencia": number|null},
#   "maximas": number[]|null,
#   "minimas": number[]|null
# }

# REGRAS:
# 1) Se qualquer campo essencial faltar ou for null OU listas forem vazias → responda apenas "sem_niveis".
# 2) Se existe algum x em maximas tal que x > levels.resistencia → (antes de responder) chame a tool limpar_team_session_state e responda apenas "acima".
# 3) Se existe algum y em minimas tal que y < levels.suporte → (antes de responder) chame a tool limpar_team_session_state e responda apenas "abaixo".
# 4) Caso contrário → responda apenas "entre".

# SAÍDA: UMA palavra: "acima" | "abaixo" | "entre" | "sem_niveis".
# NUNCA devolva texto extra além de uma dessas palavras.
    
trade_conductor_leader = Team(
    name="Roteador de agentes",
    mode="route",
    # model=Claude(id="claude-3-5-haiku-20241022"),
    model=Claude(id="claude-3-haiku-20240307"),
    # model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        TeamSessionTools(
            ler_state_team=True,
            enable_all=False,
        ),
    ],
    members=[trade_conductor, price_monitor],
    team_session_state={"suporte": None, "resistencia": None, "policy": {"id": "GESTAO_V1_LITE", "checksum": "a1b2c3"}},
    description="Agente especializado em rotear o trade_conductor ou o price_monitor com o resultado da tool ler_team_session_state_team.",
    instructions=dedent("""
Você é um roteador de agentes que direciona quando executar o trade_conductor ou o price_monitor com o resultado da tool ler_team_session_state_team.
Você não processa a requisição do usuário, você apenas repassa a requisição para o trade_conductor ou para o price_monitor.

Execute a tool ler_team_session_state_team para obter os preços de suporte e resistência.
- Se o team_session_state não tiver suporte e resistência, acione o trade_conductor com as seguintes instruções:
    1) Retorne 'Sem suporte e resistência registradas para monitorar, acionando o condutor de trades\n'.
    2) Repasse o conteúdo completo da requisição para o trade_conductor, com exceção de ##MAXIMAS e ##MINIMAS.
- Se o team_session_state tiver suporte e resistência, acione o price_monitor com as seguintes instruções:
    1) Retorne 'Suporte e resistência identificadas para monitorar, acionando o monitor de preço\n'.
    2) Repasse apenas ##MAXIMAS e ##MINIMAS para o price_monitor.
    3) Observe a resposta do price_monitor para determinar se deve acionar o trade_conductor:
    4) Se o price_monitor retornar "acima" ou "abaixo", acione o trade_conductor.
    5) Se o price_monitor retornar "entre", não acione o trade_conductor.
    """),
    debug_mode=True,
    show_members_responses=True,
    show_tool_calls=True,
)

# Sugestão de instrução para o trade_conductor:
# Você é um roteador. Passos:
# 1) Leia suporte/resistência do team_session_state (tool). 
# 2) Se não houver níveis → chame o trade_conductor com um handoff JSON mínimo (event: "no_levels").
# 3) Se houver níveis → extraia do conteúdo do usuário apenas o bloco JSON de {preco_atual, maximas, minimas} ou construa um JSON equivalente.
# 4) Envie ao price_monitor APENAS o JSON {preco_atual, levels{suporte,resistencia}, maximas, minimas}. 
# 5) Se o price_monitor responder "acima" ou "abaixo" → chame o trade_conductor com handoff JSON:
#    {policy_id, event: "breakout_above"|"breakout_below", price, levels, deltas? }.
# 6) Se responder "entre" → encerre.
# 7) Se "sem_niveis" → chame o trade_conductor com handoff {event:"no_levels"}.
# Não encaminhe o conteúdo completo do usuário para os agentes.

app = Playground(agents=[
    trade_conductor
]).get_app()

if __name__ == "__main__":
    serve_playground_app("trade_conductor:app", reload=True)