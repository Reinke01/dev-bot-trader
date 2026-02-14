import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
from datetime import datetime
from managers.results_manager import ResultsManager
from entidades.estado_trade import EstadoDeTrade
from indicadores.indicadores_osciladores import calcula_rsi
from indicadores.padroes_velas import engolfo_alta, engolfo_baixa
from utils.utilidades import ajusta_start_time, calcula_percentual_perda_na_compra, calcula_percentual_lucro_na_compra
from corretoras.funcoes_bybit import carregar_dados_historicos

cliente = HTTP()

start = '2023-01-01'
# end = '2024-12-31'
end = datetime.now().strftime('%Y-%m-%d')

# variáveis para o trade
cripto = 'BTCUSDT'   # BTCUSDT   #XRPUSDT
tempo_grafico = '60' # 15
saldo = 1000
risco_retorno = 3.4    # 3.5 - 3.4
qtd_velas_stop = 17  # 16 - 18 
taxa_corretora = 0.055
alavancagem = 1
emas = [9, 21]
ema_rapida = emas[0]
ema_lenta = emas[1]
# setup = 'trade estruturado de risco/retorno com duas emas'
setup = f'Engolfos, rrr {risco_retorno}, velas {qtd_velas_stop}'

pular_velas = 999

df = carregar_dados_historicos(cripto, tempo_grafico, emas, start, end, pular_velas)

df['RSI'] =calcula_rsi(df) 
df['engolfo_alta'] = engolfo_alta(df)
df['engolfo_baixa'] = engolfo_baixa(df)

estado_de_trade = EstadoDeTrade.DE_FORA

preco_stop = 0
preco_alvo = 0
preco_entrada = 0

resultados = ResultsManager(
    saldo,
    taxa_corretora,
    setup,
    cripto,
    tempo_grafico,
    start,
    end,
    alavancagem
)

for i in range(pular_velas, len(df)):
    sub_df = df.iloc[:i]

    ano = sub_df.index[-1].year
    mes = sub_df.index[-1].month

    resultados.initialize_month(ano, mes)
        
    if estado_de_trade == EstadoDeTrade.COMPRADO:

        if sub_df['maxima'].iloc[-1] >= preco_alvo:
            estado_de_trade = EstadoDeTrade.DE_FORA
            percentual_ganho = calcula_percentual_lucro_na_compra(preco_entrada, preco_alvo)
            resultados.update_on_gain(ano, mes, percentual_ganho)
            
        elif sub_df['minima'].iloc[-1] <= preco_stop:
            estado_de_trade = EstadoDeTrade.DE_FORA
            percentual_perda = calcula_percentual_perda_na_compra(preco_entrada, preco_stop)
            resultados.update_on_loss(ano, mes, percentual_perda)

    # Lógica para buscar entrada nas operações, seja de compra ou de venda
    elif estado_de_trade == EstadoDeTrade.DE_FORA:

            if sub_df['engolfo_alta'].iloc[-2] == True:

                # IF - Lógica para buscar o gatílho de compra caso tenha encontrado a vela referência
                if sub_df['maxima'].iloc[-1] > sub_df['maxima'].iloc[-2]:
                    # Tirar comentários dos prints abaixo para visualizar os preços quando precisar testar
                    # print('comprou na máxima da vela na posição i', i)
                    preco_entrada = sub_df['maxima'].iloc[-2]
                    # print('preço de compra:', preco_entrada)
                    # print('comprou na vela que abriu em:', df['tempo_abertura'].iloc[i])
                    estado_de_trade = EstadoDeTrade.COMPRADO

                    # PARA TESTAR: mudar o i para i+1 para adicionar a vela gatilho na contagem
                    preco_stop = sub_df['minima'].iloc[-qtd_velas_stop : ].min()
                    # print('preço de stop:', preco_stop)
                    preco_alvo = ((preco_entrada - preco_stop) * risco_retorno) + preco_entrada   
                    # print('preço de alvo:', preco_alvo)
                    # print('---------------')
                    resultados.update_on_trade_open(ano, mes)

resultados.get_results()           
# resultados.save_summarized_results_to_xlsx()

# Lógica para buscar vendas
        # elif sub_df['fechamento'].iloc[-2] < sub_df['EMA_200'].iloc[-2]:

        #     if sub_df['fechamento'].iloc[-2] < sub_df['EMA_9'].iloc[-2] and sub_df['fechamento'].iloc[-2] < sub_df['EMA_21'].iloc[-2]:
