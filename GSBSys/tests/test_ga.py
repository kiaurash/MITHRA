"""Tests for src/ga/ (chromosome, operators, evolution) and src/utils/parallel.py."""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.ga.chromosome import (
    CONTINUOUS_GENES,
    DISCRETE_GENES,
    GENE_BOUNDS,
    GENE_NAMES,
    N_GENES,
    clip_to_bounds,
    init_individual,
    init_population_lhs,
)
from src.ga.operators import crossover_hybrid, get_sigma_fraction, mutate_hybrid
from src.ga.evolution import run_single_restart
from src.utils.parallel import run_restarts_parallel, run_restarts_sequential


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_individual(deap_creator):
    """Create one random DEAP individual."""
    return init_individual(deap_creator.Individual)


# OBV (type=12) forces period=0 — the generic [5,100] bound does not apply.
_INDICATOR_PERIOD_BOUNDS = {
    0: (5, 50), 1: (10, 100), 2: (5, 50), 3: (10, 30), 4: (10, 50),
    5: (8, 20), 6: (10, 30), 7: (5, 50), 8: (10, 30), 9: (5, 50),
    10: (10, 100), 11: (10, 100), 12: (0, 0), 13: (10, 50), 14: (10, 30),
}


def _check_bounds(ind):
    """Assert each gene is within its valid bounds, period adjusted for OBV."""
    for i, name in enumerate(GENE_NAMES):
        lo, hi = GENE_BOUNDS[name]
        # Period genes: use indicator-specific bounds when type is known
        if name in ("ind1_period", "ind2_period", "ind3_period"):
            slot = ["ind1_period", "ind2_period", "ind3_period"].index(name)
            ind_type = int(ind[slot * 3])
            lo, hi = _INDICATOR_PERIOD_BOUNDS[ind_type]
        assert lo <= ind[i] <= hi, f"Gene {name} ({ind[i]}) out of bounds [{lo}, {hi}]"


def _dummy_fitness(ind) -> Tuple[float, ...]:
    """Fitness = weighted sum of continuous genes (cheap, deterministic enough)."""
    return (float(sum(ind[i] for i in CONTINUOUS_GENES)),)


def _zero_fitness(ind) -> Tuple[float, ...]:
    """Always returns zero fitness — simulates all-zero population collapse."""
    return (0.0,)


# ---------------------------------------------------------------------------
# Chromosome tests
# ---------------------------------------------------------------------------


class TestChromosome:
    def test_n_genes_is_13(self):
        assert N_GENES == 13

    def test_discrete_plus_continuous_cover_all_genes(self):
        all_genes = sorted(DISCRETE_GENES + CONTINUOUS_GENES)
        assert all_genes == list(range(N_GENES))

    def test_gene_names_length(self):
        assert len(GENE_NAMES) == N_GENES

    def test_init_individual_length(self, deap_creator):
        ind = _make_individual(deap_creator)
        assert len(ind) == N_GENES

    def test_init_individual_within_bounds(self, deap_creator):
        for _ in range(20):
            ind = _make_individual(deap_creator)
            _check_bounds(ind)

    def test_discrete_genes_are_integers(self, deap_creator):
        for _ in range(20):
            ind = _make_individual(deap_creator)
            for i in DISCRETE_GENES:
                assert ind[i] == int(ind[i]), f"Discrete gene {i} is not integer: {ind[i]}"

    def test_clip_to_bounds_fixes_overflow(self, deap_creator):
        ind = _make_individual(deap_creator)
        # Force out-of-bounds
        ind[9] = 999.0   # entry_threshold max is 50.0
        ind[10] = -5.0   # stop_loss_pct min is 0.01
        clip_to_bounds(ind)
        assert ind[9] == 50.0
        assert ind[10] == 0.01

    def test_clip_rounds_discrete_genes(self, deap_creator):
        ind = _make_individual(deap_creator)
        ind[0] = 7.6   # ind1_type — should round to 8
        clip_to_bounds(ind)
        assert ind[0] == 8.0

    def test_init_population_lhs_size(self, deap_creator):
        pop = init_population_lhs(deap_creator.Individual, n=50)
        assert len(pop) == 50

    def test_init_population_lhs_within_bounds(self, deap_creator):
        pop = init_population_lhs(deap_creator.Individual, n=30)
        for ind in pop:
            _check_bounds(ind)

    def test_obv_period_fixed_to_zero(self, deap_creator):
        """OBV (type=12) must have period=0."""
        for _ in range(30):
            ind = _make_individual(deap_creator)
            for slot in range(3):
                type_idx = slot * 3
                period_idx = slot * 3 + 1
                if int(ind[type_idx]) == 12:
                    assert ind[period_idx] == 0.0, "OBV period must be 0"


# ---------------------------------------------------------------------------
# Operator tests
# ---------------------------------------------------------------------------


class TestOperators:
    def test_crossover_returns_two_individuals(self, deap_creator):
        ind1 = _make_individual(deap_creator)
        ind2 = _make_individual(deap_creator)
        c1, c2 = crossover_hybrid(ind1, ind2)
        assert len(c1) == N_GENES
        assert len(c2) == N_GENES

    def test_crossover_preserves_bounds(self, deap_creator):
        for _ in range(10):
            ind1 = _make_individual(deap_creator)
            ind2 = _make_individual(deap_creator)
            c1, c2 = crossover_hybrid(ind1, ind2)
            _check_bounds(c1)
            _check_bounds(c2)

    def test_crossover_discrete_genes_are_integers(self, deap_creator):
        ind1 = _make_individual(deap_creator)
        ind2 = _make_individual(deap_creator)
        c1, c2 = crossover_hybrid(ind1, ind2)
        for i in DISCRETE_GENES:
            assert c1[i] == int(c1[i])
            assert c2[i] == int(c2[i])

    def test_mutate_returns_single_tuple(self, deap_creator):
        ind = _make_individual(deap_creator)
        result = mutate_hybrid(ind, sigma_fraction=0.1)
        assert isinstance(result, tuple) and len(result) == 1

    def test_mutate_preserves_bounds(self, deap_creator):
        for _ in range(20):
            ind = _make_individual(deap_creator)
            mutate_hybrid(ind, sigma_fraction=0.5)  # large sigma to stress-test bounds
            _check_bounds(ind)

    def test_mutate_discrete_genes_remain_integers(self, deap_creator):
        for _ in range(20):
            ind = _make_individual(deap_creator)
            mutate_hybrid(ind, sigma_fraction=0.2)
            for i in DISCRETE_GENES:
                assert ind[i] == int(ind[i])

    def test_get_sigma_fraction_early(self):
        assert get_sigma_fraction(0, 1000) == 0.20
        assert get_sigma_fraction(100, 1000) == 0.20
        assert get_sigma_fraction(199, 1000) == 0.20

    def test_get_sigma_fraction_mid(self):
        assert get_sigma_fraction(200, 1000) == 0.10
        assert get_sigma_fraction(400, 1000) == 0.10
        assert get_sigma_fraction(599, 1000) == 0.10

    def test_get_sigma_fraction_late(self):
        assert get_sigma_fraction(600, 1000) == 0.05
        assert get_sigma_fraction(1000, 1000) == 0.05


# ---------------------------------------------------------------------------
# Evolution tests (small config — 10 gens, pop=20)
# ---------------------------------------------------------------------------


class _SmallConfig:
    """Minimal config stub for tests (avoid loading YAML)."""
    population_size = 20
    n_generations = 10
    cxpb = 0.9
    mutpb = 0.1


