from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout, CondicaoEntrada, StopConfig, AlvoConfig
from vectorbt_project.generator_vectorbt import gerar_por_nome

from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()

import vectorbt as vbt

def evaluate_individual(df, individual):
    """Evaluate an individual's genome by running the strategy with its parameters"""
    genome = individual.genome
    
    # Skip evaluation if ema_curta >= ema_longa
    if genome['ema_curta_long'] >= genome['ema_longa_long'] or genome['ema_curta_short'] >= genome['ema_longa_short']:
        return -float('inf')
    
    # Convert RR from integer to float (divide by 10)
    rr_long = genome['rr_long'] / 10
    rr_short = genome['rr_short'] / 10
    
    # Create strategy with individual's parameters
    nome = f"emas_{genome['ema_curta_long']}_{genome['ema_longa_long']}_{genome['ema_curta_short']}_{genome['ema_longa_short']}_stop_{genome['stop_long']}_{genome['stop_short']}_rr_{rr_long}_{rr_short}"
    estrategia = DoubleEmaBreakout(
        nome=nome,
        tipo="long_short",
        condicoes_entrada=[
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": genome['ema_curta_long']}),
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": genome['ema_longa_long']}),
            CondicaoEntrada(tipo="rompe_maxima_anterior", parametros={}),
            CondicaoEntrada(tipo="fechamento_abaixo_ema", parametros={"periodo": genome['ema_curta_short']}),
            CondicaoEntrada(tipo="fechamento_abaixo_ema", parametros={"periodo": genome['ema_longa_short']}),
            CondicaoEntrada(tipo="rompe_minima_anterior", parametros={})
        ],
        stop=StopConfig(tipo="minima_das_ultimas", parametros={"quantidade": [genome['stop_long'], genome['stop_short']]}),
        alvo=AlvoConfig(tipo="rr", parametros={"multiplicador": [rr_long, rr_short]})
    )
    
    try:
        entries, exits, _, _, size = gerar_por_nome("double_ema_breakout_orders_long_short_dual_params", df, estrategia)
        
        order_price = entries.combine_first(exits)
        
        pf = vbt.Portfolio.from_orders(
            close=df['fechamento'],
            price=order_price,
            size_type='targetpercent',
            size=size,
            init_cash=1000,
            fees=0.00055,
            freq='15min',
            direction='both'
        )
        
        stats = pf.stats()
        
        # Fitness function: weighted combination of return and drawdown
        fitness = stats['Total Return [%]'] * (1 - stats['Max Drawdown [%]'] / 100)
        
        # Store metadata for later analysis
        individual.metadata = {
            "stats": stats,
            "params": {
                "params_long": {
                    "ema_curta_long": genome['ema_curta_long'],
                    "ema_longa_long": genome['ema_longa_long'],
                    "stop_long": genome['stop_long'],
                    "rr_long": rr_long,
                },
                "params_short": {
                    "ema_curta_short": genome['ema_curta_short'],
                    "ema_longa_short": genome['ema_longa_short'],
                    "stop_short": genome['stop_short'],
                    "rr_short": rr_short
                }
            }
        }
        
        return fitness
        
    except Exception as e:
        print(f"Error evaluating individual: {e}")
        return -float('inf')