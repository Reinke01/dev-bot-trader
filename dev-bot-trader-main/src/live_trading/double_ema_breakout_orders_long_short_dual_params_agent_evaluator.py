import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from pathlib import Path
from datetime import datetime, timedelta
from entidades.estado_trade import EstadoDeTrade
from entidades.lado_operacao import LadoOperacao
from entidades.risco_operacao import RiscoOperacao
from corretoras.funcoes_bybit import busca_velas, tem_trade_aberto, saldo_da_conta, quantidade_minima_para_operar
# Import que funciona em ambos os contextos
if __name__ == '__main__':
    # Execução direta - import local
    from agent_execution_with_parser import executar_trade_conductor_se_necessario
else:
    # Importado por outro módulo (API) - import absoluto
    from live_trading.agent_execution_with_parser import executar_trade_conductor_se_necessario
from agentes.trade_entry_evaluator import trade_entry_evaluator
from agentes.prompts.trade_entry_evaluator import prompt_trade_entry_evaluator
from agentes.parsers.trade_entry_evaluator_parser import TradeEntryEvaluatorParser
from managers.data_manager import prepare_multi_timeframe_technical_data, prepare_market_data
from utils.utilidades import calcular_risco_retorno_compra, calcular_risco_retorno_venda
from utils.logging import get_logger, LogCategory

# Nome do módulo para logs (automático)
MODULE_NAME = Path(__file__).stem

# Valores padrão
subconta = 1
cripto = 'SOLUSDT'
tempo_grafico = '15'
frequencia_agente_horas = 4
executar_agente_no_start = False
lado_operacao = LadoOperacao.AMBOS

# Parâmetros para compra
ema_rapida_compra = 5
ema_lenta_compra = 15

# Parâmetros para venda
ema_rapida_venda = 21
ema_lenta_venda = 125

# Define percentual de perda ao montar operação:
# MUITO_BAIXO (0.5%), BAIXO (1%), MEDIO (2%), ALTO (5%), MUITO_ALTO (8%)
risco_por_operacao = RiscoOperacao.BAIXO

# Define apetite a risco para aceitar trades com maior ou menor probabilidade de sucesso:
# apetite_a_risco = "BAIXO"

