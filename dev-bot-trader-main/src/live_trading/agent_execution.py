"""
Módulo para controle de execução de agentes em live trading.

Este módulo centraliza funções relacionadas ao controle temporal
e execução de agentes durante operações de live trading.
"""

from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentes.trade_conductor import trade_conductor, trade_conductor_leader
from agentes.prompts.trade_conductor_prompt import prompt_trade_conductor, prompt_trade_conductor_leader
from managers.data_manager import prepare_multi_timeframe_technical_data
from utils.notifications.telegram_client import get_telegram_client

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
    trailing_stop,
    vela_abertura_trade
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
        agora - ultima_execucao_trade_conductor >= timedelta(hours=frequencia_agente_horas)          # tempo de intervalo padrão entre execuções
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

        print(f"Executando análise do trade_conductor - {agora.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        
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
            df.reset_index(),
            df_1w.reset_index(),
            df_1d.reset_index(),
            vela_abertura_trade,
        ))

        # Enviar análise via Telegram
        client = get_telegram_client()
        if client:
            timestamp = agora.strftime('%Y-%m-%d %H:%M:%S')
            # Truncar conteúdo se muito longo
            content = resposta.content
            max_content_length = 4000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "...\n[Conteúdo truncado]"
            
            formatted_message = f"""🤖 <b>Análise Trade Conductor</b>

📊 <b>Par:</b> {cripto}
🕐 <b>Horário:</b> {timestamp}

📋 <b>Análise:</b>
<pre>{content}</pre>

#TradingBot #CryptoAnalysis #{cripto.replace('USDT', '')}"""
            client.send(formatted_message)

        print(resposta.content, flush=True)
        print(f"Próxima análise do agente programada para: {(agora + timedelta(hours=frequencia_agente_horas)).strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        
        return agora
    
    return ultima_execucao_trade_conductor