"""
Módulo de gerenciamento de resultados.

Este módulo centraliza a lógica de salvamento de resultados, criação de DataFrames
e gerenciamento de arquivos para análises de estratégias de trading.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional


def criar_diretorios_resultados() -> None:
    """Cria a estrutura de diretórios para salvar os resultados."""
    diretorios = [
        "data/results",
        "data/results/strategies",
        "data/results/strategies/csv",
        "data/results/strategies/json",
        "data/results/strategies/plots",
        "data/results/strategies/html"
    ]
    
    for diretorio in diretorios:
        os.makedirs(diretorio, exist_ok=True)


def gerar_nome_arquivo(nome_estrategia: str, simbolo: str, intervalo: str, 
                        data_inicio: str, data_fim: str, timestamp: str) -> str:
    """
    Gera nome padronizado para arquivos de resultado.
    
    Args:
        nome_estrategia: Nome da estratégia
        simbolo: Símbolo do ativo
        intervalo: Intervalo temporal
        data_inicio: Data de início
        data_fim: Data de fim
        timestamp: Timestamp atual
        
    Returns:
        Nome do arquivo formatado
    """
    # Limpar nome da estratégia para uso em arquivo
    nome_limpo = nome_estrategia.lower().replace(" ", "_").replace("/", "_")
    
    return f"{timestamp}_{nome_limpo}_{simbolo}_{intervalo}_{data_inicio}_{data_fim}"


def gerar_dataframe_resultado_basico(stats: pd.Series, parametros_dict: Dict[str, Any], 
                                    simbolo: str, intervalo: str, periodo: str,
                                    saldo_inicial: float = 1000) -> pd.DataFrame:
    """
    Gera DataFrame com métricas básicas de resultado.
    
    Args:
        stats: Estatísticas do portfolio do VectorBT
        parametros_dict: Parâmetros da estratégia
        simbolo: Símbolo do ativo
        intervalo: Intervalo temporal
        periodo: Período de análise
        saldo_inicial: Saldo inicial do backtest
        
    Returns:
        DataFrame com os resultados
    """
    resultado_base = {
        "moeda": simbolo,
        "intervalo": intervalo,
        "periodo": periodo,
        "saldo_inicial": saldo_inicial,
        "saldo_final": stats['End Value'],
        "retorno_total": stats['Total Return [%]'],
        "max_drawdown": stats['Max Drawdown [%]'],
        "max_drawdown_duration": stats['Max Drawdown Duration'],
        "trades": stats['Total Trades'],
        "win_rate": stats['Win Rate [%]'],
        "ganho_medio": stats['Avg Winning Trade [%]'],
        "perda_media": stats['Avg Losing Trade [%]'],
        "melhor_trade": stats['Best Trade [%]'],
        "pior_trade": stats['Worst Trade [%]'],
        "sharpe_ratio": stats['Sharpe Ratio'],
        "sortino_ratio": stats['Sortino Ratio'],
        "calmar_ratio": stats['Calmar Ratio'],
    }
    
    # Adicionar parâmetros da estratégia
    resultado_base.update(parametros_dict)
    
    return pd.DataFrame([resultado_base])


def salvar_resultados_completos(df_resultado: pd.DataFrame, nome_estrategia: str, 
                                simbolo: str, intervalo: str, data_inicio: str, 
                                data_fim: str) -> Dict[str, str]:
    """
    Salva os resultados em CSV e JSON.
    
    Args:
        df_resultado: DataFrame com os resultados
        nome_estrategia: Nome da estratégia
        simbolo: Símbolo do ativo
        intervalo: Intervalo temporal
        data_inicio: Data de início
        data_fim: Data de fim
        
    Returns:
        Dict com os caminhos dos arquivos salvos
    """
    criar_diretorios_resultados()
    
    # Gerar timestamp e nome do arquivo
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = gerar_nome_arquivo(nome_estrategia, simbolo, intervalo, data_inicio, data_fim, now)
    
    # Definir caminhos
    caminho_csv = f"data/results/strategies/csv/{nome_arquivo}.csv"
    caminho_json = f"data/results/strategies/json/{nome_arquivo}.json"
    
    # Salvar arquivos
    df_resultado.to_csv(caminho_csv, index=False)
    df_resultado.to_json(caminho_json, orient="records", indent=4)
    
    return {
        "csv": caminho_csv,
        "json": caminho_json
    }


def salvar_graficos_html(fig_plotly, fig_perf, nome_estrategia: str, simbolo: str, 
                        intervalo: str, data_inicio: str, data_fim: str) -> Dict[str, str]:
    """
    Salva gráficos em HTML.
    
    Args:
        fig_plotly: Figura principal do Plotly
        fig_perf: Figura de performance do Plotly
        nome_estrategia: Nome da estratégia
        simbolo: Símbolo do ativo
        intervalo: Intervalo temporal
        data_inicio: Data de início
        data_fim: Data de fim
        
    Returns:
        Dict com os caminhos dos arquivos HTML salvos
    """
    criar_diretorios_resultados()
    
    # Gerar timestamp e nome do arquivo
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = gerar_nome_arquivo(nome_estrategia, simbolo, intervalo, data_inicio, data_fim, now)
    
    # Definir caminhos
    caminho_html = f"data/results/strategies/html/{nome_arquivo}.html"
    caminho_html_pf = f"data/results/strategies/html/{nome_arquivo}_performance.html"
    
    # Salvar gráficos
    fig_plotly.write_html(caminho_html)
    if fig_perf is not None:
        fig_perf.write_html(caminho_html_pf)
    
    return {
        "grafico_velas": caminho_html,
        "grafico_performance": caminho_html_pf if fig_perf is not None else None
    }


def processar_periodo_dataframe(df: pd.DataFrame, data_inicio: str) -> str:
    """
    Gera string de período formatada a partir do DataFrame.
    
    Args:
        df: DataFrame com dados históricos
        data_inicio: Data de início
        
    Returns:
        String formatada do período
    """
    return f"{data_inicio} : {df.index[-1]}"
