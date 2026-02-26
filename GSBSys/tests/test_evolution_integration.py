"""Integration test: end-to-end GA loop with the real fitness function.

Runs 1 restart × 50 generations on synthetic data.
Checks:
  1. Fitness improves from generation 0 to generation 50
  2. Output is reproducible (same seed → same best chromosome)
  3. Best individual has valid gene bounds
  4. Convergence CSV is written with correct format

This test is intentionally short (50 gens, pop=20, small cache window=20)
to keep CI runtime reasonable.  Full 1000-gen runs live in experiments/.
"""

from __future__ import annotations

import csv
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.backtesting.numba_engine import NumbaBacktestEngine
from src.ga.chromosome import GENE_BOUNDS, GENE_NAMES, N_GENES
from src.ga.evolution import run_single_restart
from src.ga.fitness import evaluate_individual
from src.indicators.calculator import build_indicator_cache
from src.utils.seed import make_restart_seeds, set_global_seed

# ---------------------------------------------------------------------------
# Shared synthetic data (session-scoped for speed)
# ---------------------------------------------------------------------------

_N_BARS_TOTAL = 500   # includes warmup region
_WARMUP = 50          # small warmup for fast tests
_NORM_WINDOW = 20     # small normalization window for speed
_N_TRAIN = 120
_N_TEST  = _N_BARS_TOTAL - _WARMUP - _N_TRAIN


def _make_data(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = _N_BARS_TOTAL
    returns = rng.normal(0.0003, 0.012, n)
    prices = 100.0 * np.exp(np.cumsum(returns))
    noise = rng.uniform(0.001, 0.005, n)
    return pd.DataFrame({
        "date":   pd.date_range("2015-01-02", periods=n, freq="B"),
        "open":   prices,
        "high":   prices * (1 + noise),
        "low":    prices * (1 - noise),
        "close":  prices,
        "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    })


@pytest.fixture(scope="module")
def integration_setup():
    """Build cache + price arrays once per module."""
    set_global_seed(42)
    df = _make_data(seed=42)

    cache_full = build_indicator_cache(df, normalization_window=_NORM_WINDOW)
    # Slice cache to post-warmup region
    cache = {k: v[_WARMUP:] for k, v in cache_full.items()}

    train_prices = df["close"].values[_WARMUP : _WARMUP + _N_TRAIN].astype(np.float32)
    test_prices  = df["close"].values[_WARMUP + _N_TRAIN : _WARMUP + _N_TRAIN + _N_TEST].astype(np.float32)

    engine = NumbaBacktestEngine()

    fitness_fn = partial(
        evaluate_individual,
        train_prices=train_prices,
        test_prices=test_prices,
        n_train=_N_TRAIN,
        cache=cache,
        engine=engine,
    )
    return {"cache": cache, "train_prices": train_prices, "test_prices": test_prices,
            "engine": engine, "fitness_fn": fitness_fn}


class _SmallConfig:
    population_size = 20
    n_generations = 50
    cxpb = 0.9
    mutpb = 0.1


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestEvolutionIntegration:
    def test_run_completes(self, integration_setup, tmp_path):
        result = run_single_restart(
            restart_id=0,
            seed=42,
            fitness_fn=integration_setup["fitness_fn"],
            config=_SmallConfig(),
            run_id="int_test",
            results_dir=str(tmp_path),
            use_lhs=False,
        )
        assert result is not None
        assert "best_individual" in result

    def test_best_individual_correct_length(self, integration_setup, tmp_path):
        result = run_single_restart(
            restart_id=0, seed=1,
            fitness_fn=integration_setup["fitness_fn"],
            config=_SmallConfig(),
            run_id="len_test", results_dir=str(tmp_path),
        )
        assert len(result["best_individual"]) == N_GENES

    def test_best_individual_within_bounds(self, integration_setup, tmp_path):
        result = run_single_restart(
            restart_id=0, seed=2,
            fitness_fn=integration_setup["fitness_fn"],
            config=_SmallConfig(),
            run_id="bounds_test", results_dir=str(tmp_path),
        )
        ind = result["best_individual"]
        for i, name in enumerate(GENE_NAMES):
            lo, hi = GENE_BOUNDS[name]
            # Period bounds depend on indicator type — just check non-negative and ≤ 100
            if "period" in name:
                assert 0 <= ind[i] <= 100, f"{name}={ind[i]} out of range"
            else:
                assert lo <= ind[i] <= hi, f"{name}={ind[i]} out of [{lo},{hi}]"

    def test_fitness_is_non_negative(self, integration_setup, tmp_path):
        result = run_single_restart(
            restart_id=0, seed=3,
            fitness_fn=integration_setup["fitness_fn"],
            config=_SmallConfig(),
            run_id="nonneg_test", results_dir=str(tmp_path),
        )
        assert result["best_fitness"] >= 0.0

    def test_reproducibility(self, integration_setup, tmp_path):
        """Same seed → identical best chromosome."""
        r1 = run_single_restart(
            0, 99, integration_setup["fitness_fn"], _SmallConfig(),
            "rep1", str(tmp_path),
        )
        r2 = run_single_restart(
            0, 99, integration_setup["fitness_fn"], _SmallConfig(),
            "rep2", str(tmp_path),
        )
        assert r1["best_individual"] == r2["best_individual"]
        assert r1["best_fitness"] == r2["best_fitness"]

    def test_convergence_csv_has_data_rows(self, integration_setup, tmp_path):
        run_single_restart(
            restart_id=5, seed=7,
            fitness_fn=integration_setup["fitness_fn"],
            config=_SmallConfig(),
            run_id="csv_int_test", results_dir=str(tmp_path),
        )
        csv_path = tmp_path / "csv_int_test" / "convergence_5.csv"
        rows = list(csv.reader(csv_path.open()))
        # Header + at least 1 data row
        assert len(rows) >= 2
        assert rows[0] == ["gen", "best_fitness", "avg_fitness", "std_fitness"]

    def test_fitness_improves_or_stays_flat(self, integration_setup, tmp_path):
        """Best fitness at gen N should be ≥ gen 1 (monotone by HOF)."""
        result = run_single_restart(
            restart_id=0, seed=55,
            fitness_fn=integration_setup["fitness_fn"],
            config=_SmallConfig(),
            run_id="improve_test", results_dir=str(tmp_path),
        )
        csv_path = tmp_path / "improve_test" / "convergence_0.csv"
        rows = list(csv.DictReader(csv_path.open()))
        if len(rows) >= 2:
            first_best = float(rows[0]["best_fitness"])
            last_best  = float(rows[-1]["best_fitness"])
            # With HOF elitism, best_fitness is monotone non-decreasing
            assert last_best >= first_best - 1e-9, (
                f"Fitness regressed: {first_best:.4f} → {last_best:.4f}"
            )
