"""
Ver resultados do Scanner de Moedas
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from scanner.symbols import SYMBOLS
from api.services.scanner_service import ScannerService
import time

print("🔍 SCANNER DE OPORTUNIDADES DE TRADING")
print("="*60)
print(f"📊 Monitorando {len(SYMBOLS)} moedas")
print("⏱️  Atualizando a cada 60 segundos...")
print("🎯 Pontuação: 0 (fraco) → 5 (forte)")
print("="*60)

scanner = ScannerService()
scanner.scan_limit = 20  # Primeiras 20 moedas para teste rápido

print("\n🔄 Executando varredura inicial (pode levar ~30 segundos)...\n")

scanner._scan_all_symbols_sync()

results = scanner.get_results()

if results:
    print(f"✅ Encontradas {len(results)} oportunidades!\n")
    print("="*80)
    print(f"{'#':<4} {'MOEDA':<12} {'SCORE':<8} {'PREÇO':<12} {'RSI':<8} {'TENDÊNCIA':<15}")
    print("="*80)
    
    for idx, r in enumerate(results[:10], 1):  # Top 10
        symbol = r['symbol']
        score = r['score']
        price = f"${r['price']:,.2f}"
        rsi = f"{r['rsi']:.1f}"
        trend = r['trend_status']
        
        # Emoji baseado no score
        emoji = "🔥" if score >= 4 else "✨" if score >= 3 else "📊"
        
        print(f"{idx:<4} {symbol:<12} {emoji} {score:<5} {price:<12} {rsi:<8} {trend:<15}")
    
    print("="*80)
    
    # Destacar as melhores oportunidades (score 4-5)
    top_signals = [r for r in results if r['score'] >= 4]
    if top_signals:
        print(f"\n🔥 MELHORES OPORTUNIDADES (Score ≥ 4):")
        for r in top_signals:
            print(f"   • {r['symbol']}: Score {r['score']} | Preço: ${r['price']:,.2f} | RSI: {r['rsi']:.1f}")
    
    print(f"\n💡 Para rodar o bot em uma moeda específica:")
    print(f"   python src/live_trading/...evaluator.py --cripto {results[0]['symbol']} --is_simulator")
    
else:
    print("❌ Nenhum resultado encontrado. Verifique a conexão com a Bybit.")

print("\n" + "="*60)
print("✅ Varredura concluída!")
print("="*60)
