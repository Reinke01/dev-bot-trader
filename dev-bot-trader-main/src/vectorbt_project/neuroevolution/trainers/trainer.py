from ..evolutionary_runners.evolutionary_runner import run_evolution
from entidades.estrategias_descritivas.double_ema_breakout import DoubleEmaBreakout
from vectorbt_project.utils.telegram_compatibility import apply_vectorbt_telegram_patch
apply_vectorbt_telegram_patch()
import vectorbt as vbt

param_ranges = {
    "param_ema_curta": (5, 30),
    "param_ema_longa": (15, 100),
    "param_stop": (2, 20),
    "param_rr": (1, 5)
}

def train():
    df = vbt.YFData.download("BTC-USD", start="2023-01-01", interval="15m").get(["Open", "High", "Low", "Close"])
    df.columns = df.columns.str.lower()

    top_individuals = run_evolution(df, DoubleEmaBreakout, param_ranges, generations=5, pop_size=10)
    for ind in top_individuals:
        print("\n🥇 Melhor indivíduo:")
        print("Genoma:", ind.genome)
        print("Fitness:", ind.fitness)
        print("Metadata:", ind.metadata)