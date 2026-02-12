import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st
import time

from corretoras.funcoes_bybit import carregar_dados_historicos, busca_velas
from indicadores.topos_fundos import topos_fundos_cinco_velas, topos_fundos_toNDArray, topos_fundos_duas_velas, topos_fundos_tres_velas, topos_fundos_quatro_velas, topos_fundos_quatro_velas_v2

def identificar_topos_fundos(df, coluna='fechamento', height=None, threshold=None, distance=None, prominence=None, width=None, wlen=None, rel_height=0.5, plateau_size=None):
    """
    Identifica topos e fundos em uma série temporal usando find_peaks.
    
    Args:
        df: DataFrame com os dados
        coluna: Nome da coluna para análise (default: 'fechamento')
        ordem: Distância mínima entre picos (default: 3)
        prominence: Proeminência mínima dos picos (default: 0.75)
    
    Returns:
        DataFrame com nova coluna 'last_peak_type' onde:
        1 = fundo
        -1 = topo
        0 = não é pico
    """
    arr = df[coluna].values
    last_peak_type = np.zeros(len(df), dtype=int)
    
    # Encontrar fundos (mínimos locais)
    fundos, properties_fundos = find_peaks(-arr, height=height, threshold=threshold, distance=distance, prominence=prominence, width=width, wlen=wlen, rel_height=rel_height, plateau_size=plateau_size)
    last_peak_type[fundos] = 1
    
    # Encontrar topos (máximos locais)
    topos, properties_topos = find_peaks(arr, height=height, threshold=threshold, distance=distance, prominence=prominence, width=width, wlen=wlen, rel_height=rel_height, plateau_size=plateau_size)
    last_peak_type[topos] = -1
    
    # Adicionar ao DataFrame
    df['last_peak_type'] = last_peak_type
    
    # Adicionar propriedades dos picos e usar iloc para acessar por posição numérica
    if height is not None:
        df['peak_heights'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_heights')] = properties_fundos['peak_heights']
        df.iloc[topos, df.columns.get_loc('peak_heights')] = properties_topos['peak_heights']

    if threshold is not None:
        df['peak_left_thresholds'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_left_thresholds')] = properties_fundos['left_thresholds']
        df.iloc[topos, df.columns.get_loc('peak_left_thresholds')] = properties_topos['left_thresholds']

        df['peak_right_thresholds'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_right_thresholds')] = properties_fundos['right_thresholds']
        df.iloc[topos, df.columns.get_loc('peak_right_thresholds')] = properties_topos['right_thresholds']

    if prominence is not None:
        df['peak_prominences'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_prominences')] = properties_fundos['prominences']
        df.iloc[topos, df.columns.get_loc('peak_prominences')] = properties_topos['prominences']

        df['peak_right_bases'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_right_bases')] = properties_fundos['right_bases']
        df.iloc[topos, df.columns.get_loc('peak_right_bases')] = properties_topos['right_bases']

        df['peak_left_bases'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_left_bases')] = properties_fundos['left_bases']
        df.iloc[topos, df.columns.get_loc('peak_left_bases')] = properties_topos['left_bases']

    if width is not None:
        df['peak_widths'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_widths')] = properties_fundos['widths']
        df.iloc[topos, df.columns.get_loc('peak_widths')] = properties_topos['widths']

        df['peak_width_heights'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_width_heights')] = properties_fundos['width_heights']
        df.iloc[topos, df.columns.get_loc('peak_width_heights')] = properties_topos['width_heights']

        df['peak_left_ips'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_left_ips')] = properties_fundos['left_ips']
        df.iloc[topos, df.columns.get_loc('peak_left_ips')] = properties_topos['left_ips']

        df['peak_right_ips'] = 0.0
        df.iloc[fundos, df.columns.get_loc('peak_right_ips')] = properties_fundos['right_ips']
        df.iloc[topos, df.columns.get_loc('peak_right_ips')] = properties_topos['right_ips']

    if plateau_size is not None:
        df['plateau_sizes'] = 0.0
        df.iloc[fundos, df.columns.get_loc('plateau_sizes')] = properties_fundos['plateau_sizes']
        df.iloc[topos, df.columns.get_loc('plateau_sizes')] = properties_topos['plateau_sizes']

        df['left_edges'] = 0.0
        df.iloc[fundos, df.columns.get_loc('left_edges')] = properties_fundos['left_edges']
        df.iloc[topos, df.columns.get_loc('left_edges')] = properties_topos['left_edges']

        df['right_edges'] = 0.0
        df.iloc[fundos, df.columns.get_loc('right_edges')] = properties_fundos['right_edges']
        df.iloc[topos, df.columns.get_loc('right_edges')] = properties_topos['right_edges']

    return df, fundos, topos

def plotar_grafico_velas_plotly(df, fundos, topos):
    """
    Cria um gráfico interativo com velas e indicadores usando Plotly.
    
    Args:
        df: DataFrame com os dados
        fundos: Índices dos fundos identificados
        topos: Índices dos topos identificados
    """
    # Criar figura com subplots (candles no topo, volume embaixo)
    fig = go.Figure()
    
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
        )
    )
    
    # Adicionar fundos detectados (triângulo azul para baixo)
    if len(fundos) > 0:
        fig.add_trace(
            go.Scatter(
                x=df.iloc[fundos].index,
                y=df.iloc[fundos]['minima']*0.999,
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='yellow',
                ),
                name='Fundos'
            )
        )
    
    # Adicionar topos detectados (triângulo vermelho para cima)
    if len(topos) > 0:
        fig.add_trace(
            go.Scatter(
                x=df.iloc[topos].index,
                y=df.iloc[topos]['maxima']*1.001,
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='yellow',
                ),
                name='Topos'
            )
        )
    
    # Atualizar layout
    fig.update_layout(
        title='Análise de Topos e Fundos',
        yaxis_title='Preço',
        xaxis_title='Data/Hora',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800  # Aumentar altura do gráfico
    )
    
    return fig

# Configurações do Streamlit
st.set_page_config(
    page_title="Análise de Topos e Fundos",
    page_icon="📈",
    layout="wide"
)

# Título
st.title("Análise de Topos e Fundos em Tempo Real")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    simbolo = st.text_input("Símbolo", value="SOLUSDT")
    intervalo = st.selectbox("Intervalo", options=['3', '5', '15', '30', '60', '120', '240'], index=2)
    window = st.slider("Janela de Análise", min_value=100, max_value=1000, value=300, step=50)
    use_distance = st.checkbox(
        "Usar distância personalizada",
        value=False
    )
    distance = st.slider(
        "Distância Mínima entre Picos",
        min_value=2,
        max_value=35,
        value=7,
        disabled=not use_distance
    )
    use_prominence = st.checkbox(
        "Usar proeminência personalizada",
        value=False
    )
    prominence = st.slider(
        "Proeminência dos Picos", 
        min_value=0.1, 
        max_value=10.0, 
        value=0.95, 
        step=0.05,
        disabled=not use_prominence
    )
    wlen_type = st.checkbox(
        "Usar largura personalizada",
        value=False
    )
    wlen = st.slider(
        "Largura dos Picos", 
        min_value=1, 
        max_value=20, 
        value=5, 
        step=1,
        disabled=not wlen_type
    )
    update_interval = st.slider("Intervalo de Atualização (segundos)", min_value=1, max_value=60, value=5)

    # Separador
    st.sidebar.markdown("---")

    # Controles de visualização
    st.sidebar.header("Modo de Visualização")

    # Inicializar session_state se necessário
    if 'posicao_final' not in st.session_state:
        st.session_state.posicao_final = window

    # Checkbox para alternar entre modo ao vivo e fixo
    modo_fixo = st.sidebar.checkbox("Modo Fixo", value=False, help="Visualizar uma janela fixa de velas ao invés do modo ao vivo")

    if modo_fixo:
        # Slider para selecionar a posição final da janela
        st.session_state.posicao_final = st.sidebar.slider(
            "Posição Final",
            min_value=window,
            max_value=1000,  # Valor máximo arbitrário
            value=st.session_state.posicao_final,
            help="Selecione a posição final da janela de análise"
        )
        
        # Botões para navegação
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("◀ Anterior") and st.session_state.posicao_final > window:
                st.session_state.posicao_final -= 1
                st.rerun()
        with col2:
            if st.button("Próximo ▶") and st.session_state.posicao_final < 1000:
                st.session_state.posicao_final += 1
                st.rerun()

# Criar containers para os elementos que serão atualizados
stats_container = st.empty()
chart_container = st.empty()
signals_container = st.empty()

# Loop principal
while True:
    try:
        # Carregar dados
        df = busca_velas(simbolo, intervalo, [9, 21])
        if df is None or len(df) == 0:
            st.error("Não foi possível carregar os dados. Tentando novamente...")
            time.sleep(5)
            continue
            
        df.columns = df.columns.str.lower()
        
        # Aplicar a janela de visualização
        if modo_fixo:
            inicio = max(0, st.session_state.posicao_final - window)
            fim = st.session_state.posicao_final
            df = df.iloc[inicio:fim]
        else:
            df = df.iloc[-window:]

        if not use_distance:
            distance = None
        if not use_prominence:
            prominence = None
        if not wlen_type:
            wlen = None
        
        # Identificar topos e fundos
        df, fundos, topos = identificar_topos_fundos(
            df,
            coluna='fechamento',
            distance=distance,
            prominence=prominence,
            wlen=wlen,
        )
        # df, fundos, topos = topos_fundos_quatro_velas_v2(df)
        # fundos, topos = topos_fundos_toNDArray(fundos, topos)

        # Atualizar estatísticas
        with stats_container.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Topos", len(topos))
            with col2:
                st.metric("Total de Fundos", len(fundos))
            with col3:
                st.metric("Último Preço", f"${df['fechamento'].iloc[-1]:.2f}")
            with col4:
                st.metric("Variação 24h", f"{((df['fechamento'].iloc[-1] / df['fechamento'].iloc[-96]) - 1) * 100:.2f}%")

        # Atualizar gráfico com chave única baseada no timestamp
        fig = plotar_grafico_velas_plotly(df, fundos, topos)
        chart_container.plotly_chart(fig, use_container_width=True)

        # Mostrar últimos sinais
        with signals_container.container():
            st.subheader("Últimos 5 sinais encontrados")
            sinais = pd.DataFrame({
                'Data': df.index,
                'Preço': df['fechamento'],
                'Tipo': df['last_peak_type'].map({1: 'Fundo', -1: 'Topo', 0: 'Nenhum'}),
                'Altura': df['peak_heights'] if 'peak_heights' in df.columns else 0,
                'Limite Esquerdo': df['peak_left_thresholds'] if 'peak_left_thresholds' in df.columns else 0,
                'Limite Direito': df['peak_right_thresholds'] if 'peak_right_thresholds' in df.columns else 0,
                'Proeminência': df['peak_prominences'] if 'peak_prominences' in df.columns else 0,
                'Base Esquerda': df['peak_left_bases'] if 'peak_left_bases' in df.columns else 0,
                'Base Direita': df['peak_right_bases'] if 'peak_right_bases' in df.columns else 0,
                'Largura': df['peak_widths'] if 'peak_widths' in df.columns else 0,
                'Largura Máxima': df['peak_width_heights'] if 'peak_width_heights' in df.columns else 0,
                'IP Esquerdo': df['peak_left_ips'] if 'peak_left_ips' in df.columns else 0,
                'IP Direito': df['peak_right_ips'] if 'peak_right_ips' in df.columns else 0,
                'Platô': df['plateau_sizes'] if 'plateau_sizes' in df.columns else 0,
                'Base Esquerda': df['left_edges'] if 'left_edges' in df.columns else 0,
                'Base Direita': df['right_edges'] if 'right_edges' in df.columns else 0
            })
            st.dataframe(
                sinais[sinais['Tipo'] != 'Nenhum'].tail(10),
                hide_index=True,
                use_container_width=True
            )

        # Aguardar antes da próxima atualização
        if modo_fixo:   
            time.sleep(300)
        else:
            time.sleep(update_interval)

    except Exception as e:
        st.error(f"Erro ao atualizar dados: {str(e)}")
        time.sleep(5)
