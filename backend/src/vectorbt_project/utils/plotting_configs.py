"""
Configurações de plotagem para diferentes estratégias.

Este módulo centraliza as configurações visuais específicas para cada tipo de estratégia,
permitindo personalização consistente dos gráficos gerados.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class PlottingConfig:
    """Configuração de plotagem para uma estratégia específica."""
    title_prefix: str
    subtitle_template: str
    entry_color: str
    exit_color: str
    entry_symbol: str
    exit_symbol: str
    indicators: List[str]
    template: str = 'plotly_dark'
    show_volume: bool = True
    show_peaks: bool = False
    
    # Configurações específicas para diferentes tipos de entrada
    long_entry_color: str = "lime"
    long_entry_symbol: str = "triangle-up"
    short_entry_color: str = "red"
    short_entry_symbol: str = "triangle-down"
    exit_unified_color: str = "white"
    exit_unified_symbol: str = "x"


# Configurações padrão para cada tipo de estratégia
STRATEGY_PLOTTING_CONFIGS: Dict[str, PlottingConfig] = {
    "double_ema_breakout_signals": PlottingConfig(
        title_prefix="Estratégia Double EMA Breakout",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="lime",
        exit_color="red",
        entry_symbol="triangle-up",
        exit_symbol="triangle-down",
        indicators=["ema_curta", "ema_longa"]
    ),
    
    "double_ema_breakout_orders": PlottingConfig(
        title_prefix="Estratégia Double EMA Breakout",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="lime",
        exit_color="red",
        entry_symbol="triangle-up",
        exit_symbol="triangle-down",
        indicators=["ema_curta", "ema_longa"]
    ),
    
    "double_ema_breakout_orders_long_short": PlottingConfig(
        title_prefix="Estratégia Double EMA Breakout Long/Short",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="lime",
        exit_color="white",
        entry_symbol="triangle-up",
        exit_symbol="x",
        indicators=["ema_curta", "ema_longa"]
    ),
    
    "double_ema_breakout_orders_short": PlottingConfig(
        title_prefix="Estratégia Double EMA Breakout Short",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="red",
        exit_color="lime",
        entry_symbol="triangle-down",
        exit_symbol="triangle-up",
        indicators=["ema_curta", "ema_longa"]
    ),
    
    "double_ema_breakout_orders_long_short_peaks": PlottingConfig(
        title_prefix="Estratégia Double EMA Breakout Long Short Peaks",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="lime",
        exit_color="yellow",
        entry_symbol="triangle-up",
        exit_symbol="triangle-up",
        indicators=["ema_curta", "ema_longa"],
        show_peaks=True
    ),
    
    "double_ema_breakout_orders_long_short_dual_params": PlottingConfig(
        title_prefix="Estratégia Double EMA Breakout Long/Short Dual Params",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="lime",
        exit_color="white",
        entry_symbol="triangle-up",
        exit_symbol="x",
        indicators=["ema_curta_long", "ema_longa_long", "ema_curta_short", "ema_longa_short"]
    ),
    
    "bollinger_bands_long": PlottingConfig(
        title_prefix="Estratégia Bollinger Bands Long",
        subtitle_template="{simbolo} - {intervalo}min",
        entry_color="lime",
        exit_color="red",
        entry_symbol="triangle-up",
        exit_symbol="triangle-down",
        indicators=["banda_superior", "banda_inferior", "media_movel"]
    )
}


def get_plotting_config(strategy_name: str) -> PlottingConfig:
    """
    Retorna a configuração de plotagem para uma estratégia específica.
    
    Args:
        strategy_name: Nome da estratégia
        
    Returns:
        PlottingConfig: Configuração de plotagem da estratégia
        
    Raises:
        KeyError: Se a estratégia não estiver configurada
    """
    if strategy_name not in STRATEGY_PLOTTING_CONFIGS:
        # Usar configuração padrão para estratégias não configuradas
        return STRATEGY_PLOTTING_CONFIGS["double_ema_breakout_orders"]
    
    return STRATEGY_PLOTTING_CONFIGS[strategy_name]


def get_indicator_colors() -> Dict[str, str]:
    """Retorna cores padrão para indicadores comuns."""
    return {
        "ema_curta": "green",
        "ema_longa": "yellow",
        "ema_curta_long": "green",
        "ema_longa_long": "yellow", 
        "ema_curta_short": "orange",
        "ema_longa_short": "red",
        "banda_superior": "red",
        "banda_inferior": "green",
        "media_movel": "orange",
        "stop_loss": "orange",
        "take_profit": "green"
    }
