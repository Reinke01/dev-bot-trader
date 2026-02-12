import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()

import pandas as pd
import vectorbt as vbt
import numpy as np
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout, CondicaoEntrada, StopConfig, AlvoConfig
from vectorbt_project.generator_vectorbt import gerar_por_nome
from corretoras.funcoes_bybit import carregar_dados_historicos

from datetime import datetime
import os

# Imports dos novos módulos utilitários
from vectorbt_project.utils.reporting import gerar_relatorio_detalhado, exibir_resultados_salvamento, exibir_trades_resumo, formatar_parametros_ema_simples
from vectorbt_project.utils.plotting import plotar_grafico_velas_plotly, plotar_performance_plotly
from vectorbt_project.utils.results_manager import gerar_dataframe_resultado_basico, salvar_resultados_completos, processar_periodo_dataframe

# Configurações
simbolo = 'SOLUSDT'
intervalo = '15'
data_inicio = '2025-01-01'
data_fim = datetime.now().strftime('%Y-%m-%d')

# Parâmetros da estratégia
ema_curta = 5   # 5
ema_longa = 80   # 15
stop = 16        # 17
rr = 4.1         # 4.1

def main():
    # Carregar dados
    df = carregar_dados_historicos(simbolo, intervalo, [9, 21], data_inicio, data_fim)
    df.columns = df.columns.str.lower()
    
    # Configurar estratégia
    nome = "Double EMA Breakout Orders"
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
        entries, exits, stop_price, target_price = gerar_por_nome("double_ema_breakout_orders", df, estrategia)
        
        # Criar portfólio com ordens
        size = pd.Series(0, index=df.index, dtype='float64')
        size[entries.notna()] = 1.0  # Abre operação com 100% do capital disponível
        size[exits.notna()] = -1.0   # Fecha operação com 100% do capital utilizado na abertura
        size = size.where(size != 0, np.nan)
        
        order_price = entries.combine_first(exits)
        
        pf = vbt.Portfolio.from_orders(
            close=df['fechamento'][999:],
            price=order_price[999:],
            size_type='percent',
            size=size[999:],
            init_cash=1000,
            fees=0.00055,
            freq=f'{intervalo}min',
            direction='longonly'
        )
        
        # Gerar estatísticas
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
            strategy_name="double_ema_breakout_orders", 
            simbolo=simbolo, 
            intervalo=intervalo,
            ema_curta=ema_curta,
            ema_longa=ema_longa
        )
        fig_perf = plotar_performance_plotly(pf, entries[999:], exits[999:], "double_ema_breakout_orders")
        
        # Exibir resultados
        exibir_resultados_salvamento(caminhos)
        
        # Exibir relatório detalhado
        gerar_relatorio_detalhado(stats, nome, parametros)
        
        # Exibir trades
        exibir_trades_resumo(pf)

        # # Mostrar gráficos
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

if __name__ == "__main__":
    main()
