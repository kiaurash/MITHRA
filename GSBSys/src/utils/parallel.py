"""Parallel GA restart execution.

Runs n_restarts independent GA restarts in parallel using
``multiprocessing.Pool`` with the spawn context (required on Windows;
also safer on macOS with fork + Numba).

Worker safety:
  - Each worker calls run_single_restart(), which re-registers DEAP creator
    with hasattr guards at the top of the function.
  - fitness_fn must be a picklable top-level function (not a lambda or closure).
  - The cache dict is passed as an argument — it must contain only NumPy arrays
    and Python scalars (pickle-safe).

Usage::

    from src.utils.parallel import run_restarts_parallel
    from src.ga.fitness import evaluate_individual
    from functools import partial

    eval_fn = partial(evaluate_individual, cache=cache, engine=engine)
    results = run_restarts_parallel(seeds, eval_fn, config)
"""

from __future__ import annotations

import multiprocessing
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.ga.evolution import run_single_restart


def run_restarts_parallel(
    seeds: List[int],
    fitness_fn: Callable[[list], Tuple[float, ...]],
    config: Any,
    run_id: str = "default",
    results_dir: str = "results",
    n_workers: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Run all GA restarts in parallel and return sorted results.

    Restart 0 uses Latin Hypercube Sampling for population initialization;
    restarts 1–N use random initialization seeded from ``seeds[i]``.

    Args:
        seeds:       List of int seeds, one per restart.  Length = n_restarts.
        fitness_fn:  Top-level callable — must be picklable (no lambdas).
        config:      GAConfig with population_size, n_generations, cxpb, mutpb.
        run_id:      Unique identifier for output files.
        results_dir: Root directory for convergence CSV files.
        n_workers:   Number of parallel workers. Defaults to min(len(seeds), cpu_count).

    Returns:
        List of result dicts from run_single_restart(), sorted by
        best_fitness descending (best result first).
    """
    n_restarts = len(seeds)
    if n_workers is None:
        n_workers = min(n_restarts, os.cpu_count() or 1)

    # Build argument tuples for each restart
    args_list = [
        (
            restart_id,
            seeds[restart_id],
            fitness_fn,
            config,
            run_id,
            results_dir,
            restart_id == 0,  # use_lhs=True for restart 0 only
        )
        for restart_id in range(n_restarts)
    ]

    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(processes=n_workers) as pool:
        results = pool.starmap(run_single_restart, args_list)

    results.sort(key=lambda r: r["best_fitness"], reverse=True)
    return results


def run_restarts_sequential(
    seeds: List[int],
    fitness_fn: Callable[[list], Tuple[float, ...]],
    config: Any,
    run_id: str = "default",
    results_dir: str = "results",
) -> List[Dict[str, Any]]:
    """Sequential fallback — same interface as run_restarts_parallel.

    Use in tests or single-core environments where spawning workers is
    prohibitively expensive.
    """
    results = []
    for restart_id, seed in enumerate(seeds):
        result = run_single_restart(
            restart_id=restart_id,
            seed=seed,
            fitness_fn=fitness_fn,
            config=config,
            run_id=run_id,
            results_dir=results_dir,
            use_lhs=(restart_id == 0),
        )
        results.append(result)

    results.sort(key=lambda r: r["best_fitness"], reverse=True)
    return results
