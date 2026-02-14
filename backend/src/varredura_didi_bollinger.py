"""
VARREDURA DIDI + BOLLINGER
Analisa múltiplas moedas e ranqueia por score
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from corretoras.funcoes_bybit import busca_velas
from indicadores.padroes_velas import engolfo_alta, piercing_line_alta
from indicadores.bandas_bollinger import bandas_bollinger
from indicadores.indicadores_osciladores import calcula_rsi
from utils.notifications.telegram_client import get_telegram_client
import pandas as pd
import time

# Lista de moedas para analisar
MOEDAS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT',
    'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'ETCUSDT',
    'NEARUSDT', 'ARBUSDT', 'OPUSDT', 'APTUSDT', 'INJUSDT'
]

def calcular_didi_index(df):
    df['didi_curta'] = df['fechamento'].rolling(window=3).mean()
    df['didi_media'] = df['fechamento'].rolling(window=8).mean()
    df['didi_longa'] = df['fechamento'].rolling(window=20).mean()
    return df

def detectar_agulhada(df, tolerancia=0.01):
    agulhadas_compra = []
    for i in range(21, len(df)):
        curta = df['didi_curta'].iloc[i]
        media = df['didi_media'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        curta_ant = df['didi_curta'].iloc[i-1]
        longa_ant = df['didi_longa'].iloc[i-1]
        
        max_val = max(curta, media, longa)
        min_val = min(curta, media, longa)
        spread = (max_val - min_val) / max_val
        
        if spread < tolerancia and curta_ant < longa_ant and curta > longa:
            agulhadas_compra.append(i)
    
    return agulhadas_compra

def detectar_punto(df):
    puntos_compra = []
    for i in range(2, len(df)):
        curta = df['didi_curta'].iloc[i]
        media = df['didi_media'].iloc[i]
        longa = df['didi_longa'].iloc[i]
        curta_ant = df['didi_curta'].iloc[i-1]
        media_ant = df['didi_media'].iloc[i-1]
        
        if curta_ant <= media_ant and curta > media and curta < longa:
            puntos_compra.append(i)
    
    return puntos_compra

def analisar_moeda(simbolo):
    """Analisa uma moeda e retorna score + dados"""
    try:
        # Buscar dados
        df = busca_velas(simbolo, '60', [9, 21])
        
        # Didi
        df = calcular_didi_index(df)
        agulhadas_compra = detectar_agulhada(df)
        puntos_compra = detectar_punto(df)
        
        # Bollinger
        df = bandas_bollinger(df, periodo=20, desvios=2)
        
        # RSI
        df['rsi'] = calcula_rsi(df, 14)
        
        # Padrões
        df['engolfo_alta'] = engolfo_alta(df)
        df['piercing_line'] = piercing_line_alta(df)
        
        # Dados atuais
        preco_atual = df['fechamento'].iloc[-1]
        didi_curta = df['didi_curta'].iloc[-1]
        didi_media = df['didi_media'].iloc[-1]
        didi_longa = df['didi_longa'].iloc[-1]
        
        max_didi = max(didi_curta, didi_media, didi_longa)
        min_didi = min(didi_curta, didi_media, didi_longa)
        spread_didi = ((max_didi - min_didi) / max_didi) * 100
        
        bb_superior = df['banda_superior'].iloc[-1]
        bb_inferior = df['banda_inferior'].iloc[-1]
        bb_media = df['media_movel'].iloc[-1]
        bb_largura = ((bb_superior - bb_inferior) / bb_media) * 100
        
        posicao_bb = ((preco_atual - bb_inferior) / (bb_superior - bb_inferior)) * 100
        distancia_inf = ((preco_atual - bb_inferior) / bb_inferior) * 100
        
        rsi_atual = df['rsi'].iloc[-1]
        volume_atual = df['volume'].iloc[-1]
        volume_medio = df['volume'].rolling(20).mean().iloc[-1]
        volume_ratio = (volume_atual / volume_medio) * 100
        
        # Calcular score
        score = 0
        sinais = []
        
        # Agulhada
        if len(agulhadas_compra) > 0 and agulhadas_compra[-1] >= len(df) - 3:
            score += 4
            sinais.append("Agulhada")
            if distancia_inf < 3:
                score += 2
                sinais.append("Agulhada+BB_Inf")
        
        # Punto
        if len(puntos_compra) > 0 and puntos_compra[-1] >= len(df) - 5:
            score += 2
            sinais.append("Punto")
            if distancia_inf < 5:
                score += 2
                sinais.append("Punto+BB_Inf")
        
        # Squeeze
        if bb_largura < 8:
            score += 1
            sinais.append("Squeeze")
            if spread_didi < 3:
                score += 2
                sinais.append("Squeeze+Didi")
        
        # Banda inferior
        if posicao_bb < 20:
            score += 2
            sinais.append("BB_Baixo")
            if distancia_inf < 2:
                score += 1
                sinais.append("Tocando_BB_Inf")
        
        # Médias próximas
        if spread_didi < 2:
            score += 2
            sinais.append("Didi_Convergindo")
        elif spread_didi < 5:
            score += 1
        
        # RSI
        if rsi_atual < 30:
            score += 2
            sinais.append("RSI_Oversold")
        
        # Volume
        if volume_ratio > 150:
            score += 2
            sinais.append("Volume_Alto")
        
        # Padrões
        if df['engolfo_alta'].iloc[-1]:
            score += 2
            sinais.append("Engolfo")
        if df['piercing_line'].iloc[-1]:
            score += 1
            sinais.append("Piercing")
        
        return {
            'simbolo': simbolo,
            'score': score,
            'preco': preco_atual,
            'rsi': rsi_atual,
            'spread_didi': spread_didi,
            'posicao_bb': posicao_bb,
            'distancia_inf': distancia_inf,
            'bb_largura': bb_largura,
            'volume_ratio': volume_ratio,
            'sinais': sinais,
            'agulhadas': len(agulhadas_compra),
            'puntos': len(puntos_compra),
            'ultimo_punto': len(df) - puntos_compra[-1] if puntos_compra else None
        }
        
    except Exception as e:
        print(f"⚠️ Erro ao analisar {simbolo}: {e}")
        return None

def varredura_completa():
    print("\n🔍 VARREDURA DIDI + BOLLINGER")
    print("=" * 80)
    print(f"📊 Analisando {len(MOEDAS)} moedas...\n")
    
    resultados = []
    
    for i, moeda in enumerate(MOEDAS, 1):
        print(f"⏳ [{i}/{len(MOEDAS)}] Analisando {moeda}...", end=' ')
        resultado = analisar_moeda(moeda)
        
        if resultado:
            resultados.append(resultado)
            emoji = "🟢" if resultado['score'] >= 12 else "🟡" if resultado['score'] >= 6 else "⚪"
            print(f"{emoji} Score: {resultado['score']}/20")
        else:
            print("❌ Erro")
        
        time.sleep(0.5)  # Evitar rate limit
    
    # Ordenar por score
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    # Exibir resultados
    print("\n" + "=" * 80)
    print("🏆 RANKING - MELHORES SETUPS")
    print("=" * 80)
    print(f"{'#':<4} {'MOEDA':<12} {'SCORE':<8} {'RSI':<8} {'BB%':<8} {'SINAIS':<30}")
    print("-" * 80)
    
    for i, r in enumerate(resultados[:10], 1):
        emoji = "🟢🟢" if r['score'] >= 15 else "🟢" if r['score'] >= 12 else "🟡" if r['score'] >= 6 else "⚪"
        moeda_nome = r['simbolo'].replace('USDT', '')
        sinais_str = ", ".join(r['sinais'][:3]) if r['sinais'] else "Nenhum"
        
        print(f"{i:<4} {moeda_nome:<12} {emoji} {r['score']}/20  "
              f"RSI:{r['rsi']:<6.1f} BB:{r['posicao_bb']:<5.0f}%  {sinais_str}")
    
    # Top 3 detalhado
    print("\n" + "=" * 80)
    print("🥇 TOP 3 - ANÁLISE DETALHADA")
    print("=" * 80)
    
    for i, r in enumerate(resultados[:3], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        moeda_nome = r['simbolo'].replace('USDT', '')
        
        print(f"\n{medal} {i}. {moeda_nome} - Score: {r['score']}/20")
        print(f"   💰 Preço: ${r['preco']:,.4f}")
        print(f"   📊 RSI: {r['rsi']:.1f}")
        print(f"   📈 Didi Spread: {r['spread_didi']:.1f}%")
        print(f"   📊 Posição BB: {r['posicao_bb']:.0f}% | Dist Inf: {r['distancia_inf']:.1f}%")
        print(f"   📏 Largura BB: {r['bb_largura']:.1f}%")
        print(f"   📊 Volume: {r['volume_ratio']:.0f}%")
        
        if r['sinais']:
            print(f"   ✅ Sinais: {', '.join(r['sinais'])}")
        
        if r['ultimo_punto']:
            print(f"   🎯 Último Punto: há {r['ultimo_punto']} velas")
    
    # Recomendação
    print("\n" + "=" * 80)
    print("💡 RECOMENDAÇÃO")
    print("=" * 80)
    
    melhor = resultados[0]
    moeda_melhor = melhor['simbolo'].replace('USDT', '')
    
    if melhor['score'] >= 15:
        print(f"\n🟢🟢 EXCELENTE! {moeda_melhor} tem SETUP PERFEITO!")
        print(f"   Score {melhor['score']}/20 indica alta probabilidade de reversão")
        print(f"   Considere entrada imediata com stop em ${melhor['preco'] * 0.97:.2f}")
    elif melhor['score'] >= 12:
        print(f"\n🟢 MUITO BOM! {moeda_melhor} tem SETUP FORTE!")
        print(f"   Score {melhor['score']}/20 é favorável")
        print(f"   Aguarde 1-2 velas de confirmação antes de entrar")
    elif melhor['score'] >= 9:
        print(f"\n🟡 BOM! {moeda_melhor} tem SETUP MODERADO")
        print(f"   Score {melhor['score']}/20 indica possibilidade")
        print(f"   Entre apenas com stop apertado")
    elif melhor['score'] >= 6:
        print(f"\n🟡 {moeda_melhor} lidera mas setup ainda é fraco")
        print(f"   Score {melhor['score']}/20 precisa melhorar")
        print(f"   Aguarde mais sinais se acumularem")
    else:
        print(f"\n⚪ ATENÇÃO! Mesmo o melhor ({moeda_melhor}) tem score baixo")
        print(f"   Score {melhor['score']}/20 indica mercado sem setup claro")
        print(f"   Recomendado: AGUARDAR mercado melhorar")
    
    # Enviar para Telegram
    mensagem_telegram = f"""
