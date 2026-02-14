import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import os
import pandas as pd
from entidades.estrategias_descritivas.loader import carregar_classe_descritiva_por_nome
from vectorbt_project.generator_vectorbt import gerar_por_nome
from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()
import vectorbt as vbt

# Load candles (teste com Yahoo Finance)
df = vbt.YFData.download("BTC-USD", start="2025-02-10", interval="5m").get(['Open', 'High', 'Low', 'Close'])
df.columns = df.columns.str.lower()  # garantir compatibilidade com os nomes usados

# Caminho dos arquivos .json das estratégias
caminho = "configs/strategies/"
resultados = []

# Executar todas as estratégias
for arquivo in os.listdir(caminho):
    if not arquivo.endswith(".json"):
        continue

    nome = arquivo.replace(".json", "")
    print(f"\n▶️ Rodando estratégia: {nome}")

    try:
        ClasseDescritiva = carregar_classe_descritiva_por_nome(nome)
        estrategia = ClasseDescritiva.from_json(os.path.join(caminho, arquivo))
        entries, exits, stop_price, target_price = gerar_por_nome(nome, df, estrategia)
        pf = vbt.Portfolio.from_signals(df['close'], entries, exits)
        stats = pf.stats()

        resultados.append({
            "estrategia": nome,
            "retorno_total": stats['Total Return [%]'],
            "max_drawdown": stats['Max Drawdown [%]'],
            "trades": stats['Total Trades']
        })
    except Exception as e:
        print(f"❌ Erro ao rodar {nome}: {e}")

# Mostrar ranking
df_resultados = pd.DataFrame(resultados).sort_values(by="retorno_total", ascending=False)

for nome in df_resultados['estrategia']:
    # Reexecutar para obter os dados de entradas, saídas, stop e alvo
    estrategia = carregar_classe_descritiva_por_nome(nome).from_json(os.path.join(caminho, f"{nome}.json"))
    entries, exits, stop_price, target_price = gerar_por_nome(nome, df, estrategia)

    # Adicionar colunas ao DataFrame de resultados
    df_resultados[f'entries_{nome}'] = entries
    df_resultados[f'exits_{nome}'] = exits
    df_resultados[f'stop_{nome}'] = stop_price
    df_resultados[f'target_{nome}'] = target_price


print("\n🏁 Resultados ordenados por retorno total:\n")
print(df_resultados)

# (Opcional) Salvar CSV
os.makedirs("data/results", exist_ok=True)
df_resultados.to_csv("data/results/resumo_estrategias.csv", index=False)

# (Opcional) salvar por estratégia individual
# for row in resultados:
#     nome = row['estrategia']
#     path = f"data/resultados/{nome}_stats.json"
#     with open(path, 'w') as f:
#         json.dump(row, f, indent=4)