import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from entidades.estado_trade import EstadoDeTrade
from corretoras.funcoes_bybit import busca_velas, tem_trade_aberto, saldo_da_conta, quantidade_minima_para_operar, abre_compra
from utils.utilidades import quantidade_cripto_para_operar

# Valores padrão
cripto = 'SOLUSDT'
tempo_grafico = '15'
qtd_velas_stop = 17
risco_retorno = 4.1
ema_rapida = 5
ema_lenta = 15
alavancagem = 1
subconta = 1

def start_live_trading_bot(
    cripto = cripto,
    tempo_grafico = tempo_grafico,
    qtd_velas_stop = qtd_velas_stop,
    risco_retorno = risco_retorno,
    ema_rapida = ema_rapida,
    ema_lenta = ema_lenta,
    alavancagem = alavancagem,
    subconta = subconta
):
    print('Bot started', flush=True)
    print(f'Cripto: {cripto}', flush=True)
    print(f'Tempo gráfico: {tempo_grafico}', flush=True)
    print(f'Velas Stop: {qtd_velas_stop}', flush=True)
    print(f'Risco/Retorno: {risco_retorno}', flush=True)
    print(f'EMAs: {ema_rapida}, {ema_lenta}', flush=True)

    # ADICIONAR MAIS TENTATIVAS CASO DÊ ERRO (RETRY)
    for tentativa in range(5):
        try:
            estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = tem_trade_aberto(cripto, subconta)
            print(f'Estado de trade: {estado_de_trade}', flush=True)
            print(f'Preço de entrada: {preco_entrada}', flush=True)
            print(f'Preço de stop: {preco_stop}', flush=True)
            print(f'Preço de alvo: {preco_alvo}', flush=True)
            print(f'Tamanho da posição: {tamanho_posicao}', flush=True)
            print(f'Trailing stop: {trailing_stop}', flush=True)
            break

        except Exception as e:
            print(f'Erro ao buscar trade aberto: {e}', flush=True)
            
            if tentativa < 4:
                print('Tentando novamente...', flush=True)
                time.sleep(2)
            elif tentativa == 4:
                print('Não foi possível buscar trade aberto. Encerrando programa.', flush=True)
                exit()

    vela_fechou_trade = None

    while True:
        try:
            df = busca_velas(cripto, tempo_grafico, [ema_rapida, ema_lenta])
            # print('preço atual:', df['fechamento'].iloc[-1])
            # print(df)

            if df.empty:
                print('DataFrame vazio')
            else:

                if estado_de_trade == EstadoDeTrade.COMPRADO:
                    # print('está comprado')
                    # print('buscando saída no stop ou no alvo...')

                    # Lógica para atualizar o stop e o alvo caso eu tenha alterado eles na corretora
                    #   os "_" são para ignorar as variáveis que não são necessárias  
                    estado_de_trade, _, preco_stop, preco_alvo, _, _ = tem_trade_aberto(cripto, subconta)

                    # representa a mesma coisa da linha de cima, mas com mais requisições da corretora
                    #   não é uma boa prática porque o lopp demora mais, com mais requisições
                    # preco_stop = tem_trade_aberto(cripto, subconta)[2]
                    # preco_alvo = tem_trade_aberto(cripto, subconta)[3]

                    if df['maxima'].iloc[-1] >= preco_alvo and preco_alvo != 0:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        print(f"Bateu alvo na vela que abriu {df.index[-1]}, no preço de {preco_alvo}", flush=True)
                        print('-' * 10)

                    elif df['minima'].iloc[-1] <= preco_stop:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        print(f"Bateu stop na vela que abriu {df.index[-1]}, no preço de {preco_stop}", flush=True)
                        print('-' * 10)

                    # Avaliação se o trade foi fechado na mão na corretora, ela devolve o estado de trade DE_FORA
                    elif estado_de_trade == EstadoDeTrade.DE_FORA:
                        vela_fechou_trade = df.index[-1]
                        print('Trade fechado manualmente na corretora', flush=True)
                        print('-' * 10)

                    # Atualiza preço de stop e alvo caso eu tenha alterado eles na corretora
                    # estado_de_trade, preco_entrada, preco_stop, preco_alvo = tem_trade_aberto(cripto, subconta)

                elif estado_de_trade == EstadoDeTrade.DE_FORA and df.index[-1] != vela_fechou_trade:
                    # print('Procurando trades de compra...')
                    # verifica se temos uma vela referência que fechou acima das EMAS
                    if df['fechamento'].iloc[-2] > df[f'EMA_{ema_rapida}'].iloc[-2] and df['fechamento'].iloc[-2] > df[f'EMA_{ema_lenta}'].iloc[-2]:
                        # verificar se a vela atual superou a máxima da vela referência
                        if df['maxima'].iloc[-1] > df['maxima'].iloc[-2]:
                            saldo = saldo_da_conta(subconta) * alavancagem
                            # print('saldo:', saldo)

                            qtidade_minima_para_operar = quantidade_minima_para_operar(cripto, subconta)
                            # print(f'Mínimo para {cripto}: {qtidade_minima_para_operar}')

                            qtd_cripto_para_operar = quantidade_cripto_para_operar(saldo, qtidade_minima_para_operar, df['fechamento'].iloc[-1])
                            # print(f'Quantidade para operar: {qtd_cripto_para_operar}')
                            
                            preco_entrada = df['maxima'].iloc[-2]
                            preco_stop = df['minima'].iloc[-qtd_velas_stop : -1].min()
                            preco_alvo = ((preco_entrada - preco_stop) * risco_retorno) + preco_entrada
                            
                            abre_compra(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, subconta)

                            print(f"Entrou na compra na vela que abriu em {df.index[-1]}, no preço de {preco_entrada}, com stop em {preco_stop} e alvo em {preco_alvo}", flush=True)
                            estado_de_trade = EstadoDeTrade.COMPRADO
                            print('-' * 10)

        except ConnectionError as ce:
            print(f'Erro de conexão: {ce}', flush=True)
        except ValueError as ve:
            print(f'Erro de valor: {ve}', flush=True)
        except KeyboardInterrupt:
            print('Programa encerrado pelo usuário', flush=True)
            exit()
        except Exception as e:
            print(f'Erro desconhecido: {e}', flush=True)

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
    args = parser.parse_args()
    
    start_live_trading_bot(
        subconta=args.subconta,
        cripto=args.cripto,
        tempo_grafico=args.tempo_grafico,
        qtd_velas_stop=args.qtd_velas_stop,
        risco_retorno=args.risco_retorno,
        ema_rapida=args.ema_rapida,
        ema_lenta=args.ema_lenta,
        alavancagem=args.alavancagem
    )