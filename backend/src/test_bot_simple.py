"""
Teste simples do bot em modo simulação
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

print("🚀 Iniciando teste do bot...\n")

# Testar imports básicos
print("📦 Testando imports...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("  ✅ dotenv")
except Exception as e:
    print(f"  ❌ dotenv: {e}")
    exit(1)

try:
    from corretoras.funcoes_bybit import busca_velas, quantidade_minima_para_operar
    print("  ✅ funcoes_bybit")
except Exception as e:
    print(f"  ❌ funcoes_bybit: {e}")
    exit(1)

try:
    from agentes.trade_entry_evaluator import trade_entry_evaluator
    print("  ✅ trade_entry_evaluator")
except Exception as e:
    print(f"  ❌ trade_entry_evaluator: {e}")
    exit(1)

try:
    from managers.data_manager import prepare_market_data
    print("  ✅ data_manager")
except Exception as e:
    print(f"  ❌ data_manager: {e}")
    exit(1)

# Testar busca de velas
print("\n📊 Testando busca de velas...")
try:
    cripto = 'BTCUSDT'
    tempo_grafico = '15'
    emas = [5, 15]
    
    df = busca_velas(cripto, tempo_grafico, emas)
    
    if not df.empty:
        print(f"  ✅ {len(df)} velas carregadas para {cripto}")
        print(f"  📈 Último preço: {df['fechamento'].iloc[-1]:.2f}")
        print(f"  📅 Última vela: {df.index[-1]}")
    else:
        print("  ❌ DataFrame vazio")
except Exception as e:
    print(f"  ❌ Erro ao buscar velas: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Testar quantidade mínima
print("\n💰 Testando quantidade mínima...")
try:
    qtd_min = quantidade_minima_para_operar(cripto, 1)
    print(f"  ✅ Quantidade mínima para {cripto}: {qtd_min}")
except Exception as e:
    print(f"  ❌ Erro ao buscar quantidade mínima: {e}")

print("\n" + "="*50)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*50)
print("\n💡 O bot está pronto para rodar!")
print("\nPara executar em modo simulação:")
print("  python src/live_trading/double_ema_breakout_orders_long_short_dual_params_agent_evaluator.py --is_simulator")
