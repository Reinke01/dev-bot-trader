from pybit.unified_trading import HTTP
from entidades.estado_trade import EstadoDeTrade
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
from utils.utilidades import ajusta_start_time
from utils.data_loader import obter_caminho_velas, carregar_velas_json, salvar_velas_json

load_dotenv()

API_KEY = os.getenv('BYBIT_API_KEY')
API_SECRET = os.getenv('BYBIT_API_SECRET')

API_KEY2 = os.getenv('BYBIT_API_KEY2')
API_SECRET2 = os.getenv('BYBIT_API_SECRET2')

API_KEY3 = os.getenv('BYBIT_API_KEY3')
API_SECRET3 = os.getenv('BYBIT_API_SECRET3')

API_KEY4 = os.getenv('BYBIT_API_KEY4')
API_SECRET4 = os.getenv('BYBIT_API_SECRET4')

API_KEY5 = os.getenv('BYBIT_API_KEY5')
API_SECRET5 = os.getenv('BYBIT_API_SECRET5')

cliente = HTTP()
cliente1 = HTTP(api_key=API_KEY, api_secret=API_SECRET, recv_window=50000)
cliente2 = HTTP(api_key=API_KEY2, api_secret=API_SECRET2, recv_window=50000)
cliente3 = HTTP(api_key=API_KEY3, api_secret=API_SECRET3, recv_window=50000)
cliente4 = HTTP(api_key=API_KEY4, api_secret=API_SECRET4, recv_window=50000)
cliente5 = HTTP(api_key=API_KEY5, api_secret=API_SECRET5, recv_window=50000)

def busca_cliente(nro_subconta):
    if nro_subconta == 1:
        return cliente1
    elif nro_subconta == 2:
        return cliente2
    elif nro_subconta == 3:
        return cliente3
    elif nro_subconta == 4:
        return cliente4
    elif nro_subconta == 5:
        return cliente5

def carregar_dados_historicos(cripto, tempo_grafico, emas, start, end, pular_velas=999, remove_velas=True):
    print('Carregando dados históricos...')
    start_ajustado = ajusta_start_time(start, tempo_grafico, pular_velas)
    start_timestamp = int(pd.to_datetime(start_ajustado).timestamp() * 1000)
    end_timestamp =  int(pd.to_datetime(end).timestamp() * 1000)
    
    caminho_arquivo = obter_caminho_velas(cripto, tempo_grafico, start, end)
    velas_sem_estrutura = carregar_velas_json(caminho_arquivo)

    if velas_sem_estrutura is None:
        velas_sem_estrutura = []

        while start_timestamp < end_timestamp:
            resposta = cliente.get_kline(symbol=cripto, interval=tempo_grafico, limit=1000, start=start_timestamp)
            velas_sem_estrutura += resposta['result']['list'][::-1]
            start_timestamp = int(velas_sem_estrutura[-1][0]) + 1000

        # Remove as velas com a data maior ou igual ao end_timestamp
        if remove_velas:
            while velas_sem_estrutura and int(velas_sem_estrutura[-1][0]) >= end_timestamp:
                velas_sem_estrutura.pop()

        salvar_velas_json(caminho_arquivo, velas_sem_estrutura)
        print(f'Velas salvas no arquivo: {caminho_arquivo}')
    else:
        print(f'Velas carregadas do arquivo: {caminho_arquivo}')

    colunas = ['tempo_abertura', 'abertura', 'maxima', 'minima', 'fechamento', 'volume', 'turnover']

    df = pd.DataFrame(velas_sem_estrutura, columns=colunas)

    df['tempo_abertura'] = pd.to_datetime(df['tempo_abertura'].astype(np.int64), unit='ms')
    df.set_index('tempo_abertura', inplace=True)
    df['abertura'] = df['abertura'].astype(float)
    df['maxima'] = df['maxima'].astype(float)
    df['minima'] = df['minima'].astype(float)
    df['fechamento'] = df['fechamento'].astype(float)
    df['volume'] = df['volume'].astype(float)

    ema_rapida = emas[0]
    ema_lenta = emas[1]
    df[f'EMA_{ema_rapida}'] = df['fechamento'].ewm(span=ema_rapida, adjust=False).mean()
    df[f'EMA_{ema_lenta}'] = df['fechamento'].ewm(span=ema_lenta, adjust=False).mean() 

    return df

