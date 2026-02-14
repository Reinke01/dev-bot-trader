# src/vectorbt_project/neuroevolution/trainers/base_trainer.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class BaseTrainer(ABC):
    def __init__(
        self,
        symbol: str,
        interval: str,
        start_date: str,
        end_date: str = None,
        population_size: int = 500,
        generations: int = 15,
        elite_size: int = 25,
        param_ranges: Dict[str, tuple] = None
    ):
        self.symbol = symbol
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.population_size = population_size
        self.generations = generations
        self.elite_size = elite_size
        self.param_ranges = param_ranges
        self.results = []
        
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Carrega e prepara os dados históricos"""
        pass
    
    @abstractmethod
    def setup_evolver(self, df: pd.DataFrame) -> Any:
        """Configura o otimizador evolutivo"""
        pass
    
    @abstractmethod
    def process_results(self, best_individuals: List[Any]) -> List[Dict[str, Any]]:
        """Processa os resultados da otimização"""
        pass
    
    @abstractmethod
    def save_results(self, results: List[Dict[str, Any]]) -> None:
        """Salva os resultados em arquivos"""
        pass
    
    @abstractmethod
    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        """Imprime o resumo dos resultados"""
        pass
    
    def run(self) -> List[Dict[str, Any]]:
        """Executa o processo completo de treinamento"""
        # Carrega dados
        df = self.load_data()
        
        # Configura e executa o evolver
        evolver = self.setup_evolver(df)
        best_individuals = evolver.evolve()
        
        # Processa resultados
        results = self.process_results(best_individuals)
        
        # Salva resultados
        self.save_results(results)
        
        # Imprime resumo
        self.print_summary(results)
        
        return results