import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()

import pandas as pd
import vectorbt as vbt
import numpy as np
from entidades.estrategias_descritivas.base import BaseEstrategiaDescritiva, CondicaoEntrada, StopConfig, AlvoConfig
from vectorbt_project.generator_vectorbt import gerar_por_nome
from corretoras.funcoes_bybit import carregar_dados_historicos

from datetime import datetime

# Imports dos novos módulos utilitários
from vectorbt_project.utils.reporting import gerar_relatorio_detalhado, exibir_resultados_salvamento, exibir_trades_resumo, formatar_parametros_bollinger
from vectorbt_project.utils.plotting import plotar_grafico_velas_plotly, plotar_performance_plotly
from vectorbt_project.utils.results_manager import gerar_dataframe_resultado_basico, salvar_resultados_completos, processar_periodo_dataframe

# Configurações
simbolo = 'BTCUSDT'
intervalo = '15'
data_inicio = '2025-06-01'
data_fim = datetime.now().strftime('%Y-%m-%d')

# Parâmetros da estratégia Bollinger Bands
periodo_bb = 20      # Período da média móvel das Bandas de Bollinger
desvios_bb = 3       # Número de desvios padrão
stop = 16            # Quantidade de velas para calcular o stop

def main():
    # Carregar dados
    df = carregar_dados_historicos(simbolo, intervalo, [9, 21], data_inicio, data_fim)
    df.columns = df.columns.str.lower()
    
    # Configurar estratégia
    nome = "Bollinger Bands Long"
    print(f"Executando a estratégia {nome} para {simbolo} com velas de {intervalo} minutos...")
    estrategia = BaseEstrategiaDescritiva(
        nome=nome,
        tipo="long",
        condicoes_entrada=[
            CondicaoEntrada(tipo="fffd_periodo", parametros={"periodo": periodo_bb}),
            CondicaoEntrada(tipo="fffd_desvios", parametros={"desvios": desvios_bb}),
            CondicaoEntrada(tipo="rompe_maxima_anterior", parametros={})
        ],
        stop=StopConfig(tipo="minima_das_ultimas", parametros={"quantidade": stop}),
        alvo=AlvoConfig(tipo="banda_superior", parametros={})
    )
    
    try:
        entries, exits, stop_price, target_price = gerar_por_nome("bollinger_bands_long", df, estrategia)
        
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
        parametros = formatar_parametros_bollinger(periodo_bb, desvios_bb, stop)
        
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
            strategy_name="bollinger_bands_long", 
            simbolo=simbolo, 
            intervalo=intervalo
        )
        fig_perf = plotar_performance_plotly(pf, entries[999:], exits[999:], "bollinger_bands_long")
        
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

if __name__ == "__main__":
    main() 