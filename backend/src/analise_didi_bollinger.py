"""
Análise COMPLETA: Didi Index + Bollinger Bands
A combinação brasileira com volatilidade!
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from corretoras.funcoes_bybit import busca_velas
from managers.data_manager import prepare_market_data
from indicadores.padroes_velas import engolfo_alta, piercing_line_alta
from indicadores.bandas_bollinger import bandas_bollinger
from indicadores.indicadores_osciladores import calcula_rsi
from utils.notifications.telegram_client import get_telegram_client
import pandas as pd
import numpy as np

def calcular_didi_index(df):
    """Calcula o Didi Index"""
    df['didi_curta'] = df['fechamento'].rolling(window=3).mean()
    df['didi_media'] = df['fechamento'].rolling(window=8).mean()
    df['didi_longa'] = df['fechamento'].rolling(window=20).mean()
    return df

def detectar_agulhada(df, tolerancia=0.01):
    """Detecta Agulhada"""
    agulhadas_compra = []
    agulhadas_venda = []
    
    for i in range(21, len(df)):
        curta = df['didi_curta'].iloc[i]
        media = df['didi_media'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        
        curta_ant = df['didi_curta'].iloc[i-1]
        longa_ant = df['didi_longa'].iloc[i-1]
        
        max_val = max(curta, media, longa)
        min_val = min(curta, media, longa)
        spread = (max_val - min_val) / max_val
        
        if spread < tolerancia:
            if (curta_ant < longa_ant and curta > longa):
                agulhadas_compra.append(i)
            elif (curta_ant > longa_ant and curta < longa):
                agulhadas_venda.append(i)
    
    return agulhadas_compra, agulhadas_venda

def detectar_punto(df):
    """Detecta Punto"""
    puntos_compra = []
    puntos_venda = []
    
    for i in range(2, len(df)):
        curta = df['didi_curta'].iloc[i]
        media = df['didi_media'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        
        curta_ant = df['didi_curta'].iloc[i-1]
        media_ant = df['didi_media'].iloc[i-1]
        
        if curta_ant <= media_ant and curta > media and curta < longa:
            puntos_compra.append(i)
        elif curta_ant >= media_ant and curta < media and curta > longa:
            puntos_venda.append(i)
    
    return puntos_compra, puntos_venda

def analisar_didi_bollinger(simbolo='BTCUSDT'):
    print(f"\n🇧🇷 ANÁLISE DIDI + BOLLINGER - {simbolo}")
    print("=" * 75)
    
    # Buscar dados
    df = busca_velas(simbolo, '60', [9, 21])  # 1 hora
    
    # ===== DIDI INDEX =====
    df = calcular_didi_index(df)
    agulhadas_compra, agulhadas_venda = detectar_agulhada(df)
    puntos_compra, puntos_venda = detectar_punto(df)
    
    # ===== BOLLINGER BANDS =====
    df = bandas_bollinger(df, periodo=20, desvios=2)
    
    # RSI
    df['rsi'] = calcula_rsi(df, 14)
    
    # Padrões
    df['engolfo_alta'] = engolfo_alta(df)
    df['piercing_line'] = piercing_line_alta(df)
    
    # ===== DADOS ATUAIS =====
    preco_atual = df['fechamento'].iloc[-1]
    
    # Didi
    didi_curta = df['didi_curta'].iloc[-1]
    didi_media = df['didi_media'].iloc[-1]
    didi_longa = df['didi_longa'].iloc[-1]
    max_didi = max(didi_curta, didi_media, didi_longa)
    min_didi = min(didi_curta, didi_media, didi_longa)
    spread_didi = ((max_didi - min_didi) / max_didi) * 100
    
    # Bollinger
    bb_superior = df['banda_superior'].iloc[-1]
    bb_inferior = df['banda_inferior'].iloc[-1]
    bb_media = df['media_movel'].iloc[-1]
    bb_largura = ((bb_superior - bb_inferior) / bb_media) * 100
    
    # Posição no Bollinger
    posicao_bb = ((preco_atual - bb_inferior) / (bb_superior - bb_inferior)) * 100
    distancia_inf = ((preco_atual - bb_inferior) / bb_inferior) * 100
    distancia_sup = ((bb_superior - preco_atual) / preco_atual) * 100
    
    # RSI
    rsi_atual = df['rsi'].iloc[-1]
    
    # Volume
    volume_atual = df['volume'].iloc[-1]
    volume_medio = df['volume'].rolling(20).mean().iloc[-1]
    volume_ratio = (volume_atual / volume_medio) * 100
    
    # ===== ANÁLISE DE CONFLUÊNCIA =====
    score = 0
    sinais = []
    sinais_fortes = []
    confluencias = []
    
    # 1. AGULHADA + BOLLINGER (0-6 pontos) ⭐⭐⭐
    if len(agulhadas_compra) > 0 and agulhadas_compra[-1] >= len(df) - 3:
        score += 4
        sinais_fortes.append("🚀🚀🚀 AGULHADA DE COMPRA!")
        
        # Se agulhada + banda inferior = SUPER SINAL!
        if distancia_inf < 3:
            score += 2
            confluencias.append("⚡⚡ CONFLUÊNCIA MÁXIMA: Agulhada + Banda Inferior!")
    
    # 2. PUNTO + BOLLINGER (0-4 pontos) ⭐⭐
    if len(puntos_compra) > 0 and puntos_compra[-1] >= len(df) - 5:
        score += 2
        sinais_fortes.append("🚀 PUNTO DE COMPRA!")
        
        if distancia_inf < 5:
            score += 2
            confluencias.append("⚡ CONFLUÊNCIA: Punto + Próximo Banda Inferior!")
    
    # 3. BOLLINGER SQUEEZE + DIDI CONVERGINDO (0-3 pontos) ⭐
    if bb_largura < 8:  # Squeeze
        score += 1
        sinais.append(f"✅ Bollinger Squeeze ({bb_largura:.1f}%) - Explosão próxima!")
        
        if spread_didi < 3:  # Médias convergindo
            score += 2
            confluencias.append("⚡ Squeeze + Médias Convergindo = Setup Perfeito!")
    
    # 4. PREÇO NA BANDA INFERIOR (0-3 pontos)
    if posicao_bb < 20:  # Nos 20% inferiores
        score += 2
        sinais.append(f"✅ Preço na zona baixa BB ({posicao_bb:.0f}%)")
        
        if distancia_inf < 2:
            score += 1
            sinais_fortes.append("🔥 TOCANDO BANDA INFERIOR!")
    
    # 5. DIDI MÉDIAS PRÓXIMAS (0-2 pontos)
    if spread_didi < 2:
        score += 2
        sinais.append(f"✅ Médias Didi MUITO próximas ({spread_didi:.1f}%)")
    elif spread_didi < 5:
        score += 1
        sinais.append(f"✅ Médias Didi se aproximando ({spread_didi:.1f}%)")
    
    # 6. RSI EXTREMO (0-2 pontos)
    if rsi_atual < 30:
        score += 2
        sinais.append(f"✅ RSI Oversold ({rsi_atual:.1f})")
    
    # 7. VOLUME (0-2 pontos)
    if volume_ratio > 150:
        score += 2
        sinais.append(f"✅ Volume elevado ({volume_ratio:.0f}%)")
    
    # 8. PADRÕES DE VELA (0-2 pontos)
    if df['engolfo_alta'].iloc[-1]:
        score += 2
        sinais_fortes.append("🚀 ENGOLFO DE ALTA!")
    if df['piercing_line'].iloc[-1]:
        score += 1
        sinais.append("✅ Piercing Line")
    
    # ===== CLASSIFICAÇÃO =====
    if score >= 15:
        classificacao = "🟢🟢🟢 SETUP PERFEITO - COMPRAR AGORA!"
        emoji = "💎💎💎"
        acao = "COMPRAR!"
    elif score >= 12:
        classificacao = "🟢🟢 SETUP EXCELENTE - Alta Probabilidade"
        emoji = "💎💎"
        acao = "PREPARAR"
    elif score >= 9:
        classificacao = "🟢 SETUP BOM - Entrada Viável"
        emoji = "💎"
        acao = "OBSERVAR"
    elif score >= 6:
        classificacao = "🟡 SETUP MODERADO - Aguardar Confirmação"
        emoji = "👀"
        acao = "AGUARDAR"
    elif score >= 3:
        classificacao = "⚪ SETUP FRACO - Poucos Sinais"
        emoji = "⏰"
        acao = "ESPERAR"
    else:
        classificacao = "🔴 SEM SETUP - Não Entrar"
        emoji = "❌"
        acao = "EVITAR"
    
    # Tendência Didi
    if didi_curta > didi_media > didi_longa:
        tendencia_didi = "🟢 Alta"
    elif didi_curta < didi_media < didi_longa:
        tendencia_didi = "🔴 Baixa"
    else:
        tendencia_didi = "🟡 Indefinida"
    
    # ===== MENSAGEM =====
    mensagem = f"""
