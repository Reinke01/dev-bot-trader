import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()

import vectorbt as vbt
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout, CondicaoEntrada, StopConfig, AlvoConfig
from vectorbt_project.generator_vectorbt import gerar_por_nome
from corretoras.funcoes_bybit import carregar_dados_historicos

from datetime import datetime

# Imports dos novos módulos utilitários
from vectorbt_project.utils.reporting import gerar_relatorio_detalhado, exibir_resultados_salvamento, exibir_trades_resumo, formatar_parametros_ema_simples
from vectorbt_project.utils.plotting import plotar_grafico_velas_plotly, plotar_performance_plotly
from vectorbt_project.utils.results_manager import gerar_dataframe_resultado_basico, salvar_resultados_completos, processar_periodo_dataframe

# Configurações gerais do grid (Bybit)
simbolo = 'BTCUSDT'
intervalo = '15'
data_inicio = '2025-07-01'
data_fim = datetime.now().strftime('%Y-%m-%d')

# Parâmetros do grid - possível separar a geração de combinações em utils/grid_generator.py
ema_curta = 9
ema_longa = 51
stop = 15
rr = 2.3

def main():
    # Carregar candles
    df = carregar_dados_historicos(simbolo, intervalo, [9, 21], data_inicio, data_fim)
    df.columns = df.columns.str.lower()

    # Garantir pasta de resultados
    os.makedirs("data/results", exist_ok=True)

    # Executar estratégia
    nome = f"Double Ema Breakout Signals"
    print(f"Executando a estratégia {nome} para {simbolo} com velas de {intervalo} minutos...")
    estrategia = DoubleEmaBreakout(
        nome=nome,
        tipo="long",
        condicoes_entrada=[
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": ema_curta}),
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": ema_longa}),
            CondicaoEntrada(tipo="rompe_maxima_anterior", parametros={})
        ],
        stop=StopConfig(tipo="minima_das_ultimas", parametros={"quantidade": stop}),
        alvo=AlvoConfig(tipo="rr", parametros={"multiplicador": rr})
    )

    try:
        entries, exits, stop_price, target_price = gerar_por_nome("double_ema_breakout_signals", df, estrategia)
        
        # Entradas e saídas no preço de fechamento da vela
        pf = vbt.Portfolio.from_signals(
            close=df['fechamento'][999:],
            entries=entries[999:],
            exits=exits[999:],
            init_cash=1000,
            size_type='percent',
            fees=0.00055,
            size=1.0,
            direction='longonly',
            # sl_stop=0.02,
            freq=f'{intervalo}min'
        )
        
        stats = pf.stats()
        
        # Preparar parâmetros da estratégia
        parametros = formatar_parametros_ema_simples(ema_curta, ema_longa, stop, rr)
        
        # Gerar DataFrame de resultado
        periodo = processar_periodo_dataframe(df, data_inicio)
        df_resultado = gerar_dataframe_resultado_basico(stats, parametros, simbolo, intervalo, periodo)
        
        # Salvar resultados
        caminhos = salvar_resultados_completos(df_resultado, nome, simbolo, intervalo, data_inicio, data_fim)
        
        # Gerar gráficos
        fig_plotly = plotar_grafico_velas_plotly(
            df=df[985:], 
            entries=entries[985:], 
            exits=exits[985:], 
            stop_price=stop_price[985:], 
            target_price=target_price[985:],
            strategy_name="double_ema_breakout_signals", 
            simbolo=simbolo, 
            intervalo=intervalo,
            ema_curta=ema_curta,
            ema_longa=ema_longa
        )
        fig_perf = plotar_performance_plotly(pf, entries[999:], exits[999:], "double_ema_breakout_signals")
        
        # Exibir resultados
        exibir_resultados_salvamento(caminhos)
        
        # Exibir relatório detalhado
        gerar_relatorio_detalhado(stats, nome, parametros)
        
        # Exibir trades
        exibir_trades_resumo(pf)

        # Mostrar gráficos
        fig = pf.plot(
            subplots=[
                'trades',         # Trades realizados
                'trade_pnl',      # PNL por trade
                'cum_returns',    # Retornos cumulativos
                'underwater',     # Underwater plot (tempo em drawdown)
                'drawdowns',      # Drawdowns
            ],
        )
        
        fig_plotly.show()
        fig_perf.show()
        fig.show()
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        raise
        
    #     # Gerar relatório detalhado
    #     gerar_relatorio_detalhado(stats)
        
    #     # Plotar resultados
    #     fig_matplotlib = plotar_resultados(pf, df, entries, exits, stop_price, target_price)
    #     fig_velas = plotar_grafico_velas_plotly(df, entries, exits, stop_price, target_price)
    #     fig_performance = plotar_performance_plotly(pf, entries, exits)
        
    #     # Mostrar gráficos
    #     plt.show()
    #     fig_velas.show()
    #     fig_performance.show()
        
    #     # Salvar resultados
    #     resultados = [{
    #         "moeda": simbolo,
    #         "intervalo": intervalo,
    #         "periodo": f"{data_inicio} : {df.index[-1]}",
    #         "ema_curta": ema_curta,
    #         "ema_longa": ema_longa,
    #         "stop": stop,
    #         "rr": rr,
    #         "retorno_total": stats['Total Return [%]'],
    #         "max_drawdown": stats['Max Drawdown [%]'],
    #         "trades": stats['Total Trades']
    #     }]
        
    #     # Criar subpastas de resultados
    #     os.makedirs("data/results/strategies/csv", exist_ok=True)
    #     os.makedirs("data/results/strategies/json", exist_ok=True)
        
    #     # Salvar resultados
    #     df_resultado = pd.DataFrame(resultados)
    #     now = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     caminho_csv = f"data/results/strategies/csv/double_ema_breakout_signals_{now}.csv"
    #     df_resultado.to_csv(caminho_csv, index=False)
        
    #     print(f"\n🏁 Teste concluído. Resultado salvo em {caminho_csv}")
    #     print(df_resultado)
        
    #     # Exportar como JSON
    #     df_resultado.to_json(f"data/results/strategies/json/double_ema_breakout_signals_{now}.json", orient="records", indent=4)
        
    #     # Validação dos resultados
    #     print(stats)
    #     print(pf.orders.records_readable)
    #     print(pf.trades.records_readable)
        
    # except Exception as e:
    #     print(f"Erro em {nome}: {e}")

if __name__ == "__main__":
    main()