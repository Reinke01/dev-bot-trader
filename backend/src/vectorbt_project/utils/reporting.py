"""
Módulo de relatórios e exibição de resultados.

Este módulo centraliza as funções de geração de relatórios e exibição de resultados
para análises de estratégias de trading, eliminando duplicação de código.
"""

from typing import Dict, Any, List
import pandas as pd


def gerar_relatorio_detalhado(stats: pd.Series, estrategia_nome: str, parametros_dict: Dict[str, Any]) -> None:
    """
    Gera um relatório detalhado do desempenho da estratégia.
    
    Args:
        stats: Estatísticas do portfolio do VectorBT
        estrategia_nome: Nome da estratégia
        parametros_dict: Dicionário com os parâmetros da estratégia
    """
    print(f"\n📊 Relatório de Desempenho:")
    print(f"   - Estratégia: {estrategia_nome}")
    print(f"   - Parâmetros:")
    
    for key, value in parametros_dict.items():
        # Formatar chaves de forma mais legível
        key_formatted = key.replace("_", " ").title()
        print(f"     - {key_formatted}: {value}")
    
    print("-" * 50)
    print(stats)
    print("-" * 50)


def exibir_resultados_salvamento(caminhos_dict: Dict[str, str]) -> None:
    """
    Exibe informações sobre onde os resultados foram salvos.
    
    Args:
        caminhos_dict: Dicionário com os caminhos dos arquivos salvos
    """
    print("\n✅ Execução concluída!")
    print(f"\n📊 Resultados salvos em:")
    
    for tipo, caminho in caminhos_dict.items():
        tipo_formatado = tipo.upper()
        print(f"   - {tipo_formatado}: {caminho}")


def exibir_trades_resumo(pf, num_trades: int = 5) -> None:
    """
    Exibe um resumo dos trades do portfolio.
    
    Args:
        pf: Portfolio do VectorBT
        num_trades: Número de trades a exibir no início e fim
    """
    print(f"\n📈 Primeiros {num_trades} trades:")
    print(pf.trades.records_readable.head(num_trades))
    
    print(f"\n📈 Últimos {num_trades} trades:")
    print(pf.trades.records_readable.tail(num_trades))


def formatar_parametros_ema_simples(ema_curta: int, ema_longa: int, stop: int, rr: float) -> Dict[str, Any]:
    """
    Formata parâmetros para estratégias de EMA simples.
    
    Args:
        ema_curta: Período da EMA curta
        ema_longa: Período da EMA longa
        stop: Parâmetro de stop
        rr: Risk/Reward ratio
        
    Returns:
        Dict com parâmetros formatados
    """
    return {
        "ema_curta": ema_curta,
        "ema_longa": ema_longa,
        "stop": stop,
        "rr": rr
    }


def formatar_parametros_ema_dual(ema_curta_long: int, ema_longa_long: int, stop_long: int, rr_long: float,
                                ema_curta_short: int, ema_longa_short: int, stop_short: int, rr_short: float) -> Dict[str, Any]:
    """
    Formata parâmetros para estratégias de EMA com parâmetros duais (long/short).
    
    Args:
        ema_curta_long: EMA curta para operações long
        ema_longa_long: EMA longa para operações long
        stop_long: Stop para operações long
        rr_long: Risk/Reward para operações long
        ema_curta_short: EMA curta para operações short
        ema_longa_short: EMA longa para operações short
        stop_short: Stop para operações short
        rr_short: Risk/Reward para operações short
        
    Returns:
        Dict com parâmetros formatados
    """
    return {
        "ema_curta_long": ema_curta_long,
        "ema_longa_long": ema_longa_long,
        "stop_long": stop_long,
        "rr_long": rr_long,
        "ema_curta_short": ema_curta_short,
        "ema_longa_short": ema_longa_short,
        "stop_short": stop_short,
        "rr_short": rr_short
    }


def formatar_parametros_bollinger(periodo_bb: int, desvios_bb: int, stop: int) -> Dict[str, Any]:
    """
    Formata parâmetros para estratégias de Bollinger Bands.
    
    Args:
        periodo_bb: Período da média móvel das Bandas de Bollinger
        desvios_bb: Número de desvios padrão
        stop: Parâmetro de stop
        
    Returns:
        Dict com parâmetros formatados
    """
    return {
        "periodo_bb": periodo_bb,
        "desvios_bb": desvios_bb,
        "stop": stop
    }
