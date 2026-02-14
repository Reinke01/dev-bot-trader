"""
VARREDURA PROFISSIONAL
Sistema completo com todos os indicadores avançados
Score 0-100 profissional
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from indicadores.advanced_scoring import get_scoring_system
from utils.notifications.telegram_client import get_telegram_client
import time

# Lista expandida de moedas
MOEDAS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
    'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT',
    'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'ETCUSDT',
    'NEARUSDT', 'ARBUSDT', 'OPUSDT', 'APTUSDT', 'INJUSDT'
]

def varredura_profissional():
    print("\n" + "=" * 90)
    print("🎯 VARREDURA PROFISSIONAL - ANÁLISE MULTI-DIMENSIONAL")
    print("=" * 90)
    print(f"📊 Analisando {len(MOEDAS)} moedas com sistema avançado (0-100)...")
    print("📈 Market Trend | 🏗️ Structure | 📐 Fibonacci | 🎯 Wyckoff | 💎 Didi+BB\n")
    
    scoring_system = get_scoring_system()
    resultados = []
    
    for i, moeda in enumerate(MOEDAS, 1):
        print(f"⏳ [{i}/{len(MOEDAS)}] Analisando {moeda}...", end=' ', flush=True)
        
        try:
            analise = scoring_system.analyze_complete(moeda)
            
            if 'error' not in analise:
                resultados.append(analise)
                
                score = analise['score_final']
                emoji = analise['classification']['emoji']
                
                print(f"{emoji} {score:.1f}/100")
            else:
                print(f"❌ Erro: {analise['error']}")
        
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
        
        time.sleep(0.3)  # Rate limit
    
    # Ordenar por score
    resultados.sort(key=lambda x: x['score_final'], reverse=True)
    
    # ==========================
    # EXIBIR RESULTADOS
    # ==========================
    print("\n" + "=" * 90)
    print("🏆 RANKING - ANÁLISE PROFISSIONAL")
    print("=" * 90)
    print(f"{'#':<4} {'MOEDA':<12} {'SCORE':<12} {'NÍVEL':<18} {'SINAIS PRINCIPAIS':<40}")
    print("-" * 90)
    
    for i, r in enumerate(resultados[:15], 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else ""
        moeda_nome = r['simbolo'].replace('USDT', '')
        score = r['score_final']
        emoji = r['classification']['emoji']
        nivel = r['classification']['level']
        sinais = ", ".join(r['main_signals'][:2]) if r['main_signals'] else "Nenhum"
        
        print(f"{medal:<2}{i:<2} {moeda_nome:<12} {emoji} {score:<7.1f}  {nivel:<18} {sinais:<40}")
    
    # ==========================
    # TOP 3 DETALHADO
    # ==========================
    print("\n" + "=" * 90)
    print("💎 TOP 3 - ANÁLISE DETALHADA PROFISSIONAL")
    print("=" * 90)
    
    for i, r in enumerate(resultados[:3], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        moeda_nome = r['simbolo'].replace('USDT', '')
        
        print(f"\n{medal} {i}. {moeda_nome} - Score: {r['score_final']:.1f}/100")
        print(f"   {r['classification']['emoji']} {r['classification']['level']} - {r['classification']['description']}")
        print(f"   💰 Preço: ${r['price_current']:,.4f}")
        print(f"   📊 {r['recommendation']}")
        
        # Detalhes dos indicadores
        details = r['details']
        
        print(f"\n   📈 MARKET TREND:")
        print(f"      • Tendência: {details['market_trend']['trend']} (Confiança: {details['market_trend']['confidence']:.0f}%)")
        print(f"      • ADX: {details['market_trend']['adx']['value']:.1f} - {details['market_trend']['adx']['interpretation']}")
        print(f"      • Supertrend: {details['market_trend']['supertrend']['trend']}")
        
        print(f"\n   🏗️ STRUCTURE:")
        print(f"      • Tipo: {details['structure']['structure_type']}")
        print(f"      • {details['structure']['interpretation']}")
        if details['structure']['bos']['detected']:
            print(f"      • ⚡ BOS {details['structure']['bos']['type']} detectado!")
        if details['structure']['choch']['detected']:
            print(f"      • ⚡ ChoCH {details['structure']['choch']['type']} detectado!")
        
        print(f"\n   📐 FIBONACCI:")
        print(f"      • Movimento: {details['fibonacci']['last_move']}")
        print(f"      • {details['fibonacci']['interpretation']}")
        
        print(f"\n   🎯 WYCKOFF:")
        print(f"      • Fase: {details['wyckoff']['phase_description']}")
        if details['wyckoff']['spring']['detected']:
            print(f"      • 🚀 SPRING DETECTADO - {details['wyckoff']['spring']['signal']}")
        if details['wyckoff']['upthrust']['detected']:
            print(f"      • ⚠️ UPTHRUST DETECTADO - {details['wyckoff']['upthrust']['signal']}")
        
        if r['main_signals']:
            print(f"\n   ✅ SINAIS PRINCIPAIS:")
            for sinal in r['main_signals']:
                print(f"      • {sinal}")
    
    # ==========================
    # RECOMENDAÇÃO GERAL
    # ==========================
    print("\n" + "=" * 90)
    print("💡 ANÁLISE PROFISSIONAL - RECOMENDAÇÃO")
    print("=" * 90)
    
    melhor = resultados[0]
    moeda_melhor = melhor['simbolo'].replace('USDT', '')
    score_melhor = melhor['score_final']
    
    excelentes = [r for r in resultados if r['score_final'] >= 90]
    muito_bons = [r for r in resultados if 75 <= r['score_final'] < 90]
    bons = [r for r in resultados if 60 <= r['score_final'] < 75]
    
    print(f"\n📊 ESTATÍSTICAS DO MERCADO:")
    print(f"   • Setups EXCELENTES (90-100): {len(excelentes)}")
    print(f"   • Setups MUITO BONS (75-89): {len(muito_bons)}")
    print(f"   • Setups BONS (60-74): {len(bons)}")
    
    print(f"\n🎯 MELHOR OPORTUNIDADE: {moeda_melhor}")
    print(f"   {melhor['recommendation']}")
    
    if score_melhor >= 90:
        print(f"\n   💎 CONFLUÊNCIA PERFEITA!")
        print(f"   ✅ Todos os indicadores alinhados")
        print(f"   ✅ Alta probabilidade de sucesso")
        print(f"   ✅ ENTRADA FORTE RECOMENDADA")
    elif score_melhor >= 75:
        print(f"\n   🟢 SETUP FORTE!")
        print(f"   ✅ Múltiplos indicadores favoráveis")
        print(f"   ✅ Boa oportunidade de entrada")
    elif score_melhor >= 60:
        print(f"\n   🟡 SETUP MODERADO")
        print(f"   ⚠️ Aguardar confirmação adicional")
        print(f"   ⚠️ Entrada com cautela")
    else:
        print(f"\n   ⚪ MERCADO SEM SETUPS CLAROS")
        print(f"   ⏰ Aguardar melhores condições")
        print(f"   ⏰ Reavaliar em 4-6 horas")
    
    # ==========================
    # TELEGRAM
    # ==========================
    print("\n📤 Enviando para Telegram...")
    
    mensagem_telegram = f"""
