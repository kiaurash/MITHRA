"""Experiment 04: Phase 3 robustness — walk-forward, sensitivity, regime testing.

Demonstrates the full Phase 3 robustness pipeline on synthetic SPY-like data:
  Module 1  Walk-Forward GA       (rolling re-optimisation)
  Module 2  Sensitivity Analysis  (per-gene ±10% perturbation)
  Module 3  Regime Testing        (bull/bear/sideways breakdown)

Usage:
    python experiments/04_phase3_robustness.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
from src.robustness.regime_classifier import RegimeLabel, run_regime_testing
from src.robustness.sensitivity import run_sensitivity_analysis
from src.robustness.walk_forward import run_walk_forward_ga
from src.validation.family_grouping import run_family_grouping

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Synthetic data generator
# ---------------------------------------------------------------------------

def generate_synthetic_ohlcv(n_bars: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, 0.012, n_bars)
    close = 100.0 * np.exp(np.cumsum(returns))
    noise = rng.uniform(0.001, 0.005, n_bars)
    high  = close * (1 + noise)
    low   = close * (1 - noise)
    open_ = np.roll(close, 1); open_[0] = close[0]
    volume = rng.integers(500_000, 3_000_000, n_bars).astype(float)
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars, freq="D"),
        "open":   open_.astype(np.float32),
        "high":   high.astype(np.float32),
        "low":    low.astype(np.float32),
        "close":  close.astype(np.float32),
        "volume": volume,
    })


# Best individual from experiments/03_phase2_validation.py
BEST_INDIVIDUAL = [
    0, 14, 1.2,
    5,  9, 0.8,
    13, 20, 1.0,
    0.3, 0.04, 0.08, 1.0,
]

WARMUP_BARS  = 252
NORM_WINDOW  = 252


def main() -> None:
    log.info("Phase 3 robustness experiment starting …")
    warmup_jit()
    engine = NumbaBacktestEngine()

    # Full-period data (warmup + 2× train + enough test windows)
    total_bars = WARMUP_BARS + 504 + 5 * 126   # warmup + 2yr + 5 × 6mo
    df = generate_synthetic_ohlcv(total_bars, seed=42)

    # -----------------------------------------------------------------------
    # Module 1: Walk-Forward GA
    # -----------------------------------------------------------------------
    log.info("Module 1: Walk-Forward GA …")

    def mock_ga_runner(train_df: pd.DataFrame) -> list:
        """For the demo, return the best individual without re-running GA."""
        return BEST_INDIVIDUAL

    wf_result = run_walk_forward_ga(
        df, mock_ga_runner, engine,
        train_bars=504, test_bars=126, step_bars=126,
        normalization_window=NORM_WINDOW, warmup_bars=WARMUP_BARS,
    )
    log.info("  Windows: %d total, %d profitable",
             wf_result.n_total_windows, wf_result.n_profitable_windows)
    log.info("  Avg OOS PF: %.3f | MVP=%s | Production=%s",
             wf_result.avg_test_pf,
             "PASS" if wf_result.passed_mvp else "FAIL",
             "PASS" if wf_result.passed_production else "FAIL")
    for w in wf_result.windows:
        log.info("    Window %d: PF=%.3f  trades=%d  [%s]",
                 w.window_idx, w.test_profit_factor, w.n_test_trades,
                 "profit" if w.profitable else "loss")

    # -----------------------------------------------------------------------
    # Module 2: Sensitivity Analysis
    # -----------------------------------------------------------------------
    log.info("Module 2: Sensitivity Analysis …")

    # Build a FamilyResult for CoV correlation
    rng = np.random.default_rng(0)
    restart_results = [
        {"best_individual": [g + rng.normal(0, abs(g) * 0.05 + 1e-6) if isinstance(g, float) else g
                             for g in BEST_INDIVIDUAL],
         "best_fitness": 100.0 + rng.normal(0, 20)}
        for _ in range(10)
    ]
    family_result = run_family_grouping(restart_results)

    sens_result = run_sensitivity_analysis(
        BEST_INDIVIDUAL, df, engine,
        normalization_window=NORM_WINDOW, warmup_bars=WARMUP_BARS,
        family_result=family_result,
    )
    log.info("  Base PF: %.3f | Mean sensitivity: %.4f",
             sens_result.base_pf, sens_result.mean_sensitivity)
    log.info("  Most sensitive gene: %s", sens_result.most_sensitive_gene)
    if sens_result.cov_correlation is not None:
        log.info("  Sensitivity ↔ CoV correlation: %.4f", sens_result.cov_correlation)
    log.info("  Top-5 sensitive genes:")
    sorted_gs = sorted(sens_result.gene_sensitivities, key=lambda g: g.sensitivity, reverse=True)
    for gs in sorted_gs[:5]:
        log.info("    %-20s  sens=%.4f  +PF=%.3f  -PF=%.3f",
                 gs.gene_name, gs.sensitivity, gs.plus_pf, gs.minus_pf)

    # -----------------------------------------------------------------------
    # Module 3: Regime Testing
    # -----------------------------------------------------------------------
    log.info("Module 3: Regime Testing …")
    regime_result = run_regime_testing(
        BEST_INDIVIDUAL, df, engine,
        normalization_window=NORM_WINDOW, warmup_bars=WARMUP_BARS,
        regime_window=63,
    )
    log.info("  Dominant regime : %s (%d bars)",
             regime_result.dominant_regime.value, {
                 RegimeLabel.BULL:     regime_result.bull.n_bars,
                 RegimeLabel.BEAR:     regime_result.bear.n_bars,
                 RegimeLabel.SIDEWAYS: regime_result.sideways.n_bars,
             }[regime_result.dominant_regime])
    log.info("  Best regime     : %s", regime_result.best_regime.value)
    log.info("  Worst regime    : %s", regime_result.worst_regime.value)
    for perf in [regime_result.bull, regime_result.bear, regime_result.sideways]:
        log.info("    %-10s  bars=%-5d  PF=%.3f  ret=%.2f%%  [%s]",
                 perf.label.value, perf.n_bars, perf.profit_factor,
                 perf.total_return_pct, "profit" if perf.profitable else "loss")

    log.info("Phase 3 experiment complete.")


if __name__ == "__main__":
    main()