def busca_velas(cripto, tempo_grafico, emas):
    # Busca as velas sem estrutura da corretora e inverte a lista
    resposta = cliente.get_kline(symbol=cripto, interval=tempo_grafico, limit=1000)
    velas_sem_estrutura = resposta['result']['list'][::-1]
    
    # Cria um DataFrame com as velas
    colunas = ['tempo_abertura', 'abertura', 'maxima', 'minima', 'fechamento', 'volume', 'turnover']
    df = pd.DataFrame(velas_sem_estrutura, columns=colunas)

    # Ajustar os tipos de dados e criar novas colunas para as EMAS
    df['tempo_abertura'] = pd.to_datetime(df['tempo_abertura'].astype(np.int64), unit='ms')
    df.set_index('tempo_abertura', inplace=True)
    df['abertura'] = df['abertura'].astype(float)
    df['maxima'] = df['maxima'].astype(float)
    df['minima'] = df['minima'].astype(float)
    df['fechamento'] = df['fechamento'].astype(float)
    df['volume'] = df['volume'].astype(float)
    ema_rapida = emas[0]
    ema_lenta = emas[1]
    df[f'EMA_{ema_rapida}'] = df['fechamento'].ewm(span=ema_rapida, adjust=False).mean()
    df[f'EMA_{ema_lenta}'] = df['fechamento'].ewm(span=ema_lenta, adjust=False).mean()

    return df

def tem_trade_aberto(cripto, nro_subconta):
    resposta = busca_cliente(nro_subconta).get_positions(category='linear', symbol=cripto)
    dados = resposta['result']['list'][0]

    preco_entrada = dados['avgPrice']
    if preco_entrada == '':
        preco_entrada = 0
    else:
        preco_entrada = float(preco_entrada)
    
    tamanho_posicao = dados['size']
    if tamanho_posicao == '':
        tamanho_posicao = 0
    else:
        tamanho_posicao = float(tamanho_posicao)

    preco_stop = dados['stopLoss']
    if preco_stop == '':
        preco_stop = 0
    else:
        preco_stop = float(preco_stop)

    preco_alvo = dados['takeProfit']
    if preco_alvo == '':
        preco_alvo = 0
    else:
        preco_alvo = float(preco_alvo)

    trailing_stop = dados['trailingStop']
    if trailing_stop == '':
        trailing_stop = 0
    else:
        trailing_stop = float(trailing_stop)

    estado_de_trade = dados['side']
    if estado_de_trade == '':
        estado_de_trade = EstadoDeTrade.DE_FORA
    elif estado_de_trade == 'Buy':
        estado_de_trade = EstadoDeTrade.COMPRADO
    elif estado_de_trade == 'Sell':
        estado_de_trade = EstadoDeTrade.VENDIDO

    return estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop

def saldo_da_conta(nro_subconta):
    resposta = busca_cliente(nro_subconta).get_wallet_balance(accountType='UNIFIED', coin='USDT')
    resultado = resposta['result']['list'][0]
    
    for campo in ['totalAvailableBalance', 'totalMarginBalance', 'totalEquity']:
        try:
            valor = resultado[campo]
            if valor and valor != '':
                return float(valor)
        except (ValueError, KeyError, TypeError):
            continue
    
    return 0.0

def quantidade_minima_para_operar(cripto, nro_subconta):
    resposta = busca_cliente(nro_subconta).get_instruments_info(category='linear', symbol=cripto)
    quantidade_minima_para_operar = resposta['result']['list'][0]['lotSizeFilter']['minOrderQty']
    if quantidade_minima_para_operar == '':
        quantidade_minima_para_operar = 0
    else:
        quantidade_minima_para_operar = float(quantidade_minima_para_operar)
    return quantidade_minima_para_operar

