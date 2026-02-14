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
# Import absoluto ao invés de relativo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from live_trading.agent_execution_with_parser import executar_trade_conductor_se_necessario
from corretoras.funcoes_bybit import ajusta_stop
from agentes.trade_entry_evaluator import trade_entry_evaluator
from agentes.prompts.trade_entry_evaluator import prompt_trade_entry_evaluator
from agentes.parsers.trade_entry_evaluator_parser import TradeEntryEvaluatorParser
from managers.data_manager import prepare_multi_timeframe_technical_data, prepare_market_data
from utils.utilidades import risco_retorno_compra, risco_retorno_venda
from utils.logging import get_logger, LogCategory

# Nome do módulo para logs (automático)
MODULE_NAME = Path(__file__).stem

# Valores padrão
subconta = 1
cripto = 'BTCUSDT'
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

# Trailing Stop Configuration
BREAK_EVEN_PROGRESSO = 0.5  # 50%
TRAILING_STOP_PROGRESSO = 0.75  # 75%
TRAILING_STOP_RECUO_COMPRA = 0.99  # 1%
TRAILING_STOP_RECUO_VENDA = 1.01  # 1%

def avaliar_condicoes_de_saida(df, estado_de_trade, preco_alvo, preco_stop, logger, cripto):
    """Avalia se as condições de saída (take profit ou stop loss) foram atingidas."""
    vela_fechou_trade = None
    novo_estado = estado_de_trade

    if estado_de_trade == EstadoDeTrade.COMPRADO:
        if df['maxima'].iloc[-1] >= preco_alvo and preco_alvo != 0:
            novo_estado = EstadoDeTrade.DE_FORA
            vela_fechou_trade = df.index[-1]
            logger.trading(LogCategory.TARGET_HIT, "Take profit atingido", MODULE_NAME,
                          symbol=cripto, tempo_abertura=df.index[-1], preco_alvo=preco_alvo,
                          preco_atual=df['maxima'].iloc[-1])
        elif df['minima'].iloc[-1] <= preco_stop:
            novo_estado = EstadoDeTrade.DE_FORA
            vela_fechou_trade = df.index[-1]
            logger.trading(LogCategory.STOP_HIT, "Stop loss atingido", MODULE_NAME,
                          symbol=cripto, tempo_abertura=df.index[-1], preco_stop=preco_stop,
                          preco_atual=df['minima'].iloc[-1])
    elif estado_de_trade == EstadoDeTrade.VENDIDO:
        if df['minima'].iloc[-1] <= preco_alvo:
            novo_estado = EstadoDeTrade.DE_FORA
            vela_fechou_trade = df.index[-1]
            logger.trading(LogCategory.TARGET_HIT, "Take profit atingido", MODULE_NAME,
                          symbol=cripto, tempo_abertura=df.index[-1], preco_alvo=preco_alvo,
                          preco_atual=df['minima'].iloc[-1])
        elif df['maxima'].iloc[-1] >= preco_stop and preco_stop != 0:
            novo_estado = EstadoDeTrade.DE_FORA
            vela_fechou_trade = df.index[-1]
            logger.trading(LogCategory.STOP_HIT, "Stop loss atingido", MODULE_NAME,
                          symbol=cripto, tempo_abertura=df.index[-1], preco_stop=preco_stop,
                          preco_atual=df['maxima'].iloc[-1])

    return novo_estado, vela_fechou_trade


