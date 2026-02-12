import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()

import pandas as pd
import vectorbt as vbt
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout, CondicaoEntrada, StopConfig, AlvoConfig
from vectorbt_project.generator_vectorbt import gerar_por_nome
from corretoras.funcoes_bybit import carregar_dados_historicos

from datetime import datetime
import time
import os
from itertools import product
import psutil
import numpy as np

# Configurações gerais do grid (Bybit)
simbolo = 'SOLUSDT'
intervalo = '15'
data_inicio = '2023-01-01'
data_fim = datetime.now().strftime('%Y-%m-%d')

# Parâmetros do grid
grid_ema_curta = list(range(5, 50, 3))
grid_ema_longa = list(range(15, 151, 5))
grid_stop = list(range(12, 21, 1))
grid_rr = [round(x, 1) for x in list([1.5 + 0.1 * i for i in range(36)])]  # de 1.5 a 5.1 com passo de 0.1
# grid_ema_curta = [5]
# grid_ema_longa = [15]
# grid_stop = [17]
# grid_rr = [4.1]

# Carregar candles
df = carregar_dados_historicos(simbolo, intervalo, [9, 21], data_inicio, data_fim)
df.columns = df.columns.str.lower()

# Garantir pasta de resultados
os.makedirs("data/results", exist_ok=True)

# Executar todas as combinações
resultados = []

total = len([
    (c, l, s, r)
    for c, l, s, r in product(grid_ema_curta, grid_ema_longa, grid_stop, grid_rr)
    if l > c
])
print(f"Executando {total} combinações...")

testados = 0
start = time.time()

for ema_curta in grid_ema_curta:
    for ema_longa in grid_ema_longa:
        if ema_longa <= ema_curta:
            continue  # evita combinações incoerentes
        for stop in grid_stop:
            for rr in grid_rr:
                percent = (testados + 1) / total * 100
                testados += 1
                bar = '█' * int(percent / 2) + '-' * (50 - int(percent / 2))
                elapsed = time.time() - start
                tempo_medio = elapsed / testados
                estimado_restante = (total - testados) * tempo_medio
                estimado_str = f"{int(estimado_restante // 60)}m {int(estimado_restante % 60)}s"

                print(f"\r[{bar}] {percent:.2f}% - {testados+1}/{total} | "
                f"Decorrido: {int(elapsed // 60)}m {int(elapsed % 60)}s | "
                f"Estimado: {estimado_str} | "
                f"[RAM] {psutil.virtual_memory().percent}% usada", end='', flush=True)

                nome = f"ema_{ema_curta}_{ema_longa}_stop_{stop}_rr_{rr}"
                estrategia = DoubleEmaBreakout(
                    nome=nome,
                    tipo="short",
                    condicoes_entrada=[
                        CondicaoEntrada(tipo="fechamento_abaixo_ema", parametros={"periodo": ema_curta}),
                        CondicaoEntrada(tipo="fechamento_abaixo_ema", parametros={"periodo": ema_longa}),
                        CondicaoEntrada(tipo="rompe_minima_anterior", parametros={})
                    ],
                    stop=StopConfig(tipo="maxima_das_ultimas", parametros={"quantidade": stop}),
                    alvo=AlvoConfig(tipo="rr", parametros={"multiplicador": rr})
                )

                try:
                    entries, exits, _, _ = gerar_por_nome("double_ema_breakout_orders_short", df, estrategia)

                    size = pd.Series(0, index=df.index, dtype='float64')
                    size[entries.notna()] = 1.0  # Venda (1)
                    size[exits.notna()] = -1.0   # Compra (-1)
                    size = size.where(size != 0, np.nan)

                    order_price = entries.combine_first(exits)
                    
                    # Criar portfólio com sinais e preços de execução
                    pf = vbt.Portfolio.from_orders(
                        close=df['fechamento'],
                        price=order_price,
                        size_type='percent',
                        size=size,
                        init_cash=1000,
                        fees=0.00055,  # Taxa de corretagem
                        freq=f'{intervalo}min',  # Frequência de 15 minutos
                        direction='shortonly'
                    )
                    stats = pf.stats()

                    resultados.append({
                        "moeda": simbolo,
                        "intervalo": intervalo,
                        "periodo": f"{data_inicio} : {data_fim}",
                        "estrategia": nome,
                        "ema_curta": ema_curta,
                        "ema_longa": ema_longa,
                        "stop": stop,
                        "rr": rr,
                        "saldo_inicial": 1000,
                        "saldo_final": stats['End Value'],
                        "fitness": stats['Total Return [%]'] * (1 - stats['Max Drawdown [%]'] / 100),
                        "retorno_total": stats['Total Return [%]'],
                        "max_drawdown": stats['Max Drawdown [%]'],
                        "max_drawdown_duration": stats['Max Drawdown Duration'],
                        "trades": stats['Total Trades'],
                        "win_rate": stats['Win Rate [%]'],
                        "ganho_medio": stats['Avg Winning Trade [%]'],
                        "perda_media": stats['Avg Losing Trade [%]'],
                        'melhor_trade': stats['Best Trade [%]'],
                        'pior_trade': stats['Worst Trade [%]'],
                        "sharpe_ratio": stats['Sharpe Ratio'],
                        "sortino_ratio": stats['Sortino Ratio'],
                        "calmar_ratio": stats['Calmar Ratio'],
                    })

                except Exception as e:
                    print(f"Erro em {nome}: {e}")

# Criar subpastas de resultados, se ainda não existirem
os.makedirs("data/results/grids", exist_ok=True)
os.makedirs("data/results/tops", exist_ok=True)

# Salvar resultados por ordem de retorno_total e menor max_drawdown
df_resultados = pd.DataFrame(resultados).sort_values(by="fitness", ascending=False)

now = datetime.now().strftime("%Y%m%d_%H%M%S")
caminho_csv = f"data/results/grids/{now}_double_ema_breakout_orders_short_{simbolo}_{intervalo}_{data_inicio}_{data_fim}.csv"
df_resultados.to_csv(caminho_csv, index=False)

print(f"\n🏁 Grid search concluído:")
nro_resultados = 100
top_resultados = df_resultados.head(nro_resultados).sort_values(by="retorno_total", ascending=False)
print(top_resultados)

# Exportar top resultados como JSON
caminho_json = f"data/results/tops/{now}_top{nro_resultados}_double_ema_breakout_orders_short_{simbolo}_{intervalo}_{data_inicio}_{data_fim}.json"
top_resultados.to_json(caminho_json, orient="records", indent=4)

# Exibir resultados
print("\n✅ Execução concluída!")
print(f"\n📊 Resultados salvos em:")
print(f"   - CSV: {caminho_csv}")
print(f"   - JSON: {caminho_json}") 