def start_live_trading_bot(
    subconta = subconta,
    cripto = cripto,
    tempo_grafico = tempo_grafico,
    lado_operacao = lado_operacao,
    frequencia_agente_horas = frequencia_agente_horas,
    executar_agente_no_start = executar_agente_no_start,
    ema_rapida_compra = ema_rapida_compra,
    ema_lenta_compra = ema_lenta_compra,
    ema_rapida_venda = ema_rapida_venda,
    ema_lenta_venda = ema_lenta_venda,
    risco_por_operacao = risco_por_operacao,
    bot_id = f"{datetime.now().timestamp():.0f}",
    stop_flag = None
):
    compras_habilitadas = lado_operacao in [LadoOperacao.AMBOS, LadoOperacao.APENAS_COMPRA]
    vendas_habilitadas = lado_operacao in [LadoOperacao.AMBOS, LadoOperacao.APENAS_VENDA]

    logger = get_logger(bot_id)

    logger.info(LogCategory.BOT_START, "🚀 Bot de trading iniciado com Entry Evaluator", MODULE_NAME,
        subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao=lado_operacao.value,
        risco_por_operacao=risco_por_operacao.value, frequencia_agente_horas=frequencia_agente_horas,
        executar_agente_no_start=executar_agente_no_start,
        compras_habilitadas=compras_habilitadas, vendas_habilitadas=vendas_habilitadas,
        ema_rapida_compra=ema_rapida_compra if compras_habilitadas else None, 
        ema_lenta_compra=ema_lenta_compra if compras_habilitadas else None,
        ema_rapida_venda=ema_rapida_venda if vendas_habilitadas else None,
        ema_lenta_venda=ema_lenta_venda if vendas_habilitadas else None
    )

    for tentativa in range(5):
        try:
            estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = tem_trade_aberto(cripto, subconta)
            qtd_min_para_operar = quantidade_minima_para_operar(cripto, subconta)
            
            if estado_de_trade in [EstadoDeTrade.COMPRADO, EstadoDeTrade.VENDIDO]:
                if estado_de_trade == EstadoDeTrade.COMPRADO and preco_stop < preco_entrada:
                    risco_retorno = calcular_risco_retorno_compra(preco_entrada, preco_stop, preco_alvo)
                elif estado_de_trade == EstadoDeTrade.VENDIDO and preco_stop > preco_entrada:
                    risco_retorno = calcular_risco_retorno_venda(preco_entrada, preco_stop, preco_alvo)
                else:
                    risco_retorno = None
                
                emoji = "🟢" if estado_de_trade == EstadoDeTrade.COMPRADO else "🔴"
                logger.trading(LogCategory.POSITION_STATUS, f"{emoji} Posição {estado_de_trade.value} ativa", MODULE_NAME,
                    symbol=cripto, estado_de_trade=estado_de_trade, preco_entrada=preco_entrada,
                    preco_stop=preco_stop, preco_alvo=preco_alvo, tamanho_posicao=tamanho_posicao,
                    trailing_stop=trailing_stop, risco_retorno=risco_retorno, 
                    stop_gain_ativo="Stop Gain ativado! Lucro garantido!" if (risco_retorno is None) else "Aguardando ajuste de stop")
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
    vela_executou_trade_entry_evaluator = None
    ultima_execucao_trade_conductor = None

    if estado_de_trade in [EstadoDeTrade.COMPRADO, EstadoDeTrade.VENDIDO]:
        if not executar_agente_no_start:
            ultima_execucao_trade_conductor = datetime.now()
            next_execution = ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)
            logger.info(LogCategory.AGENT_SCHEDULE, "Agente condutor não será executado no start", MODULE_NAME,
                symbol=cripto, proxima_execucao=next_execution.strftime("%Y-%m-%d %H:%M:%S"), 
                frequencia_agente_horas=frequencia_agente_horas, status="Aguardando stop, alvo ou avaliação do condutor")
    else:
        logger.info(LogCategory.TRADE_SEARCH, "🔍 Procurando oportunidades de trade", MODULE_NAME,
            subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao=lado_operacao.value)

    while True:
        # Verificar sinal de parada
        if stop_flag and stop_flag.is_set():
            logger.info(LogCategory.BOT_STOP, 
                "🛑 Bot recebeu sinal de parada da API", MODULE_NAME,
                symbol=cripto, bot_id=bot_id)
            break
        
        try:
            # Buscar dados com todas as EMAs necessárias (união das EMAs de compra e venda)
            df = busca_velas(cripto, tempo_grafico, [5, 15])
            df = df.drop(columns=['EMA_5', 'EMA_15'])
            df['ema_rapida_compra'] = df['fechamento'].ewm(span=ema_rapida_compra, adjust=False).mean()
            df['ema_lenta_compra'] = df['fechamento'].ewm(span=ema_lenta_compra, adjust=False).mean()
            df['ema_rapida_venda'] = df['fechamento'].ewm(span=ema_rapida_venda, adjust=False).mean()
            df['ema_lenta_venda'] = df['fechamento'].ewm(span=ema_lenta_venda, adjust=False).mean()

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
                            subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao=lado_operacao.value)

                elif estado_de_trade == EstadoDeTrade.VENDIDO:
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

                    if df['minima'].iloc[-1] <= preco_alvo:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        logger.trading(LogCategory.TARGET_HIT, "Take profit atingido", MODULE_NAME,
                            symbol=cripto, tempo_abertura=df.index[-1], preco_alvo=preco_alvo,
                            preco_atual=df['minima'].iloc[-1])
                    
                    elif df['maxima'].iloc[-1] >= preco_stop and preco_stop != 0:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        logger.trading(LogCategory.STOP_HIT, "Stop loss atingido", MODULE_NAME,
                            symbol=cripto, tempo_abertura=df.index[-1], preco_stop=preco_stop,
                            preco_atual=df['maxima'].iloc[-1])

                    elif estado_de_trade == EstadoDeTrade.DE_FORA:
                        vela_fechou_trade = df.index[-1]
                        logger.trading(LogCategory.MANUAL_CLOSE, "Trade fechado manualmente na corretora", MODULE_NAME,
                            symbol=cripto, tempo_abertura=df.index[-1])
                        logger.info("TRADE_SEARCH", "🔍 Procurando oportunidades de trade", MODULE_NAME,
                            subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao=lado_operacao.value)

                elif estado_de_trade == EstadoDeTrade.DE_FORA and df.index[-1] != vela_fechou_trade:
                    if compras_habilitadas:
                        vela_referencia_condition = df['fechamento'].iloc[-2] > df['ema_rapida_compra'].iloc[-2] and df['fechamento'].iloc[-2] > df['ema_lenta_compra'].iloc[-2]
                        breakout_condition = df['maxima'].iloc[-1] > df['maxima'].iloc[-2]
                        
                        if vela_referencia_condition and breakout_condition:
                            estado_de_trade, _, _, _, _, _ = tem_trade_aberto(cripto, subconta)
                            if estado_de_trade == EstadoDeTrade.DE_FORA:
                                if df.index[-1] != vela_executou_trade_entry_evaluator:
                                    logger.agent(LogCategory.AGENT_EXECUTION, "🤖 Iniciando análise de compra", MODULE_NAME,
                                        agent_name="Entry Evaluator", symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao="compra")
                                    vela_executou_trade_entry_evaluator = df.index[-1]

                                    saldo = saldo_da_conta(subconta)
                                    df_1w, df_1d, df = prepare_multi_timeframe_technical_data(df, cripto)
                                    df_1h = busca_velas(cripto, '60', [9, 21])
                                    df_1h = prepare_market_data(df_1h, use_emas=True, emas_periods=[200], use_peaks=True, peaks_distance=21)
                                    resposta = trade_entry_evaluator.run(prompt_trade_entry_evaluator(
                                        saldo, tempo_grafico, ema_rapida_compra, ema_lenta_compra, cripto,
                                        qtd_min_para_operar, subconta, 'compra', df, df_1w, df_1d, df_1h
                                    ))
                                    
                                    logger.agent(LogCategory.AGENT_RESPONSE, "Resposta do Entry Evaluator recebida", MODULE_NAME,
                                        agent_name="Entry Evaluator", symbol=cripto, response_length=len(resposta.content), response_content=resposta.content)
                                    
                                    abriu_trade = TradeEntryEvaluatorParser.processar_resposta(resposta, cripto, subconta, tempo_grafico, risco_por_operacao.value, logger)
                                    
                                    if abriu_trade:
                                        vela_abertura_trade = df.index[-1]
                                        ultima_execucao_trade_conductor = datetime.now()
                                        next_execution = (ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)).strftime('%Y-%m-%d %H:%M:%S')
                                        logger.agent(LogCategory.AGENT_SCHEDULE, "Análise do condutor programada", MODULE_NAME,
                                            agent_name="Trade Conductor", symbol=cripto, proxima_execucao=next_execution)
                                    else:
                                        logger.info(LogCategory.TRADE_SEARCH, "🔍 Procurando oportunidades de trade", MODULE_NAME,
                                            subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao=lado_operacao.value)

                    if vendas_habilitadas:
                        vela_venda_condition = df['fechamento'].iloc[-2] < df['ema_rapida_venda'].iloc[-2] and df['fechamento'].iloc[-2] < df['ema_lenta_venda'].iloc[-2]
                        breakout_condition = df['minima'].iloc[-1] < df['minima'].iloc[-2]
                        
                        if vela_venda_condition and breakout_condition:
                            estado_de_trade, _, _, _, _, _ = tem_trade_aberto(cripto, subconta)
                            if estado_de_trade == EstadoDeTrade.DE_FORA:
                                if df.index[-1] != vela_executou_trade_entry_evaluator:
                                    logger.agent(LogCategory.AGENT_EXECUTION, "🤖 Iniciando análise de venda", MODULE_NAME,
                                        agent_name="Entry Evaluator", symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao="venda")
                                    vela_executou_trade_entry_evaluator = df.index[-1]
                                    
                                    saldo = saldo_da_conta(subconta)
                                    df_1w, df_1d, df = prepare_multi_timeframe_technical_data(df, cripto)
                                    df_1h = busca_velas(cripto, '60', [9, 21])
                                    df_1h = prepare_market_data(df_1h, use_emas=True, emas_periods=[200], use_peaks=True, peaks_distance=21)
                                    resposta = trade_entry_evaluator.run(prompt_trade_entry_evaluator(
                                        saldo, tempo_grafico, ema_rapida_venda, ema_lenta_venda, cripto,
                                        qtd_min_para_operar, subconta, 'venda', df, df_1w, df_1d, df_1h
                                    ))
                                    
                                    logger.agent(LogCategory.AGENT_RESPONSE, "Resposta do Entry Evaluator recebida", MODULE_NAME,
                                        agent_name="Entry Evaluator", symbol=cripto, response_length=len(resposta.content), response_content=resposta.content)
                                    
                                    abriu_trade = TradeEntryEvaluatorParser.processar_resposta(resposta, cripto, subconta, tempo_grafico, risco_por_operacao.value, logger)
                                    
                                    if abriu_trade:
                                        vela_abertura_trade = df.index[-1]
                                        ultima_execucao_trade_conductor = datetime.now()
                                        next_execution = (ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)).strftime('%Y-%m-%d %H:%M:%S')
                                        logger.agent(LogCategory.AGENT_SCHEDULE, "Análise do condutor programada", MODULE_NAME,
                                            agent_name="Trade Conductor", symbol=cripto, proxima_execucao=next_execution)
                                    else:
                                        logger.info(LogCategory.TRADE_SEARCH, "🔍 Procurando oportunidades de trade", MODULE_NAME,
                                            subconta=subconta, symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao=lado_operacao.value)

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

    # Se chegou aqui, o bot foi encerrado pela API
    logger.info(LogCategory.BOT_STOP, "Bot encerrado pela API", MODULE_NAME,
        symbol=cripto, bot_id=bot_id)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--subconta', type=int, default=subconta)
    parser.add_argument('--cripto', type=str, default=cripto)
    parser.add_argument('--tempo_grafico', type=str, default=tempo_grafico)
    parser.add_argument('--lado_operacao', type=str, 
        default=lado_operacao.value, choices=[lado.value for lado in LadoOperacao],
        help='Modo de operação: compra, venda, ambos')
    parser.add_argument('--risco_por_operacao', type=float,
        default=risco_por_operacao.value, choices=[risco.value for risco in RiscoOperacao],
        help='Risco por operação: 0.005, 0.01, 0.02, 0.05, 0.08')
    parser.add_argument('--frequencia_agente_horas', type=float, default=frequencia_agente_horas)
    parser.add_argument('--executar_agente_no_start', type=bool, default=executar_agente_no_start,
        help='Executar agente condutor no start: True, False')
    
    # Parâmetros de compra
    parser.add_argument('--ema_rapida_compra', type=int, default=ema_rapida_compra)
    parser.add_argument('--ema_lenta_compra', type=int, default=ema_lenta_compra)
    
    # Parâmetros de venda
    parser.add_argument('--ema_rapida_venda', type=int, default=ema_rapida_venda)
    parser.add_argument('--ema_lenta_venda', type=int, default=ema_lenta_venda)
    
    args = parser.parse_args()
    start_live_trading_bot(
        subconta=args.subconta,
        cripto=args.cripto,
        tempo_grafico=args.tempo_grafico,
        lado_operacao=LadoOperacao(args.lado_operacao),
        frequencia_agente_horas=args.frequencia_agente_horas,
        executar_agente_no_start=args.executar_agente_no_start,
        ema_rapida_compra=args.ema_rapida_compra,
        ema_lenta_compra=args.ema_lenta_compra,
        ema_rapida_venda=args.ema_rapida_venda,
        ema_lenta_venda=args.ema_lenta_venda,
        risco_por_operacao=RiscoOperacao(args.risco_por_operacao)
    ) 