def busca_cliente(nro_subconta):
    return None

def carregar_dados_historicos(cripto, tempo_grafico, emas, start, end, pular_velas=999, remove_velas=True):
    return None

def busca_velas(cripto, tempo_grafico, emas):
    return None

def tem_trade_aberto(cripto):
    return None

def saldo_da_conta():
    return None

def quantidade_minima_para_operar(cripto):
    return None

def abre_compra(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo):
    return None
    # Bybit
    # busca_cliente(nro_subconta).place_order(
    #     category='linear',
    #     symbol=cripto,
    #     side='Buy',
    #     orderType='Market',
    #     qty=qtd_cripto_para_operar,
    #     stopLoss=preco_stop,
    #     takeProfit=preco_alvo
    # )

def abre_venda(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return None
    # Bybit
    # busca_cliente(nro_subconta).place_order(
    #     category='linear',
    #     symbol=cripto,
    #     side='Sell',
    #     orderType='Market',
    #     qty=qtd_cripto_para_operar,
    #     stopLoss=preco_stop,
    #     takeProfit=preco_alvo
    # )

# TODO: VALIDAR AS FUNÇÕES ABAIXO COM TESTES NO LIVE_TRADING
# Para fechar posição sem alvo definido, geralmente por condução de trade
def fecha_compra(cripto, nro_subconta):
    return None
    # Bybit
    # busca_cliente(nro_subconta).place_order(
    #     category='linear',
    #     symbol=cripto,
    #     side='Sell',
    #     orderType='Market',
    #     qty='0',
    #     reduceOnly=True,
    #     closeOnTrigger=True
    # )

# Para fechar posição sem alvo definido, geralmente por condução de trade
def fecha_venda(cripto, nro_subconta):
    return None
    # Bybit
    # busca_cliente(nro_subconta).place_order(
    #     category='linear',
    #     symbol=cripto,
    #     side='Buy',
    #     orderType='Market',
    #     qty='0',
    #     reduceOnly=True,
    #     closeOnTrigger=True
    # )

# Para abrir posição na superação da máxima de uma vela referência
def abre_compra_limit(cripto, preco, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return None
    # Bybit
    # busca_cliente(nro_subconta).place_order(
    #     category='linear',
    #     symbol=cripto,
    #     side='Buy',
    #     orderType='Limit',
    #     qty=qtd_cripto_para_operar,
    #     price=preco,
    #     stopLoss=preco_stop,
    #     takeProfit=preco_alvo
    # )

# Para abrir posição na perda da mínima de uma vela referência
def abre_venda_limit(cripto, preco, qtd_cripto_para_operar, preco_stop, preco_alvo, nro_subconta):
    return None
    # Bybit
    # busca_cliente(nro_subconta).place_order(
    #     category='linear',
    #     symbol=cripto,
    #     side='Sell',
    #     orderType='Limit',
    #     qty=qtd_cripto_para_operar,
    #     price=preco,
    #     stopLoss=preco_stop,
    #     takeProfit=preco_alvo
    # )

# Para cancelar ordens limit para o caso de atualização da vela referência ou quando ela deixa de existir
def cancela_todas_ordens(cripto, nro_subconta):
    return None
    # Bybit
    # busca_cliente(nro_subconta).cancel_all_orders(
    #     category='linear',
    #     symbol=cripto
    # )