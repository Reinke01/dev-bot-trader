# estratégia para decidir entre compra e venda com base no último pico, se é topo ou fundo
# se é fundo, comprar até aparecer um topo
# se é topo, vender até aparecer um fundo
# criar a coluna last_peak_type, 1 para fundo e -1 para topo (gera derivação com info de último pico do gráfico diário)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import pandas as pd
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout
import numpy as np
from vectorbt import nb
from scipy.signal import find_peaks

# ==========================================
# Versão completa com Numba (sem vetorização)
# Entrada no preço de máxima ou mínima da vela referência, saída no preço de stop ou alvo
# Combina estratégias long e short em uma única função
# ==========================================
@nb.njit
def double_ema_breakout_long_short_nb(close, high, low, ema1, ema2, q_stop, rr, last_peak_type):
    entries = np.full(close.shape, np.nan)
    exits = np.full(close.shape, np.nan)
    stop_price = np.full(close.shape, np.nan)
    target_price = np.full(close.shape, np.nan)
    size = np.full(close.shape, np.nan)

    in_trade = False
    entry_price = 0.0
    stop_value = 0.0
    target_value = 0.0
    current_position = 0  # 0 = sem posição, 1 = long, -1 = short

    for i in range(999, len(close)):
        # Condições para long
        long_cond1 = close[i - 1] > ema1[i - 1]
        long_cond2 = close[i - 1] > ema2[i - 1]
        long_cond3 = high[i] > high[i - 1]

        # Condições para short
        short_cond1 = close[i - 1] < ema1[i - 1]
        short_cond2 = close[i - 1] < ema2[i - 1]
        short_cond3 = low[i] < low[i - 1]

        if not in_trade:
            # Verificar entrada long
            if long_cond1 and long_cond2 and long_cond3:
                entry_price = high[i - 1]
                min_stop = low[i - q_stop + 1:i + 1]
                if len(min_stop) == q_stop:
                    stop_value = np.min(min_stop)
                    target_value = entry_price + (entry_price - stop_value) * rr

                    entries[i] = entry_price
                    stop_price[i] = stop_value
                    target_price[i] = target_value
                    size[i] = 1.0  # Entrada long (compra)
                    in_trade = True
                    current_position = 1

            # Verificar entrada short
            elif short_cond1 and short_cond2 and short_cond3:
                entry_price = low[i - 1]
                max_stop = high[i - q_stop + 1:i + 1]
                if len(max_stop) == q_stop:
                    stop_value = np.max(max_stop)
                    target_value = entry_price - (stop_value - entry_price) * rr

                    entries[i] = entry_price
                    stop_price[i] = stop_value
                    target_price[i] = target_value
                    size[i] = -1.0  # Entrada short (venda)
                    in_trade = True
                    current_position = -1

        elif in_trade:
            stop_price[i] = stop_value
            target_price[i] = target_value
            current_high = high[i]
            current_low = low[i]

            # Saída por topo/fundo
            if current_position == 1:  # Em posição long
                if current_high >= target_value or current_low <= stop_value:
                    exits[i] = target_value if current_high >= target_value else stop_value
                    size[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0
                
                elif last_peak_type[i-6] == -1:  # topo
                    exits[i] = close[i-1]
                    size[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0
            else:  # Em posição short
                if current_low <= target_value or current_high >= stop_value:
                    exits[i] = target_value if current_low <= target_value else stop_value
                    size[i] = 0.0  # Saída short (compra)
                    in_trade = False
                    current_position = 0

                elif last_peak_type[i-6] == 1:  # fundo
                    exits[i] = close[i-1]
                    size[i] = 0.0  # Saída short (compra)
                    in_trade = False
                    current_position = 0

    return entries, exits, stop_price, target_price, size

# ===========================================================
# Versão procedural para utilização com Numba
# ===========================================================
def gerar_estrategiaaa(df: pd.DataFrame, estrategia: DoubleEmaBreakout):
    close = df['fechamento'].values
    high = df['maxima'].values
    low = df['minima'].values

    # Extrair parâmetros
    p1 = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2 = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop = int(estrategia.stop.parametros['quantidade'])
    rr = float(estrategia.alvo.parametros['multiplicador'])

    # Indicadores
    ema1 = pd.Series(close).ewm(span=p1).mean().values
    ema2 = pd.Series(close).ewm(span=p2).mean().values

    # last_peak_type deve estar no DataFrame
    last_peak_type = df['last_peak_type'].values

    # Chamar a função com Numba
    entries, exits, stop_price, target_price, size = double_ema_breakout_long_short_nb(
        close, high, low, ema1, ema2, q_stop, rr, last_peak_type
    )

    index = df.index
    return (
        pd.Series(entries, index=index),
        pd.Series(exits, index=index),
        pd.Series(stop_price, index=index),
        pd.Series(target_price, index=index),
        pd.Series(size, index=index)
    )

# ===========================================================
# Versão procedural sem Numba para manipulação direta do DataFrame
# ===========================================================
def gerar_estrategia(df: pd.DataFrame, estrategia: DoubleEmaBreakout):
    """
    Versão procedural que extrai parâmetros da estratégia e executa 
    a navegação das velas manipulando dados diretamente do DataFrame
    """
    # Extrair parâmetros da estratégia
    p1 = int(estrategia.condicoes_entrada[0].parametros['periodo'])
    p2 = int(estrategia.condicoes_entrada[1].parametros['periodo'])
    q_stop = int(estrategia.stop.parametros['quantidade'])
    rr = float(estrategia.alvo.parametros['multiplicador'])
    
    # Criar cópias das colunas necessárias
    close = df['fechamento'].copy()
    high = df['maxima'].copy()
    low = df['minima'].copy()
    # last_peak_type = df['last_peak_type'].copy()
    
    # Calcular indicadores
    ema1 = close.ewm(span=p1).mean()
    ema2 = close.ewm(span=p2).mean()
    
    # Inicializar arrays de resultado
    entries = pd.Series(np.nan, index=df.index)
    exits = pd.Series(np.nan, index=df.index)
    stop_price = pd.Series(np.nan, index=df.index)
    target_price = pd.Series(np.nan, index=df.index)
    size = pd.Series(np.nan, index=df.index)
    
    # Variáveis de estado
    in_trade = False
    entry_price = 0.0
    stop_value = 0.0
    target_value = 0.0
    current_position = 0  # 0 = sem posição, 1 = long, -1 = short
    
    # Inicializar coluna last_peak_type se não existir
    if 'last_peak_type' not in df.columns:
        df['last_peak_type'] = 0
    
    # Iterar através das velas a partir do índice 999
    for i in range(999, len(df)):
        # Validação e criação incremental da coluna 'last_peak_type' até a posição i
        # Garante que a coluna existe e só atualiza até a vela i (inclusive)
        
        fechamento_slice = df['fechamento'].iloc[:i+1].values
        
        # Detecta fundos (mínimos locais) com parâmetros ajustados
        try:
            fundos, _ = find_peaks(-fechamento_slice, distance=21)
        except:
            fundos = np.array([])
        
        # Detecta topos (máximos locais) com parâmetros ajustados  
        try:
            topos, _ = find_peaks(fechamento_slice, distance=21)
        except:
            topos = np.array([])
        
        # Cria array temporário para o slice
        last_peak_type_slice = np.zeros(i+1, dtype=int)
        if len(fundos) > 0:
            last_peak_type_slice[fundos] = 1
        if len(topos) > 0:
            last_peak_type_slice[topos] = -1
        
        # Atualiza apenas o trecho relevante da coluna no DataFrame
        df.loc[df.index[:i+1], 'last_peak_type'] = last_peak_type_slice
        
        # Condições para long
        long_cond1 = close.iloc[i-1] > ema1.iloc[i-1]
        long_cond2 = close.iloc[i-1] > ema2.iloc[i-1]
        long_cond3 = high.iloc[i] > high.iloc[i-1]
        
        # Condições para short
        short_cond1 = close.iloc[i-1] < ema1.iloc[i-1]
        short_cond2 = close.iloc[i-1] < ema2.iloc[i-1]
        short_cond3 = low.iloc[i] < low.iloc[i-1]
        
        if not in_trade:
            # Verificar entrada long
            if long_cond1 and long_cond2 and long_cond3:
                entry_price = high.iloc[i-1]
                
                # Calcular stop baseado nas mínimas das últimas q_stop velas
                start_idx = max(0, i - q_stop + 1)
                min_stop = low.iloc[start_idx:i+1].min()
                
                stop_value = min_stop
                target_value = entry_price + (entry_price - stop_value) * rr
                
                entries.iloc[i] = entry_price
                stop_price.iloc[i] = stop_value
                target_price.iloc[i] = target_value
                size.iloc[i] = 1.0  # Entrada long (compra)
                in_trade = True
                current_position = 1
                
            # Verificar entrada short
            elif short_cond1 and short_cond2 and short_cond3:
                entry_price = low.iloc[i-1]
                
                # Calcular stop baseado nas máximas das últimas q_stop velas
                start_idx = max(0, i - q_stop + 1)
                max_stop = high.iloc[start_idx:i+1].max()
                
                stop_value = max_stop
                target_value = entry_price - (stop_value - entry_price) * rr
                
                entries.iloc[i] = entry_price
                stop_price.iloc[i] = stop_value
                target_price.iloc[i] = target_value
                size.iloc[i] = -1.0  # Entrada short (venda)
                in_trade = True
                current_position = -1
                
        elif in_trade:
            # Manter informações de stop e target
            stop_price.iloc[i] = stop_value
            target_price.iloc[i] = target_value
            
            current_high = high.iloc[i]
            current_low = low.iloc[i]
            
            # Saída por topo/fundo ou stop/target
            if current_position == 1:  # Em posição long
                # Verificar saída por target ou stop
                if current_high >= target_value or current_low <= stop_value:
                    exit_price = target_value if current_high >= target_value else stop_value
                    exits.iloc[i] = exit_price
                    size.iloc[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0
                    
                # Verificar saída por topo (last_peak_type == -1)
                elif df['last_peak_type'].iloc[i-3] == -1:  # topo
                    exits.iloc[i] = close.iloc[i-1]
                    size.iloc[i] = 0.0  # Saída long (venda)
                    in_trade = False
                    current_position = 0
                    
            else:  # Em posição short (current_position == -1)
                # Verificar saída por target ou stop
                if current_low <= target_value or current_high >= stop_value:
                    exit_price = target_value if current_low <= target_value else stop_value
                    exits.iloc[i] = exit_price
                    size.iloc[i] = 0.0  # Saída short (compra)
                    in_trade = False
                    current_position = 0
                    
                # Verificar saída por fundo (last_peak_type == 1)
                elif df['last_peak_type'].iloc[i-3] == 1:  # fundo
                    exits.iloc[i] = close.iloc[i-1]
                    size.iloc[i] = 0.0  # Saída short (compra)
                    in_trade = False
                    current_position = 0
    
    return entries, exits, stop_price, target_price, size