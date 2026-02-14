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
from utils.utilidades import ajusta_start_time, calcula_percentual_perda_na_compra, calcula_percentual_lucro_na_compra, calcula_percentual_perda_na_venda, calcula_percentual_lucro_na_venda
from corretoras.funcoes_bybit import carregar_dados_historicos

cliente = HTTP()

start = '2023-01-01'
# end = '2024-12-31'
end = datetime.now().strftime('%Y-%m-%d')

# variáveis para o trade
cripto = 'BTCUSDT'   # BTCUSDT   #XRPUSDT
tempo_grafico = '15' # 15
saldo = 1000
risco_retorno = 4.5    # 3.5 - 3.4
qtd_velas_stop = 25  # 16 - 18 
taxa_corretora = 0.055
alavancagem = 1
emas = [5, 15]
ema_rapida = emas[0]
ema_lenta = emas[1]
ema_conducao = 200

# setup = 'trade estruturado de risco/retorno com duas emas'
setup = f'EMAs {emas}, condução {ema_conducao}, rrr {risco_retorno}, velas {qtd_velas_stop}'

pular_velas = 999

df = carregar_dados_historicos(cripto, tempo_grafico, emas, start, end, pular_velas)

df[f'EMA_{ema_conducao}'] = df['fechamento'].ewm(span=ema_conducao, adjust=False).mean()
df['RSI'] = calcula_rsi(df)

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

        # condição para avaliar fechamento abaixo da ema de condução; fechou abaixo e fechou o trade imediatamente
        elif sub_df['fechamento'].iloc[-1] < sub_df[f'EMA_{ema_conducao}'].iloc[-1]:
            if sub_df['fechamento'].iloc[-1] > preco_entrada:
                estado_de_trade = EstadoDeTrade.DE_FORA
                percentual_ganho = calcula_percentual_lucro_na_compra(preco_entrada, sub_df['fechamento'].iloc[-1])
                resultados.update_on_gain(ano, mes, percentual_ganho)
            elif sub_df['fechamento'].iloc[-1] < preco_entrada:
                estado_de_trade = EstadoDeTrade.DE_FORA
                percentual_perda = calcula_percentual_perda_na_compra(preco_entrada, sub_df['fechamento'].iloc[-1])
                resultados.update_on_loss(ano, mes, percentual_perda)

        # condição para avaliar fechamento abaixo da ema de condução; fechou abaixo e perdeu a mínima da vela que fechou abaixo
        # elif (sub_df['fechamento'].iloc[-2] < sub_df[f'EMA_{ema_conducao}'].iloc[-2] 
        #         and sub_df['minima'].iloc[-1] < sub_df['minima'].iloc[-2]):
        #     if sub_df['minima'].iloc[-2] > preco_entrada:
        #         estado_de_trade = EstadoDeTrade.DE_FORA
        #         percentual_ganho = calcula_percentual_lucro_na_compra(preco_entrada, sub_df['minima'].iloc[-2])
        #         resultados.update_on_gain(ano, mes, percentual_ganho)
        #     elif sub_df['minima'].iloc[-2] < preco_entrada:
        #         estado_de_trade = EstadoDeTrade.DE_FORA
        #         percentual_perda = calcula_percentual_perda_na_compra(preco_entrada, sub_df['minima'].iloc[-2])
        #         resultados.update_on_loss(ano, mes, percentual_perda)

    elif estado_de_trade == EstadoDeTrade.VENDIDO:
        if sub_df['minima'].iloc[-1] <= preco_alvo:
            estado_de_trade = EstadoDeTrade.DE_FORA
            percentual_ganho = calcula_percentual_lucro_na_venda(preco_entrada, preco_alvo)
            resultados.update_on_gain(ano, mes, percentual_ganho)
            
        elif sub_df['maxima'].iloc[-1] >= preco_stop:
            estado_de_trade = EstadoDeTrade.DE_FORA
            percentual_perda = calcula_percentual_perda_na_venda(preco_entrada, preco_stop)
            resultados.update_on_loss(ano, mes, percentual_perda)

        # condição para avaliar fechamento acima da ema de condução; fechou acima e fechou o trade imediatamente
        elif sub_df['fechamento'].iloc[-1] > sub_df[f'EMA_{ema_conducao}'].iloc[-1]:
            if sub_df['fechamento'].iloc[-1] < preco_entrada:
                estado_de_trade = EstadoDeTrade.DE_FORA
                percentual_ganho = calcula_percentual_lucro_na_venda(preco_entrada, sub_df['fechamento'].iloc[-1])
                resultados.update_on_gain(ano, mes, percentual_ganho)
            elif sub_df['fechamento'].iloc[-1] > preco_entrada:
                estado_de_trade = EstadoDeTrade.DE_FORA
                percentual_perda = calcula_percentual_perda_na_venda(preco_entrada, sub_df['fechamento'].iloc[-1])
                resultados.update_on_loss(ano, mes, percentual_perda)

        # condição para avaliar fechamento acima da ema de condução; fechou acima e superou a máxima da vela que fechou acima
        # elif (sub_df['fechamento'].iloc[-2] > sub_df[f'EMA_{ema_conducao}'].iloc[-2] 
        #         and sub_df['maxima'].iloc[-1] > sub_df['maxima'].iloc[-2]):
        #     if sub_df['maxima'].iloc[-2] < preco_entrada:
        #         estado_de_trade = EstadoDeTrade.DE_FORA
        #         percentual_ganho = calcula_percentual_lucro_na_venda(preco_entrada, sub_df['maxima'].iloc[-2])
        #         resultados.update_on_gain(ano, mes, percentual_ganho)
        #     elif sub_df['maxima'].iloc[-2] > preco_entrada:
        #         estado_de_trade = EstadoDeTrade.DE_FORA
        #         percentual_perda = calcula_percentual_perda_na_venda(preco_entrada, sub_df['maxima'].iloc[-2])
        #         resultados.update_on_loss(ano, mes, percentual_perda)

    elif estado_de_trade == EstadoDeTrade.DE_FORA:
        # condições de compra
        if sub_df['fechamento'].iloc[-2] > sub_df[f'EMA_{ema_conducao}'].iloc[-2]:
            if sub_df['fechamento'].iloc[-2] > sub_df[f'EMA_{ema_rapida}'].iloc[-2] and sub_df['fechamento'].iloc[-2] > sub_df[f'EMA_{ema_lenta}'].iloc[-2]:
                if sub_df['maxima'].iloc[-1] > sub_df['maxima'].iloc[-2]:
                    preco_entrada = sub_df['maxima'].iloc[-2]
                    estado_de_trade = EstadoDeTrade.COMPRADO
                    preco_stop = sub_df['minima'].iloc[-qtd_velas_stop : ].min()
                    preco_alvo = ((preco_entrada - preco_stop) * risco_retorno) + preco_entrada   
                    resultados.update_on_trade_open(ano, mes)

        # condições de venda
        elif sub_df['fechamento'].iloc[-2] < sub_df[f'EMA_{ema_conducao}'].iloc[-2]:
            if sub_df['fechamento'].iloc[-2] < sub_df[f'EMA_{ema_rapida}'].iloc[-2] and sub_df['fechamento'].iloc[-2] < sub_df[f'EMA_{ema_lenta}'].iloc[-2]:
                if sub_df['minima'].iloc[-1] < sub_df['minima'].iloc[-2]:
                    estado_de_trade = EstadoDeTrade.VENDIDO
                    preco_entrada = sub_df['minima'].iloc[-2]
                    preco_stop = sub_df['maxima'].iloc[-qtd_velas_stop : ].max()
                    preco_alvo = preco_entrada - ((preco_stop - preco_entrada) * risco_retorno)   
                    resultados.update_on_trade_open(ano, mes)

resultados.get_results()           
resultados.save_summarized_results_to_xlsx()