def abre_compra(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Buy',
        orderType='Market',
        qty=qtd_cripto_para_operar,
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

def abre_venda(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Sell',
        orderType='Market',
        qty=qtd_cripto_para_operar,
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# TODO: VALIDAR AS FUNÇÕES ABAIXO COM TESTES NO LIVE_TRADING
# Para fechar posição sem alvo definido, geralmente por condução de trade
def fecha_compra(cripto, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Sell',
        orderType='Market',
        qty='0',
        reduceOnly=True,
        closeOnTrigger=True
    )

# Para fechar posição sem alvo definido, geralmente por condução de trade
def fecha_venda(cripto, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Buy',
        orderType='Market',
        qty='0',
        reduceOnly=True,
        closeOnTrigger=True
    )

# Para abrir posição de compra abaixo do preço atual
def abre_compra_limit(cripto, preco, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Buy',
        orderType='Limit',
        qty=qtd_cripto_para_operar,
        price=preco,
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# Para abrir posição de venda acima do preço atual
def abre_venda_limit(cripto, preco, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Sell',
        orderType='Limit',
        qty=qtd_cripto_para_operar,
        price=preco,
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# Para abrir posição de compra acima do preço atual (rompimento de resistência) - Limit Order (proteção contra slippage)
def abre_compra_stop_limit(cripto, preco, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Buy',
        orderType='Limit',
        qty=qtd_cripto_para_operar,
        price=preco*1.0001,
        triggerPrice=preco,
        triggerBy='LastPrice',
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# Para abrir posição de venda acima do preço atual (rompimento de suporte) - Limit Order (proteção contra slippage)
def abre_venda_stop_limit(cripto, preco, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Sell',
        orderType='Limit',
        qty=qtd_cripto_para_operar,
        price=preco*0.9999,
        triggerPrice=preco,
        triggerBy='LastPrice',
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# Para abrir posição de compra acima do preço atual (rompimento de resistência) - Market Order (execução imediata garantida)
def abre_compra_stop_market(cripto, preco_trigger, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Buy',
        orderType='Market',
        qty=qtd_cripto_para_operar,
        triggerPrice=preco_trigger,
        triggerBy='LastPrice',
        triggerDirection=1,  # 1 = Rising (preço subindo)
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# Para abrir posição de venda abaixo do preço atual (rompimento de suporte) - Market Order (execução imediata garantida)
def abre_venda_stop_market(cripto, preco_trigger, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Sell',
        orderType='Market',
        qty=qtd_cripto_para_operar,
        triggerPrice=preco_trigger,
        triggerBy='LastPrice',
        triggerDirection=2,  # 2 = Falling (preço descendo)
        stopLoss=preco_stop,
        takeProfit=preco_alvo
    )

# Para cancelar ordens limit para o caso de atualização da vela referência ou quando ela deixa de existir
def cancela_todas_ordens(cripto, nro_subconta):
    return busca_cliente(nro_subconta).cancel_all_orders(
        category='linear',
        symbol=cripto
    )

# Atualiza o stop_loss da posição aberta
def ajusta_stop(cripto, preco_stop, nro_subconta):
    return busca_cliente(nro_subconta).set_trading_stop(
        category='linear',
        symbol=cripto,
        tpslMode='Full',
        positionIdx=0, # 0: one-way, 1: hedge buy, 2: hedge sell
        stopLoss=preco_stop
    )

# Atualiza o take_profit da posição aberta
def ajusta_alvo(cripto, preco_alvo, nro_subconta):
    return busca_cliente(nro_subconta).set_trading_stop(
        category='linear',
        symbol=cripto,
        tpslMode='Full',
        positionIdx=0, # 0: one-way, 1: hedge buy, 2: hedge sell
        takeProfit=preco_alvo
    )

# Aciona o trailing stop para uma posição aberta
def aciona_trailing_stop_imediato(cripto, trailing_stop, nro_subconta):
    return busca_cliente(nro_subconta).set_trading_stop(
        category='linear',
        symbol=cripto,
        tpslMode='Full',
        positionIdx=0, # 0: one-way, 1: hedge buy, 2: hedge sell
        trailingStop=trailing_stop
    )

# Aciona o trailing stop para uma posição aberta
def aciona_trailing_stop_preco(cripto, trailing_stop, preco_ativacao_trailing_stop, nro_subconta):
    return busca_cliente(nro_subconta).set_trading_stop(
        category='linear',
        symbol=cripto,
        tpslMode='Full',
        positionIdx=0, # 0: one-way, 1: hedge buy, 2: hedge sell
        trailingStop=trailing_stop,
        activePrice=preco_ativacao_trailing_stop
    )

# Fecha parcialmente uma posição de compra
def fecha_parcial_compra(cripto, qtd_cripto_para_vender, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Sell',
        orderType='Market',
        qty=qtd_cripto_para_vender,
        reduceOnly=True
    )

# Fecha parcialmente uma posição de venda
def fecha_parcial_venda(cripto, qtd_cripto_para_comprar, nro_subconta):
    return busca_cliente(nro_subconta).place_order(
        category='linear',
        symbol=cripto,
        side='Buy',
        orderType='Market',
        qty=qtd_cripto_para_comprar,
        reduceOnly=True
    )

def busca_pnl(nro_subconta, dias=30):
    """
    Busca dados de PnL dos últimos N dias.
    
    Args:
        nro_subconta: Número da subconta
        dias: Número de dias para buscar (padrão: 30)
    
    Returns:
        DataFrame com os trades e PnL
    """
    from datetime import datetime, timedelta
    
    cliente = busca_cliente(nro_subconta)
    
    # Calcular timestamps
    agora = datetime.now()
    data_final = agora
    
    # Lista para armazenar todos os trades
    todos_trades = []

    # Janela de ~6.9 dias (margem de segurança para não exceder 7 dias)
    janela_dias = timedelta(days=6, hours=23)
    
    # Fazer múltiplas chamadas de 7 dias cada
    periodos_necessarios = (dias + 6) // 7  # Arredonda para cima
    
    for i in range(periodos_necessarios):
        # Calcular o range de 7 dias para esta iteração
        end_time = int(data_final.timestamp() * 1000)
        start_time = int((data_final - janela_dias).timestamp() * 1000)
        
        # Fazer a chamada à API
        resposta = cliente.get_closed_pnl(
            category='linear',
            limit=100,
            startTime=start_time,
            endTime=end_time
        )

        # Verificar se a resposta tem os campos esperados
        if 'result' not in resposta or 'list' not in resposta['result']:
            continue
        
        trades = resposta['result']['list']
        if trades:
            todos_trades.extend(trades)
        
        # Mover para o próximo período de 7 dias
        data_final = data_final - janela_dias
    
    # Se não há trades, retorna DataFrame vazio
    if len(todos_trades) == 0:
        return pd.DataFrame()
    
    # Processar os trades
    trades_pnl = []
    for trade in todos_trades:

        if trade['updatedTime'] == '' or trade['updatedTime'] is None or not trade.get('updatedTime'):
            continue

        trades_pnl.append({
            'data': trade['updatedTime'],
            'pnl': round(float(trade['closedPnl']) if trade['closedPnl'] != '' else 0.0, 2),
            'símbolo': trade['symbol']
        })

    if not trades_pnl:
        return pd.DataFrame()
    
    df_trades_pnl = pd.DataFrame(trades_pnl)
    df_trades_pnl['data'] = pd.to_datetime(df_trades_pnl['data'].astype(np.int64), unit='ms')
    
    # Remover duplicatas (caso haja sobreposição entre chamadas)
    df_trades_pnl = df_trades_pnl.drop_duplicates(subset=['data', 'símbolo'], keep='first')
    
    # Ordenar por data
    df_trades_pnl = df_trades_pnl.sort_values('data', ascending=False).reset_index(drop=True)
    
    return df_trades_pnl

def busca_lsr_open_interest(cripto, tempo_grafico, quantidade):
    resposta_lsr = cliente.get_long_short_ratio(category='linear', symbol=cripto, period=tempo_grafico, limit=quantidade)
    lsr = resposta_lsr['result']['list']

    resposta_open_interest = cliente.get_open_interest(category='linear', symbol=cripto, intervalTime=tempo_grafico, limit=quantidade)
    open_interest = resposta_open_interest['result']['list']

    lsr_open_interest = []

    if len(lsr) > 0 and len(open_interest) > 0:
        for index, item in enumerate(lsr):

            if item['timestamp'] == '' or item['timestamp'] is None or not item.get('timestamp') or index >= len(open_interest):
                continue

            buy_ratio = float(item['buyRatio']) if item['buyRatio'] != '' else 0.0
            sell_ratio = float(item['sellRatio']) if item['sellRatio'] != '' else 0.0
            relacao = buy_ratio / sell_ratio if sell_ratio != 0 else 0.0
            open_interest_valor = float(open_interest[index]['openInterest']) if open_interest[index]['openInterest'] != '' else 0.0
            lsr_open_interest.append({
                'data': item['timestamp'],
                'lsr': round(relacao, 2),
                'open_interest': round(open_interest_valor, 0)
            })

            if not lsr_open_interest:
                return pd.DataFrame()

        df_lsr_open_interest = pd.DataFrame(lsr_open_interest)
        df_lsr_open_interest['data'] = pd.to_datetime(df_lsr_open_interest['data'].astype(np.int64), unit='ms')
        return df_lsr_open_interest
    else:
        return pd.DataFrame()

# TODO: Falta implementar funções para definir alvos parciais (fecha_parcial_compra_limit, fecha_parcial_venda_limit)