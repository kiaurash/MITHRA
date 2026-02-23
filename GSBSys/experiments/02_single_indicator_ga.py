"""Experiment 02: Single-indicator GA — reproduce POC result with Phase 1 engine.

Goal: Run 1 restart × 100 generations with the real fitness function on
synthetic SPY-like data. Expect PF ≥ 1.0 on the test set.

Usage:
    python experiments/02_single_indicator_ga.py

This experiment validates the full Phase 1 stack end-to-end:
  Data → Indicator Cache → Signal Generation → Backtest → Fitness → GA

It does NOT use yfinance (avoids network dependency); instead it generates
synthetic trending price data that mimics an equity time series.
"""

from __future__ import annotations

import logging
import sys
import time
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
from src.ga.evolution import run_single_restart
from src.ga.fitness import evaluate_individual
from src.indicators.calculator import build_indicator_cache
from src.utils.seed import make_restart_seeds, set_global_seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_SEED = 42
N_BARS = 1_000       # ~4 years of daily data (post-warmup headroom)
WARMUP_BARS = 252
TRAIN_RATIO = 0.4
N_GENS = 100
POP_SIZE = 30        # Small for speed in experiment


class _Config:
    population_size = POP_SIZE
    n_generations = N_GENS
    cxpb = 0.95
    mutpb = 0.05


# ---------------------------------------------------------------------------
# Synthetic data generator
# ---------------------------------------------------------------------------

def _make_synthetic_ohlcv(n: int, seed: int = 0) -> pd.DataFrame:
    """Generate synthetic trending OHLCV data."""
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, 0.012, n)  # slight upward drift, ~1.2% daily vol
    prices = 100.0 * np.exp(np.cumsum(returns))
    prices = np.clip(prices, 1.0, None)
    noise = rng.uniform(0.001, 0.005, n)
    return pd.DataFrame({
        "date":   pd.date_range("2015-01-02", periods=n, freq="B"),
        "open":   prices,
        "high":   prices * (1 + noise),
        "low":    prices * (1 - noise),
        "close":  prices,
        "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    set_global_seed(BASE_SEED)

    logger.info("Generating synthetic price data (%d bars)...", N_BARS + WARMUP_BARS)
    df = _make_synthetic_ohlcv(N_BARS + WARMUP_BARS, seed=BASE_SEED)

    logger.info("Building indicator cache (normalization_window=50 for speed)...")
    t0 = time.perf_counter()
    cache = build_indicator_cache(df, normalization_window=50)
    logger.info("Cache built in %.2fs  (%d entries)", time.perf_counter() - t0, len(cache))

    # Train/test split (post-warmup)
    post_warmup = df.iloc[WARMUP_BARS:].reset_index(drop=True)
    n_total = len(post_warmup)
    n_train = max(1, int(n_total * TRAIN_RATIO))
    n_test = n_total - n_train

    # Prices for each split — use the full-data row offsets
    # cache arrays are indexed from bar 0 of df (includes warmup rows)
    train_start = WARMUP_BARS
    test_start  = WARMUP_BARS + n_train

    train_prices = df["close"].values[train_start : train_start + n_train].astype(np.float32)
    test_prices  = df["close"].values[test_start  : test_start  + n_test ].astype(np.float32)

    # Slice of cache arrays corresponding to post-warmup region
    # Build a sub-cache sliced to [WARMUP_BARS:] for signal generation
    sliced_cache = {k: v[WARMUP_BARS:] for k, v in cache.items()}

    logger.info("Train bars: %d  Test bars: %d", n_train, n_test)

    engine = NumbaBacktestEngine()
    warmup_jit()

    fitness_fn = partial(
        evaluate_individual,
        train_prices=train_prices,
        test_prices=test_prices,
        n_train=n_train,
        cache=sliced_cache,
        engine=engine,
    )

    seeds = make_restart_seeds(BASE_SEED, n=1)
    logger.info("Running 1 restart × %d generations (pop=%d)...", N_GENS, POP_SIZE)

    t1 = time.perf_counter()
    result = run_single_restart(
        restart_id=0,
        seed=seeds[0],
        fitness_fn=fitness_fn,
        config=_Config(),
        run_id="exp02",
        results_dir="results",
        use_lhs=True,
    )
    elapsed = time.perf_counter() - t1

    ind = result["best_individual"]
    best_fit = result["best_fitness"]

    logger.info("Completed in %.1fs  best_fitness=%.4f  gens_run=%d  converged_early=%s",
                elapsed, best_fit, result["n_generations_run"], result["converged_early"])

    # Report on best individual
    logger.info("Best chromosome: %s", [round(x, 4) for x in ind])

    test_fit = fitness_fn(ind)
    logger.info("Re-evaluated fitness: %.4f", test_fit[0])

    # Backtest best individual for PF
    from src.indicators.signal_generator import generate_signals_weighted_sum
    signals = generate_signals_weighted_sum(ind, sliced_cache)
    test_result = engine.run(
        signals[n_train:], test_prices,
        float(ind[10]), float(ind[11]), float(ind[12]),
    )

    logger.info("Test set — PF: %.3f  Trades: %d  Total PnL: $%.2f",
                test_result.profit_factor, test_result.n_trades, test_result.total_pnl)

    if test_result.profit_factor >= 1.0:
        logger.info("PASS: PF %.3f >= 1.0", test_result.profit_factor)
    else:
        logger.warning("SUBPAR: PF %.3f < 1.0 (short run — more gens needed)", test_result.profit_factor)


if __name__ == "__main__":
    main()
