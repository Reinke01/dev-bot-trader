"""
Script AVANÇADO para Análise de Reversão
Indicadores múltiplos para máxima precisão
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from corretoras.funcoes_bybit import busca_velas
from managers.data_manager import prepare_market_data
from indicadores.padroes_velas import engolfo_alta, engolfo_baixa, piercing_line_alta, harami_alta
from indicadores.bandas_bollinger import bandas_bollinger
from indicadores.indicadores_osciladores import calcula_rsi
from utils.notifications.telegram_client import get_telegram_client
import pandas as pd
import pandas_ta as ta
import numpy as np

def calcular_stochastic_rsi(df, periodo=14, smooth_k=3, smooth_d=3):
    """Stochastic RSI - Mais sensível para reversões"""
    rsi = ta.rsi(df['fechamento'], length=periodo)
    stoch_rsi = (rsi - rsi.rolling(periodo).min()) / (rsi.rolling(periodo).max() - rsi.rolling(periodo).min()) * 100
    k = stoch_rsi.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return k, d

def calcular_mfi(df, periodo=14):
    """Money Flow Index - RSI com Volume"""
    typical_price = (df['maxima'] + df['minima'] + df['fechamento']) / 3
    money_flow = typical_price * df['volume']
    
    positive_flow = pd.Series(0.0, index=df.index)
    negative_flow = pd.Series(0.0, index=df.index)
    
    for i in range(1, len(df)):
        if typical_price.iloc[i] > typical_price.iloc[i-1]:
            positive_flow.iloc[i] = money_flow.iloc[i]
        elif typical_price.iloc[i] < typical_price.iloc[i-1]:
            negative_flow.iloc[i] = money_flow.iloc[i]
    
    positive_mf = positive_flow.rolling(periodo).sum()
    negative_mf = negative_flow.rolling(periodo).sum()
    
    mfi = 100 - (100 / (1 + positive_mf / negative_mf))
    return mfi

def calcular_williams_r(df, periodo=14):
    """Williams %R - Confirmação de oversold/overbought"""
    highest_high = df['maxima'].rolling(periodo).max()
    lowest_low = df['minima'].rolling(periodo).min()
    williams_r = -100 * (highest_high - df['fechamento']) / (highest_high - lowest_low)
    return williams_r

def calcular_vwap(df):
    """Volume Weighted Average Price"""
    typical_price = (df['maxima'] + df['minima'] + df['fechamento']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap

def analisar_reversao_avancada(simbolo='BTCUSDT'):
    print(f"\n🔍 ANÁLISE AVANÇADA DE REVERSÃO - {simbolo}")
    print("=" * 70)
    
    # Buscar dados
    df = busca_velas(simbolo, '60', [9, 21, 200])  # 1 hora
    df = prepare_market_data(df, use_emas=True, emas_periods=[20, 50, 200])
    
    # ===== INDICADORES BÁSICOS =====
    df['rsi'] = calcula_rsi(df, 14)
    df = bandas_bollinger(df, periodo=20, desvios=2)
    
    # ===== NOVOS INDICADORES AVANÇADOS =====
    df['stoch_k'], df['stoch_d'] = calcular_stochastic_rsi(df)
    df['mfi'] = calcular_mfi(df)
    df['williams_r'] = calcular_williams_r(df)
    df['vwap'] = calcular_vwap(df)
    
    # MACD
    macd_result = ta.macd(df['fechamento'])
    df['macd'] = macd_result['MACD_12_26_9']
    df['macd_signal'] = macd_result['MACDs_12_26_9']
    df['macd_histogram'] = macd_result['MACDh_12_26_9']
    
    # EMAs
    df['ema_20'] = df['fechamento'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['fechamento'].ewm(span=50, adjust=False).mean()
    df['ema_200'] = df['fechamento'].ewm(span=200, adjust=False).mean()
    
    # Padrões de vela
    df['engolfo_alta'] = engolfo_alta(df)
    df['piercing_line'] = piercing_line_alta(df)
    df['harami_alta'] = harami_alta(df)
    
    # ===== DADOS ATUAIS =====
    preco_atual = df['fechamento'].iloc[-1]
    rsi_atual = df['rsi'].iloc[-1]
    stoch_k_atual = df['stoch_k'].iloc[-1]
    stoch_d_atual = df['stoch_d'].iloc[-1]
    mfi_atual = df['mfi'].iloc[-1]
    williams_r_atual = df['williams_r'].iloc[-1]
    vwap_atual = df['vwap'].iloc[-1]
    
    macd_atual = df['macd'].iloc[-1]
    macd_signal_atual = df['macd_signal'].iloc[-1]
    macd_hist_atual = df['macd_histogram'].iloc[-1]
    macd_hist_anterior = df['macd_histogram'].iloc[-2]
    
    volume_atual = df['volume'].iloc[-1]
    volume_medio = df['volume'].rolling(20).mean().iloc[-1]
    volume_ratio = (volume_atual / volume_medio) * 100
    
    banda_inferior = df['banda_inferior'].iloc[-1]
    distancia_vwap = ((preco_atual - vwap_atual) / vwap_atual) * 100
    
    # ===== SCORE DE REVERSÃO (0-15) =====
    score = 0
    sinais = []
    sinais_fortes = []
    
    # 1. RSI Extremo (0-3 pontos)
    if rsi_atual < 30:
        score += 2
        sinais.append(f"✅ RSI Sobrevenda ({rsi_atual:.1f})")
        if rsi_atual < 25:
            score += 1
            sinais_fortes.append(f"🔥 RSI EXTREMO ({rsi_atual:.1f})")
    
    # 2. Stochastic RSI (0-3 pontos) ⭐ NOVO
    if stoch_k_atual < 20:
        score += 2
        sinais.append(f"✅ Stoch RSI Oversold (K: {stoch_k_atual:.1f})")
        if stoch_k_atual < 10:
            score += 1
            sinais_fortes.append(f"🔥 Stoch RSI EXTREMO ({stoch_k_atual:.1f})")
    
    # Cruzamento Stochastic (sinal de reversão)
    if stoch_k_atual > stoch_d_atual and df['stoch_k'].iloc[-2] <= df['stoch_d'].iloc[-2]:
        score += 2
        sinais_fortes.append("🚀 CRUZAMENTO STOCH RSI - Reversão iniciando!")
    
    # 3. Money Flow Index (0-2 pontos) ⭐ NOVO
    if mfi_atual < 30:
        score += 2
        sinais.append(f"✅ MFI Oversold ({mfi_atual:.1f}) - Pressão compradora baixa")
        if mfi_atual < 20:
            sinais_fortes.append(f"🔥 MFI EXTREMO ({mfi_atual:.1f})")
    
    # 4. Williams %R (0-2 pontos) ⭐ NOVO
    if williams_r_atual < -80:
        score += 2
        sinais.append(f"✅ Williams %R Oversold ({williams_r_atual:.1f})")
    
    # 5. MACD (0-3 pontos) ⭐ NOVO
    if macd_hist_atual > macd_hist_anterior and macd_hist_anterior < 0:
        score += 2
        sinais_fortes.append("🚀 MACD Histogram VIRANDO - Momentum mudando!")
    
    if macd_atual > macd_signal_atual and df['macd'].iloc[-2] <= df['macd_signal'].iloc[-2]:
        score += 3
        sinais_fortes.append("🚀🚀 CRUZAMENTO MACD - Sinal FORTE de reversão!")
    
    # 6. VWAP (0-2 pontos) ⭐ NOVO
    if preco_atual < vwap_atual and distancia_vwap < -5:
        score += 2
        sinais.append(f"✅ Preço {abs(distancia_vwap):.1f}% abaixo VWAP - Desconto!")
    
    # 7. Volume Climax (0-2 pontos)
    if volume_ratio > 200:
        score += 2
        sinais.append(f"✅ Volume Climax ({volume_ratio:.0f}%)")
    
    # 8. Bollinger Bands (0-2 pontos)
    distancia_bb = ((preco_atual - banda_inferior) / banda_inferior) * 100
    if distancia_bb < 2:
        score += 2
        sinais.append(f"✅ Tocando Banda Inferior")
    
    # 9. Padrões de Reversão (0-2 pontos)
    if df['engolfo_alta'].iloc[-1]:
        score += 2
        sinais_fortes.append("🚀 ENGOLFO DE ALTA!")
    if df['piercing_line'].iloc[-1]:
        score += 1
        sinais.append("✅ Piercing Line")
    
    # ===== CLASSIFICAÇÃO =====
    if score >= 12:
        classificacao = "🟢🟢 REVERSÃO CONFIRMADA - Entrada AGORA!"
        emoji = "🚀🚀🚀"
        acao = "COMPRAR"
    elif score >= 9:
        classificacao = "🟢 ALTA PROBABILIDADE - Aguardar 1-2 velas"
        emoji = "🚀🚀"
        acao = "PREPARAR"
    elif score >= 6:
        classificacao = "🟡 SINAIS MODERADOS - Observar de perto"
        emoji = "👀"
        acao = "OBSERVAR"
    elif score >= 3:
        classificacao = "⚪ SINAIS FRACOS - Aguardar mais"
        emoji = "⏰"
        acao = "AGUARDAR"
    else:
        classificacao = "🔴 SEM REVERSÃO - Não entrar"
        emoji = "❌"
        acao = "EVITAR"
    
    # ===== CONFLUÊNCIA (quantos indicadores concordam) =====
    oversold_count = sum([
        rsi_atual < 30,
        stoch_k_atual < 20,
        mfi_atual < 30,
        williams_r_atual < -80
    ])
    
    confluencia = f"{oversold_count}/4 indicadores em oversold"
    
    # ===== MENSAGEM =====
    mensagem = f"""