def gerenciar_trailing_stop(df, estado_de_trade, preco_entrada, preco_stop, preco_alvo, cripto, subconta, logger, is_simulator):
    """Gerencia a lógica de trailing stop inteligente."""
    preco_atual = df['fechamento'].iloc[-1]
    novo_preco_stop = preco_stop

    if estado_de_trade == EstadoDeTrade.COMPRADO and preco_alvo > preco_entrada:
        distancia_pnl = preco_atual - preco_entrada
        distancia_alvo = preco_alvo - preco_entrada
        if distancia_pnl > 0:
            progresso = distancia_pnl / distancia_alvo
            if progresso >= BREAK_EVEN_PROGRESSO and preco_stop < preco_entrada:
                novo_preco_stop = preco_entrada
                logger.trading(LogCategory.POSITION_UPDATE, "🛡️ Break-even ativado! Stop movido para entrada", MODULE_NAME,
                              symbol=cripto, preco_stop=novo_preco_stop, progresso=f"{progresso*100:.1f}%")
            elif progresso >= TRAILING_STOP_PROGRESSO:
                stop_proposto = round(preco_atual * TRAILING_STOP_RECUO_COMPRA, 2)
                if stop_proposto > novo_preco_stop:
                    novo_preco_stop = stop_proposto
                    logger.trading(LogCategory.POSITION_UPDATE, "📈 Trailing Stop subindo!", MODULE_NAME,
                                  symbol=cripto, preco_stop=novo_preco_stop, preco_atual=preco_atual)

    elif estado_de_trade == EstadoDeTrade.VENDIDO and preco_alvo < preco_entrada:
        distancia_pnl = preco_entrada - preco_atual
        distancia_alvo = preco_entrada - preco_alvo
        if distancia_pnl > 0:
            progresso = distancia_pnl / distancia_alvo
            if progresso >= BREAK_EVEN_PROGRESSO and preco_stop > preco_entrada:
                novo_preco_stop = preco_entrada
                logger.trading(LogCategory.POSITION_UPDATE, "🛡️ Break-even ativado! Stop movido para entrada", MODULE_NAME,
                              symbol=cripto, preco_stop=novo_preco_stop, progresso=f"{progresso*100:.1f}%")
            elif progresso >= TRAILING_STOP_PROGRESSO:
                stop_proposto = round(preco_atual * TRAILING_STOP_RECUO_VENDA, 2)
                if stop_proposto < novo_preco_stop:
                    novo_preco_stop = stop_proposto
                    logger.trading(LogCategory.POSITION_UPDATE, "📈 Trailing Stop descendo!", MODULE_NAME,
                                  symbol=cripto, preco_stop=novo_preco_stop, preco_atual=preco_atual)
    
    if novo_preco_stop != preco_stop and not is_simulator:
        ajusta_stop(cripto, novo_preco_stop, subconta)
        
    return novo_preco_stop

def gerenciar_trade_aberto(
    estado_de_trade, df, cripto, subconta, tempo_grafico,
    frequencia_agente_horas, ultima_execucao_trade_conductor, vela_abertura_trade,
    qtd_min_para_operar, logger, is_simulator,
    preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop
):
    """Gerencia um trade que já está aberto, verificando saídas e ajustando stops."""
    estado_de_trade_atual = estado_de_trade
    if not is_simulator:
        (estado_de_trade_atual, preco_entrada, preco_stop, 
         preco_alvo, tamanho_posicao, trailing_stop) = tem_trade_aberto(cripto, subconta)
        if estado_de_trade_atual == EstadoDeTrade.DE_FORA:
             # Trade foi fechado manualmente ou por um evento não capturado
             vela_fechou_trade = df.index[-1]
             logger.trading(LogCategory.MANUAL_CLOSE, "Trade fechado (detectado)", MODULE_NAME, symbol=cripto, tempo_abertura=df.index[-1])
             return EstadoDeTrade.DE_FORA, vela_fechou_trade, ultima_execucao_trade_conductor, 0,0,0,0,0
    
    ultima_execucao_trade_conductor = executar_trade_conductor_se_necessario(
        ultima_execucao_trade_conductor, frequencia_agente_horas, df, cripto, subconta,
        tempo_grafico, estado_de_trade_atual, preco_entrada, preco_alvo, preco_stop,
        tamanho_posicao, qtd_min_para_operar, trailing_stop, vela_abertura_trade, logger
    )

    novo_estado, vela_fechou_trade = avaliar_condicoes_de_saida(df, estado_de_trade_atual, preco_alvo, preco_stop, logger, cripto)

    if novo_estado != estado_de_trade_atual:
        return novo_estado, vela_fechou_trade, ultima_execucao_trade_conductor, 0,0,0,0,0

    # Gerenciar trailing stop
    preco_stop_novo = gerenciar_trailing_stop(df, estado_de_trade_atual, preco_entrada, preco_stop, preco_alvo, cripto, subconta, logger, is_simulator)

    # Retornar o estado atualizado
    return estado_de_trade_atual, None, ultima_execucao_trade_conductor, preco_entrada, preco_stop_novo, preco_alvo, tamanho_posicao, trailing_stop

