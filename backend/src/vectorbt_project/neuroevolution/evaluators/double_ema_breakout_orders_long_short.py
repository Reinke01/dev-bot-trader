from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout, CondicaoEntrada, StopConfig, AlvoConfig
from vectorbt_project.generator_vectorbt import gerar_por_nome
from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()
import vectorbt as vbt

def evaluate_individual(df, individual):
    """Evaluate an individual's genome by running the strategy with its parameters"""
    genome = individual.genome
    
    # Skip evaluation if ema_curta >= ema_longa
    if genome['ema_curta'] >= genome['ema_longa']:
        return -float('inf')
    
    # Convert RR from integer to float (divide by 10)
    rr = genome['rr'] / 10
    
    # Create strategy with individual's parameters
    nome = f"ema_{genome['ema_curta']}_{genome['ema_longa']}_stop_{genome['stop']}_rr_{rr}"
    estrategia = DoubleEmaBreakout(
        nome=nome,
        tipo="long_short",
        condicoes_entrada=[
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": genome['ema_curta']}),
            CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": genome['ema_longa']}),
            CondicaoEntrada(tipo="rompe_maxima_anterior", parametros={})
        ],
        stop=StopConfig(tipo="minima_das_ultimas", parametros={"quantidade": genome['stop']}),
        alvo=AlvoConfig(tipo="rr", parametros={"multiplicador": rr})
    )
    
    try:
        entries, exits, _, _, size = gerar_por_nome("double_ema_breakout_orders_long_short", df, estrategia)
        
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
                "ema_curta": genome['ema_curta'],
                "ema_longa": genome['ema_longa'],
                "stop": genome['stop'],
                "rr": rr
            }
        }
        
        return fitness
        
    except Exception as e:
        print(f"Error evaluating individual: {e}")
        return -float('inf')