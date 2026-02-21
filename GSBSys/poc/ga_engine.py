"""
Genetic Algorithm engine module for GA Trading System POC

Implements DEAP-based GA with configuration from implementation plan:
- Population: 100
- Generations: 1000
- Crossover probability (CXPB): 0.7
- Mutation probability (MUTPB): 0.2
"""

import random
import numpy as np
from deap import base, creator, tools, algorithms
from typing import Callable, List, Tuple
import pandas as pd
from config import (
    POPULATION_SIZE, GENERATIONS, CXPB, MUTPB, INDPB, GENE_BOUNDS
)


def setup_deap(fitness_function: Callable) -> Tuple[base.Toolbox, tools.Statistics]:
    """
    Setup DEAP framework with toolbox and statistics.

    Args:
        fitness_function: Function to evaluate individual fitness

    Returns:
        Tuple of (toolbox, statistics)
    """
    # Create fitness and individual classes (only if not already created)
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # Maximize fitness

    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)

    # Initialize toolbox
    toolbox = base.Toolbox()

    # Gene generators for each parameter
    # [rsi_buy, rsi_sell, stop_loss, take_profit, position_size]
    toolbox.register("attr_rsi_buy", random.uniform, *GENE_BOUNDS['rsi_buy'])
    toolbox.register("attr_rsi_sell", random.uniform, *GENE_BOUNDS['rsi_sell'])
    toolbox.register("attr_stop_loss", random.uniform, *GENE_BOUNDS['stop_loss'])
    toolbox.register("attr_take_profit", random.uniform, *GENE_BOUNDS['take_profit'])
    toolbox.register("attr_position_size", random.uniform, *GENE_BOUNDS['position_size'])

    # Individual generator
    toolbox.register(
        "individual",
        tools.initCycle,
        creator.Individual,
        (
            toolbox.attr_rsi_buy,
            toolbox.attr_rsi_sell,
            toolbox.attr_stop_loss,
            toolbox.attr_take_profit,
            toolbox.attr_position_size
        ),
        n=1
    )

    # Population generator
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Genetic operators
    toolbox.register("evaluate", fitness_function)
    toolbox.register("mate", tools.cxTwoPoint)  # Two-point crossover
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=INDPB)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Statistics
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    return toolbox, stats


def repair_individual(individual: List[float]) -> List[float]:
    """
    Repair individual to ensure all constraints are satisfied.

    Constraints:
    - rsi_buy < rsi_sell
    - stop_loss < take_profit
    - All genes within bounds

    Args:
        individual: Individual to repair

    Returns:
        Repaired individual
    """
    # Unpack
    rsi_buy, rsi_sell, stop_loss, take_profit, position_size = individual

    # Enforce bounds
    rsi_buy = np.clip(rsi_buy, *GENE_BOUNDS['rsi_buy'])
    rsi_sell = np.clip(rsi_sell, *GENE_BOUNDS['rsi_sell'])
    stop_loss = np.clip(stop_loss, *GENE_BOUNDS['stop_loss'])
    take_profit = np.clip(take_profit, *GENE_BOUNDS['take_profit'])
    position_size = np.clip(position_size, *GENE_BOUNDS['position_size'])

    # Enforce rsi_buy < rsi_sell
    if rsi_buy >= rsi_sell:
        mid = (rsi_buy + rsi_sell) / 2
        rsi_buy = mid - 5
        rsi_sell = mid + 5

    # Enforce stop_loss < take_profit
    if stop_loss >= take_profit:
        mid = (stop_loss + take_profit) / 2
        stop_loss = mid * 0.8
        take_profit = mid * 1.2

    return [rsi_buy, rsi_sell, stop_loss, take_profit, position_size]


def run_evolution(
    toolbox: base.Toolbox,
    stats: tools.Statistics,
    population_size: int = POPULATION_SIZE,
    n_generations: int = GENERATIONS,
    cxpb: float = CXPB,
    mutpb: float = MUTPB,
    verbose: bool = True
) -> Tuple[list, tools.Logbook]:
    """
    Run genetic algorithm evolution.

    Args:
        toolbox: DEAP toolbox with registered operators
        stats: Statistics object
        population_size: Population size
        n_generations: Number of generations
        cxpb: Crossover probability
        mutpb: Mutation probability
        verbose: Print progress

    Returns:
        Tuple of (final_population, logbook)
    """
    # Create initial population
    population = toolbox.population(n=population_size)

    # Repair all individuals
    for ind in population:
        ind[:] = repair_individual(ind)

    # Hall of fame to keep best individuals
    hof = tools.HallOfFame(10)

    # Logbook to track statistics
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + stats.fields

    # Evaluate initial population
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    # Update hall of fame and statistics
    hof.update(population)
    record = stats.compile(population)
    logbook.record(gen=0, nevals=len(population), **record)

    if verbose:
        print(f"Gen 0: {record}")

    # Evolution loop
    for gen in range(1, n_generations + 1):
        # Select offspring
        offspring = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Repair all offspring
        for ind in offspring:
            ind[:] = repair_individual(ind)

        # Evaluate offspring with invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid_ind))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Replace population
        population[:] = offspring

        # Update hall of fame and statistics
        hof.update(population)
        record = stats.compile(population)
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)

        # Print progress every 100 generations
        if verbose and (gen % 100 == 0 or gen == n_generations):
            print(f"Gen {gen}: {record}")
            print(f"  Best individual: {hof[0]}")
            print(f"  Best fitness: {hof[0].fitness.values[0]:.6f}")

    return population, logbook, hof


if __name__ == "__main__":
    # Test GA engine with simple fitness function
    print("Testing GA engine with dummy fitness function...")

    def dummy_fitness(individual):
        """Simple test fitness: maximize negative sum of absolute values"""
        return (sum([-abs(x) for x in individual]),)

    toolbox, stats = setup_deap(dummy_fitness)

    print("\nRunning 10 generations as test...")
    pop, log, hof = run_evolution(toolbox, stats, population_size=20, n_generations=10, verbose=True)

    print(f"\nBest individual found: {hof[0]}")
    print(f"Best fitness: {hof[0].fitness.values[0]:.6f}")