🔍 ANÁLISE AVANÇADA DE REVERSÃO - {simbolo}

{emoji} SCORE: {score}/15
{classificacao}

⚡ AÇÃO: {acao}
🎯 Confluência: {confluencia}

💰 PREÇO ATUAL: ${preco_atual:,.2f}

📊 INDICADORES PRINCIPAIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• RSI (14): {rsi_atual:.1f}
• Stoch RSI: K={stoch_k_atual:.1f} | D={stoch_d_atual:.1f}
• MFI: {mfi_atual:.1f}
• Williams %R: {williams_r_atual:.1f}

📈 MOMENTUM:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• MACD: {macd_atual:.2f}
• Signal: {macd_signal_atual:.2f}
• Histogram: {macd_hist_atual:.2f}

💹 VOLUME & PREÇO:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• Volume: {volume_ratio:.0f}% da média
• VWAP: ${vwap_atual:,.2f}
• Distância VWAP: {distancia_vwap:+.1f}%
"""
    
    if sinais_fortes:
        mensagem += "\n🔥 SINAIS FORTES:\n"
        for sinal in sinais_fortes:
            mensagem += f"{sinal}\n"
    
    if sinais:
        mensagem += "\n✅ SINAIS DETECTADOS:\n"
        for sinal in sinais:
            mensagem += f"{sinal}\n"
    
    # Recomendação detalhada
    mensagem += "\n💡 RECOMENDAÇÃO:\n"
    if score >= 12:
        mensagem += f"""
