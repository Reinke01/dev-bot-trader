# src/vectorbt_project/neuroevolution/trainers/double_ema_breakout_orders.py
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from corretoras.funcoes_bybit import carregar_dados_historicos
from vectorbt_project.neuroevolution.evolutionary_runners.double_ema_breakout_orders_long_short import DoubleEMAEvolverLongShort
from vectorbt_project.neuroevolution.trainers.base_trainer import BaseTrainer

class DoubleEMABreakoutLongShortTrainer(BaseTrainer):
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
            'ema_curta': (5, 50),
            'ema_longa': (10, 200),
            'stop': (5, 21),
            'rr': (15, 55)  # Será dividido por 10 para obter valores RR reais
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
    
    def setup_evolver(self, df: pd.DataFrame) -> DoubleEMAEvolverLongShort:
        """Configura o otimizador evolutivo"""
        return DoubleEMAEvolverLongShort(
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
            rr = genome['rr'] / 10
            
            if best_individual.fitness not in [result['fitness'] for result in results]:
                results.append({
                    "moeda": self.symbol,
                    "intervalo": self.interval,
                    "periodo": f"{self.start_date} : {self.end_date}",
                    "estrategia": f"ema_{genome['ema_curta']}_{genome['ema_longa']}_stop_{genome['stop']}_rr_{rr}",
                    "ema_curta": int(genome['ema_curta']),
                    "ema_longa": int(genome['ema_longa']),
                    "stop": int(genome['stop']),
                    "rr": float(rr),
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
        
        caminho_arquivo = f"data/results/evolutionary/{now}_double_ema_orders_long_short_{self.symbol}_{self.interval}_{self.start_date}_{self.end_date}"
        
        # Salva CSV
        df_results.to_csv(f"{caminho_arquivo}.csv", index=False)
        
        # Prepara e salva JSON
        results_json = []
        for _, row in df_results.iterrows():
            result_json = {
                "fitness": round(float(row["fitness"]), 2),
                "params": {
                    "ema_curta": int(row["ema_curta"]),
                    "ema_longa": int(row["ema_longa"]),
                    "stop": int(row["stop"]),
                    "rr": float(row["rr"])
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
        print(f"  EMA Curta: {best_result['ema_curta']}")
        print(f"  EMA Longa: {best_result['ema_longa']}")
        print(f"  Stop: {best_result['stop']}")
        print(f"  RR: {best_result['rr']}")
        print(f"Performance:")
        print(f"  Fitness: {best_result['fitness']:.2f}")
        print(f"  Retorno Total: {best_result['retorno_total']:.2f}%")
        print(f"  Max Drawdown: {best_result['max_drawdown']:.2f}%")
        print(f"  Win Rate: {best_result['win_rate']:.2f}%")
        print(f"  Trades: {best_result['trades']}")
        
        print(f"\nMelhores parâmetros para Fitness:")
        print(f"  EMA Curta: {best_fitness['ema_curta']}")
        print(f"  EMA Longa: {best_fitness['ema_longa']}")
        print(f"  Stop: {best_fitness['stop']}")
        print(f"  RR: {best_fitness['rr']}")
        print(f"Performance:")
        print(f"  Fitness: {best_fitness['fitness']:.2f}")
        print(f"  Retorno Total: {best_fitness['retorno_total']:.2f}%")
        print(f"  Max Drawdown: {best_fitness['max_drawdown']:.2f}%")
        print(f"  Win Rate: {best_fitness['win_rate']:.2f}%")
        print(f"  Trades: {best_fitness['trades']}")

def run_evolutionary_double_ema_long_short():
    trainer = DoubleEMABreakoutLongShortTrainer()
    trainer.run()

if __name__ == "__main__":
    run_evolutionary_double_ema_long_short()