🇧🇷 DIDI + BOLLINGER - {simbolo}

{emoji} SCORE: {score}/20
{classificacao}

⚡ AÇÃO: {acao}

💰 PREÇO ATUAL: ${preco_atual:,.2f}

═══════════════════════════════════════
📊 DIDI INDEX (3, 8, 20):
═══════════════════════════════════════
• Curta (3):  ${didi_curta:,.2f}
• Média (8):  ${didi_media:,.2f}
• Longa (20): ${didi_longa:,.2f}

• Tendência: {tendencia_didi}
• Spread: {spread_didi:.2f}%
• Última Agulhada Compra: {len(df) - agulhadas_compra[-1] if agulhadas_compra else 'N/A'} velas
• Último Punto Compra: {len(df) - puntos_compra[-1] if puntos_compra else 'N/A'} velas

═══════════════════════════════════════
📈 BOLLINGER BANDS (20, 2):
═══════════════════════════════════════
• Superior: ${bb_superior:,.2f}
• Média:    ${bb_media:,.2f}
• Inferior: ${bb_inferior:,.2f}

• Largura BB: {bb_largura:.1f}%
• Posição: {posicao_bb:.0f}% (0=inf, 100=sup)
• Distância Inf: +{distancia_inf:.1f}%
• Distância Sup: +{distancia_sup:.1f}%