class TestEvolution:
    def test_run_single_restart_returns_dict(self, tmp_path):
        result = run_single_restart(
            restart_id=0,
            seed=42,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="test_run",
            results_dir=str(tmp_path),
            use_lhs=False,
        )
        assert isinstance(result, dict)
        assert "best_individual" in result
        assert "best_fitness" in result

    def test_best_individual_length(self, tmp_path):
        result = run_single_restart(
            restart_id=0,
            seed=7,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="test_run",
            results_dir=str(tmp_path),
        )
        assert len(result["best_individual"]) == N_GENES

    def test_best_individual_within_bounds(self, tmp_path):
        result = run_single_restart(
            restart_id=0,
            seed=99,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="test_run",
            results_dir=str(tmp_path),
        )
        ind = result["best_individual"]
        for i, name in enumerate(GENE_NAMES):
            lo, hi = GENE_BOUNDS[name]
            assert lo <= ind[i] <= hi, f"Best ind gene {name} out of bounds"

    def test_convergence_csv_created(self, tmp_path):
        run_single_restart(
            restart_id=3,
            seed=1,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="csv_test",
            results_dir=str(tmp_path),
        )
        csv_path = tmp_path / "csv_test" / "convergence_3.csv"
        assert csv_path.exists()

    def test_convergence_csv_has_header(self, tmp_path):
        run_single_restart(
            restart_id=0,
            seed=1,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="hdr_test",
            results_dir=str(tmp_path),
        )
        csv_path = tmp_path / "hdr_test" / "convergence_0.csv"
        lines = csv_path.read_text().strip().split("\n")
        assert lines[0] == "gen,best_fitness,avg_fitness,std_fitness"

    def test_reproducibility_same_seed(self, tmp_path):
        """Same seed must produce identical best_individual."""
        r1 = run_single_restart(0, 42, _dummy_fitness, _SmallConfig(), "rep1", str(tmp_path))
        r2 = run_single_restart(0, 42, _dummy_fitness, _SmallConfig(), "rep2", str(tmp_path))
        assert r1["best_individual"] == r2["best_individual"]

    def test_different_seeds_may_differ(self, tmp_path):
        """Different seeds should usually produce different results."""
        r1 = run_single_restart(0, 1, _dummy_fitness, _SmallConfig(), "d1", str(tmp_path))
        r2 = run_single_restart(0, 2, _dummy_fitness, _SmallConfig(), "d2", str(tmp_path))
        # Not guaranteed, but highly likely with different seeds
        # Just verify they both ran successfully
        assert r1["seed"] == 1
        assert r2["seed"] == 2

    def test_lhs_restart_works(self, tmp_path):
        result = run_single_restart(
            restart_id=0,
            seed=42,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="lhs_test",
            results_dir=str(tmp_path),
            use_lhs=True,
        )
        assert len(result["best_individual"]) == N_GENES

    def test_logger_is_defined(self):
        """evolution.py must define a module-level logger (not cause NameError)."""
        from src.ga.evolution import logger as ev_logger
        assert isinstance(ev_logger, logging.Logger)

    def test_all_zero_population_warning_does_not_raise(self, tmp_path):
        """When all fitness=0 and gen>50, logger.warning must not raise NameError.

        The convergence monitor is patched to never early-stop so the loop
        runs past gen 50 and the warning branch is exercised.
        """
        class _ZeroFitnessConfig:
            population_size = 5
            n_generations = 55
            cxpb = 0.0
            mutpb = 0.0

        never_stop = MagicMock()
        never_stop.update.return_value = False

        with patch("src.ga.evolution._ConvergenceMonitor", return_value=never_stop):
            result = run_single_restart(
                restart_id=7,
                seed=0,
                fitness_fn=_zero_fitness,
                config=_ZeroFitnessConfig(),
                run_id="zero_warn_test",
                results_dir=str(tmp_path),
            )

        assert result["best_fitness"] == 0.0
        assert result["restart_id"] == 7


# ---------------------------------------------------------------------------
# Sequential parallel runner tests
# ---------------------------------------------------------------------------


class TestParallel:
    def test_sequential_returns_list(self, tmp_path):
        from src.utils.seed import make_restart_seeds
        seeds = make_restart_seeds(base_seed=42, n=3)
        results = run_restarts_sequential(
            seeds=seeds,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="par_test",
            results_dir=str(tmp_path),
        )
        assert isinstance(results, list)
        assert len(results) == 3

    def test_sequential_sorted_by_fitness_desc(self, tmp_path):
        from src.utils.seed import make_restart_seeds
        seeds = make_restart_seeds(base_seed=7, n=3)
        results = run_restarts_sequential(
            seeds=seeds,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="sort_test",
            results_dir=str(tmp_path),
        )
        fitnesses = [r["best_fitness"] for r in results]
        assert fitnesses == sorted(fitnesses, reverse=True)

    def test_sequential_all_have_correct_fields(self, tmp_path):
        from src.utils.seed import make_restart_seeds
        seeds = make_restart_seeds(base_seed=1, n=2)
        results = run_restarts_sequential(
            seeds=seeds,
            fitness_fn=_dummy_fitness,
            config=_SmallConfig(),
            run_id="fields_test",
            results_dir=str(tmp_path),
        )
        required = {"best_individual", "best_fitness", "restart_id", "seed", "n_generations_run", "converged_early"}
        for r in results:
            assert required.issubset(r.keys())

    def test_parallel_calls_warmup_jit_before_pool(self, tmp_path):
        """run_restarts_parallel must call warmup_jit() before spawning workers."""
        from src.utils.seed import make_restart_seeds

        seeds = make_restart_seeds(base_seed=99, n=1)
        with (
            patch("src.utils.parallel.warmup_jit") as mock_warmup,
            patch("src.utils.parallel.multiprocessing.get_context") as mock_ctx,
        ):
            # Make Pool.starmap return a minimal valid result without spawning
            mock_pool = MagicMock()
            mock_pool.__enter__ = MagicMock(return_value=mock_pool)
            mock_pool.__exit__ = MagicMock(return_value=False)
            mock_pool.starmap.return_value = [
                {
                    "restart_id": 0, "seed": seeds[0], "best_individual": [0.0] * 13,
                    "best_fitness": 1.0, "n_generations_run": 5, "converged_early": False,
                }
            ]
            mock_ctx.return_value.Pool.return_value = mock_pool

            run_restarts_parallel(
                seeds=seeds,
                fitness_fn=_dummy_fitness,
                config=_SmallConfig(),
                run_id="warmup_test",
                results_dir=str(tmp_path),
            )

        mock_warmup.assert_called_once()
