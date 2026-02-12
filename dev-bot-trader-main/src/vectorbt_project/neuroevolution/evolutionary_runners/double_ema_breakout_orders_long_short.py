import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from vectorbt_project.neuroevolution.population import Population
from vectorbt_project.neuroevolution.evaluators.double_ema_breakout_orders_long_short import evaluate_individual

class DoubleEMAEvolverLongShort:
    def __init__(self, df, population_size=50, generations=20, elite_size=5, param_ranges=None):
        self.df = df
        self.population_size = population_size
        self.generations = generations
        self.elite_size = elite_size
        
        # Define parameter ranges for evolution
        self.param_ranges = param_ranges
        
        # Initialize population
        self.population = Population(population_size, self.param_ranges)
        self.population.initialize()
    
    def evolve(self):
        """Run the evolutionary process"""
        best_fitness = -float('inf')
        generations_without_improvement = 0
        
        print(f"Avaliando {self.population.size} individuos por geração...")
        for generation in range(self.generations):
            print(f"\nAvaliando geração {generation + 1}/{self.generations}...")
            # Evaluate all individuals
            for individual in self.population.individuals:
                if individual.fitness is None:
                    individual.fitness = evaluate_individual(self.df, individual)
            
            # Sort population by fitness
            self.population.sort_by_fitness()
            
            best_individuals = []
            # Store best results
            for individual in self.population.get_elite(self.elite_size):
                if individual.fitness not in [best_individual.fitness for best_individual in best_individuals]:
                    best_individuals.append(individual)

            #best_individuals = self.population[:self.elite_size]
                
            # Print progress
            # print(f"\nGeneration {generation + 1}/{self.generations}")
            print(f"Best Fitness: {best_individuals[0].fitness:.2f}")
            print(f"Retorno Total: {best_individuals[0].metadata['stats']['Total Return [%]']:.2f}%")
            print(f"Max Drawdown: {best_individuals[0].metadata['stats']['Max Drawdown [%]']:.2f}%")
            print(f"Win Rate: {best_individuals[0].metadata['stats']['Win Rate [%]']:.2f}%")
            print(f"Parameters: {best_individuals[0].metadata['params']}")
            
            # Create new population
            new_population = []
            
            # Elitism: keep best individuals
            new_population.extend(best_individuals)
            
            # Fill rest of population with offspring
            while len(new_population) < self.population_size:
                # Tournament selection
                parent1 = max(random.sample(self.population.individuals, 3), key=lambda x: x.fitness)
                parent2 = max(random.sample(self.population.individuals, 3), key=lambda x: x.fitness)
                
                # Crossover
                child = self.population.crossover(parent1, parent2)
                
                # Mutation
                child.genome = self.population.mutate(child.genome, self.param_ranges)
                
                # Skip invalid individuals (ema_curta >= ema_longa)
                if child.genome['ema_curta'] >= child.genome['ema_longa']:
                    continue
                
                new_population.append(child)
            
            self.population.individuals = new_population

            current_best_fitness = self.population.individuals[0].fitness
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
                
            # Early stopping
            if generations_without_improvement >= 10:
                print("Early stopping: No improvement in 10 generations")
                break
        
        return best_individuals