═══════════════════════════════════════
📊 OUTROS INDICADORES:
═══════════════════════════════════════
• RSI (14): {rsi_atual:.1f}
• Volume: {volume_ratio:.0f}% da média
"""
    
    if confluencias:
        mensagem += "\n⚡ CONFLUÊNCIAS DETECTADAS:\n"
        for conf in confluencias:
            mensagem += f"{conf}\n"
    
    if sinais_fortes:
        mensagem += "\n🔥 SINAIS FORTES:\n"
        for sinal in sinais_fortes:
            mensagem += f"{sinal}\n"
    
    if sinais:
        mensagem += "\n✅ SINAIS:\n"
        for sinal in sinais:
            mensagem += f"{sinal}\n"
    
    # Recomendação
    mensagem += "\n💡 INTERPRETAÇÃO:\n"
    
    if score >= 15:
        mensagem += f"""
💎 SETUP PERFEITO!
• Didi + Bollinger totalmente alinhados
• Múltiplas confluências
• Stop: ${preco_atual * 0.97:.2f} (-3%)
• Alvo 1: ${bb_media:.2f} (Média BB)
• Alvo 2: ${bb_superior:.2f} (Banda Superior)
• Risk/Reward: Excelente!
"""
    elif score >= 12:
        mensagem += """
💎 Setup muito forte!
• Maioria dos indicadores alinhados
• Alta probabilidade de reversão
• Aguardar 1-2 velas de confirmação
"""
    elif score >= 9:
        mensagem += """
🟢 Setup favorável
• Bons sinais presentes
• Entrada viável com stop apertado
• Observar volume e padrões
"""
    elif score >= 6:
        mensagem += """
🟡 Setup em formação
• Alguns sinais presentes
• Falta confirmação final
• Observar próximas 2-4 horas
"""
    else:
        mensagem += """
⏰ Setup ainda não formado
• Poucos sinais alinhados
• Aguardar mais confluências
• Reavaliar em 4-6 horas
"""
    
    mensagem += f"\n\n#{simbolo.replace('USDT', '')} #DidiIndex #BollingerBands #Brasil"
    
    # Exibir
    print(mensagem)
    
    # Telegram
    print("\n📤 Enviando para Telegram...")
    telegram = get_telegram_client()
    if telegram:
        telegram.send(mensagem)
        print("✅ Análise enviada!")
    
    print("\n" + "=" * 75)
    
    return score, confluencias

if __name__ == '__main__':
    simbolo = 'BTCUSDT'
    if len(sys.argv) > 1:
        moeda = sys.argv[1].upper()
        if not moeda.endswith('USDT'):
            moeda += 'USDT'
        simbolo = moeda
    
    try:
        analisar_didi_bollinger(simbolo)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
