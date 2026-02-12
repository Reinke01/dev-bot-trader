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
from vectorbt_project.utils.reporting import gerar_relatorio_detalhado, exibir_resultados_salvamento, exibir_trades_resumo, formatar_parametros_ema_dual
from vectorbt_project.utils.plotting import plotar_grafico_velas_plotly, plotar_performance_plotly
from vectorbt_project.utils.results_manager import gerar_dataframe_resultado_basico, salvar_resultados_completos, processar_periodo_dataframe

# Configurações
simbolo = 'SOLUSDT' #'BTCUSDT'
intervalo = '15'
data_inicio = '2025-01-01'
data_fim = datetime.now().strftime('%Y-%m-%d')

# Parâmetros de compra da estratégia
ema_curta_long = 48
ema_longa_long = 161
stop_long = 18
rr_long = 1.7

# Parâmetros de venda da estratégia
ema_curta_short = 49
ema_longa_short = 140
stop_short = 20
rr_short = 2.0

def main():
    # Carregar dados
    df = carregar_dados_historicos(simbolo, intervalo, [9, 21], data_inicio, data_fim)
    df.columns = df.columns.str.lower()
    
    # Configurar estratégia
    nome = "Double EMA Breakout Orders Long/Short Params"
    print(f"Executando a estratégia {nome} para {simbolo} com velas de {intervalo} minutos...")
    estrategia = DoubleEmaBreakout(
        nome=nome,
        tipo="long_short",
        condicoes_entrada=[
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": ema_curta_long}),
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": ema_longa_long}),
            CondicaoEntrada(tipo="rompe_maxima_anterior", parametros={}),
            CondicaoEntrada(tipo="fechamento_abaixo_ema", parametros={"periodo": ema_curta_short}),
            CondicaoEntrada(tipo="fechamento_abaixo_ema", parametros={"periodo": ema_longa_short}),
            CondicaoEntrada(tipo="rompe_minima_anterior", parametros={})
        ],
        stop=StopConfig(tipo="minima_das_ultimas", parametros={"quantidade": [stop_long, stop_short]}),
        alvo=AlvoConfig(tipo="rr", parametros={"multiplicador": [rr_long, rr_short]})
    )
    
    try:
        # Gerar sinais usando a função específica para long/short
        entries, exits, stop_price, target_price, size = gerar_por_nome("double_ema_breakout_orders_long_short_dual_params", df, estrategia)
        
        # Criar portfólio com ordens
        order_price = entries.combine_first(exits)
        
        pf = vbt.Portfolio.from_orders(
            close=df['fechamento'][999:],
            price=order_price[999:],
            size_type='targetpercent',
            size=size[999:],
            init_cash=1000,
            fees=0.00055,
            freq=f'{intervalo}min',
            direction='both'  # Permitir posições long e short
        )
        
        # Gerar estatísticas
        stats = pf.stats()
        
        # Preparar parâmetros da estratégia
        parametros = formatar_parametros_ema_dual(ema_curta_long, ema_longa_long, stop_long, rr_long,
                                                ema_curta_short, ema_longa_short, stop_short, rr_short)
        
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
            strategy_name="double_ema_breakout_orders_long_short_dual_params", 
            simbolo=simbolo, 
            intervalo=intervalo,
            size=size[985:],
            ema_curta_long=ema_curta_long,
            ema_longa_long=ema_longa_long,
            ema_curta_short=ema_curta_short,
            ema_longa_short=ema_longa_short
        )
        fig_perf = plotar_performance_plotly(pf, entries[999:], exits[999:], "double_ema_breakout_orders_long_short_dual_params")
        
        # Exibir resultados
        exibir_resultados_salvamento(caminhos)
        
        # Exibir relatório detalhado
        gerar_relatorio_detalhado(stats, nome, parametros)
        
        # Exibir trades
        exibir_trades_resumo(pf)

        # Mostrar gráficos
        fig = pf.plot(
            subplots=[
                # ('fechamento', dict(
                #     title=f'Preço de {simbolo}',
                #     yaxis_kwargs=dict(
                #         title='Preço'
                #     )
                # )),
                # 'orders',         # Ordens executadas
                'trades',         # Trades realizados
                'trade_pnl',      # PNL por trade
                'cum_returns',    # Retornos cumulativos
                'underwater',     # Underwater plot (tempo em drawdown)
                'drawdowns',      # Drawdowns
                # 'value',          # Valor total do portfolio
                # 'asset_flow',     # Fluxo de ativos
                # 'asset_value',    # Valor do ativo
                # 'assets',         # Ativos
                # 'cash',           # Cash disponível
                # 'cash_flow',      # Fluxo de cash
                # 'gross_exposure', # Exposição bruta
                # 'net_exposure',   # Exposição líquida
            ],
            # width=None,             # Ajusta largura automaticamente
            # make_subplots_kwargs=dict(rows=10, cols=2),
            # template='plotly_dark',  # Tema escuro
        )

        # vbt.plotting.Scatter(
        #     data=df['fechamento'],
        #     x_labels=df.index,
        #     trace_names=['Preço'],
        #     trace_kwargs=dict(line=dict(color='blue')),
        #     add_trace_kwargs=dict(row=1,col=1),
        #     fig=fig
        # )
        
        fig_plotly.show()
        fig_perf.show()
        fig.show()
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {str(e)}")
        raise

if __name__ == "__main__":
    main() 