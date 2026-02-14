import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
from datetime import datetime
from managers.results_manager import ResultsManager
from entidades.estado_trade import EstadoDeTrade
from utils.utilidades import calcula_percentual_perda_na_compra, calcula_percentual_lucro_na_compra, verifica_dia_util
from corretoras.funcoes_bybit import carregar_dados_historicos

cliente = HTTP()

start = '2023-01-01'
# end = '2024-09-01'
end = datetime.now().strftime('%Y-%m-%d')

# variáveis para o trade
cripto = 'BTCUSDT'   # BTCUSDT   #XRPUSDT
tempo_grafico = '15' # 15
saldo = 1000
risco_retorno = 4.1    # 3.5 - 3.4
qtd_velas_stop = 17  # 16 - 18 
taxa_corretora = 0.055
alavancagem = 1
emas = [5, 15]
ema_rapida = emas[0]
ema_lenta = emas[1]
# setup = 'trade estruturado de risco/retorno com duas emas'
setup = f'EMAs {emas}, rrr {risco_retorno}, velas {qtd_velas_stop}'

pular_velas = 999

df = carregar_dados_historicos(cripto, tempo_grafico, emas, start, end, pular_velas)

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

print('Iniciando backtest...')
for i in range(pular_velas, len(df)):
    sub_df = df.iloc[:i]

    ano = sub_df.index[-1].year
    mes = sub_df.index[-1].month

    resultados.initialize_month(ano, mes)

    if estado_de_trade == EstadoDeTrade.COMPRADO:
        if sub_df['maxima'].iloc[-1] >= preco_alvo:
            estado_de_trade = EstadoDeTrade.DE_FORA
            preco_fechamento = sub_df['fechamento'].iloc[-1]
            percentual_ganho = calcula_percentual_lucro_na_compra(preco_entrada, preco_fechamento)
            resultados.update_on_gain(ano, mes, percentual_ganho)
            
        elif sub_df['minima'].iloc[-1] <= preco_stop:
            estado_de_trade = EstadoDeTrade.DE_FORA
            preco_fechamento = sub_df['fechamento'].iloc[-1]
            percentual_perda = calcula_percentual_perda_na_compra(preco_entrada, preco_fechamento)
            resultados.update_on_loss(ano, mes, percentual_perda)

    elif estado_de_trade == EstadoDeTrade.DE_FORA:
            # Lógica para buscar a vela referência
            fechamento_anterior = sub_df['fechamento'].iloc[-2]
            acima_ema_rapida = fechamento_anterior > sub_df[f'EMA_{ema_rapida}'].iloc[-2]
            acima_ema_lenta = fechamento_anterior > sub_df[f'EMA_{ema_lenta}'].iloc[-2]
            vela_referencia = acima_ema_rapida and acima_ema_lenta
            gatilho_operação = sub_df['maxima'].iloc[-1] > sub_df['maxima'].iloc[-2]
            
            # dia_util = verifica_dia_util(sub_df['tempo_abertura'].iloc[-1])
            
            # if vela_referencia and gatilho_operação and dia_util:
            if vela_referencia and gatilho_operação:
                preco_entrada = sub_df['fechamento'].iloc[-1]
                estado_de_trade = EstadoDeTrade.COMPRADO
                preco_stop = sub_df['minima'].iloc[-qtd_velas_stop : ].min()
                preco_alvo = ((preco_entrada - preco_stop) * risco_retorno) + preco_entrada   
                resultados.update_on_trade_open(ano, mes)

resultados.get_results()           
resultados.save_summarized_results_to_xlsx()