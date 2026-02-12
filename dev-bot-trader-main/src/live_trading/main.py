import subprocess

scripts = [
    #'src/live_trading/live_trading.py', # depreciado
    # 'src/live_trading/live_trading2.py', # depreciado
    # 'src/live_trading/live_trading3_sell.py', # depreciado
    'src/live_trading/double_ema_breakout_orders.py --subconta 1 --cripto SOLUSDT --tempo_grafico 15 --ema_rapida 5 --ema_lenta 15 --qtd_velas_stop 17 --risco_retorno 4.1 --alavancagem 1',
    # 'src/live_trading/double_ema_breakout_orders_short.py --subconta 1 --cripto SOLUSDT --tempo_grafico 15 --ema_rapida 9 --ema_lenta 21 --qtd_velas_stop 17 --risco_retorno 3.5 --alavancagem 1',
    # 'src/live_trading/double_ema_breakout_orders_long_short.py --subconta 1 --cripto SOLUSDT --tempo_grafico 15 --ema_rapida 5 --ema_lenta 15 --qtd_velas_stop 17 --risco_retorno 4.1 --alavancagem 1',
    # 'src/live_trading/double_ema_breakout_orders_long_short_dual_params.py --subconta 1 --cripto SOLUSDT --tempo_grafico 15 --ema_rapida_compra 5 --ema_lenta_compra 15 --qtd_velas_stop_compra 17 --risco_retorno_compra 4.1 --ema_rapida_venda 5 --ema_lenta_venda 15 --qtd_velas_stop_venda 17 --risco_retorno_venda 4.1 --alavancagem 1',
]

processes = [subprocess.Popen(['python', script]) for script in scripts]

try:
    while True:
        pass 

except KeyboardInterrupt:
    print("Finalizando processos...")

    for process in processes:
        process.terminate()
        process.wait()

    print("Todos os processos foram encerrados.")