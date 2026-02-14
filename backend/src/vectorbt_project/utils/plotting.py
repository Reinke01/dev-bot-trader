"""
Módulo de plotagem e visualização.

Este módulo centraliza as funções de plotagem para estratégias de trading,
eliminando duplicação de código e permitindo visualizações consistentes.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Dict, Any, Tuple
from .plotting_configs import PlottingConfig, get_plotting_config, get_indicator_colors


def plotar_grafico_velas_plotly(df: pd.DataFrame, entries: pd.Series, exits: pd.Series, 
                                stop_price: pd.Series, target_price: pd.Series,
                                strategy_name: str, simbolo: str, intervalo: str,
                                size: Optional[pd.Series] = None,
                                ema_curta: Optional[int] = None,
                                ema_longa: Optional[int] = None,
                                ema_curta_long: Optional[int] = None,
                                ema_longa_long: Optional[int] = None,
                                ema_curta_short: Optional[int] = None,
                                ema_longa_short: Optional[int] = None) -> go.Figure:
    """
    Cria um gráfico interativo com velas e indicadores usando Plotly.
    
    Args:
        df: DataFrame com dados OHLCV
        entries: Série com sinais de entrada
        exits: Série com sinais de saída
        stop_price: Série com preços de stop loss
        target_price: Série com preços de take profit
        strategy_name: Nome da estratégia
        simbolo: Símbolo do ativo
        intervalo: Intervalo temporal
        size: Série com tamanhos das operações (para long/short)
        ema_curta: Período da EMA curta (opcional)
        ema_longa: Período da EMA longa (opcional)
        ema_curta_long: Período da EMA curta para operações long (dual params)
        ema_longa_long: Período da EMA longa para operações long (dual params)
        ema_curta_short: Período da EMA curta para operações short (dual params)
        ema_longa_short: Período da EMA longa para operações short (dual params)
        
    Returns:
        Figura do Plotly
    """
    config = get_plotting_config(strategy_name)
    indicator_colors = get_indicator_colors()
    
    # Criar título
    title_main = f"{config.title_prefix} ({simbolo} - {intervalo}min)"
    
    # Criar subplots
    fig = make_subplots(
        rows=2, 
        cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        subplot_titles=(title_main, 'Volume'),
        row_heights=[0.8, 0.2]
    )
    
    # Adicionar velas
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['abertura'],
            high=df['maxima'],
            low=df['minima'],
            close=df['fechamento'],
            name='Velas',
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
    
    # Adicionar indicadores técnicos
    _adicionar_indicadores_tecnicos(fig, df, config.indicators, indicator_colors, 
                                    ema_curta, ema_longa, ema_curta_long, ema_longa_long, 
                                    ema_curta_short, ema_longa_short)
    
    # Adicionar sinais de entrada e saída
    _adicionar_sinais_entrada_saida(fig, entries, exits, df, config, size)
    
    # Adicionar stop loss e take profit
    _adicionar_stop_take_profit(fig, df, stop_price, target_price, indicator_colors)
    
    # Adicionar peaks se configurado
    if config.show_peaks and 'last_peak_type' in df.columns:
        _adicionar_peaks(fig, df)
    
    # Adicionar volume
    _adicionar_volume(fig, df)
    
    # Configurar layout
    _configurar_layout(fig, config, simbolo, intervalo)
    
    return fig


def plotar_performance_plotly(pf, entries: pd.Series = None, exits: pd.Series = None, 
                            strategy_name: str = "") -> go.Figure:
    """
    Cria um gráfico interativo da performance do portfólio usando Plotly.
    
    Args:
        pf: Portfolio do VectorBT
        entries: Série com sinais de entrada
        exits: Série com sinais de saída
        strategy_name: Nome da estratégia
        
    Returns:
        Figura do Plotly
    """
    config = get_plotting_config(strategy_name)
    
    # Calcular equity e drawdown
    equity = pf.value()
    drawdown = (equity / equity.cummax() - 1) * 100
    
    # Criar figura com subplots
    fig = make_subplots(
        rows=2, 
        cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        subplot_titles=('Equity', 'Drawdown (%)'),
        row_heights=[0.7, 0.3]
    )
    
    # Adicionar equity
    fig.add_trace(
        go.Scatter(
            x=equity.index,
            y=equity,
            name='Equity',
            line=dict(color='green', width=2)
        ),
        row=1, col=1
    )
    
    # Marcar trades reais na equity usando dados do portfolio
    _marcar_trades_equity_do_portfolio(fig, pf, equity)
    
    # Adicionar drawdown
    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown,
            name='Drawdown',
            fill='tozeroy',
            line=dict(color='red', width=1)
        ),
        row=2, col=1
    )
    
    # Configurar layout
    fig.update_layout(
        title='Performance da Estratégia',
        height=600,
        width=1200,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template=config.template
    )
    
    # Atualizar eixos Y
    fig.update_yaxes(title_text="Valor ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    
    return fig


def plotar_resultados_matplotlib(pf, df: pd.DataFrame, entries: pd.Series, exits: pd.Series,
                                stop_price: pd.Series, target_price: pd.Series,
                                strategy_name: str) -> plt.Figure:
    """
    Gera visualizações detalhadas dos resultados usando Matplotlib.
    
    Args:
        pf: Portfolio do VectorBT
        df: DataFrame com dados OHLCV
        entries: Série com sinais de entrada
        exits: Série com sinais de saída
        stop_price: Série com preços de stop loss
        target_price: Série com preços de take profit
        strategy_name: Nome da estratégia
        
    Returns:
        Figura do Matplotlib
    """
    config = get_plotting_config(strategy_name)
    
    # Criar figura com subplots
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1])
    
    # Subplot 1: Preço e sinais
    ax1 = fig.add_subplot(gs[0])
    
    # Plotar preço
    ax1.plot(df.index, df['fechamento'], label='Preço', color='blue', alpha=0.7)
    
    # Adicionar indicadores
    _adicionar_indicadores_matplotlib(ax1, df, config.indicators)
    
    # Plotar sinais
    _plotar_sinais_matplotlib(ax1, entries, exits, df, config)
    
    # Adicionar stop e target
    ax1.plot(df.index, stop_price, color='orange', linestyle='--', label='Stop Loss')
    ax1.plot(df.index, target_price, color='purple', linestyle='--', label='Take Profit')
    
    ax1.set_title(f'{config.title_prefix} - Sinais de Trading')
    ax1.legend()
    ax1.grid(True)
    
    # Subplot 2: Equity Curve
    ax2 = fig.add_subplot(gs[1])
    equity = pf.value()
    ax2.plot(equity.index, equity, label='Equity', color='green')
    ax2.set_title('Curva de Equity')
    ax2.grid(True)
    
    # Subplot 3: Drawdown
    ax3 = fig.add_subplot(gs[2])
    drawdown = (equity / equity.cummax() - 1) * 100
    ax3.plot(drawdown.index, drawdown, label='Drawdown', color='red')
    ax3.set_title('Drawdown (%)')
    ax3.grid(True)
    
    plt.tight_layout()
    return fig


def _adicionar_indicadores_tecnicos(fig: go.Figure, df: pd.DataFrame, 
                                    indicators: list, colors: Dict[str, str],
                                    ema_curta: Optional[int] = None,
                                    ema_longa: Optional[int] = None,
                                    ema_curta_long: Optional[int] = None,
                                    ema_longa_long: Optional[int] = None,
                                    ema_curta_short: Optional[int] = None,
                                    ema_longa_short: Optional[int] = None) -> None:
    """Adiciona indicadores técnicos ao gráfico."""
    for indicator in indicators:
        if indicator in ['ema_curta', 'ema_longa', 'ema_curta_long', 'ema_longa_long', 'ema_curta_short', 'ema_longa_short']:
            # Calcular EMAs dinamicamente usando valores passados como parâmetro
            if indicator == 'ema_curta' and ema_curta is not None:
                ema_series = df['fechamento'].ewm(span=ema_curta, adjust=False).mean()
                if not ema_series.isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=ema_series,
                            name=f'EMA {ema_curta}',
                            line=dict(color=colors.get(indicator, 'green'), width=1)
                        ),
                        row=1, col=1
                    )
            elif indicator == 'ema_longa' and ema_longa is not None:
                ema_series = df['fechamento'].ewm(span=ema_longa, adjust=False).mean()
                if not ema_series.isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=ema_series,
                            name=f'EMA {ema_longa}',
                            line=dict(color=colors.get(indicator, 'yellow'), width=1)
                        ),
                        row=1, col=1
                    )
            elif indicator == 'ema_curta_long' and ema_curta_long is not None:
                ema_series = df['fechamento'].ewm(span=ema_curta_long, adjust=False).mean()
                if not ema_series.isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=ema_series,
                            name=f'EMA {ema_curta_long} (Long)',
                            line=dict(color=colors.get(indicator, 'green'), width=1)
                        ),
                        row=1, col=1
                    )
            elif indicator == 'ema_longa_long' and ema_longa_long is not None:
                ema_series = df['fechamento'].ewm(span=ema_longa_long, adjust=False).mean()
                if not ema_series.isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=ema_series,
                            name=f'EMA {ema_longa_long} (Long)',
                            line=dict(color=colors.get(indicator, 'yellow'), width=1)
                        ),
                        row=1, col=1
                    )
            elif indicator == 'ema_curta_short' and ema_curta_short is not None:
                ema_series = df['fechamento'].ewm(span=ema_curta_short, adjust=False).mean()
                if not ema_series.isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=ema_series,
                            name=f'EMA {ema_curta_short} (Short)',
                            line=dict(color=colors.get(indicator, 'orange'), width=1)
                        ),
                        row=1, col=1
                    )
            elif indicator == 'ema_longa_short' and ema_longa_short is not None:
                ema_series = df['fechamento'].ewm(span=ema_longa_short, adjust=False).mean()
                if not ema_series.isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=ema_series,
                            name=f'EMA {ema_longa_short} (Short)',
                            line=dict(color=colors.get(indicator, 'red'), width=1)
                        ),
                        row=1, col=1
                    )
            elif indicator == 'ema_curta' and ema_curta is None:
                # Fallback para valores padrão se não especificado
                for periodo in [5, 9, 21]:
                    ema_series = df['fechamento'].ewm(span=periodo, adjust=False).mean()
                    if not ema_series.isna().all():
                        fig.add_trace(
                            go.Scatter(
                                x=df.index,
                                y=ema_series,
                                name=f'EMA {periodo}',
                                line=dict(color=colors.get(indicator, 'green'), width=1)
                            ),
                            row=1, col=1
                        )
                        break
            elif indicator == 'ema_longa' and ema_longa is None:
                # Fallback para valores padrão se não especificado
                for periodo in [45, 51, 80]:
                    ema_series = df['fechamento'].ewm(span=periodo, adjust=False).mean()
                    if not ema_series.isna().all():
                        fig.add_trace(
                            go.Scatter(
                                x=df.index,
                                y=ema_series,
                                name=f'EMA {periodo}',
                                line=dict(color=colors.get(indicator, 'yellow'), width=1)
                            ),
                            row=1, col=1
                        )
                        break
        elif indicator in df.columns:
            # Indicador já calculado no DataFrame
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[indicator],
                    name=indicator.replace('_', ' ').title(),
                    line=dict(color=colors.get(indicator, 'blue'), width=1)
                ),
                row=1, col=1
            )


def _adicionar_sinais_entrada_saida(fig: go.Figure, entries: pd.Series, exits: pd.Series,
                                    df: pd.DataFrame, config: PlottingConfig,
                                    size: Optional[pd.Series] = None) -> None:
    """Adiciona sinais de entrada e saída ao gráfico."""
    # Entradas
    if size is not None:
        # Estratégia long/short com diferentes tipos de entrada
        _adicionar_entradas_long_short(fig, entries, df, size, config)
    else:
        # Estratégia simples (long ou short apenas)
        _adicionar_entradas_simples(fig, entries, df, config)
    
    # Saídas
    _adicionar_saidas(fig, exits, df, config)


def _adicionar_entradas_long_short(fig: go.Figure, entries: pd.Series, df: pd.DataFrame,
                                    size: pd.Series, config: PlottingConfig) -> None:
    """Adiciona entradas para estratégias long/short."""
    # Encontrar índices válidos (onde ambos entries e size não são NaN)
    valid_entries = entries.dropna()
    valid_size = size.dropna()
    
    # Encontrar interseção dos índices válidos
    common_indices = valid_entries.index.intersection(valid_size.index)
    
    if len(common_indices) > 0:
        entry_x = common_indices
        entry_y = valid_entries.loc[common_indices].values
        entry_size_values = valid_size.loc[common_indices].values
        
        # Criar máscaras para long e short
        long_mask = entry_size_values > 0
        short_mask = entry_size_values < 0
        
        # Entradas long
        if any(long_mask):
            long_indices = entry_x[long_mask]
            long_values = entry_y[long_mask]
            fig.add_trace(
                go.Scatter(
                    x=long_indices,
                    y=long_values,
                    mode='markers',
                    marker=dict(
                        symbol=config.long_entry_symbol,
                        size=12,
                        color=config.long_entry_color,
                        line=dict(color='green'),
                    ),
                    name='Entradas Long'
                ),
                row=1, col=1
            )
        
        # Entradas short
        if any(short_mask):
            short_indices = entry_x[short_mask]
            short_values = entry_y[short_mask]
            fig.add_trace(
                go.Scatter(
                    x=short_indices,
                    y=short_values,
                    mode='markers',
                    marker=dict(
                        symbol=config.short_entry_symbol,
                        size=12,
                        color=config.short_entry_color,
                        line=dict(color='darkred'),
                    ),
                    name='Entradas Short'
                ),
                row=1, col=1
            )


def _adicionar_entradas_simples(fig: go.Figure, entries: pd.Series, df: pd.DataFrame,
                                config: PlottingConfig) -> None:
    """Adiciona entradas para estratégias simples (apenas long ou short)."""
    # Filtrar apenas valores não-NaN
    entry_indices = entries.dropna().index
    
    if len(entry_indices) > 0:
        entry_y = entries.dropna().values
        
        fig.add_trace(
            go.Scatter(
                x=entry_indices,
                y=entry_y,
                mode='markers',
                marker=dict(
                    symbol=config.entry_symbol,
                    size=12,
                    color=config.entry_color,
                    line=dict(color='green' if config.entry_color == 'lime' else 'darkred'),
                ),
                name='Entradas'
            ),
            row=1, col=1
        )


def _adicionar_saidas(fig: go.Figure, exits: pd.Series, df: pd.DataFrame,
                        config: PlottingConfig) -> None:
    """Adiciona sinais de saída ao gráfico."""
    # Filtrar apenas valores não-NaN
    exit_indices = exits.dropna().index
    
    if len(exit_indices) > 0:
        exit_y = exits.dropna().values
        
        fig.add_trace(
            go.Scatter(
                x=exit_indices,
                y=exit_y,
                mode='markers',
                marker=dict(
                    symbol=config.exit_symbol,
                    size=12,
                    color=config.exit_color,
                    line=dict(color='black' if config.exit_color == 'white' else 'green'),
                ),
                name='Saídas'
            ),
            row=1, col=1
        )


def _adicionar_stop_take_profit(fig: go.Figure, df: pd.DataFrame, stop_price: pd.Series,
                                target_price: pd.Series, colors: Dict[str, str]) -> None:
    """Adiciona linhas de stop loss e take profit."""
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=stop_price,
            mode='lines',
            line=dict(color=colors.get('stop_loss', 'orange'), width=1, dash='dash'),
            name='Stop Loss'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=target_price,
            mode='lines',
            line=dict(color=colors.get('take_profit', 'green'), width=1, dash='dash'),
            name='Take Profit'
        ),
        row=1, col=1
    )


def _adicionar_peaks(fig: go.Figure, df: pd.DataFrame) -> None:
    """Adiciona marcação de topos e fundos detectados."""
    # Fundos
    fundos_idx = df.index[df['last_peak_type'] == 1]
    fundos_val = df.loc[fundos_idx, 'fechamento']
    if len(fundos_idx) > 0:
        fig.add_trace(
            go.Scatter(
                x=fundos_idx,
                y=fundos_val,
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=10,
                    color='blue',
                    line=dict(color='navy'),
                ),
                name='Fundos (findpeaks)'
            ),
            row=1, col=1
        )
    
    # Topos
    topos_idx = df.index[df['last_peak_type'] == -1]
    topos_val = df.loc[topos_idx, 'fechamento']
    if len(topos_idx) > 0:
        fig.add_trace(
            go.Scatter(
                x=topos_idx,
                y=topos_val,
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=10,
                    color='orange',
                    line=dict(color='darkorange'),
                ),
                name='Topos (findpeaks)'
            ),
            row=1, col=1
        )


def _adicionar_volume(fig: go.Figure, df: pd.DataFrame) -> None:
    """Adiciona gráfico de volume."""
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker=dict(
                color='white',
                opacity=0.75
            )
        ),
        row=2, col=1
    )


def _marcar_trades_equity_do_portfolio(fig: go.Figure, pf, equity: pd.Series) -> None:
    """Marca trades reais na curva de equity usando dados do portfolio."""
    try:
        # Obter dados dos trades do portfolio
        trades = pf.trades.records_readable
        
        if len(trades) == 0:
            return  # Nenhum trade para marcar
        
        # Obter timestamps de entrada e saída dos trades
        entry_times = []
        exit_times = []
        entry_values = []
        exit_values = []
        
        for _, trade in trades.iterrows():
            entry_time = trade['Entry Timestamp']
            exit_time = trade['Exit Timestamp']
            
            # Verificar se os timestamps existem no equity
            if entry_time in equity.index:
                entry_times.append(entry_time)
                entry_values.append(equity.loc[entry_time])
                
            if exit_time in equity.index:
                exit_times.append(exit_time)
                exit_values.append(equity.loc[exit_time])
        
        # Adicionar marcadores de entrada
        if entry_times:
            fig.add_trace(
                go.Scatter(
                    x=entry_times,
                    y=entry_values,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=10,
                        color='green',
                        line=dict(color='darkgreen', width=1)
                    ),
                    name='Abertura Posição',
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # Adicionar marcadores de saída
        if exit_times:
            fig.add_trace(
                go.Scatter(
                    x=exit_times,
                    y=exit_values,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=10,
                        color='red',
                        line=dict(color='darkred', width=1)
                    ),
                    name='Fechamento Posição',
                    showlegend=True
                ),
                row=1, col=1
            )
            
    except Exception as e:
        # Se houver erro, não marcar trades (falha silenciosa)
        print(f"Aviso: Não foi possível marcar trades na equity: {e}")
        pass


def _marcar_trades_equity(fig: go.Figure, entries: pd.Series, exits: pd.Series,
                            equity: pd.Series) -> None:
    """Marca trades reais na curva de equity, não todos os sinais."""
    # Para estratégias from_signals, precisamos filtrar apenas os trades únicos
    # não todos os sinais individuais
    
    # Encontrar mudanças de estado (entrada/saída de posições)
    valid_entries = entries.dropna()
    valid_exits = exits.dropna()
    
    # Criar um conjunto combinado de todos os pontos de trade
    all_trades = []
    
    # Adicionar entradas
    for idx in valid_entries.index:
        if idx in equity.index:
            all_trades.append((idx, 'entry'))
    
    # Adicionar saídas
    for idx in valid_exits.index:
        if idx in equity.index:
            all_trades.append((idx, 'exit'))
    
    # Ordenar por data
    all_trades.sort(key=lambda x: x[0])
    
    # Filtrar apenas mudanças reais de posição (evitar duplicatas consecutivas)
    filtered_trades = []
    last_action = None
    
    for timestamp, action in all_trades:
        if action != last_action:  # Só adicionar se for uma mudança real
            filtered_trades.append((timestamp, action))
            last_action = action
    
    # Separar entradas e saídas filtradas
    entry_points = [(t, equity.loc[t]) for t, action in filtered_trades if action == 'entry']
    exit_points = [(t, equity.loc[t]) for t, action in filtered_trades if action == 'exit']
    
    # Adicionar marcadores de entrada
    if entry_points:
        entry_times, entry_values = zip(*entry_points)
        fig.add_trace(
            go.Scatter(
                x=entry_times,
                y=entry_values,
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=10,
                    color='green',
                    line=dict(color='darkgreen', width=1)
                ),
                name='Abertura Posição',
                showlegend=True
            ),
            row=1, col=1
        )
    
    # Adicionar marcadores de saída
    if exit_points:
        exit_times, exit_values = zip(*exit_points)
        fig.add_trace(
            go.Scatter(
                x=exit_times,
                y=exit_values,
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=10,
                    color='red',
                    line=dict(color='darkred', width=1)
                ),
                name='Fechamento Posição',
                showlegend=True
            ),
            row=1, col=1
        )


def _configurar_layout(fig: go.Figure, config: PlottingConfig, simbolo: str, intervalo: str) -> None:
    """Configura o layout do gráfico."""
    title = f"{config.title_prefix} - {simbolo} ({intervalo}min)"
    
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template=config.template
    )
    
    # Atualizar eixos Y
    fig.update_yaxes(title_text="Preço", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)


def _adicionar_indicadores_matplotlib(ax, df: pd.DataFrame, indicators: list) -> None:
    """Adiciona indicadores técnicos ao gráfico Matplotlib."""
    for indicator in indicators:
        if indicator in ['ema_curta', 'ema_longa']:
            # Similar à lógica do Plotly, mas para matplotlib
            pass
        elif indicator in df.columns:
            ax.plot(df.index, df[indicator], label=indicator.replace('_', ' ').title())


def _plotar_sinais_matplotlib(ax, entries: pd.Series, exits: pd.Series, 
                                df: pd.DataFrame, config: PlottingConfig) -> None:
    """Adiciona sinais ao gráfico Matplotlib."""
    # Simplificado para matplotlib
    if len(entries.dropna()) > 0:
        entry_x = entries.dropna().index
        entry_y = df.loc[entry_x, 'fechamento'] if hasattr(entries, 'index') else entries.dropna().values
        ax.scatter(entry_x, entry_y, color=config.entry_color, marker='^', label='Entradas', s=100)
    
    if len(exits.dropna()) > 0:
        exit_x = exits.dropna().index
        exit_y = df.loc[exit_x, 'fechamento'] if hasattr(exits, 'index') else exits.dropna().values
        ax.scatter(exit_x, exit_y, color=config.exit_color, marker='v', label='Saídas', s=100)