🎯 VARREDURA PROFISSIONAL

🏆 TOP 3 SETUPS (Score 0-100):

"""
    
    for i, r in enumerate(resultados[:3], 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        moeda_nome = r['simbolo'].replace('USDT', '')
        
        mensagem_telegram += f"{medal} {moeda_nome}: {r['classification']['emoji']} {r['score_final']:.1f}/100\n"
        mensagem_telegram += f"   {r['classification']['level']}\n"
        mensagem_telegram += f"   {r['recommendation']}\n\n"
    
    mensagem_telegram += f"📊 Mercado:\n"
    mensagem_telegram += f"   • {len(excelentes)} Excelentes (90+)\n"
    mensagem_telegram += f"   • {len(muito_bons)} Muito Bons (75+)\n"
    mensagem_telegram += f"   • {len(bons)} Bons (60+)\n\n"
    
    mensagem_telegram += "#VarreduraProfissional #AnaliseTecnica"
    
    telegram = get_telegram_client()
    if telegram:
        telegram.send(mensagem_telegram)
        print("✅ Enviado para o Telegram!")
    
    print("\n" + "=" * 90)
    print("✅ VARREDURA PROFISSIONAL CONCLUÍDA!")
    print("=" * 90)
    
    return resultados

if __name__ == '__main__':
    try:
        varredura_profissional()
    except KeyboardInterrupt:
        print("\n\n⚠️ Varredura interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
