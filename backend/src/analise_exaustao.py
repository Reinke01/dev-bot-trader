"""
Script para Análise de Indicadores de Exaustão
Detecta sinais de reversão e exaustão de movimento
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from corretoras.funcoes_bybit import busca_velas
from managers.data_manager import prepare_market_data
from indicadores.padroes_velas import engolfo_alta, engolfo_baixa, piercing_line_alta, harami_alta
from indicadores.bandas_bollinger import bandas_bollinger
from indicadores.indicadores_osciladores import calcula_rsi, encontra_topos_e_fundos
from utils.notifications.telegram_client import get_telegram_client
import pandas as pd

def analisar_exaustao(simbolo='BTCUSDT'):
    print(f"\n🔍 ANÁLISE DE EXAUSTÃO - {simbolo}")
    print("=" * 60)
    
    # Buscar dados
    df = busca_velas(simbolo, '60', [9, 21, 200])  # 1 hora
    df = prepare_market_data(df, use_emas=True, emas_periods=[20, 50, 200])
    
    # Calcular indicadores
    df['rsi'] = calcula_rsi(df, 14)
    df = bandas_bollinger(df, periodo=20, desvios=2)
    
    # Padrões de vela
    df['engolfo_alta'] = engolfo_alta(df)
    df['engolfo_baixa'] = engolfo_baixa(df)
    df['piercing_line'] = piercing_line_alta(df)
    df['harami_alta'] = harami_alta(df)
    
    # Dados atuais
    preco_atual = df['fechamento'].iloc[-1]
    rsi_atual = df['rsi'].iloc[-1]
    volume_atual = df['volume'].iloc[-1]
    volume_medio = df['volume'].rolling(20).mean().iloc[-1]
    volume_ratio = (volume_atual / volume_medio) * 100
    
    # Banda de Bollinger
    banda_superior = df['banda_superior'].iloc[-1]
    banda_inferior = df['banda_inferior'].iloc[-1]
    media_bb = df['media_movel'].iloc[-1]
    distancia_banda_inf = ((preco_atual - banda_inferior) / banda_inferior) * 100
    
    # EMAs (calcular manualmente)
    df['ema_20'] = df['fechamento'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['fechamento'].ewm(span=50, adjust=False).mean()
    df['ema_200'] = df['fechamento'].ewm(span=200, adjust=False).mean()
    
    ema_20 = df['ema_20'].iloc[-1]
    ema_50 = df['ema_50'].iloc[-1]
    ema_200 = df['ema_200'].iloc[-1]
    
    # Divergências RSI (últimas 10 velas)
    topos_max, _, fundos_min, _ = encontra_topos_e_fundos(df.tail(50), dinstance=5, prominence=0.5)
    
    # Score de exaustão (0-10)
    score_exaustao = 0
    sinais = []
    
    # 1. RSI Extremo
    if rsi_atual < 30:
        score_exaustao += 2
        sinais.append(f"✅ RSI Sobrevenda ({rsi_atual:.1f})")
        if rsi_atual < 25:
            score_exaustao += 1
            sinais.append(f"✅✅ RSI EXTREMO ({rsi_atual:.1f}) - Raro!")
    elif rsi_atual > 70:
        score_exaustao += 2
        sinais.append(f"⚠️ RSI Sobrecompra ({rsi_atual:.1f})")
    
    # 2. Volume Climax
    if volume_ratio > 200:
        score_exaustao += 2
        sinais.append(f"✅ Volume Climax ({volume_ratio:.0f}% da média)")
    elif volume_ratio > 150:
        score_exaustao += 1
        sinais.append(f"✅ Volume Elevado ({volume_ratio:.0f}%)")
    
    # 3. Bollinger Bands
    if distancia_banda_inf < 2:
        score_exaustao += 2
        sinais.append(f"✅ Tocando Banda Inferior ({distancia_banda_inf:.1f}%)")
    elif preco_atual < media_bb:
        score_exaustao += 1
        sinais.append(f"⚪ Abaixo da Média BB")
    
    # 4. Padrões de Reversão
    if df['engolfo_alta'].iloc[-1]:
        score_exaustao += 2
        sinais.append("✅✅ ENGOLFO DE ALTA detectado!")
    if df['piercing_line'].iloc[-1]:
        score_exaustao += 1
        sinais.append("✅ Piercing Line detectada")
    if df['harami_alta'].iloc[-1]:
        score_exaustao += 1
        sinais.append("✅ Harami de Alta detectada")
    
    # 5. Análise de Divergência RSI
    if len(fundos_min) >= 2:
        # Verificar se preço fez nova mínima mas RSI não
        ultimos_fundos = fundos_min[-2:]
        precos_fundos = df['minima'].iloc[ultimos_fundos]
        rsi_fundos = df['rsi'].iloc[ultimos_fundos]
        
        if len(precos_fundos) >= 2 and len(rsi_fundos) >= 2:
            if precos_fundos.iloc[-1] < precos_fundos.iloc[-2] and rsi_fundos.iloc[-1] > rsi_fundos.iloc[-2]:
                score_exaustao += 3
                sinais.append("✅✅✅ DIVERGÊNCIA ALTA RSI - Forte sinal!")
    
    # Classificação
    if score_exaustao >= 8:
        classificacao = "🟢 EXAUSTÃO CONFIRMADA - Alta probabilidade de reversão"
        emoji = "🚀"
    elif score_exaustao >= 5:
        classificacao = "🟡 SINAIS DE EXAUSTÃO - Possível reversão"
        emoji = "⚠️"
    elif score_exaustao >= 3:
        classificacao = "⚪ EXAUSTÃO FRACA - Aguardar confirmação"
        emoji = "👀"
    else:
        classificacao = "🔴 SEM SINAIS DE EXAUSTÃO"
        emoji = "❌"
    
    # Montar mensagem
    mensagem = f"""
