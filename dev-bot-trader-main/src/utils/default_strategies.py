DEFAULT_STRATEGIES = {
    "double_ema_breakout_orders": {
        "script": "src/live_trading/double_ema_breakout_orders.py",
        "name": "Double EMA Breakout Long",
        "description": "Estratégia de compra em rompimento de EMAs",
        "default_config": {
            "cripto": "SOLUSDT",
            "tempo_grafico": "15",
            "ema_rapida": "5",
            "ema_lenta": "15",
            "qtd_velas_stop": 17,
            "risco_retorno": 4.1,
            "alavancagem": 1,
            "subconta": 1
        }
    },
    "double_ema_breakout_orders_short": {
        "script": "src/live_trading/double_ema_breakout_orders_short.py",
        "name": "Double EMA Breakout Short",
        "description": "Estratégia de venda em rompimento de EMAs",
        "default_config": {
            "cripto": "SOLUSDT",
            "tempo_grafico": "15",
            "ema_rapida": "9",
            "ema_lenta": "21",
            "qtd_velas_stop": 17,
            "risco_retorno": 3.5,
            "alavancagem": 1,
            "subconta": 1
        }
    },
    "double_ema_breakout_orders_long_short": {
        "script": "src/live_trading/double_ema_breakout_orders_long_short.py",
        "name": "Double EMA Breakout Long/Short",
        "description": "Estratégia de breakout com EMAs para long e short",
        "default_config": {
            "cripto": "SOLUSDT",
            "tempo_grafico": "15",
            "ema_rapida": "5",
            "ema_lenta": "45",
            "qtd_velas_stop": 13,
            "risco_retorno": 1.7,
            "alavancagem": 1,
            "subconta": 1
        }
    },
    "double_ema_breakout_orders_long_short_dual_params": {
        "script": "src/live_trading/double_ema_breakout_orders_long_short_dual_params.py",
        "name": "Double EMA Breakout Long/Short Dual Params",
        "description": "Estratégia de breakout com EMAs para long e short com parâmetros duplos",
        "default_config": {
            "cripto": "SOLUSDT",
            "tempo_grafico": "15",
            "ema_rapida_compra": "5",
            "ema_lenta_compra": "45",
            "qtd_velas_stop_compra": 13,
            "risco_retorno_compra": 1.7,
            "ema_rapida_venda": "5",
            "ema_lenta_venda": "45",
            "qtd_velas_stop_venda": 13,
            "risco_retorno_venda": 1.7,
            "alavancagem": 1,
            "subconta": 1
        }
    }
}