🟢 ENTRADA FORTE RECOMENDADA!
• Stop Loss: ${preco_atual * 0.97:.2f} (-3%)
• Alvo 1: ${vwap_atual:.2f} (VWAP)
• Alvo 2: ${df['ema_20'].iloc[-1]:.2f} (EMA 20)
• Risk/Reward: Excelente
"""
    elif score >= 9:
        mensagem += f"""
🟡 Aguardar 1-2 velas de confirmação
• Se engolfo aparecer → ENTRAR
• Se Stoch cruzar → ENTRAR
• Se MACD cruzar → ENTRAR
"""
    elif score >= 6:
        mensagem += """
👀 Observar próximas 2-4 horas
• Múltiplos sinais presentes
• Falta confirmação final
"""
    else:
        mensagem += """
⏰ Ainda não é o momento
• Aguardar mais indicadores alinharem
"""
    
    mensagem += f"\n\n#{simbolo.replace('USDT', '')} #Reversão #Indicadores"
    
    # Exibir
    print(mensagem)
    
    # Telegram
    print("\n📤 Enviando para Telegram...")
    telegram = get_telegram_client()
    if telegram:
        telegram.send(mensagem)
        print("✅ Análise enviada!")
    
    print("\n" + "=" * 70)
    return score, sinais_fortes

if __name__ == '__main__':
    simbolo = 'BTCUSDT'
    if len(sys.argv) > 1:
        moeda = sys.argv[1].upper()
        if not moeda.endswith('USDT'):
            moeda += 'USDT'
        simbolo = moeda
    
    try:
        analisar_reversao_avancada(simbolo)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