🔍 ANÁLISE DE EXAUSTÃO - {simbolo}

{emoji} SCORE: {score_exaustao}/10
{classificacao}

💰 DADOS ATUAIS:
• Preço: ${preco_atual:,.2f}
• RSI (14): {rsi_atual:.1f}
• Volume: {volume_ratio:.0f}% da média

📊 BOLLINGER BANDS:
• Superior: ${banda_superior:,.2f}
• Média: ${media_bb:,.2f}
• Inferior: ${banda_inferior:,.2f}
• Distância da Inf: {distancia_banda_inf:.1f}%

📈 EMAs:
• EMA 20: ${ema_20:,.2f}
• EMA 50: ${ema_50:,.2f}
• EMA 200: ${ema_200:,.2f}

🎯 SINAIS DETECTADOS:
"""
    
    if sinais:
        for sinal in sinais:
            mensagem += f"\n{sinal}"
    else:
        mensagem += "\n❌ Nenhum sinal de exaustão detectado"
    
    mensagem += f"\n\n💡 RECOMENDAÇÃO:"
    
    if score_exaustao >= 8:
        mensagem += """
✅ FORTE probabilidade de reversão
✅ Considere entrada com stop apertado
✅ Aguarde confirmação em próximas velas
"""
    elif score_exaustao >= 5:
        mensagem += """
⚠️ Sinais presentes mas aguarde confirmação
⚠️ Observe próximas 2-4 velas
⚠️ Se engolfo/RSI subir → possível entrada
"""
    elif score_exaustao >= 3:
        mensagem += """
👀 Exaustão fraca - continue observando
👀 Aguarde mais sinais se acumularem
"""
    else:
        mensagem += """
❌ Sem sinais claros de exaustão
❌ Aguarde RSI < 30 ou padrões de reversão
"""
    
    mensagem += f"\n\n#{simbolo.replace('USDT', '')} #Exaustão #Reversão"
    
    # Exibir no terminal
    print(mensagem)
    
    # Enviar para Telegram
    print("\n📤 Enviando para Telegram...")
    telegram = get_telegram_client()
    if telegram:
        telegram.send(mensagem)
        print("✅ Análise enviada para o Telegram!")
    else:
        print("⚠️ Telegram não disponível")
    
    print("\n" + "=" * 60)
    
    return score_exaustao, sinais

if __name__ == '__main__':
    import sys
    
    simbolo = 'BTCUSDT'
    if len(sys.argv) > 1:
        moeda = sys.argv[1].upper()
        if not moeda.endswith('USDT'):
            moeda += 'USDT'
        simbolo = moeda
    
    try:
        analisar_exaustao(simbolo)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
