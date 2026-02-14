# src/vectorbt_project/neuroevolution/trainers/double_ema_breakout_orders.py
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from corretoras.funcoes_bybit import carregar_dados_historicos
from vectorbt_project.neuroevolution.evolutionary_runners.double_ema_breakout_orders_long_short_dual_params import DoubleEMAEvolverLongShortDualParams
from vectorbt_project.neuroevolution.trainers.base_trainer import BaseTrainer

class DoubleEMABreakoutLongShortDualParamsTrainer(BaseTrainer):
    def __init__(
        self,
        symbol: str = 'SOLUSDT',
        interval: str = '15',
        start_date: str = '2024-01-01',
        # end_date: str = datetime.now().strftime('%Y-%m-%d'),
        end_date: str = '2024-09-01',
        
        # Otimização rápida
        population_size: int = 500,
        generations: int = 15,
        elite_size: int = 25

        # # Otimização intensa
        # population_size: int = 1000,
        # generations: int = 40,
        # elite_size: int = 50

        # Otimização robusta
        # population_size: int = 2500,
        # generations: int = 40,
        # elite_size: int = 125
        
        # Exploração Extensiva
        # population_size: int = 5000, 
        # generations: int = 50, 
        # elite_size: int = 250,
    ):
        # Define os ranges de parâmetros padrão
        param_ranges = {
            'ema_curta_long': (5, 50),
            'ema_longa_long': (10, 200),
            'stop_long': (5, 21),
            'rr_long': (15, 55),  # Será dividido por 10 para obter valores RR reais
            'ema_curta_short': (5, 50),
            'ema_longa_short': (10, 200),
            'stop_short': (5, 21),
            'rr_short': (15, 55),  # Será dividido por 10 para obter valores RR reais
        }
        
        super().__init__(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            population_size=population_size,
            generations=generations,
            elite_size=elite_size,
            param_ranges=param_ranges
        )
    
    def load_data(self) -> pd.DataFrame:
        """Carrega e prepara os dados históricos"""
        df = carregar_dados_historicos(
            self.symbol, 
            self.interval, 
            [9, 21], 
            self.start_date, 
            self.end_date
        )
        df.columns = df.columns.str.lower()
        return df
    
    def setup_evolver(self, df: pd.DataFrame) -> DoubleEMAEvolverLongShortDualParams:
        """Configura o otimizador evolutivo"""
        return DoubleEMAEvolverLongShortDualParams(
            df,
            population_size=self.population_size,
            generations=self.generations,
            elite_size=self.elite_size,
            param_ranges=self.param_ranges
        )
    
    def process_results(self, best_individuals: List[Any]) -> List[Dict[str, Any]]:
        """Processa os resultados da otimização"""
        results = []
        for best_individual in best_individuals:
            genome = best_individual.genome
            rr_long = genome['rr_long'] / 10
            rr_short = genome['rr_short'] / 10  
            
            if best_individual.fitness not in [result['fitness'] for result in results]:
                results.append({
                    "moeda": self.symbol,
                    "intervalo": self.interval,
                    "periodo": f"{self.start_date} : {self.end_date}",
                    "estrategia": f"emas_{genome['ema_curta_long']}_{genome['ema_longa_long']}_{genome['ema_curta_short']}_{genome['ema_longa_short']}_stop_{genome['stop_long']}_{genome['stop_short']}_rr_{rr_long}_{rr_short}",
                    "ema_curta_long": int(genome['ema_curta_long']),
                    "ema_longa_long": int(genome['ema_longa_long']),
                    "stop_long": int(genome['stop_long']),
                    "rr_long": float(rr_long),
                    "ema_curta_short": int(genome['ema_curta_short']),
                    "ema_longa_short": int(genome['ema_longa_short']),
                    "stop_short": int(genome['stop_short']),
                    "rr_short": float(rr_short),
                    "saldo_inicial": float(1000),
                    "saldo_final": round(float(best_individual.metadata["stats"]['End Value']), 2),
                    "fitness": round(float(best_individual.fitness), 2),
                    "retorno_total": round(float(best_individual.metadata["stats"]['Total Return [%]']), 2),
                    "max_drawdown": round(float(best_individual.metadata["stats"]['Max Drawdown [%]']), 2),
                    "max_drawdown_duration": str(best_individual.metadata["stats"]['Max Drawdown Duration']),
                    "trades": int(best_individual.metadata["stats"]['Total Trades']),
                    "win_rate": round(float(best_individual.metadata["stats"]['Win Rate [%]']), 2),
                    "ganho_medio": round(float(best_individual.metadata["stats"]['Avg Winning Trade [%]']), 2),
                    "perda_media": round(float(best_individual.metadata["stats"]['Avg Losing Trade [%]']), 2),
                    "melhor_trade": round(float(best_individual.metadata["stats"]['Best Trade [%]']), 2),
                    "pior_trade": round(float(best_individual.metadata["stats"]['Worst Trade [%]']), 2),
                    "sharpe_ratio": round(float(best_individual.metadata["stats"]['Sharpe Ratio']), 2),
                    "sortino_ratio": round(float(best_individual.metadata["stats"]['Sortino Ratio']), 2),
                    "calmar_ratio": round(float(best_individual.metadata["stats"]['Calmar Ratio']), 2)
                })
        return results
    
    def save_results(self, results: List[Dict[str, Any]]) -> None:
        """Salva os resultados em arquivos CSV e JSON"""
        os.makedirs("data/results/evolutionary", exist_ok=True)
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Converte resultados para DataFrame e ordena por retorno_total
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('retorno_total', ascending=False)
        
        caminho_arquivo = f"data/results/evolutionary/{now}_double_ema_orders_long_short_dual_params_{self.symbol}_{self.interval}_{self.start_date}_{self.end_date}"
        
        # Salva CSV
        df_results.to_csv(f"{caminho_arquivo}.csv", index=False)
        
        # Prepara e salva JSON
        results_json = []
        for _, row in df_results.iterrows():
            result_json = {
                "fitness": round(float(row["fitness"]), 2),
                "params": {
                    "ema_curta_long": int(row["ema_curta_long"]),
                    "ema_longa_long": int(row["ema_longa_long"]),
                    "stop_long": int(row["stop_long"]),
                    "rr_long": float(row["rr_long"]),
                    "ema_curta_short": int(row["ema_curta_short"]),
                    "ema_longa_short": int(row["ema_longa_short"]),
                    "stop_short": int(row["stop_short"]),
                    "rr_short": float(row["rr_short"])
                },
                "stats": {
                    "saldo_inicial": float(row["saldo_inicial"]),
                    "saldo_final": round(float(row["saldo_final"]), 2),
                    "retorno_total": round(float(row["retorno_total"]), 2),
                    "max_drawdown": round(float(row["max_drawdown"]), 2),
                    "max_drawdown_duration": str(row["max_drawdown_duration"]),
                    "trades": int(row["trades"]),
                    "win_rate": round(float(row["win_rate"]), 2),
                    "ganho_medio": round(float(row["ganho_medio"]), 2),
                    "perda_media": round(float(row["perda_media"]), 2),
                    "melhor_trade": round(float(row["melhor_trade"]), 2),
                    "pior_trade": round(float(row["pior_trade"]), 2),
                    "sharpe_ratio": round(float(row["sharpe_ratio"]), 2),
                    "sortino_ratio": round(float(row["sortino_ratio"]), 2),
                    "calmar_ratio": round(float(row["calmar_ratio"]), 2)
                }
            }
            results_json.append(result_json)
        
        with open(f"{caminho_arquivo}.json", "w") as f:
            json.dump(results_json, f, indent=4)
    
    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        """Imprime o resumo dos resultados"""
        best_result = max(results, key=lambda x: x['retorno_total'])
        best_fitness = max(results, key=lambda x: x['fitness'])

        print(f"\n🏁 Evolutionary optimization completed!")
        print(f"Results saved in data/results/evolutionary/")
        print(f"\nMelhores parâmetros para Retorno Total:")
        print(f"  EMA Curta Longa: {best_result['ema_curta_long']}")
        print(f"  EMA Longa Longa: {best_result['ema_longa_long']}")
        print(f"  Stop Longa: {best_result['stop_long']}")
        print(f"  RR Longa: {best_result['rr_long']}")
        print(f"  EMA Curta Curta: {best_result['ema_curta_short']}")
        print(f"  EMA Longa Curta: {best_result['ema_longa_short']}")
        print(f"  Stop Curta: {best_result['stop_short']}")
        print(f"  RR Curta: {best_result['rr_short']}")
        print(f"Performance:")
        print(f"  Fitness: {best_result['fitness']:.2f}")
        print(f"  Retorno Total: {best_result['retorno_total']:.2f}%")
        print(f"  Max Drawdown: {best_result['max_drawdown']:.2f}%")
        print(f"  Win Rate: {best_result['win_rate']:.2f}%")
        print(f"  Trades: {best_result['trades']}")
        
        print(f"\nMelhores parâmetros para Fitness:")
        print(f"  EMA Curta Longa: {best_fitness['ema_curta_long']}")
        print(f"  EMA Longa Longa: {best_fitness['ema_longa_long']}")
        print(f"  Stop Longa: {best_fitness['stop_long']}")
        print(f"  RR Longa: {best_fitness['rr_long']}")
        print(f"  EMA Curta Curta: {best_fitness['ema_curta_short']}")
        print(f"  EMA Longa Curta: {best_fitness['ema_longa_short']}")
        print(f"  Stop Curta: {best_fitness['stop_short']}")
        print(f"  RR Curta: {best_fitness['rr_short']}")
        print(f"Performance:")
        print(f"  Fitness: {best_fitness['fitness']:.2f}")
        print(f"  Retorno Total: {best_fitness['retorno_total']:.2f}%")
        print(f"  Max Drawdown: {best_fitness['max_drawdown']:.2f}%")
        print(f"  Win Rate: {best_fitness['win_rate']:.2f}%")
        print(f"  Trades: {best_fitness['trades']}")

def run_evolutionary_double_ema_long_short_dual_params():
    trainer = DoubleEMABreakoutLongShortDualParamsTrainer()
    trainer.run()

if __name__ == "__main__":
    run_evolutionary_double_ema_long_short_dual_params()