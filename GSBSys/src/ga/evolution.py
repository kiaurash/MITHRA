"""Single-restart GA evolution loop.

Each restart is an independent run of the DEAP eaSimple-style loop with:
  - HallOfFame(2) elitism: top 2 individuals injected into each generation
  - Adaptive sigma: anneals 0.20 → 0.10 → 0.05 across generations
  - Convergence monitor: early-restart if std < 0.001 for 50+ gens OR
    no >1% improvement in 100 gens
  - Convergence log: written to results/{run_id}/convergence_{restart_id}.csv

IMPORTANT — Windows spawn multiprocessing:
  DEAP creator uses global module state. On Windows (spawn context), each
  worker subprocess starts fresh and creator.Individual is undefined.
  run_single_restart() re-registers creator at the top of each call with
  hasattr guards.
"""

from __future__ import annotations

import csv
import os
import random
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from src.ga.chromosome import (
    N_GENES,
    clip_to_bounds,
    init_individual,
    init_population_lhs,
)
from src.ga.operators import crossover_hybrid, get_sigma_fraction, mutate_hybrid
from src.utils.seed import set_global_seed


# ---------------------------------------------------------------------------
# DEAP registration helper (called once per process)
# ---------------------------------------------------------------------------


def _register_deap() -> Tuple[Any, Any, Any]:
    """Import and register DEAP creator with hasattr guards.

    Safe to call multiple times in the same process (guards prevent
    RuntimeError: 'FitnessMax' has already been created).

    Returns:
        (creator, base, tools) DEAP modules.
    """
    from deap import base, creator, tools

    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)

    return creator, base, tools


# ---------------------------------------------------------------------------
# Convergence monitor
# ---------------------------------------------------------------------------


class _ConvergenceMonitor:
    """Tracks stagnation for early-restart triggering."""

    def __init__(self, std_tol: float = 0.001, patience_std: int = 50, patience_pct: int = 100):
        self.std_tol = std_tol
        self.patience_std = patience_std
        self.patience_pct = patience_pct
        self._flat_count = 0
        self._no_improvement_count = 0
        self._best_fitness = -np.inf

    def update(self, best_fitness: float, std_fitness: float) -> bool:
        """Return True if early-restart should trigger."""
        # Std stagnation
        if std_fitness < self.std_tol:
            self._flat_count += 1
        else:
            self._flat_count = 0

        # No >1% improvement
        if self._best_fitness > 0:
            improvement = (best_fitness - self._best_fitness) / abs(self._best_fitness)
        else:
            improvement = best_fitness - self._best_fitness

        if improvement > 0.01:
            self._best_fitness = best_fitness
            self._no_improvement_count = 0
        else:
            self._no_improvement_count += 1

        if self._best_fitness == -np.inf:
            self._best_fitness = best_fitness

        return (
            self._flat_count >= self.patience_std
            or self._no_improvement_count >= self.patience_pct
        )


# ---------------------------------------------------------------------------
# Single restart
# ---------------------------------------------------------------------------


def run_single_restart(
    restart_id: int,
    seed: int,
    fitness_fn: Callable[[list], Tuple[float, ...]],
    config: Any,
    run_id: str = "default",
    results_dir: str = "results",
    use_lhs: bool = False,
) -> Dict[str, Any]:
    """Run one complete GA restart and return the best individual found.

    This function is designed to run in a subprocess (Windows spawn).
    It re-registers DEAP creator at the top with hasattr guards.

    Args:
        restart_id:  Index of this restart (0–9).
        seed:        Random seed for this restart.
        fitness_fn:  Callable (individual) → (fitness_value,). Must be
                     picklable (plain function, not lambda/closure).
        config:      GAConfig instance with n_generations, population_size,
                     cxpb, mutpb fields.
        run_id:      Unique run identifier for output directory naming.
        results_dir: Root directory for convergence CSV output.
        use_lhs:     If True, use Latin Hypercube Sampling for initial
                     population (restart 0 only).

    Returns:
        dict with keys:
          - ``best_individual``: list of 13 gene values
          - ``best_fitness``: float
          - ``restart_id``: int
          - ``seed``: int
          - ``n_generations_run``: int (may be < n_generations on early stop)
          - ``converged_early``: bool
    """
    # Re-register DEAP in this process (critical for Windows spawn)
    creator, base, tools = _register_deap()

    set_global_seed(seed)

    # --- Toolbox ---
    toolbox = base.Toolbox()
    toolbox.register("individual", init_individual, creator.Individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", fitness_fn)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # --- Population ---
    if use_lhs:
        pop = init_population_lhs(creator.Individual, n=config.population_size)
    else:
        pop = toolbox.population(n=config.population_size)

    hof = tools.HallOfFame(2)

    # --- Convergence logging ---
    log_path = Path(results_dir) / run_id / f"convergence_{restart_id}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    csv_file = open(log_path, "w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow(["gen", "best_fitness", "avg_fitness", "std_fitness"])

    monitor = _ConvergenceMonitor()
    converged_early = False
    gen = 0

    try:
        # Evaluate initial population
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        hof.update(pop)

        for gen in range(1, config.n_generations + 1):
            sigma = get_sigma_fraction(gen, config.n_generations)

            # Selection
            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))

            # Crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < config.cxpb:
                    crossover_hybrid(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in offspring:
                if random.random() < config.mutpb:
                    mutate_hybrid(mutant, sigma_fraction=sigma)
                    del mutant.fitness.values

            # Evaluate invalid individuals
            invalid = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = list(map(toolbox.evaluate, invalid))
            for ind, fit in zip(invalid, fitnesses):
                ind.fitness.values = fit

            # Elitism: inject HOF top-2 (replace worst 2 offspring)
            offspring.sort(key=lambda x: x.fitness.values[0])
            for i, elite in enumerate(hof):
                offspring[i] = toolbox.clone(elite)

            pop[:] = offspring
            hof.update(pop)

            # Stats
            fits = [ind.fitness.values[0] for ind in pop]
            best_fit = max(fits)
            avg_fit = float(np.mean(fits))
            std_fit = float(np.std(fits))

            writer.writerow([gen, best_fit, avg_fit, std_fit])

            # Warn if entire population has collapsed to zero fitness
            if best_fit == 0.0 and gen > 50:
                logger.warning(
                    "Restart %d gen %d: all-zero population. "
                    "Penalties may be too strict or no profitable signals exist.",
                    restart_id if "restart_id" in dir() else -1,
                    gen,
                )

            if monitor.update(best_fit, std_fit):
                converged_early = True
                break

    finally:
        csv_file.close()

    best = hof[0]
    return {
        "best_individual": list(best),
        "best_fitness": best.fitness.values[0],
        "restart_id": restart_id,
        "seed": seed,
        "n_generations_run": gen,
        "converged_early": converged_early,
    }
