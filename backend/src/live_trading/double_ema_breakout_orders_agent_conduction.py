import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from pathlib import Path
from datetime import datetime, timedelta

from entidades.estado_trade import EstadoDeTrade
from corretoras.funcoes_bybit import busca_velas, tem_trade_aberto, saldo_da_conta, quantidade_minima_para_operar, abre_compra
from utils.utilidades import quantidade_cripto_para_operar
from agent_execution_with_parser import executar_trade_conductor_se_necessario
from utils.logging import get_logger, LogCategory
from utils.utilidades import calcular_risco_retorno_compra

# Nome do módulo para logs (automático)
MODULE_NAME = Path(__file__).stem

subconta = 1
cripto = 'SOLUSDT'
tempo_grafico = '15'
qtd_velas_stop = 17
risco_retorno = 4.1
ema_rapida = 5
ema_lenta = 15
alavancagem = 1
frequencia_agente_horas = 4
executar_agente_no_start = True

def start_live_trading_bot(
    cripto = cripto,
    tempo_grafico = tempo_grafico,
    qtd_velas_stop = qtd_velas_stop,
    risco_retorno = risco_retorno,
    ema_rapida = ema_rapida,
    ema_lenta = ema_lenta,
    alavancagem = alavancagem,
    subconta = subconta,
    frequencia_agente_horas = frequencia_agente_horas,
    executar_agente_no_start = executar_agente_no_start,
    bot_id = f"{datetime.now().timestamp():.0f}"
):
    logger = get_logger(bot_id)
    
    logger.info(LogCategory.BOT_START, "🚀 Bot de trading iniciado", MODULE_NAME,
        subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, qtd_velas_stop=qtd_velas_stop, 
        risco_retorno=risco_retorno, ema_rapida=ema_rapida, ema_lenta=ema_lenta,
        frequencia_agente_horas=frequencia_agente_horas, executar_agente_no_start=executar_agente_no_start,
        alavancagem=alavancagem)

    for tentativa in range(5):
        try:
            estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = tem_trade_aberto(cripto, subconta)
            qtd_min_para_operar = quantidade_minima_para_operar(cripto, subconta)
            
            if estado_de_trade == EstadoDeTrade.COMPRADO:
                risco_retorno = calcular_risco_retorno_compra(preco_entrada, preco_stop, preco_alvo)
                logger.trading(LogCategory.POSITION_STATUS, "🟢 Posição COMPRADO ativa", MODULE_NAME,
                    symbol=cripto, estado_de_trade=estado_de_trade.value, preco_entrada=preco_entrada,
                    preco_stop=preco_stop, preco_alvo=preco_alvo, tamanho_posicao=tamanho_posicao,
                    trailing_stop=trailing_stop, risco_retorno=risco_retorno)
            else:
                logger.info(LogCategory.POSITION_STATUS, "🔵 Sem posição aberta", MODULE_NAME,
                    symbol=cripto, estado_de_trade=estado_de_trade.value)
            break

        except Exception as e:
            logger.error(LogCategory.TRADE_STATUS_ERROR, f"Erro ao buscar trade aberto", MODULE_NAME,
                symbol=cripto, tentativa=tentativa+1, erro_message=str(e), exception=e)
            
            if tentativa < 4:
                logger.info(LogCategory.RETRY_ATTEMPT, "Tentando novamente", MODULE_NAME,
                    symbol=cripto, tentativa=tentativa+1, max_tentativas=5)
                time.sleep(2)
            elif tentativa == 4:
                logger.critical(LogCategory.FATAL_ERROR, "Não foi possível buscar trade aberto. Encerrando programa.", MODULE_NAME,
                    symbol=cripto, total_tentativas=5, erro_message=str(e))
                exit()

    vela_abertura_trade = None
    vela_fechou_trade = None
    # Se a flag executar_agente_no_start for False, marca o tempo atual para aguardar a frequência
    if executar_agente_no_start:
        ultima_execucao_trade_conductor = None
    else:
        ultima_execucao_trade_conductor = datetime.now()
        next_execution = ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)
        logger.info(LogCategory.AGENT_SCHEDULE, "Agente condutor não será executado no start", MODULE_NAME,
            symbol=cripto, proxima_execucao=next_execution.strftime("%Y-%m-%d %H:%M:%S"), 
            frequencia_agente_horas=frequencia_agente_horas, status="Aguardando stop, alvo ou avaliação do condutor")

    while True:
        try:
            df = busca_velas(cripto, tempo_grafico, [ema_rapida, ema_lenta])

            if df.empty:
                logger.warning(LogCategory.EMPTY_DATA, "DataFrame vazio - dados de mercado não disponíveis", MODULE_NAME,
                    symbol=cripto, tempo_grafico=tempo_grafico)
            else:

                if estado_de_trade == EstadoDeTrade.COMPRADO:

                    estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = tem_trade_aberto(cripto, subconta)

                    ultima_execucao_trade_conductor = executar_trade_conductor_se_necessario(
                        ultima_execucao_trade_conductor,
                        frequencia_agente_horas,
                        df,
                        cripto,
                        subconta,
                        tempo_grafico,
                        estado_de_trade,
                        preco_entrada,
                        preco_alvo,
                        preco_stop,
                        tamanho_posicao,
                        qtd_min_para_operar,
                        trailing_stop,
                        vela_abertura_trade,
                        logger
                    )

                    if df['maxima'].iloc[-1] >= preco_alvo and preco_alvo != 0:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        logger.trading(LogCategory.TARGET_HIT, "Take profit atingido", MODULE_NAME,
                            symbol=cripto, tempo_abertura=df.index[-1], preco_alvo=preco_alvo, 
                            preco_atual=df['maxima'].iloc[-1])

                    elif df['minima'].iloc[-1] <= preco_stop:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        logger.trading(LogCategory.STOP_HIT, "Stop loss atingido", MODULE_NAME,
                            symbol=cripto, tempo_abertura=df.index[-1], preco_stop=preco_stop,
                            preco_atual=df['minima'].iloc[-1])

                    elif estado_de_trade == EstadoDeTrade.DE_FORA:
                        vela_fechou_trade = df.index[-1]
                        logger.trading(LogCategory.MANUAL_CLOSE, "Trade fechado manualmente na corretora", MODULE_NAME,
                            symbol=cripto, tempo_abertura=df.index[-1])
                        logger.info(LogCategory.TRADE_SEARCH, "🔍 Procurando oportunidades de trade", MODULE_NAME,
                            subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico)

                elif estado_de_trade == EstadoDeTrade.DE_FORA and df.index[-1] != vela_fechou_trade:
                    if df['fechamento'].iloc[-2] > df[f'EMA_{ema_rapida}'].iloc[-2] and df['fechamento'].iloc[-2] > df[f'EMA_{ema_lenta}'].iloc[-2]:
                        if df['maxima'].iloc[-1] > df['maxima'].iloc[-2]:
                            saldo = saldo_da_conta(subconta) * alavancagem

                            qtd_cripto_para_operar = quantidade_cripto_para_operar(saldo, qtd_min_para_operar, df['fechamento'].iloc[-1])
                            
                            preco_entrada = df['maxima'].iloc[-2]
                            preco_stop = df['minima'].iloc[-qtd_velas_stop : -1].min()
                            preco_alvo = ((preco_entrada - preco_stop) * risco_retorno) + preco_entrada
                            
                            abre_compra(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, subconta)
                            ultima_execucao_trade_conductor = None

                            logger.trading(LogCategory.POSITION_OPEN, "🟢 Nova posição LONG aberta", MODULE_NAME,
                                symbol=cripto, tempo_abertura=df.index[-1], preco_entrada=preco_entrada,
                                preco_stop=preco_stop, preco_alvo=preco_alvo, tamanho_posicao=qtd_cripto_para_operar,
                                alavancagem=alavancagem, ema_rapida=ema_rapida, ema_lenta=ema_lenta,
                                qtd_velas_stop=qtd_velas_stop, risco_retorno=risco_retorno)
                            estado_de_trade = EstadoDeTrade.COMPRADO
                            vela_abertura_trade = df.index[-1]

        except ConnectionError as ce:
            logger.error(LogCategory.CONNECTION_ERROR, "Erro de conexão durante execução do bot", MODULE_NAME,
                symbol=cripto, erro_message=str(ce), exception=ce)
        except ValueError as ve:
            logger.error(LogCategory.VALUE_ERROR, "Erro de valor durante execução do bot", MODULE_NAME,
                symbol=cripto, erro_message=str(ve), exception=ve)
        except KeyboardInterrupt:
            logger.info(LogCategory.SHUTDOWN, "Programa encerrado pelo usuário", MODULE_NAME,
                symbol=cripto)
            exit()
        except Exception as e:
            logger.error(LogCategory.UNKNOWN_ERROR, "Erro desconhecido durante execução do bot", MODULE_NAME,
                symbol=cripto, erro_message=str(e), exception=e)

        time.sleep(0.25)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--subconta', type=int, default=subconta)
    parser.add_argument('--cripto', type=str, default=cripto)
    parser.add_argument('--tempo_grafico', type=str, default=tempo_grafico)
    parser.add_argument('--qtd_velas_stop', type=int, default=qtd_velas_stop)
    parser.add_argument('--risco_retorno', type=float, default=risco_retorno)
    parser.add_argument('--ema_rapida', type=int, default=ema_rapida)
    parser.add_argument('--ema_lenta', type=int, default=ema_lenta)
    parser.add_argument('--alavancagem', type=float, default=alavancagem)
    parser.add_argument('--frequencia_agente_horas', type=float, default=frequencia_agente_horas)
    parser.add_argument('--executar_agente_no_start', type=bool, default=executar_agente_no_start, help='Se True, executa o agente imediatamente no start. Se False, aguarda a frequência definida.')
    args = parser.parse_args()
    
    start_live_trading_bot(
        subconta=args.subconta,
        cripto=args.cripto,
        tempo_grafico=args.tempo_grafico,
        qtd_velas_stop=args.qtd_velas_stop,
        risco_retorno=args.risco_retorno,
        ema_rapida=args.ema_rapida,
        ema_lenta=args.ema_lenta,
        alavancagem=args.alavancagem,
        frequencia_agente_horas=args.frequencia_agente_horas,
        executar_agente_no_start=args.executar_agente_no_start
    )