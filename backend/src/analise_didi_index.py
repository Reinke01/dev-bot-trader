"""
Análise com DIDI INDEX - Indicador Brasileiro
Detecta Agulhadas e Puntos para reversão
Criado por Odir "Didi" Aguiar
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from corretoras.funcoes_bybit import busca_velas
from managers.data_manager import prepare_market_data
from indicadores.padroes_velas import engolfo_alta, piercing_line_alta
from indicadores.indicadores_osciladores import calcula_rsi
from utils.notifications.telegram_client import get_telegram_client
import pandas as pd
import numpy as np

def calcular_didi_index(df):
    """
    Calcula o Didi Index
    Médias: 3, 8, 20 períodos
    """
    df['didi_curta'] = df['fechamento'].rolling(window=3).mean()  # Rápida
    df['didi_media'] = df['fechamento'].rolling(window=8).mean()  # Intermediária
    df['didi_longa'] = df['fechamento'].rolling(window=20).mean() # Lenta
    return df

def detectar_agulhada(df, tolerancia=0.005):
    """
    Detecta Agulhada (cruzamento das 3 médias)
    tolerancia: % de variação aceita para considerar "juntas"
    """
    agulhadas_compra = []
    agulhadas_venda = []
    
    for i in range(21, len(df)):
        curta = df['didi_curta'].iloc[i]
        media = df['didi_media'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        
        curta_ant = df['didi_curta'].iloc[i-1]
        media_ant = df['didi_media'].iloc[i-1]
        longa_ant = df['didi_longa'].iloc[i-1]
        
        # Verificar se as médias estão próximas (formando agulhada)
        max_val = max(curta, media, longa)
        min_val = min(curta, media, longa)
        spread = (max_val - min_val) / max_val
        
        if spread < tolerancia:  # Médias muito próximas
            # Verificar se houve cruzamento
            # Agulhada de COMPRA: médias cruzam para cima
            if (curta_ant < longa_ant and curta > longa):
                agulhadas_compra.append(i)
            # Agulhada de VENDA: médias cruzam para baixo
            elif (curta_ant > longa_ant and curta < longa):
                agulhadas_venda.append(i)
    
    return agulhadas_compra, agulhadas_venda

def detectar_punto(df):
    """
    Detecta Punto (ponto)
    Curta cruza Média, mas ainda longe da Longa
    """
    puntos_compra = []
    puntos_venda = []
    
    for i in range(2, len(df)):
        curta = df['didi_curta'].iloc[i]
        media = df['didi_media'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        
        curta_ant = df['didi_curta'].iloc[i-1]
        media_ant = df['didi_media'].iloc[i-1]
        
        # Punto de COMPRA: curta cruza média para cima
        if curta_ant <= media_ant and curta > media:
            # Mas ainda abaixo da longa (não é agulhada ainda)
            if curta < longa:
                puntos_compra.append(i)
        
        # Punto de VENDA: curta cruza média para baixo
        elif curta_ant >= media_ant and curta < media:
            # Mas ainda acima da longa
            if curta > longa:
                puntos_venda.append(i)
    
    return puntos_compra, puntos_venda

def calcular_separacao_medias(df):
    """
    Calcula separação entre médias (força da tendência)
    """
    separacao = []
    for i in range(len(df)):
        curta = df['didi_curta'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        
        if pd.notna(curta) and pd.notna(longa) and longa != 0:
            sep = ((curta - longa) / longa) * 100
            separacao.append(sep)
        else:
            separacao.append(0)
    
    df['didi_separacao'] = separacao
    return df

def analisar_didi_index(simbolo='BTCUSDT'):
    print(f"\n🇧🇷 ANÁLISE DIDI INDEX - {simbolo}")
    print("=" * 70)
    
    # Buscar dados
    df = busca_velas(simbolo, '60', [9, 21])  # 1 hora
    
    # Calcular Didi Index
    df = calcular_didi_index(df)
    df = calcular_separacao_medias(df)
    
    # Detectar sinais
    agulhadas_compra, agulhadas_venda = detectar_agulhada(df, tolerancia=0.01)
    puntos_compra, puntos_venda = detectar_punto(df)
    
    # RSI para complementar
    df['rsi'] = calcula_rsi(df, 14)
    
    # Padrões de vela
    df['engolfo_alta'] = engolfo_alta(df)
    df['piercing_line'] = piercing_line_alta(df)
    
    # Dados atuais
    preco_atual = df['fechamento'].iloc[-1]
    didi_curta = df['didi_curta'].iloc[-1]
    didi_media = df['didi_media'].iloc[-1]
    didi_longa = df['didi_longa'].iloc[-1]
    separacao_atual = df['didi_separacao'].iloc[-1]
    rsi_atual = df['rsi'].iloc[-1]
    
    # Verificar posição das médias
    if didi_curta > didi_media > didi_longa:
        ordem = "🟢 Alta (3 > 8 > 20)"
        tendencia = "ALTA"
    elif didi_curta < didi_media < didi_longa:
        ordem = "🔴 Baixa (3 < 8 < 20)"
        tendencia = "BAIXA"
    else:
        ordem = "🟡 Indefinida (cruzando)"
        tendencia = "LATERAL"
    
    # Verificar proximidade das médias
    max_media = max(didi_curta, didi_media, didi_longa)
    min_media = min(didi_curta, didi_media, didi_longa)
    spread = ((max_media - min_media) / max_media) * 100
    
    # SCORE (0-12)
    score = 0
    sinais = []
    sinais_fortes = []
    
    # 1. Agulhada detectada (0-5 pontos)
    if len(agulhadas_compra) > 0 and agulhadas_compra[-1] >= len(df) - 3:
        score += 5
        sinais_fortes.append("🚀🚀🚀 AGULHADA DE COMPRA DETECTADA!")
    
    if len(agulhadas_venda) > 0 and agulhadas_venda[-1] >= len(df) - 3:
        score -= 3
        sinais_fortes.append("⚠️ Agulhada de venda recente")
    
    # 2. Punto detectado (0-3 pontos)
    if len(puntos_compra) > 0 and puntos_compra[-1] >= len(df) - 5:
        score += 3
        sinais_fortes.append("🚀🚀 PUNTO DE COMPRA - Reversão iniciando!")
    
    if len(puntos_venda) > 0 and puntos_venda[-1] >= len(df) - 5:
        score -= 2
        sinais_fortes.append("⚠️ Punto de venda recente")
    
    # 3. Médias se aproximando (0-2 pontos)
    if spread < 1.0:
        score += 2
        sinais.append(f"✅ Médias MUITO próximas ({spread:.2f}%) - Agulhada pode formar!")
    elif spread < 2.0:
        score += 1
        sinais.append(f"✅ Médias se aproximando ({spread:.2f}%)")
    
    # 4. Separação favorável (0-2 pontos)
    if separacao_atual > 0 and separacao_atual < 2:
        score += 1
        sinais.append(f"✅ Separação baixa positiva ({separacao_atual:+.2f}%)")
    elif separacao_atual < 0 and separacao_atual > -5:
        score += 1
        sinais.append(f"✅ Oversold no Didi ({separacao_atual:+.2f}%)")
    
    # 5. RSI complementar (0-2 pontos)
    if rsi_atual < 30:
        score += 2
        sinais.append(f"✅ RSI Oversold ({rsi_atual:.1f})")
    
    # 6. Padrões de vela (0-2 pontos)
    if df['engolfo_alta'].iloc[-1]:
        score += 2
        sinais_fortes.append("🚀 ENGOLFO DE ALTA!")
    if df['piercing_line'].iloc[-1]:
        score += 1
        sinais.append("✅ Piercing Line")
    
    # Classificação
    if score >= 10:
        classificacao = "🟢🟢 SINAL FORTÍSSIMO - ENTRAR AGORA!"
        emoji = "🚀🚀🚀"
        acao = "COMPRAR"
    elif score >= 7:
        classificacao = "🟢 SINAL FORTE - Entrada Recomendada"
        emoji = "🚀🚀"
        acao = "PREPARAR"
    elif score >= 4:
        classificacao = "🟡 SINAL MODERADO - Observar"
        emoji = "👀"
        acao = "OBSERVAR"
    elif score >= 0:
        classificacao = "⚪ SINAL FRACO - Aguardar"
        emoji = "⏰"
        acao = "AGUARDAR"
    else:
        classificacao = "🔴 SINAL NEGATIVO - Não entrar"
        emoji = "❌"
        acao = "EVITAR"
    
    # Mensagem
    mensagem = f"""
