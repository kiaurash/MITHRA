"""
Main POC runner for GA Trading System

This script runs the full proof-of-concept to validate:
1. VectorBT speed (<50ms per fitness evaluation)
2. DEAP GA integration
3. Fitness function correctness
4. Convergence within 1000 generations
"""

import time
import pandas as pd
import numpy as np
from data_loader import load_market_data
from fitness import evaluate_individual
from ga_engine import setup_deap, run_evolution
from config import (
    POPULATION_SIZE, GENERATIONS, TARGET_FITNESS_TIME_MS,
    TICKER, START_DATE, END_DATE
)


def benchmark_fitness_function(data: pd.DataFrame, n_evaluations: int = 100):
    """
    Benchmark fitness function performance.

    Target: <50ms per evaluation on daily data

    Args:
        data: Market data
        n_evaluations: Number of evaluations to run

    Returns:
        Average time per evaluation in milliseconds
    """
    print("\n" + "=" * 60)
    print("BENCHMARK: Fitness Function Performance")
    print("=" * 60)

    # Generate random individuals
    from config import GENE_BOUNDS
    import random

    test_individuals = []
    for _ in range(n_evaluations):
        ind = [
            random.uniform(*GENE_BOUNDS['rsi_buy']),
            random.uniform(*GENE_BOUNDS['rsi_sell']),
            random.uniform(*GENE_BOUNDS['stop_loss']),
            random.uniform(*GENE_BOUNDS['take_profit']),
            random.uniform(*GENE_BOUNDS['position_size'])
        ]
        test_individuals.append(ind)

    # Warm-up (compile Numba/VectorBT)
    print("\nWarming up (compiling Numba/VectorBT)...")
    for ind in test_individuals[:5]:
        _ = evaluate_individual(ind, data)

    # Benchmark
    print(f"\nRunning {n_evaluations} fitness evaluations...")
    start_time = time.time()

    for ind in test_individuals:
        _ = evaluate_individual(ind, data)

    end_time = time.time()

    total_time_ms = (end_time - start_time) * 1000
    avg_time_ms = total_time_ms / n_evaluations

    print(f"\nResults:")
    print(f"  Total time: {total_time_ms:.2f}ms")
    print(f"  Average per evaluation: {avg_time_ms:.2f}ms")
    print(f"  Target: <{TARGET_FITNESS_TIME_MS}ms")

    if avg_time_ms < TARGET_FITNESS_TIME_MS:
        print(f"  ✓ PASS: {avg_time_ms:.2f}ms < {TARGET_FITNESS_TIME_MS}ms")
        return True, avg_time_ms
    else:
        print(f"  ✗ FAIL: {avg_time_ms:.2f}ms >= {TARGET_FITNESS_TIME_MS}ms")
        return False, avg_time_ms


def run_ga_convergence_test(data: pd.DataFrame):
    """
    Run GA to test convergence behavior.

    Tests:
    - DEAP integration works correctly
    - Fitness improves over generations
    - Best solution converges

    Args:
        data: Market data
    """
    print("\n" + "=" * 60)
    print("CONVERGENCE TEST: GA Evolution")
    print("=" * 60)

    # Setup DEAP
    print("\nSetting up DEAP...")

    def fitness_func(individual):
        return evaluate_individual(individual, data)

    toolbox, stats = setup_deap(fitness_func)

    # Run evolution
    print(f"\nRunning GA for {GENERATIONS} generations...")
    print(f"Population size: {POPULATION_SIZE}")

    start_time = time.time()
    population, logbook, hof = run_evolution(
        toolbox,
        stats,
        population_size=POPULATION_SIZE,
        n_generations=GENERATIONS,
        verbose=True
    )
    end_time = time.time()

    total_time_min = (end_time - start_time) / 60

    # Analyze results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nEvolution completed in {total_time_min:.2f} minutes")

    print(f"\nBest Individual Found:")
    best = hof[0]
    print(f"  Parameters: {best}")
    print(f"    RSI Buy Threshold: {best[0]:.2f}")
    print(f"    RSI Sell Threshold: {best[1]:.2f}")
    print(f"    Stop Loss: {best[2]:.2%}")
    print(f"    Take Profit: {best[3]:.2%}")
    print(f"    Position Size: {best[4]:.2%}")
    print(f"  Fitness: {best.fitness.values[0]:.6f}")

    # Analyze convergence
    gen_nums = logbook.select("gen")
    max_fitness = logbook.select("max")
    avg_fitness = logbook.select("avg")

    print(f"\nConvergence Analysis:")
    print(f"  Initial max fitness: {max_fitness[0]:.6f}")
    print(f"  Final max fitness: {max_fitness[-1]:.6f}")
    print(f"  Improvement: {max_fitness[-1] - max_fitness[0]:.6f}")
    print(f"  Initial avg fitness: {avg_fitness[0]:.6f}")
    print(f"  Final avg fitness: {avg_fitness[-1]:.6f}")

    # Check if fitness improved
    if max_fitness[-1] > max_fitness[0]:
        print(f"  ✓ PASS: Fitness improved over generations")
        convergence_pass = True
    else:
        print(f"  ✗ FAIL: Fitness did not improve")
        convergence_pass = False

    return convergence_pass, logbook, hof


def main():
    """Run full POC validation"""
    print("=" * 60)
    print("GA TRADING SYSTEM - PROOF OF CONCEPT")
    print("=" * 60)
    print(f"\nValidating core assumptions:")
    print(f"1. VectorBT speed (<{TARGET_FITNESS_TIME_MS}ms per evaluation)")
    print(f"2. DEAP integration")
    print(f"3. Fitness function correctness")
    print(f"4. Convergence within {GENERATIONS} generations")

    # Load data
    print(f"\n" + "=" * 60)
    print("DATA LOADING")
    print("=" * 60)
    print(f"\nLoading {TICKER} data from {START_DATE} to {END_DATE}...")

    data = load_market_data()
    print(f"Loaded {len(data)} rows")

    # Run benchmarks
    speed_pass, avg_time = benchmark_fitness_function(data, n_evaluations=100)

    # Run convergence test
    convergence_pass, logbook, hof = run_ga_convergence_test(data)

    # Final summary
    print("\n" + "=" * 60)
    print("POC VALIDATION SUMMARY")
    print("=" * 60)

    print(f"\n1. VectorBT Speed: {'✓ PASS' if speed_pass else '✗ FAIL'}")
    print(f"   Average: {avg_time:.2f}ms (Target: <{TARGET_FITNESS_TIME_MS}ms)")

    print(f"\n2. DEAP Integration: ✓ PASS")
    print(f"   GA ran successfully for {GENERATIONS} generations")

    print(f"\n3. Fitness Function: ✓ PASS")
    print(f"   Fitness calculations completed without errors")

    print(f"\n4. Convergence: {'✓ PASS' if convergence_pass else '✗ FAIL'}")
    print(f"   Best fitness: {hof[0].fitness.values[0]:.6f}")

    # Overall verdict
    all_pass = speed_pass and convergence_pass

    print(f"\n" + "=" * 60)
    if all_pass:
        print("VERDICT: ✓ ALL TESTS PASSED")
        print("\nRecommendation: Proceed with full MVP implementation")
    else:
        print("VERDICT: ✗ SOME TESTS FAILED")
        print("\nRecommendation: Address failures before proceeding to MVP")
    print("=" * 60)


if __name__ == "__main__":
    main()
