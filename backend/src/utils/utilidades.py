from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timedelta

def quantidade_cripto_para_operar(saldo, minimo_para_operar, preco_atual):
    poderia_operar = saldo / preco_atual
    quantidade_cripto_para_operar = int(poderia_operar / minimo_para_operar) * minimo_para_operar
    quantidade_cripto_para_operar = Decimal(quantidade_cripto_para_operar)
    return quantidade_cripto_para_operar.quantize(Decimal(f'{minimo_para_operar}'), rounding=ROUND_DOWN)

def quantidade_cripto_para_parcial(tamanho_posicao, percentual, quantidade_minima_cripto):
    poderia_realizar_parcial = tamanho_posicao * percentual/100
    quantidade_cripto_para_parcial = int(poderia_realizar_parcial / quantidade_minima_cripto) * quantidade_minima_cripto
    quantidade_cripto_para_operar = Decimal(quantidade_cripto_para_parcial)
    return quantidade_cripto_para_operar.quantize(Decimal(f'{quantidade_minima_cripto}'), rounding=ROUND_DOWN)

def calcular_risco_retorno_compra(preco_entrada, preco_stop, preco_alvo):
    return round((preco_alvo - preco_entrada) / (preco_entrada - preco_stop), 2)

def calcular_risco_retorno_venda(preco_entrada, preco_stop, preco_alvo):
    return round((preco_entrada - preco_alvo) / (preco_stop - preco_entrada), 2)

# Aliases for backward compatibility
risco_retorno_compra = calcular_risco_retorno_compra
risco_retorno_venda = calcular_risco_retorno_venda

#TODO: implementar a lógica para tempos gráficos: D, W, M
def ajusta_start_time(start_time, tempo_grafico, pular_velas=999):
    start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
    
    if tempo_grafico == 'D':
        minutos_para_subtrair = pular_velas * 24 * 60
    
    elif tempo_grafico == 'W':
        minutos_para_subtrair = pular_velas * 7 * 24 * 60

    else:
        minutos_para_subtrair = pular_velas * int(tempo_grafico)

    novo_datetime = start_datetime - timedelta(minutes=minutos_para_subtrair)
    return novo_datetime.strftime('%Y-%m-%d %H:%M')

def calcula_percentual_perda_na_compra(preco_compra, preco_stop):
    return ((preco_compra - preco_stop) / preco_compra) * 100

def calcula_percentual_lucro_na_compra(preco_compra, preco_alvo):
    return ((preco_alvo - preco_compra) / preco_compra) * 100

def calcula_percentual_perda_na_venda(preco_venda, preco_stop):
    return ((preco_stop - preco_venda) / preco_venda) * 100

def calcula_percentual_lucro_na_venda(preco_venda, preco_alvo):
    return ((preco_venda - preco_alvo) / preco_venda) * 100

def verifica_dia_util(data):
    return data.weekday() < 5

def verifica_segunda_a_quinta(data):
    return data.weekday() < 4

def verifica_dia_util_ate_sexta_16h_utc(data):
    if data.weekday() == 4 and data.hour >= 16:
        return False
    return data.weekday() < 5

def ytd():
    today = datetime.now()
    ytd_start = datetime(today.year, 1, 1)
    ytd_end = today
    return ytd_start, ytd_end

def last_year():
    today = datetime.now()
    last_year_start = datetime(today.year - 1, today.month, today.day)
    last_year_end = today
    return last_year_start, last_year_end

def last_semester():
    today = datetime.now()
    if today.month < 7:
        last_semester_start = datetime(today.year - 1, today.month + 6, today.day)
    else:
        last_semester_start = datetime(today.year, today.month - 6, today.day)
    last_semester_end = today
    return last_semester_start, last_semester_end

def last_month():
    today = datetime.now()
    last_month_start = datetime(today.year, today.month - 1, today.day)
    last_month_end = today
    return last_month_start, last_month_end