🇧🇷 ANÁLISE DIDI INDEX - {simbolo}

{emoji} SCORE: {score}/12
{classificacao}

⚡ AÇÃO RECOMENDADA: {acao}

💰 PREÇO ATUAL: ${preco_atual:,.2f}

📊 DIDI INDEX (Médias Móveis):
━━━━━━━━━━━━━━━━━━━━━━━━━━
• Curta (3):  ${didi_curta:,.2f}
• Média (8):  ${didi_media:,.2f}
• Longa (20): ${didi_longa:,.2f}

📈 ANÁLISE:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ordem: {ordem}
• Tendência: {tendencia}
• Spread Médias: {spread:.2f}%
• Separação: {separacao_atual:+.2f}%
• RSI (14): {rsi_atual:.1f}

📍 SINAIS HISTÓRICOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• Agulhadas Compra: {len(agulhadas_compra)}
• Agulhadas Venda: {len(agulhadas_venda)}
• Puntos Compra: {len(puntos_compra)}
• Puntos Venda: {len(puntos_venda)}
"""
    
    if agulhadas_compra and len(agulhadas_compra) > 0:
        ultima_agulhada = len(df) - agulhadas_compra[-1]
        mensagem += f"\n🎯 Última Agulhada Compra: há {ultima_agulhada} velas"
    
    if puntos_compra and len(puntos_compra) > 0:
        ultimo_punto = len(df) - puntos_compra[-1]
        mensagem += f"\n🎯 Último Punto Compra: há {ultimo_punto} velas"
    
    if sinais_fortes:
        mensagem += "\n\n🔥 SINAIS FORTES:\n"
        for sinal in sinais_fortes:
            mensagem += f"{sinal}\n"
    
    if sinais:
        mensagem += "\n✅ SINAIS DETECTADOS:\n"
        for sinal in sinais:
            mensagem += f"{sinal}\n"
    
    # Recomendação
    mensagem += "\n💡 INTERPRETAÇÃO DIDI:\n"
    if score >= 10:
        mensagem += f"""
