"""
Módulo para controle de execução de agentes em live trading.

Este módulo centraliza funções relacionadas ao controle temporal
e execução de agentes durante operações de live trading.
"""

from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentes.trade_conductor_v2 import trade_conductor
from agentes.prompts.trade_conductor_prompt import prompt_trade_conductor
from agentes.parsers.trade_conductor_parser import TradeConductorParser
from managers.data_manager import prepare_multi_timeframe_technical_data, prepare_market_data
from corretoras.funcoes_bybit import busca_velas, fecha_compra, fecha_venda, ajusta_stop, ajusta_alvo, aciona_trailing_stop_imediato, aciona_trailing_stop_preco, fecha_parcial_compra, fecha_parcial_venda

from utils.utilidades import quantidade_cripto_para_parcial
from entidades.estado_trade import EstadoDeTrade
from utils.logging import LogCategory

# Nome do módulo para logs (automático)
MODULE_NAME = Path(__file__).stem

def executar_trade_conductor_se_necessario(
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
):
    """
    Executa o trade_conductor se necessário (a cada X horas definido pela frequência).
    
    Args:
        ultima_execucao_trade_conductor: Timestamp da última execução do agente
        frequencia_agente: Frequência em horas para execução do agente
        df: DataFrame com dados de mercado
        cripto: Par de criptomoedas (ex: 'SOLUSDT')
        subconta: ID da subconta
        tempo_grafico: Timeframe dos dados (ex: '15')
        estado_de_trade: Estado atual do trade
        preco_entrada: Preço de entrada do trade
        preco_alvo: Preço alvo do trade
        preco_stop: Preço de stop do trade
        tamanho_posicao: Tamanho da posição do trade
        trailing_stop: Trailing stop do trade
        vela_abertura_trade: Timestamp da vela de abertura do trade
    
    Returns:
        datetime: Nova última execução ou a anterior se não executou
    """
    agora = datetime.now()
    deve_executar_trade_conductor = (
        ultima_execucao_trade_conductor is None or                                                      # primeira execução ou com novo trade aberto
        agora - ultima_execucao_trade_conductor >= timedelta(hours=frequencia_agente_horas)       # tempo de intervalo padrão entre execuções
        # (agora - ultima_execucao_trade_conductor >= timedelta(hours=frequencia_agente_horas/2) and (    # condições para execução em intervalo menor
        #     df['fechamento'].iloc[-2] > df['maxima'].iloc[-13:-2].max() or
        #     df['fechamento'].iloc[-2] < df['minima'].iloc[-13:-2].min() or
        #     df['volume'].iloc[-2] > df['volume_sma'].iloc[-2] * 1.5 or
        #     df['maxima'].iloc[-2] >= (preco_alvo + preco_entrada) / 2 (para compra) or
        #     df['minima'].iloc[-2] <= (preco_alvo + preco_entrada) / 2 (para venda)
        # )) or
        # (agora - ultima_execucao_trade_conductor >= timedelta(minutes=tempo_grafico) and (    # condições para execução a cada vela
        #     df['volume'].iloc[-2] > df['volume_sma'].iloc[-2] * 2 or
        #     df['rsi'].iloc[-2] > 85 or
        #     df['rsi'].iloc[-2] < 15 or
        #     df['maxima'].iloc[-1] >= preco_alvo * 0.99 (para compra) or
        #     df['minima'].iloc[-1] <= preco_stop * 1.01 (para venda)
        # ))
    )
    
    if deve_executar_trade_conductor:
        df_1w, df_1d, df = prepare_multi_timeframe_technical_data(df, cripto)
        df_1h = busca_velas(cripto, '60', [9, 21])
        df_1h = prepare_market_data(df_1h, use_emas=True, emas_periods=[200], use_peaks=True, peaks_distance=21)

        logger.agent(LogCategory.AGENT_EXECUTION, "🤖 Iniciando análise do trade conductor", MODULE_NAME, 
            agent_name="Trade Conductor", timestamp=agora.strftime('%Y-%m-%d %H:%M:%S'), symbol=cripto, timeframe=tempo_grafico)
        
        resposta = trade_conductor.run(prompt_trade_conductor(
            subconta,
            tempo_grafico,
            cripto,
            estado_de_trade,
            preco_entrada,
            preco_alvo,
            preco_stop,
            tamanho_posicao,
            trailing_stop,
            df,
            df_1w,
            df_1d,
            df_1h,
            vela_abertura_trade,
        ))
        
        logger.agent(LogCategory.AGENT_RESPONSE, f"Resposta do trade conductor recebida", MODULE_NAME,
            agent_name="Trade Conductor", symbol=cripto, response_length=len(resposta.content), subconta=subconta, 
            response_content=resposta.content)
        
        parser = TradeConductorParser()
        resposta_json = parser.parse_response(resposta.content)

        if resposta_json is None:
            logger.error(LogCategory.PARSING_ERROR, "Resposta inválida do trade conductor - falha no parsing", MODULE_NAME,
                symbol=cripto, response_preview=resposta.content[:100] if resposta.content else "Empty response")
            return ultima_execucao_trade_conductor

        confianca = resposta_json.get('confianca', 0.0)
        acoes = resposta_json.get('acoes', [])
        # justificativa = resposta_json.get('justificativa', '')
        
        # logger.agent("AGENT_DECISION", "Análise do trade conductor concluída", MODULE_NAME,
        #             symbol=cripto, confidence=confianca, actions_count=len(acoes), 
        #             has_justification=bool(justificativa))

        if confianca < 0.75:
            logger.agent(LogCategory.AGENT_DECISION, "Confiança baixa - não executando ações do agente", MODULE_NAME,
                agent_name="Trade Conductor", symbol=cripto, confidence=confianca, threshold=0.75, decision="NO_ACTION", action="confiança_baixa")
        else:
            if acoes:
                for acao in acoes:
                    try:
                        if acao.get('acao') == 'manter':
                            logger.agent(LogCategory.AGENT_ACTION, "Manter posição", MODULE_NAME,
                                agent_name="Trade Conductor", symbol=cripto, action="manter", confidence=confianca)

                        if acao.get('acao') == 'fechar_compra':
                            logger.agent(LogCategory.AGENT_ACTION, "Executando fechamento de posição LONG", MODULE_NAME,
                                agent_name="Trade Conductor", symbol=cripto, side="SELL", action="fechar_compra", confidence=confianca)
                            fecha_compra(cripto, subconta)
                        if acao.get('acao') == 'fechar_venda':
                            logger.agent(LogCategory.AGENT_ACTION, "Executando fechamento de posição SHORT", MODULE_NAME,
                                agent_name="Trade Conductor", symbol=cripto, side="BUY", action="fechar_venda", confidence=confianca)
                            fecha_venda(cripto, subconta)

                        if acao.get('acao') == 'ajustar_stop':
                            preco_stop_novo = acao.get('preco_stop')
                            detalhes = f"Stop antigo: {preco_stop}, Novo stop: {preco_stop_novo}" if preco_stop_novo else ""
                            if ((estado_de_trade == EstadoDeTrade.COMPRADO and preco_stop_novo > preco_stop) 
                                or (estado_de_trade == EstadoDeTrade.VENDIDO and preco_stop_novo < preco_stop)):
                                logger.agent(LogCategory.AGENT_ACTION, "Ajustando stop loss da posição", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, old_stop=preco_stop, new_stop=preco_stop_novo, 
                                    action="ajustar_stop", confidence=confianca, details=detalhes)
                                ajusta_stop(cripto, preco_stop_novo, subconta)
                            else:
                                logger.agent(LogCategory.AGENT_DECISION, "Tentativa de ajustar stop loss para uma perda maior ou ganho menor do que a atual", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, old_stop=preco_stop, new_stop=preco_stop_novo, 
                                    action="ajustar_stop", confidence=confianca, details=detalhes, decision="NO_ACTION")

                        if acao.get('acao') == 'ajustar_alvo':
                            preco_alvo_novo = acao.get('preco_alvo')
                            detalhes = f"Alvo antigo: {preco_alvo}, Novo alvo: {preco_alvo_novo}" if preco_alvo_novo else ""
                            logger.agent(LogCategory.AGENT_ACTION, "Ajustando take profit da posição", MODULE_NAME,
                                agent_name="Trade Conductor", symbol=cripto, old_target=preco_alvo, new_target=preco_alvo_novo,
                                action="ajustar_alvo", confidence=confianca, details=detalhes)
                            ajusta_alvo(cripto, preco_alvo_novo, subconta)

                        if acao.get('acao') == 'acionar_trailing_stop_imediato':
                            if trailing_stop == 0:
                                preco_trailing = acao.get('preco_trailing')
                                detalhes = f"Trailing Stop: {preco_trailing}" if preco_trailing else ""
                                logger.agent(LogCategory.AGENT_ACTION, "Acionando trailing stop imediato", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, trailing_price=preco_trailing, action="acionar_trailing_stop_imediato",
                                    confidence=confianca, details=detalhes)
                                aciona_trailing_stop_imediato(cripto, str(preco_trailing), subconta)
                            else:
                                logger.agent(LogCategory.AGENT_DECISION, "Tentativa de criar trailing stop quando já existe um ativo", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, current_trailing_stop=trailing_stop, action="trailing_stop_ja_existe", decision="NO_ACTION")
                        if acao.get('acao') == 'acionar_trailing_stop_preco':
                            if trailing_stop == 0:
                                preco_trailing = acao.get('preco_trailing')
                                preco_acionamento = acao.get('preco_acionamento')
                                detalhes = f"Trailing Stop: {preco_trailing}, Ativação: {preco_acionamento}" if preco_trailing and preco_acionamento else ""
                                logger.agent(LogCategory.AGENT_ACTION, "Acionando trailing stop com preço de ativação", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, trailing_price=preco_trailing, activation_price=preco_acionamento,
                                    action="acionar_trailing_stop_preco", confidence=confianca, details=detalhes)
                                aciona_trailing_stop_preco(cripto, str(preco_trailing), str(preco_acionamento), subconta)
                            else:
                                logger.agent(LogCategory.AGENT_DECISION, "Tentativa de criar trailing stop com preço quando já existe um ativo", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, current_trailing_stop=trailing_stop, action="trailing_stop_ja_existe", decision="NO_ACTION")

                        if acao.get('acao') == 'realizar_parcial':
                            percentual = acao.get('percentual')
                            quantidade_cripto_parcial = quantidade_cripto_para_parcial(tamanho_posicao, percentual, qtd_min_para_operar)
                            if estado_de_trade == EstadoDeTrade.COMPRADO:
                                detalhes = f"Percentual: {percentual}%" if percentual else ""
                                logger.agent(LogCategory.AGENT_ACTION, "Realizando fechamento parcial de posição LONG", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, side="SELL", percentage=percentual, partial_quantity=quantidade_cripto_parcial,
                                    total_position=tamanho_posicao, action="realizar_parcial", confidence=confianca, details=detalhes)
                                # fecha_parcial_compra(cripto, quantidade_cripto_parcial, subconta)
                            elif estado_de_trade == EstadoDeTrade.VENDIDO:
                                detalhes = f"Percentual: {percentual}%" if percentual else ""
                                logger.agent(LogCategory.AGENT_ACTION, "Realizando fechamento parcial de posição SHORT", MODULE_NAME,
                                    agent_name="Trade Conductor", symbol=cripto, side="BUY", percentage=percentual, partial_quantity=quantidade_cripto_parcial,
                                    total_position=tamanho_posicao, action="realizar_parcial", confidence=confianca, details=detalhes)
                                # fecha_parcial_venda(cripto, quantidade_cripto_parcial, subconta)
                                
                    except ConnectionError as ce:
                        logger.error(LogCategory.CONNECTION_ERROR, f"Erro de conexão ao executar ação do agente", MODULE_NAME,
                            symbol=cripto, action=acao.get("acao", ""), error_message=str(ce), exception=ce)
                    except ValueError as ve:
                        logger.error(LogCategory.VALUE_ERROR, f"Erro de valor ao executar ação do agente", MODULE_NAME,
                            symbol=cripto, action=acao.get("acao", ""), error_message=str(ve), exception=ve)
                    except Exception as e:
                        logger.error(LogCategory.EXECUTION_ERROR, f"Erro desconhecido ao executar ação do agente", MODULE_NAME,
                            symbol=cripto, action=acao.get("acao", ""), error_message=str(e), exception=e)
        next_execution = agora + timedelta(hours=frequencia_agente_horas)
        logger.agent(LogCategory.AGENT_SCHEDULE, "Próxima execução do trade conductor programada", MODULE_NAME,
            agent_name="Trade Conductor", symbol=cripto, next_execution=next_execution.strftime('%Y-%m-%d %H:%M:%S'), 
            frequency_hours=frequencia_agente_horas)
        
        return agora
    
    return ultima_execucao_trade_conductor