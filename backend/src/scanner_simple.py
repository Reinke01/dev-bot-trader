"""
Scanner Simplificado - Buscar melhores moedas
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv
load_dotenv()

from corretoras.funcoes_bybit import cliente
import pandas as pd
import pandas_ta as ta
from scanner.symbols import SYMBOLS

print("🔍 SCANNER DE OPORTUNIDADES")
print("="*60)
print("📊 Analisando Top 30 moedas...")
print("="*60 + "\n")

results = []

# Analisar as top 30 moedas por volume
symbols_to_scan = SYMBOLS[:30]

for i, symbol in enumerate(symbols_to_scan, 1):
    try:
        print(f"⏳ [{i}/30] Analisando {symbol}...", end='\r')
        
        # Buscar dados de velas
        resp = cliente.get_kline(
            category="linear",
            symbol=symbol,
            interval="60",  # 1 hora
            limit=200
        )
        
        if not resp or 'result' not in resp:
            continue
            
        klines = resp['result']['list'][::-1]
        if not klines:
            continue
            
        df = pd.DataFrame(klines, columns=['ts', 'open', 'high', 'low', 'close', 'vol', 'turnover'])
        df[['open', 'high', 'low', 'close', 'vol']] = df[['open', 'high', 'low', 'close', 'vol']].astype(float)
        
        # Calcular indicadores
        ema20 = ta.ema(df['close'], length=20)
        ema50 = ta.ema(df['close'], length=50)
        ema200 = ta.ema(df['close'], length=200)
        rsi = ta.rsi(df['close'], length=14)
        
        last_close = df['close'].iloc[-1]
        last_vol = df['vol'].iloc[-1]
        avg_vol = df['vol'].tail(20).mean()
        last_rsi = rsi.iloc[-1]
        
        # Sistema de pontuação (0-5)
        score = 0
        
        # 1. Preço acima da EMA 200 (tendência de alta)
        if last_close > ema200.iloc[-1]:
            score += 1
            
        # 2. EMA 20 acima da EMA 50 (força de curto prazo)
        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 1
            
        # 3. RSI em zona neutra (45-65) - não sobrecomprado/vendido
        if 45 <= last_rsi <= 65:
            score += 1
            
        # 4. Volume acima da média (interesse crescente)
        if last_vol > (avg_vol * 1.2):
            score += 1
            
        # 5. Breakout de alta recente
        prev_high = df['high'].iloc[-2]
        if last_close > prev_high:
            score += 1
        
        # Determinar tendência
        if last_close > ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
            trend = "Alta Forte 🟢"
        elif last_close > ema20.iloc[-1] > ema50.iloc[-1]:
            trend = "Alta 🟢"
        elif last_close < ema20.iloc[-1] < ema50.iloc[-1] < ema200.iloc[-1]:
            trend = "Baixa Forte 🔴"
        elif last_close < ema20.iloc[-1] < ema50.iloc[-1]:
            trend = "Baixa 🔴"
        else:
            trend = "Lateral ⚪"
        
        results.append({
            'symbol': symbol,
            'score': score,
            'price': last_close,
            'rsi': last_rsi,
            'trend': trend,
            'volume_ratio': last_vol / avg_vol
        })
        
    except Exception as e:
        # print(f"\n⚠️ Erro ao analisar {symbol}: {e}")
        continue

print(" " * 80)  # Limpar linha

# Ordenar por score (maior primeiro)
results.sort(key=lambda x: x['score'], reverse=True)

if results:
    print(f"\n✅ {len(results)} moedas analisadas!\n")
    print("="*90)
    print(f"{'#':<4} {'MOEDA':<12} {'SCORE':<10} {'PREÇO':<15} {'RSI':<10} {'TENDÊNCIA':<20}")
    print("="*90)
    
    for idx, r in enumerate(results[:15], 1):  # Top 15
        symbol = r['symbol']
        score = r['score']
        price = f"${r['price']:,.4f}" if r['price'] < 1 else f"${r['price']:,.2f}"
        rsi = f"{r['rsi']:.1f}"
        trend = r['trend']
        
        # Emoji baseado no score
        if score >= 4:
            emoji = "🔥"
        elif score >= 3:
            emoji = "✨"
        else:
            emoji = "📊"
        
        print(f"{idx:<4} {symbol:<12} {emoji} {score:<7} {price:<15} {rsi:<10} {trend:<20}")
    
    print("="*90)
    
    # Destacar as melhores oportunidades
    top_signals = [r for r in results if r['score'] >= 4]
    if top_signals:
        print(f"\n🔥 MELHORES OPORTUNIDADES (Score ≥ 4):\n")
        for r in top_signals:
            print(f"   💎 {r['symbol']:<12} Score: {r['score']}/5 | Preço: ${r['price']:,.2f} | RSI: {r['rsi']:.1f} | {r['trend']}")
    
    print(f"\n\n💡 Para rodar o bot na melhor moeda:")
    best = results[0]
    print(f"   python src/live_trading/double_ema_breakout_orders_long_short_dual_params_agent_evaluator.py --cripto {best['symbol']} --is_simulator")
    
else:
    print("❌ Nenhum resultado encontrado.")

print("\n" + "="*90)
print("✅ Scan completo!")
print("="*90)
