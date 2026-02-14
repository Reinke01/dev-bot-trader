from agno.tools import Toolkit

from decimal import Decimal, ROUND_DOWN

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from corretoras.funcoes_bybit import busca_velas, fecha_compra, fecha_venda, ajusta_stop, ajusta_alvo, aciona_trailing_stop_imediato, aciona_trailing_stop_preco, abre_compra, abre_venda, saldo_da_conta, quantidade_minima_para_operar

class BybitTools(Toolkit):
    def __init__(
        self,
        buscar_contexto: bool = False,
        # analisar_meu_trade: bool = False,
        # buscar_saldo: bool = False,
        abrir_compra: bool = False,
        abrir_venda: bool = False,
        # fechar_posicao: bool = False,
        fechar_compra: bool = False,
        fechar_venda: bool = False,
        ajustar_stop: bool = False,
        ajustar_alvo: bool = False,
        # realizar_parcial: bool = False,
        trailing_imediato: bool = False,
        trailing_preco: bool = False,
        enable_all: bool = False,
        **kwargs
    ):
        tools = []
        if buscar_contexto or enable_all:
            tools.append(self.buscar_contexto_tecnico)
        # if analisar_meu_trade or enable_all:
        #     tools.append(self.analisar_meu_trade)
        # if buscar_saldo or enable_all:
        #     tools.append(self.buscar_saldo)
        if abrir_compra or enable_all:
            tools.append(self.abrir_compra)
        if abrir_venda or enable_all:
            tools.append(self.abrir_venda)
        # if fechar_posicao or enable_all:
        #     tools.append(self.fechar_posicao)
        if fechar_compra or enable_all:
            tools.append(self.fechar_compra)
        if fechar_venda or enable_all:
            tools.append(self.fechar_venda)
        if ajustar_stop or enable_all:
            tools.append(self.ajustar_stop)
        if ajustar_alvo or enable_all:
            tools.append(self.ajustar_alvo)
        # if realizar_parcial or enable_all:
        #     tools.append(self.realizar_parcial_compra, self.realizar_parcial_venda)
        if trailing_imediato or enable_all:
            tools.append(self.acionar_trailing_stop_imediato)
        if trailing_preco or enable_all:
            tools.append(self.acionar_trailing_stop_preco)

        super().__init__(name="bybit_tools", tools=tools, **kwargs)

    def buscar_contexto_tecnico(
        self,
        simbolo: str,         # Símbolo do ativo
        emas: list=[9,21],    # Lista de períodos das EMAs (duas EMAs)
    ) -> str:                 # Retorna DataFrame com velas e EMAs
        """Busca candles do mercado de criptomoedas e retorna o contexto técnico com as últimas velas em 3 tempos gráficos e indicadores."""
        df_1w = busca_velas(simbolo, 'W', emas)
        df_1w['EMA_200'] = df_1w['fechamento'].ewm(span=200, adjust=False).mean()
        df_1d = busca_velas(simbolo, 'D', emas)
        df_1d['EMA_200'] = df_1d['fechamento'].ewm(span=200, adjust=False).mean()
        df_15m = busca_velas(simbolo, '15', emas)
        df_15m['EMA_200'] = df_15m['fechamento'].ewm(span=200, adjust=False).mean()
        
        return f"""
    Contexto técnico (últimas velas e indicadores):
    - Semanal:
    {df_1w.tail(24).to_string()}

    - Diário:
    {df_1d.tail(45).to_string()}

    - 15 minutos:
    {df_15m.tail(50).to_string()}
        """

    # def analisar_meu_trade(
    #     self,
    #     simbolo: str,
    #     nro_subconta: int
    # ) -> dict:
    #     """Realiza uma análise detalhada do trade atual, considerando o contexto técnico."""
    #     return realiza_analise_meu_trade(simbolo, nro_subconta)

    def abrir_compra(
        self,
        simbolo: str,                  # Símbolo do ativo
        tempo_grafico: str,            # Tempo gráfico
        risco_por_operacao: float,     # Risco por operação (0.02 = 2%)
        preco_stop: float,             # Preço de stop loss
        preco_alvo: float,             # Preço de take profit
        nro_subconta: int = 1          # Número da subconta na corretora
    ) -> dict:
        """Abre uma posição comprada (long) no ativo especificado."""
        qtd_min_para_operar = quantidade_minima_para_operar(simbolo, nro_subconta)
        
        df = busca_velas(simbolo, tempo_grafico, [9,21])
        preco_atual = df['fechamento'].iloc[-1]

        if preco_atual < preco_stop:
            return {"error": "Preço atual é menor que o preço de stop"}
        elif preco_atual > preco_alvo:
            return {"error": "Preço atual é maior que o preço de alvo"}

        distancia_stop_percent = (preco_atual - preco_stop) / preco_atual

        saldo = saldo_da_conta(nro_subconta) * 0.98
        tamanho_posicao = saldo * risco_por_operacao / distancia_stop_percent
        qtd_cripto_para_operar = tamanho_posicao / preco_atual

        quantidade_cripto_para_operar = int(qtd_cripto_para_operar / qtd_min_para_operar) * qtd_min_para_operar
        quantidade_cripto_para_operar = Decimal(quantidade_cripto_para_operar)
        quantidade_cripto_para_operar = quantidade_cripto_para_operar.quantize(Decimal(f'{qtd_min_para_operar}'), rounding=ROUND_DOWN)
        return abre_compra(simbolo, str(quantidade_cripto_para_operar), str(preco_stop), str(preco_alvo), nro_subconta)

    def abrir_venda(
        self,
        simbolo: str,                  # Símbolo do ativo
        tempo_grafico: str,            # Tempo gráfico
        risco_por_operacao: float,     # Risco por operação (0.02 = 2%)
        preco_stop: float,             # Preço de stop loss
        preco_alvo: float,             # Preço de take profit
        nro_subconta: int = 1          # Número da subconta na corretora
    ) -> dict:
        """Abre uma posição vendida (short) no ativo especificado."""
        qtd_min_para_operar = quantidade_minima_para_operar(simbolo, nro_subconta)

        df = busca_velas(simbolo, tempo_grafico, [9,21])
        preco_atual = df['fechamento'].iloc[-1]

        if preco_atual > preco_stop:
            return {"error": "Preço atual é maior que o preço de stop"}
        elif preco_atual < preco_alvo:
            return {"error": "Preço atual é menor que o preço de alvo"}

        distancia_stop_percent = (preco_stop - preco_atual) / preco_atual

        saldo = saldo_da_conta(nro_subconta) * 0.98
        tamanho_posicao = saldo * risco_por_operacao / distancia_stop_percent
        qtd_cripto_para_operar = tamanho_posicao / preco_atual

        quantidade_cripto_para_operar = int(qtd_cripto_para_operar / qtd_min_para_operar) * qtd_min_para_operar
        quantidade_cripto_para_operar = Decimal(quantidade_cripto_para_operar)
        quantidade_cripto_para_operar = quantidade_cripto_para_operar.quantize(Decimal(f'{qtd_min_para_operar}'), rounding=ROUND_DOWN)
        return abre_venda(simbolo, str(quantidade_cripto_para_operar), str(preco_stop), str(preco_alvo), nro_subconta)

    def fechar_compra(
        self,
        simbolo: str,          # Símbolo do ativo
        nro_subconta: int = 1  # Número da subconta na corretora
    ) -> dict:                 # Retorna um json com o resultado da execução da ordem de fechamento de compra
        """Encerra uma posição comprada (long) no ativo especificado."""
        return fecha_compra(simbolo, nro_subconta)

    def fechar_venda(   
        self,
        simbolo: str,           # Símbolo do ativo
        nro_subconta: int = 1   # Número da subconta na corretora
    ) -> dict:                  # Retorna um json com o resultado da execução da ordem de fechamento de venda
        """Encerra uma posição vendida (short) no ativo especificado."""
        return fecha_venda(simbolo, nro_subconta)

    def ajustar_stop(
        self,
        simbolo: str,            # Símbolo do ativo
        preco_stop: float,       # Novo preço de stop loss
        nro_subconta: int = 1    # Número da subconta na corretora (padrão: 1)
    ) -> dict:                   # Retorna um json com o resultado da execução do ajuste de stop
        """Atualiza o preço de stop loss de uma posição aberta."""
        return ajusta_stop(simbolo, preco_stop, nro_subconta)

    def ajustar_alvo(
        self,
        simbolo: str,            # Símbolo do ativo
        preco_alvo: float,       # Novo preço de take profit
        nro_subconta: int = 1    # Número da subconta na corretora (padrão: 1)
    ) -> dict:                   # Retorna um json com o resultado da execução do ajuste de alvo
        """Atualiza o preço de take profit (alvo) de uma posição aberta."""
        return ajusta_alvo(simbolo, preco_alvo, nro_subconta)

    # def realizar_parcial_da_compra(
    #     self,
    #     simbolo: str,
    #     nro_subconta: int = 1,
    #     percentual: float
    # ) -> dict:
    #     """Realiza uma compra parcial do ativo especificado."""
    #     return realiza_parcial_da_compra(simbolo, nro_subconta)

    def acionar_trailing_stop_imediato(
        self,
        simbolo: str,                # Símbolo do ativo
        trailing_stop: float,        # Distância em dólares do trailing stop
        nro_subconta: int = 1        # Número da subconta na corretora (padrão: 1)
    ) -> dict:                       # Retorna um json com o resultado da execução do trailing stop
        """Aciona o trailing stop imediatamente para uma posição aberta."""
        return aciona_trailing_stop_imediato(simbolo, trailing_stop, nro_subconta)

    def acionar_trailing_stop_preco(
        self,
        simbolo: str,                        # Símbolo do ativo
        trailing_stop: float,                # Distância em dólares do trailing stop
        preco_ativacao_trailing_stop: float, # Preço de ativação do trailing stop
        nro_subconta: int = 1                # Número da subconta na corretora (padrão: 1)
    ) -> dict:                               # Retorna um json com o resultado da execução do trailing stop com preço de ativação
        """Aciona o trailing stop para uma posição aberta, ativando-o a partir de um preço específico."""
        return aciona_trailing_stop_preco(simbolo, trailing_stop, preco_ativacao_trailing_stop, nro_subconta)