def verificar_sinais_de_entrada(
    df, cripto, subconta, tempo_grafico, lado_operacao, risco_por_operacao,
    compras_habilitadas, vendas_habilitadas,
    ema_rapida_compra, ema_lenta_compra, ema_rapida_venda, ema_lenta_venda,
    vela_executou_trade_entry_evaluator, qtd_min_para_operar, frequencia_agente_horas, logger, is_simulator
):
    """Verifica sinais de entrada e executa o agente Entry Evaluator se necessário."""
    novo_estado = EstadoDeTrade.DE_FORA
    vela_abertura_trade = None
    ultima_execucao_trade_conductor = None
    
    # As variáveis de preço e posição para o modo simulador
    preco_entrada_sim, preco_stop_sim, preco_alvo_sim, tamanho_posicao_sim = 0, 0, 0, 0

    # --- LÓGICA DE COMPRA ---
    if compras_habilitadas:
        condicao_ref = df['fechamento'].iloc[-2] > df['ema_rapida_compra'].iloc[-2] and df['fechamento'].iloc[-2] > df['ema_lenta_compra'].iloc[-2]
        condicao_breakout = df['maxima'].iloc[-1] > df['maxima'].iloc[-2]
        
        if condicao_ref and condicao_breakout and df.index[-1] != vela_executou_trade_entry_evaluator:
            logger.agent(LogCategory.AGENT_EXECUTION, "🤖 Iniciando análise de compra", MODULE_NAME,
                         agent_name="Entry Evaluator", symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao="compra")
            
            saldo = saldo_da_conta(subconta) if not is_simulator else 10000 # Saldo simulado
            df_1w, df_1d, df_temp = prepare_multi_timeframe_technical_data(df.copy(), cripto)
            df_1h = busca_velas(cripto, '60', [9, 21])
            df_1h = prepare_market_data(df_1h, use_emas=True, emas_periods=[200], use_peaks=True, peaks_distance=21)
            
            resposta = trade_entry_evaluator.run(prompt_trade_entry_evaluator(
                saldo, tempo_grafico, ema_rapida_compra, ema_lenta_compra, cripto,
                qtd_min_para_operar, subconta, 'compra', df_temp, df_1w, df_1d, df_1h
            ))
            
            logger.agent(LogCategory.AGENT_RESPONSE, "Resposta do Entry Evaluator (Compra)", MODULE_NAME,
                         agent_name="Entry Evaluator", response_length=len(resposta.content))
            
            abriu_trade = TradeEntryEvaluatorParser.processar_resposta(resposta, cripto, subconta, tempo_grafico, risco_por_operacao.value, logger, is_simulator=is_simulator)
            
            if abriu_trade:
                novo_estado = EstadoDeTrade.COMPRADO
                vela_abertura_trade = df.index[-1]
                ultima_execucao_trade_conductor = datetime.now()
                next_execution = (ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)).strftime('%Y-%m-%d %H:%M:%S')
                logger.agent(LogCategory.AGENT_SCHEDULE, "Análise do condutor programada", MODULE_NAME,
                             agent_name="Trade Conductor", symbol=cripto, proxima_execucao=next_execution)
                
                if is_simulator:
                    preco_atual = df['fechamento'].iloc[-1]
                    parsed = TradeEntryEvaluatorParser().parse_response(resposta.content)
                    acao = next((a for a in parsed['acoes'] if a['acao'] == 'comprar'), None)
                    if acao:
                        preco_entrada_sim = preco_atual
                        preco_stop_sim = acao['preco_stop']
                        preco_alvo_sim = acao['preco_alvo']
                        tamanho_posicao_sim = 1
                
                # Retorna imediatamente após encontrar um trade
                return novo_estado, vela_abertura_trade, ultima_execucao_trade_conductor, df.index[-1], preco_entrada_sim, preco_stop_sim, preco_alvo_sim, tamanho_posicao_sim

    # --- LÓGICA DE VENDA ---
    if vendas_habilitadas:
        condicao_ref = df['fechamento'].iloc[-2] < df['ema_rapida_venda'].iloc[-2] and df['fechamento'].iloc[-2] < df['ema_lenta_venda'].iloc[-2]
        condicao_breakout = df['minima'].iloc[-1] < df['minima'].iloc[-2]
        
        if condicao_ref and condicao_breakout and df.index[-1] != vela_executou_trade_entry_evaluator:
            logger.agent(LogCategory.AGENT_EXECUTION, "🤖 Iniciando análise de venda", MODULE_NAME,
                         agent_name="Entry Evaluator", symbol=cripto, tempo_grafico=tempo_grafico, lado_operacao="venda")

            saldo = saldo_da_conta(subconta) if not is_simulator else 10000 # Saldo simulado
            df_1w, df_1d, df_temp = prepare_multi_timeframe_technical_data(df.copy(), cripto)
            df_1h = busca_velas(cripto, '60', [9, 21])
            df_1h = prepare_market_data(df_1h, use_emas=True, emas_periods=[200], use_peaks=True, peaks_distance=21)
            
            resposta = trade_entry_evaluator.run(prompt_trade_entry_evaluator(
                saldo, tempo_grafico, ema_rapida_venda, ema_lenta_venda, cripto,
                qtd_min_para_operar, subconta, 'venda', df_temp, df_1w, df_1d, df_1h
            ))
            
            logger.agent(LogCategory.AGENT_RESPONSE, "Resposta do Entry Evaluator (Venda)", MODULE_NAME,
                         agent_name="Entry Evaluator", response_length=len(resposta.content))
            
            abriu_trade = TradeEntryEvaluatorParser.processar_resposta(resposta, cripto, subconta, tempo_grafico, risco_por_operacao.value, logger, is_simulator=is_simulator)
            
            if abriu_trade:
                novo_estado = EstadoDeTrade.VENDIDO
                vela_abertura_trade = df.index[-1]
                ultima_execucao_trade_conductor = datetime.now()
                next_execution = (ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)).strftime('%Y-%m-%d %H:%M:%S')
                logger.agent(LogCategory.AGENT_SCHEDULE, "Análise do condutor programada", MODULE_NAME,
                             agent_name="Trade Conductor", symbol=cripto, proxima_execucao=next_execution)
                
                if is_simulator:
                    preco_atual = df['fechamento'].iloc[-1]
                    parsed = TradeEntryEvaluatorParser().parse_response(resposta.content)
                    acao = next((a for a in parsed['acoes'] if a['acao'] == 'vender'), None)
                    if acao:
                        preco_entrada_sim = preco_atual
                        preco_stop_sim = acao['preco_stop']
                        preco_alvo_sim = acao['preco_alvo']
                        tamanho_posicao_sim = 1

                # Retorna imediatamente após encontrar um trade
                return novo_estado, vela_abertura_trade, ultima_execucao_trade_conductor, df.index[-1], preco_entrada_sim, preco_stop_sim, preco_alvo_sim, tamanho_posicao_sim


    # Se nenhum trade foi aberto
    return EstadoDeTrade.DE_FORA, None, None, vela_executou_trade_entry_evaluator, 0, 0, 0, 0

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
    stop_flag = None,
    is_simulator = False
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
        ema_lenta_venda=ema_lenta_venda if vendas_habilitadas else None,
        is_simulator=is_simulator
    )

    estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = EstadoDeTrade.DE_FORA, 0, 0, 0, 0, 0
    qtd_min_para_operar = 0

    for tentativa in range(5):
        try:
            if not is_simulator:
                estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = tem_trade_aberto(cripto, subconta)
            qtd_min_para_operar = quantidade_minima_para_operar(cripto, subconta)
            
            if estado_de_trade in [EstadoDeTrade.COMPRADO, EstadoDeTrade.VENDIDO]:
                risco_retorno = None
                if estado_de_trade == EstadoDeTrade.COMPRADO and preco_stop < preco_entrada:
                    risco_retorno = risco_retorno_compra(preco_entrada, preco_stop, preco_alvo)
                elif estado_de_trade == EstadoDeTrade.VENDIDO and preco_stop > preco_entrada:
                    risco_retorno = risco_retorno_venda(preco_entrada, preco_stop, preco_alvo)
                
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
                time.sleep(2)
            else:
                logger.critical(LogCategory.FATAL_ERROR, "Não foi possível buscar estado do trade. Encerrando.", MODULE_NAME)
                return

    vela_abertura_trade = None
    vela_fechou_trade = None
    vela_executou_trade_entry_evaluator = None
    ultima_execucao_trade_conductor = None

    if estado_de_trade in [EstadoDeTrade.COMPRADO, EstadoDeTrade.VENDIDO] and not executar_agente_no_start:
        ultima_execucao_trade_conductor = datetime.now()
        next_execution = ultima_execucao_trade_conductor + timedelta(hours=frequencia_agente_horas)
        logger.info(LogCategory.AGENT_SCHEDULE, "Agente condutor não será executado no start", MODULE_NAME,
            proxima_execucao=next_execution.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        logger.info(LogCategory.TRADE_SEARCH, "🔍 Procurando oportunidades de trade", MODULE_NAME, symbol=cripto)

    while True:
        if stop_flag and stop_flag.is_set():
            logger.info(LogCategory.BOT_STOP, "🛑 Bot recebeu sinal de parada da API", MODULE_NAME, bot_id=bot_id)
            break
        
        try:
            # A busca de velas e cálculo de EMA foi movido para dentro do loop principal
            # para garantir que os dados sejam sempre os mais recentes.
            unique_emas = set([ema_rapida_compra, ema_lenta_compra, ema_rapida_venda, ema_lenta_venda])
            df = busca_velas(cripto, tempo_grafico, list(unique_emas))

            if df.empty:
                logger.warning(LogCategory.EMPTY_DATA, "DataFrame vazio", MODULE_NAME, symbol=cripto)
                time.sleep(5) # Espera um pouco mais se não houver dados
                continue

            df['ema_rapida_compra'] = df['fechamento'].ewm(span=ema_rapida_compra, adjust=False).mean()
            df['ema_lenta_compra'] = df['fechamento'].ewm(span=ema_lenta_compra, adjust=False).mean()
            df['ema_rapida_venda'] = df['fechamento'].ewm(span=ema_rapida_venda, adjust=False).mean()
            df['ema_lenta_venda'] = df['fechamento'].ewm(span=ema_lenta_venda, adjust=False).mean()

            if estado_de_trade in [EstadoDeTrade.COMPRADO, EstadoDeTrade.VENDIDO]:
                (estado_de_trade, vela_fechou_trade, ultima_execucao_trade_conductor, 
                 preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop) = gerenciar_trade_aberto(
                    estado_de_trade, df, cripto, subconta, tempo_grafico,
                    frequencia_agente_horas, ultima_execucao_trade_conductor,
                    vela_abertura_trade, qtd_min_para_operar, logger, is_simulator,
                    preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop
                )
                if vela_fechou_trade:
                     logger.info(LogCategory.TRADE_SEARCH, "🔍 Procurando novas oportunidades de trade", MODULE_NAME, symbol=cripto)

            elif estado_de_trade == EstadoDeTrade.DE_FORA and df.index[-1] != vela_fechou_trade:
                (estado_de_trade, vela_abertura_trade, ultima_execucao_trade_conductor, 
                 vela_executou_trade_entry_evaluator, preco_entrada, preco_stop, preco_alvo, tamanho_posicao) = verificar_sinais_de_entrada(
                    df, cripto, subconta, tempo_grafico, lado_operacao, risco_por_operacao,
                    compras_habilitadas, vendas_habilitadas,
                    ema_rapida_compra, ema_lenta_compra, ema_rapida_venda, ema_lenta_venda,
                    vela_executou_trade_entry_evaluator, qtd_min_para_operar, frequencia_agente_horas, logger, is_simulator
                 )

        except ConnectionError as ce:
            logger.error(LogCategory.CONNECTION_ERROR, f"Erro de conexão: {ce}", MODULE_NAME, exception=ce)
        except ValueError as ve:
            logger.error(LogCategory.VALUE_ERROR, f"Erro de valor: {ve}", MODULE_NAME, exception=ve)
        except KeyboardInterrupt:
            logger.info(LogCategory.SHUTDOWN, "Programa encerrado pelo usuário.", MODULE_NAME)
            break
        except Exception as e:
            logger.error(LogCategory.UNKNOWN_ERROR, f"Erro inesperado: {e}", MODULE_NAME, exception=e)

        time.sleep(0.25)

    logger.info(LogCategory.BOT_STOP, "Bot encerrado.", MODULE_NAME, bot_id=bot_id)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Bot de trading para Bybit com estratégia de breakout de EMA e avaliação por agente de IA.')
    
    # Argumentos principais
    parser.add_argument('--subconta', type=int, default=subconta, help='ID da subconta a ser usada.')
    parser.add_argument('--cripto', type=str, default=cripto, help='Símbolo da criptomoeda (ex: BTCUSDT).')
    parser.add_argument('--tempo_grafico', type=str, default=tempo_grafico, help='Tempo gráfico (ex: 15 para 15 minutos).')
    
    # Configurações da Estratégia
    parser.add_argument('--lado_operacao', type=str, default=lado_operacao.value, choices=[lado.value for lado in LadoOperacao], help='Lado da operação: "compra", "venda" ou "ambos".')
    parser.add_argument('--risco_por_operacao', type=float, default=risco_por_operacao.value, choices=[risco.value for risco in RiscoOperacao], help='Percentual de risco por operação.')
    
    # Parâmetros de EMA para Compra
    parser.add_argument('--ema_rapida_compra', type=int, default=ema_rapida_compra, help='Período da EMA rápida para compras.')
    parser.add_argument('--ema_lenta_compra', type=int, default=ema_lenta_compra, help='Período da EMA lenta para compras.')
    
    # Parâmetros de EMA para Venda
    parser.add_argument('--ema_rapida_venda', type=int, default=ema_rapida_venda, help='Período da EMA rápida para vendas.')
    parser.add_argument('--ema_lenta_venda', type=int, default=ema_lenta_venda, help='Período da EMA lenta para vendas.')

    # Configurações do Agente
    parser.add_argument('--frequencia_agente_horas', type=float, default=frequencia_agente_horas, help='Frequência de execução do agente condutor em horas.')
    parser.add_argument('--executar_agente_no_start', action='store_true', help='Se definido, executa o agente condutor no início, mesmo se houver um trade aberto.')

    # Modo de Simulação
    parser.add_argument('--is_simulator', action='store_true', help='Se definido, executa o bot em modo de simulação sem interagir com a corretora.')
    
    args = parser.parse_args()
    
    # Corrigir o tipo de argumento booleano que vem do argparse
    exec_on_start_flag = True if args.executar_agente_no_start else executar_agente_no_start
    is_sim_flag = True if args.is_simulator else is_simulator

    start_live_trading_bot(
        subconta=args.subconta,
        cripto=args.cripto,
        tempo_grafico=args.tempo_grafico,
        lado_operacao=LadoOperacao(args.lado_operacao),
        frequencia_agente_horas=args.frequencia_agente_horas,
        executar_agente_no_start=exec_on_start_flag,
        ema_rapida_compra=args.ema_rapida_compra,
        ema_lenta_compra=args.ema_lenta_compra,
        ema_rapida_venda=args.ema_rapida_venda,
        ema_lenta_venda=args.ema_lenta_venda,
        risco_por_operacao=RiscoOperacao(args.risco_por_operacao),
        is_simulator=is_sim_flag
    ) 