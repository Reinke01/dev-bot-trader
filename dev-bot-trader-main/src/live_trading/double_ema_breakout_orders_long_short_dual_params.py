import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from entidades.estado_trade import EstadoDeTrade
from corretoras.funcoes_bybit import busca_velas, tem_trade_aberto, saldo_da_conta, quantidade_minima_para_operar, abre_compra, abre_venda
from utils.utilidades import quantidade_cripto_para_operar

# Valores padrão
subconta = 1
cripto = 'SOLUSDT'
tempo_grafico = '15'
alavancagem = 1

# Parâmetros para compra
ema_rapida_compra = 5
ema_lenta_compra = 45
qtd_velas_stop_compra = 13
risco_retorno_compra = 1.7

# Parâmetros para venda
ema_rapida_venda = 8
ema_lenta_venda = 50
qtd_velas_stop_venda = 10
risco_retorno_venda = 2.0

def start_live_trading_bot(
    subconta = subconta,
    cripto = cripto,
    tempo_grafico = tempo_grafico,
    ema_rapida_compra = ema_rapida_compra,
    ema_lenta_compra = ema_lenta_compra,
    qtd_velas_stop_compra = qtd_velas_stop_compra,
    risco_retorno_compra = risco_retorno_compra,
    alavancagem = alavancagem,
    ema_rapida_venda = ema_rapida_venda,
    ema_lenta_venda = ema_lenta_venda,
    qtd_velas_stop_venda = qtd_velas_stop_venda,
    risco_retorno_venda = risco_retorno_venda,
):
    print('Bot started', flush=True)
    print(f'Cripto: {cripto}', flush=True)
    print(f'Tempo gráfico: {tempo_grafico}', flush=True)
    print(f'Alavancagem: {alavancagem}', flush=True)
    print(f'Parâmetros de Compra:', flush=True)
    print(f'  - EMAs: {ema_rapida_compra}, {ema_lenta_compra}', flush=True)
    print(f'  - Velas Stop: {qtd_velas_stop_compra}', flush=True)
    print(f'  - Risco/Retorno: {risco_retorno_compra}', flush=True)
    print(f'Parâmetros de Venda:', flush=True)
    print(f'  - EMAs: {ema_rapida_venda}, {ema_lenta_venda}', flush=True)
    print(f'  - Velas Stop: {qtd_velas_stop_venda}', flush=True)
    print(f'  - Risco/Retorno: {risco_retorno_venda}', flush=True)

    for tentativa in range(5):
        try:
            estado_de_trade, preco_entrada, preco_stop, preco_alvo, tamanho_posicao, trailing_stop = tem_trade_aberto(cripto, subconta)
            qtd_min_para_operar = quantidade_minima_para_operar(cripto, subconta)
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
            # Buscar dados com todas as EMAs necessárias (união das EMAs de compra e venda)
            df = busca_velas(cripto, tempo_grafico, [5, 15])
            df['ema_rapida_compra'] = df['fechamento'].ewm(span=ema_rapida_compra, adjust=False).mean()
            df['ema_lenta_compra'] = df['fechamento'].ewm(span=ema_lenta_compra, adjust=False).mean()
            df['ema_rapida_venda'] = df['fechamento'].ewm(span=ema_rapida_venda, adjust=False).mean()
            df['ema_lenta_venda'] = df['fechamento'].ewm(span=ema_lenta_venda, adjust=False).mean()

            if df.empty:
                print('DataFrame vazio')
            else:

                if estado_de_trade == EstadoDeTrade.COMPRADO:
                    estado_de_trade, _, preco_stop, preco_alvo, _, _ = tem_trade_aberto(cripto, subconta)

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

                    elif estado_de_trade == EstadoDeTrade.DE_FORA:
                        vela_fechou_trade = df.index[-1]
                        print('Trade fechado manualmente na corretora', flush=True)
                        print('-' * 10)

                elif estado_de_trade == EstadoDeTrade.VENDIDO:
                    estado_de_trade, _, preco_stop, preco_alvo, _, _ = tem_trade_aberto(cripto, subconta)

                    if df['minima'].iloc[-1] <= preco_alvo:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        print(f"Bateu alvo na vela que abriu {df.index[-1]}, no preço de {preco_alvo}", flush=True)
                        print('-' * 10)
                    
                    elif df['maxima'].iloc[-1] >= preco_stop and preco_stop != 0:
                        estado_de_trade = EstadoDeTrade.DE_FORA
                        vela_fechou_trade = df.index[-1]
                        print(f"Bateu stop na vela que abriu {df.index[-1]}, no preço de {preco_stop}", flush=True)
                        print('-' * 10)

                    elif estado_de_trade == EstadoDeTrade.DE_FORA:
                        vela_fechou_trade = df.index[-1]
                        print('Trade fechado manualmente na corretora', flush=True)
                        print('-' * 10)

                elif estado_de_trade == EstadoDeTrade.DE_FORA and df.index[-1] != vela_fechou_trade:
                    # Sinal de compra usando EMAs de compra
                    if df['fechamento'].iloc[-2] > df['ema_rapida_compra'].iloc[-2] and df['fechamento'].iloc[-2] > df['ema_lenta_compra'].iloc[-2]:
                        if df['maxima'].iloc[-1] > df['maxima'].iloc[-2]:
                            saldo = saldo_da_conta(subconta) * alavancagem
                            qtd_cripto_para_operar = quantidade_cripto_para_operar(saldo, qtd_min_para_operar, df['fechamento'].iloc[-1])
                            
                            preco_entrada = df['maxima'].iloc[-2]
                            preco_stop = df['minima'].iloc[-qtd_velas_stop_compra : ].min()
                            preco_alvo = ((preco_entrada - preco_stop) * risco_retorno_compra) + preco_entrada
                            
                            abre_compra(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, subconta)

                            print(f"Entrou na compra na vela que abriu em {df.index[-1]}, no preço de {preco_entrada}, com stop em {preco_stop} e alvo em {preco_alvo}", flush=True)
                            print(f"Parâmetros usados - EMAs: {ema_rapida_compra, ema_lenta_compra}, Velas Stop: {qtd_velas_stop_compra}, R/R: {risco_retorno_compra}, Alavancagem: {alavancagem}", flush=True)
                            estado_de_trade = EstadoDeTrade.COMPRADO
                            print('-' * 10)
                    
                    # Sinal de venda usando EMAs de venda
                    if df['fechamento'].iloc[-2] < df['ema_rapida_venda'].iloc[-2] and df['fechamento'].iloc[-2] < df['ema_lenta_venda'].iloc[-2]:
                        if df['minima'].iloc[-1] < df['minima'].iloc[-2]:
                            saldo = saldo_da_conta(subconta) * alavancagem
                            qtd_cripto_para_operar = quantidade_cripto_para_operar(saldo, qtd_min_para_operar, df['fechamento'].iloc[-1])

                            preco_entrada = df['minima'].iloc[-2]
                            preco_stop = df['maxima'].iloc[-qtd_velas_stop_venda : ].max()
                            preco_alvo = preco_entrada - ((preco_stop - preco_entrada) * risco_retorno_venda)

                            abre_venda(cripto, qtd_cripto_para_operar, preco_stop, preco_alvo, subconta)

                            print(f"Entrou na venda na vela que abriu em {df.index[-1]}, no preço de {preco_entrada}, com stop em {preco_stop} e alvo em {preco_alvo}", flush=True)
                            print(f"Parâmetros usados - EMAs: {ema_rapida_venda, ema_lenta_venda}, Velas Stop: {qtd_velas_stop_venda}, R/R: {risco_retorno_venda}, Alavancagem: {alavancagem}", flush=True)
                            estado_de_trade = EstadoDeTrade.VENDIDO
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

        time.sleep(1.0)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--subconta', type=int, default=subconta)
    parser.add_argument('--cripto', type=str, default=cripto)
    parser.add_argument('--tempo_grafico', type=str, default=tempo_grafico)
    parser.add_argument('--alavancagem', type=float, default=alavancagem)
    
    # Parâmetros de compra
    parser.add_argument('--ema_rapida_compra', type=int, default=ema_rapida_compra)
    parser.add_argument('--ema_lenta_compra', type=int, default=ema_lenta_compra)
    parser.add_argument('--qtd_velas_stop_compra', type=int, default=qtd_velas_stop_compra)
    parser.add_argument('--risco_retorno_compra', type=float, default=risco_retorno_compra)
    
    # Parâmetros de venda
    parser.add_argument('--ema_rapida_venda', type=int, default=ema_rapida_venda)
    parser.add_argument('--ema_lenta_venda', type=int, default=ema_lenta_venda)
    parser.add_argument('--qtd_velas_stop_venda', type=int, default=qtd_velas_stop_venda)
    parser.add_argument('--risco_retorno_venda', type=float, default=risco_retorno_venda)
    
    args = parser.parse_args()
    start_live_trading_bot(
        subconta=args.subconta,
        cripto=args.cripto,
        tempo_grafico=args.tempo_grafico,
        ema_rapida_compra=args.ema_rapida_compra,
        ema_lenta_compra=args.ema_lenta_compra,
        qtd_velas_stop_compra=args.qtd_velas_stop_compra,
        risco_retorno_compra=args.risco_retorno_compra,
        alavancagem=args.alavancagem,
        ema_rapida_venda=args.ema_rapida_venda,
        ema_lenta_venda=args.ema_lenta_venda,
        qtd_velas_stop_venda=args.qtd_velas_stop_venda,
        risco_retorno_venda=args.risco_retorno_venda
    ) 