🔍 VARREDURA DIDI + BOLLINGER

🏆 TOP 3 SETUPS:

"""
    
    for i, r in enumerate(resultados[:3], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        moeda_nome = r['simbolo'].replace('USDT', '')
        emoji = "🟢🟢" if r['score'] >= 15 else "🟢" if r['score'] >= 12 else "🟡" if r['score'] >= 6 else "⚪"
        
        mensagem_telegram += f"{medal} {moeda_nome}: {emoji} {r['score']}/20\n"
        mensagem_telegram += f"   RSI:{r['rsi']:.1f} | BB:{r['posicao_bb']:.0f}% | Vol:{r['volume_ratio']:.0f}%\n"
        if r['sinais']:
            mensagem_telegram += f"   {', '.join(r['sinais'][:3])}\n"
        mensagem_telegram += "\n"
    
    if melhor['score'] >= 12:
        mensagem_telegram += f"💡 {moeda_melhor} recomendado para entrada!\n"
    else:
        mensagem_telegram += "💡 Aguardar melhores setups\n"
    
    mensagem_telegram += "\n#Varredura #DidiIndex #BollingerBands"
    
    # Enviar
    print("\n📤 Enviando para Telegram...")
    telegram = get_telegram_client()
    if telegram:
        telegram.send(mensagem_telegram)
        print("✅ Varredura enviada para o Telegram!")
    
    print("\n" + "=" * 80)
    print("✅ Varredura completa!")
    print("=" * 80)
    
    return resultados

if __name__ == '__main__':
    try:
        varredura_completa()
    except KeyboardInterrupt:
        print("\n\n⚠️ Varredura interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
