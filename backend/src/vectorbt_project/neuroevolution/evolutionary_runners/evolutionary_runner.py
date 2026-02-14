from ..population import generate_initial_population, crossover, mutate
from ..evaluators.evaluator import evaluate_individual
from typing import Type
import pandas as pd
import heapq

def run_evolution(df: pd.DataFrame, estrategia_cls: Type, param_ranges: dict, generations=10, pop_size=20):
    population = generate_initial_population(pop_size, param_ranges)

    for gen in range(generations):
        print(f"\nGerando geração {gen+1}...")

        # Avalia todos
        for ind in population:
            evaluate_individual(ind, df, estrategia_cls)

        # Seleciona os top 50%
        population.sort(key=lambda x: x.fitness, reverse=True)
        survivors = population[:pop_size//2]

        # Reproduz
        offspring = []
        while len(offspring) < pop_size - len(survivors):
            p1, p2 = random.sample(survivors, 2)
            child = crossover(p1, p2)
            child.genome = mutate(child.genome, param_ranges)
            offspring.append(child)

        population = survivors + offspring

    # Retorna os top N ao final
    population.sort(key=lambda x: x.fitness, reverse=True)
    return population[:5]
