from agno.tools import Toolkit
from agno.agent import Agent
from agno.team import Team

class TeamSessionTools(Toolkit):
    def __init__(
        self,
        salvar_state: bool = False,
        limpar_state: bool = False,
        ler_state: bool = False,
        ler_state_team: bool = False,
        enable_all: bool = False,
        **kwargs
    ):
        tools = []
        if salvar_state or enable_all:
            tools.append(self.salvar_team_session_state)
        if limpar_state or enable_all:
            tools.append(self.limpar_team_session_state)
        if ler_state or enable_all:
            tools.append(self.ler_team_session_state)
        if ler_state_team or enable_all:
            tools.append(self.ler_team_session_state_team)

        super().__init__(name="team_session_tools", tools=tools, **kwargs)

    def salvar_team_session_state(
        self,
        agent: Agent,         # Agente que está salvando o estado
        suporte: float,       # Preço de suporte relevante próximo ao preço atual
        resistencia: float,   # Preço de resistência relevante próximo ao preço atual
    ) -> str:
        """Adiciona os preços de suporte e resistência para monitoramento pelo price_monitor"""
        agent.team_session_state["suporte"] = round(suporte * 0.99, 4)
        agent.team_session_state["resistencia"] = round(resistencia * 1.01, 4)
        return f"Suporte: {suporte}, Resistência: {resistencia}"

    def limpar_team_session_state(
        self,
        agent: Agent    # Agente que está limpando o estado
    ) -> str:
        """Limpa os preços de suporte e resistência do monitoramento"""
        agent.team_session_state["suporte"] = None
        agent.team_session_state["resistencia"] = None
        return f"Suporte e resistência removidos do monitoramento"

    def ler_team_session_state(
        self,
        agent: Agent    # Agente que está lendo o estado
    ) -> str:
        """Lê os preços de suporte e resistência do monitoramento"""
        suporte = agent.team_session_state["suporte"]
        resistencia = agent.team_session_state["resistencia"]
        
        if suporte is None or resistencia is None:
            return "Sem suporte e resistência registrados para monitoramento"
        
        return f"Suporte: {suporte}, Resistência: {resistencia}"

    def ler_team_session_state_team(
        self,
        team: Team      # Team que está lendo o estado
    ) -> str:
        """Lê os preços de suporte e resistência do monitoramento (versão para Team)"""
        suporte = team.team_session_state["suporte"]
        resistencia = team.team_session_state["resistencia"]
        
        if suporte is None or resistencia is None:
            return "Sem suporte e resistência registrados para monitoramento"
        
        return f"Suporte: {suporte}, Resistência: {resistencia}"
