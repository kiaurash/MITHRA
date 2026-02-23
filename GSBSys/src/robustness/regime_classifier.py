"""Regime classification and per-regime performance — Phase 3, Module 3.

Classifies each bar as BULL, BEAR, or SIDEWAYS using a rolling price
return window, then runs the full backtest and aggregates the strategy's
bar-level returns by regime to compute per-regime profit factors.

Bull/Bear/Sideways definition (default):
  At bar t, compute the return over the preceding `window` bars.
  - return > bull_threshold  (+10%)  → BULL
  - return < bear_threshold  (-10%)  → BEAR
  - otherwise                        → SIDEWAYS

The regime at bar t reflects market conditions in the lead-up to that bar,
which is information available at signal time (no lookahead).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import numpy as np
import pandas as pd

from src.backtesting.engine import BacktestEngine, BacktestResult
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum


class RegimeLabel(str, Enum):
    """Market regime classification."""

    BULL     = "bull"
    BEAR     = "bear"
    SIDEWAYS = "sideways"


# ---------------------------------------------------------------------------
# Regime classifier
# ---------------------------------------------------------------------------

def classify_regimes(
    prices: np.ndarray,
    window: int = 63,
    bull_threshold: float = 0.10,
    bear_threshold: float = -0.10,
) -> np.ndarray:
    """Classify each bar as BULL, BEAR, or SIDEWAYS.

    Uses the rolling `window`-bar return ending at bar t.  Bars within the
    first `window` bars are classified as SIDEWAYS (insufficient history).

    Args:
        prices:          1-D array of close prices.
        window:          Look-back window for return calculation (default 63 ≈ 3 months).
        bull_threshold:  Return threshold above which bar is BULL (default +10%).
        bear_threshold:  Return threshold below which bar is BEAR (default −10%).

    Returns:
        Python list of RegimeLabel values, same length as prices.
    """
    prices = np.asarray(prices, dtype=np.float64)
    n = len(prices)
    labels: list = [RegimeLabel.SIDEWAYS] * n

    for t in range(window, n):
        ret = (prices[t] - prices[t - window]) / max(prices[t - window], 1e-8)
        if ret > bull_threshold:
            labels[t] = RegimeLabel.BULL
        elif ret < bear_threshold:
            labels[t] = RegimeLabel.BEAR
        # else: already SIDEWAYS

    return labels


# ---------------------------------------------------------------------------
# Regime performance dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegimePerformance:
    """Performance metrics for one regime.

    Attributes:
        label:             Regime type.
        n_bars:            Number of bars classified as this regime.
        profit_factor:     Gross profit / gross loss from regime bars.
        total_return_pct:  Cumulative sum of bar returns (%) in this regime.
        profitable:        True if profit_factor >= 1.0.
    """

    label: RegimeLabel
    n_bars: int
    profit_factor: float
    total_return_pct: float
    profitable: bool


@dataclass(frozen=True)
class RegimeTestResult:
    """Per-regime breakdown of strategy performance.

    Attributes:
        bull:             Performance in BULL bars.
        bear:             Performance in BEAR bars.
        sideways:         Performance in SIDEWAYS bars.
        dominant_regime:  Regime with the most bars.
        best_regime:      Regime with the highest PF.
        worst_regime:     Regime with the lowest PF.
    """

    bull:     RegimePerformance
    bear:     RegimePerformance
    sideways: RegimePerformance
    dominant_regime: RegimeLabel
    best_regime:     RegimeLabel
    worst_regime:    RegimeLabel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _regime_pf(returns: np.ndarray) -> float:
    """Compute profit factor from a 1-D array of bar returns."""
    gross_profit = float(np.sum(returns[returns > 0]))
    gross_loss   = float(np.abs(np.sum(returns[returns < 0])))
    if gross_loss < 1e-12:
        return float("inf") if gross_profit > 0 else 1.0
    return gross_profit / gross_loss


def _make_regime_performance(label: RegimeLabel, returns: np.ndarray, mask: np.ndarray) -> RegimePerformance:
    """Build RegimePerformance from masked bar-level returns."""
    regime_returns = returns[mask]
    n = int(mask.sum())
    pf    = _regime_pf(regime_returns) if n > 0 else 1.0
    total = float(np.sum(regime_returns)) * 100.0
    return RegimePerformance(
        label=label,
        n_bars=n,
        profit_factor=pf,
        total_return_pct=total,
        profitable=pf >= 1.0,
    )


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_regime_testing(
    individual: list,
    df: pd.DataFrame,
    engine: BacktestEngine,
    normalization_window: int = 252,
    warmup_bars: int = 252,
    regime_window: int = 63,
    bull_threshold: float = 0.10,
    bear_threshold: float = -0.10,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
    position_size_mult: Optional[float] = None,
) -> RegimeTestResult:
    """Run strategy on full data and aggregate returns by regime.

    Regime labels are computed on the post-warmup close prices.
    The strategy bar-level returns are partitioned by regime, and
    profit factors are computed independently for each regime.

    Args:
        individual:           13-gene chromosome.
        df:                   Full OHLCV DataFrame (includes warmup rows).
        engine:               BacktestEngine implementation.
        normalization_window: Rolling indicator normalisation window.
        warmup_bars:          Bars to discard at start (default 252).
        regime_window:        Rolling window for regime classification.
        bull_threshold:       Return threshold for BULL label.
        bear_threshold:       Return threshold for BEAR label.
        stop_loss_pct:        Override SL%.
        take_profit_pct:      Override TP%.
        position_size_mult:   Override position size multiplier.

    Returns:
        RegimeTestResult with per-regime metrics and dominance summary.
    """
    sl_pct   = stop_loss_pct      if stop_loss_pct      is not None else float(individual[10])
    tp_pct   = take_profit_pct    if take_profit_pct    is not None else float(individual[11])
    pos_mult = position_size_mult if position_size_mult is not None else float(individual[12])

    # Build indicator cache and slice post-warmup
    cache = build_indicator_cache(df, normalization_window=normalization_window)
    sliced_cache = {k: v[warmup_bars:] for k, v in cache.items()}
    prices = df["close"].values[warmup_bars:].astype(np.float32)

    # Classify regimes on post-warmup prices
    regime_labels = classify_regimes(
        prices.astype(np.float64),
        window=regime_window,
        bull_threshold=bull_threshold,
        bear_threshold=bear_threshold,
    )

    # Generate signals and run full backtest
    signals = generate_signals_weighted_sum(individual, sliced_cache)
    result: BacktestResult = engine.run(signals, prices, sl_pct, tp_pct, pos_mult)

    # Use bar-level returns from BacktestResult
    # returns has length = len(prices) - 1 (daily changes)
    # Align regime_labels: drop the first bar (no return for bar 0)
    returns = result.returns  # shape (n-1,)
    labels_aligned = regime_labels[1:]  # same length as returns

    bull_mask     = np.array([l == RegimeLabel.BULL     for l in labels_aligned])
    bear_mask     = np.array([l == RegimeLabel.BEAR     for l in labels_aligned])
    sideways_mask = np.array([l == RegimeLabel.SIDEWAYS for l in labels_aligned])

    bull_perf     = _make_regime_performance(RegimeLabel.BULL,     returns, bull_mask)
    bear_perf     = _make_regime_performance(RegimeLabel.BEAR,     returns, bear_mask)
    sideways_perf = _make_regime_performance(RegimeLabel.SIDEWAYS, returns, sideways_mask)

    all_perfs = [bull_perf, bear_perf, sideways_perf]

    dominant = max(all_perfs, key=lambda p: p.n_bars).label
    best     = max(all_perfs, key=lambda p: p.profit_factor).label
    # Worst by PF (treat inf as very high for ordering)
    def _finite_pf(p: RegimePerformance) -> float:
        pf = p.profit_factor
        return pf if pf != float("inf") else 1e9

    worst = min(all_perfs, key=_finite_pf).label

    return RegimeTestResult(
        bull=bull_perf,
        bear=bear_perf,
        sideways=sideways_perf,
        dominant_regime=dominant,
        best_regime=best,
        worst_regime=worst,
    )
