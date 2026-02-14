import random
from .individual import Individual
from copy import deepcopy
from typing import List, Dict
import numpy as np

class Population:
    def __init__(self, size: int, param_ranges: Dict[str, tuple]):
        self.size = size
        self.param_ranges = param_ranges
        self.individuals: List[Individual] = []
        self.generation = 0
        self.history = {'best_fitness': [], 'avg_fitness': []}
    
    def initialize(self) -> None:
        """Initialize population with random individuals"""
        self.individuals = [self._create_random_individual() for _ in range(self.size)]
    
    def _create_random_individual(self) -> Individual:
        """Create a random individual within parameter ranges"""
        genome = {}
        for param, (min_val, max_val) in self.param_ranges.items():
            genome[param] = random.randint(min_val, max_val)
        return Individual(genome=genome)
    
    def mutate(self, genome, ranges):
        genome_new = deepcopy(genome)
        for key in genome:
            if random.random() < 0.3:
                min_val, max_val = ranges[key]
                genome_new[key] = random.randint(min_val, max_val)  # pode ser float, se for o caso
        return genome_new

    def crossover(self, parent1: Individual, parent2: Individual):
        child_genome = {}
        for key in parent1.genome:
            child_genome[key] = parent1.genome[key] if random.random() < 0.5 else parent2.genome[key]
        return Individual(genome=child_genome)
    
    def sort_by_fitness(self) -> None:
        """Sort population by fitness in descending order"""
        self.individuals.sort(key=lambda x: x.fitness if x.fitness is not None else float('-inf'), reverse=True)
    
    def update_history(self) -> None:
        """Update population statistics history"""
        fitnesses = [ind.fitness for ind in self.individuals if ind.fitness is not None]
        if fitnesses:
            self.history['best_fitness'].append(max(fitnesses))
            self.history['avg_fitness'].append(np.mean(fitnesses))
    
    def get_elite(self, elite_size: int) -> List[Individual]:
        """Get top performing individuals"""
        return [ind.clone() for ind in self.individuals[:elite_size]]
    
    def calculate_diversity(self) -> float:
        """Calculate genetic diversity of population"""
        return np.std([ind.fitness for ind in self.individuals if ind.fitness is not None])