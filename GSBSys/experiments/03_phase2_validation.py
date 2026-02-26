"""Experiment 03: Phase 2 validation — run all 4 layers on a GA result.

Demonstrates the full Phase 2 validation pipeline:
  Layer 1  Pearson equity-curve correlation gate
  Layer 2  Multi-period OOS (5 regime windows)
  Layer 3  Noise injection (8 data perturbation variants)
  Layer 4  Family grouping / parameter stability analysis

The experiment uses synthetic SPY-like data so it runs offline with no
network dependency.  It simulates 10 restart results by seeding the GA
with slight parameter variations around a known-good chromosome.

Usage:
    python experiments/03_phase2_validation.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum
from src.validation.family_grouping import run_family_grouping
from src.validation.multi_period_oos import run_multi_period_oos
from src.validation.noise_injection import run_noise_injection
from src.validation.pearson_filter import run_pearson_filter
from src.validation.report import build_report, save_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Synthetic data generator
# ---------------------------------------------------------------------------

def generate_synthetic_ohlcv(n_bars: int, seed: int = 0) -> pd.DataFrame:
    """Generate synthetic OHLCV data with a moderate upward drift."""
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, 0.012, n_bars)
    close = 100.0 * np.exp(np.cumsum(returns))
    noise = rng.uniform(0.001, 0.005, n_bars)
    high  = close * (1 + noise)
    low   = close * (1 - noise)
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    volume = rng.integers(500_000, 3_000_000, n_bars).astype(float)
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars, freq="D"),
        "open":   open_.astype(np.float32),
        "high":   high.astype(np.float32),
        "low":    low.astype(np.float32),
        "close":  close.astype(np.float32),
        "volume": volume,
    })


# ---------------------------------------------------------------------------
# Fixed chromosome (RSI + MACD + EMA, tuned for synthetic data)
# ---------------------------------------------------------------------------

BEST_INDIVIDUAL = [
    0, 14, 1.2,   # slot 0: RSI, period 14, weight 1.2
    5,  9, 0.8,   # slot 1: MACD, period 9, weight 0.8
    13, 20, 1.0,  # slot 2: EMA/SMA, period 20, weight 1.0
    0.3,          # gene 9: entry_threshold
    0.04,         # gene 10: stop_loss_pct
    0.08,         # gene 11: take_profit_pct
    1.0,          # gene 12: position_size_mult
]

WARMUP_BARS     = 252
NORM_WINDOW     = 252
TRAIN_SPLIT     = 0.40   # 40% train / 60% test


# ---------------------------------------------------------------------------
# Run layers
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("Phase 2 validation experiment starting …")

    warmup_jit()
    engine = NumbaBacktestEngine()

    # -----------------------------------------------------------------------
    # Synthetic full-period data (2010–2024 equivalent)
    # -----------------------------------------------------------------------
    total_bars = WARMUP_BARS + 3_650  # ~14 years of daily data
    df_full = generate_synthetic_ohlcv(total_bars, seed=42)

    cache_full = build_indicator_cache(df_full, normalization_window=NORM_WINDOW)
    post_warmup = df_full.iloc[WARMUP_BARS:].reset_index(drop=True)
    cache_post  = {k: v[WARMUP_BARS:] for k, v in cache_full.items()}
    prices_all  = post_warmup["close"].values.astype(np.float32)

    n_total = len(prices_all)
    n_train = int(n_total * TRAIN_SPLIT)

    train_prices = prices_all[:n_train]
    test_prices  = prices_all[n_train:]

    # -----------------------------------------------------------------------
    # Equity curves from train / test runs
    # -----------------------------------------------------------------------
    ind = BEST_INDIVIDUAL
    sl_pct  = float(ind[10])
    tp_pct  = float(ind[11])
    pos_mult = float(ind[12])

    cache_train = {k: v[:n_train] for k, v in cache_post.items()}
    cache_test  = {k: v[n_train:] for k, v in cache_post.items()}

    sig_train = generate_signals_weighted_sum(ind, cache_train)
    sig_test  = generate_signals_weighted_sum(ind, cache_test)

    res_train = engine.run(sig_train, train_prices, sl_pct, tp_pct, pos_mult)
    res_test  = engine.run(sig_test,  test_prices,  sl_pct, tp_pct, pos_mult)

    log.info("Train  | PF=%.3f  trades=%d  PnL=%.2f",
             res_train.profit_factor, res_train.n_trades, res_train.total_pnl)
    log.info("Test   | PF=%.3f  trades=%d  PnL=%.2f",
             res_test.profit_factor, res_test.n_trades, res_test.total_pnl)

    # -----------------------------------------------------------------------
    # Layer 1: Pearson filter
    # -----------------------------------------------------------------------
    log.info("Layer 1: Pearson equity curve filter …")
    pearson_result = run_pearson_filter(res_train.equity_curve, res_test.equity_curve)
    log.info("  Pearson r=%.4f | MVP=%s | Production=%s",
             pearson_result.pearson_r,
             "PASS" if pearson_result.passed_mvp else "FAIL",
             "PASS" if pearson_result.passed_production else "FAIL")

    # -----------------------------------------------------------------------
    # Layer 2: Multi-period OOS
    # -----------------------------------------------------------------------
    log.info("Layer 2: Multi-period OOS (5 regimes) …")

    def data_fn(start: str, end: str) -> pd.DataFrame:
        """Return a synthetic slice for the requested date range."""
        n = 3 * 252 + WARMUP_BARS  # 3 years + warmup
        seed = hash(start) % (2**31)
        return generate_synthetic_ohlcv(n, seed=abs(seed))

    oos_result = run_multi_period_oos(ind, engine, data_fn)
    log.info("  OOS profitable: %d/5 | MVP=%s | Production=%s",
             oos_result.n_profitable,
             "PASS" if oos_result.passed_mvp else "FAIL",
             "PASS" if oos_result.passed_production else "FAIL")
    for rr in oos_result.regime_results:
        status = "SKIP" if rr.skipped else ("profit" if rr.profitable else "loss")
        log.info("    %-28s  PF=%.3f  trades=%d  [%s]",
                 rr.label, rr.profit_factor, rr.n_trades, status)

    # -----------------------------------------------------------------------
    # Layer 3: Noise injection
    # -----------------------------------------------------------------------
    log.info("Layer 3: Noise injection (8 variants) …")
    noise_result = run_noise_injection(ind, df_full, engine,
                                       normalization_window=NORM_WINDOW,
                                       warmup_bars=WARMUP_BARS)
    log.info("  Noise profitable: %d/8 | MVP=%s | Production=%s",
             noise_result.n_profitable,
             "PASS" if noise_result.passed_mvp else "FAIL",
             "PASS" if noise_result.passed_production else "FAIL")
    for vr in noise_result.variant_results:
        log.info("    %-24s  PF=%.3f  %s",
                 vr.name, vr.profit_factor, "profit" if vr.profitable else "loss")

    # -----------------------------------------------------------------------
    # Layer 4: Family grouping
    # -----------------------------------------------------------------------
    log.info("Layer 4: Family grouping / CoV analysis …")
    rng = np.random.default_rng(0)
    restart_results = []
    for i in range(10):
        perturbed = [
            g + rng.normal(0, abs(g) * 0.05 + 1e-6) if isinstance(g, float) else g
            for g in ind
        ]
        restart_results.append({
            "best_individual": perturbed,
            "best_fitness":    100.0 + rng.normal(0, 20),
        })
    family_result = run_family_grouping(restart_results)
    log.info("  Mean CoV=%.4f | MVP=%s | Production=%s",
             family_result.mean_cov,
             "PASS" if family_result.passed_mvp else "FAIL",
             "PASS" if family_result.passed_production else "FAIL")

    # -----------------------------------------------------------------------
    # Final report
    # -----------------------------------------------------------------------
    report = build_report(pearson_result, oos_result, noise_result, family_result)
    print("\n" + report.summary)

    out_path = Path("experiments") / "results" / "03_phase2_validation_report.json"
    save_report(report, str(out_path))
    log.info("Report saved → %s", out_path)


if __name__ == "__main__":
    main()