🟢 AGULHADA CONFIRMADA OU IMINENTE!
• Este é o sinal mais forte do Didi
• Reversão de tendência confirmada
• Stop: ${preco_atual * 0.97:.2f} (-3%)
• Alvo: ${didi_longa * 1.05:.2f} (EMA 20 + 5%)
"""
    elif score >= 7:
        mensagem += """
🟢 Punto detectado ou médias se aproximando
• Reversão em formação
• Aguardar 1-2 velas de confirmação
• Se agulhada formar → ENTRAR
"""
    elif score >= 4:
        mensagem += """
🟡 Sinais moderados presentes
• Médias começando a interagir
• Observar próximas 4-6 horas
• Aguardar punto ou agulhada
"""
    else:
        mensagem += """
⏰ Ainda não há setup Didi
• Médias muito separadas ou ordem errada
• Aguardar médias se aproximarem
"""
    
    mensagem += f"\n\n📚 Sobre o Didi Index:"
    mensagem += f"\nCriado pelo brasileiro Odir 'Didi' Aguiar"
    mensagem += f"\nUm dos indicadores mais confiáveis para reversão!"
    
    mensagem += f"\n\n#{simbolo.replace('USDT', '')} #DidiIndex #Brasil"
    
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
        analisar_didi_index(simbolo)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
