"""Walk-Forward GA — Phase 3, Module 1.

Splits the full OHLCV data into rolling train/test windows and re-runs a
reduced-fidelity GA on each training window.  The resulting OOS performance
profile reveals whether the strategy adapts across time or only works on a
single regime.

Window layout (default):
  train_bars = 504  (~2 years)
  test_bars  = 126  (~6 months)
  step_bars  = 126  (~6 months, = test window)

  |--- warmup ---|--- train ---|--- test ---|
                  window 0

Each subsequent window advances by step_bars.

Pass criteria (from PRD Section 4.1):
  MVP tier:        >= 60% of windows profitable (PF >= 1.0)
  Production tier: >= 70% of windows profitable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import numpy as np
import pandas as pd

from src.backtesting.engine import BacktestEngine, BacktestResult
from src.ga.chromosome import IDX_STOP_LOSS_PCT, IDX_TAKE_PROFIT_PCT, IDX_POSITION_SIZE_MULT
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum

#: Minimum PF for a window to count as "profitable".
PROFITABLE_PF: float = 1.0

#: MVP pass threshold (fraction of windows profitable).
MVP_MIN_FRACTION: float = 0.60

#: Production pass threshold.
PRODUCTION_MIN_FRACTION: float = 0.70


@dataclass(frozen=True)
class WalkForwardWindow:
    """Result for a single walk-forward train/test window.

    Attributes:
        window_idx:        Zero-based window index.
        train_start_bar:   Inclusive start bar of train slice (post-warmup idx).
        train_end_bar:     Exclusive end bar of train slice.
        test_start_bar:    Inclusive start bar of test slice.
        test_end_bar:      Exclusive end bar of test slice.
        best_individual:   Best chromosome found on this training window.
        test_profit_factor: PF achieved on the hold-out test slice.
        test_total_pnl:    Net dollar P&L on the test slice.
        n_test_trades:     Completed trades in the test slice.
        profitable:        True if test_profit_factor >= 1.0.
    """

    window_idx: int
    train_start_bar: int
    train_end_bar: int
    test_start_bar: int
    test_end_bar: int
    best_individual: list
    test_profit_factor: float
    test_total_pnl: float
    n_test_trades: int
    profitable: bool


@dataclass(frozen=True)
class WalkForwardResult:
    """Aggregate result of the walk-forward GA.

    Attributes:
        windows:              One WalkForwardWindow per rolling window.
        n_profitable_windows: Count with PF >= 1.0.
        n_total_windows:      Total windows processed (skipped included).
        avg_test_pf:          Mean PF across all non-skipped windows.
        passed_mvp:           True if profitable fraction >= 60%.
        passed_production:    True if profitable fraction >= 70%.
    """

    windows: List[WalkForwardWindow]
    n_profitable_windows: int
    n_total_windows: int
    avg_test_pf: float
    passed_mvp: bool
    passed_production: bool


# ---------------------------------------------------------------------------
# Window slicer
# ---------------------------------------------------------------------------

def _build_windows(
    n_bars: int,
    warmup_bars: int,
    train_bars: int,
    test_bars: int,
    step_bars: int,
) -> List[tuple]:
    """Return list of (train_start, train_end, test_start, test_end) bar indices.

    All indices are relative to the post-warmup array (i.e. warmup already
    removed).  Returns empty list if data is too short for even one window.
    """
    available = n_bars - warmup_bars
    windows = []
    train_start = 0
    while True:
        train_end  = train_start + train_bars
        test_start = train_end
        test_end   = test_start + test_bars
        if test_end > available:
            break
        windows.append((train_start, train_end, test_start, test_end))
        train_start += step_bars
    return windows


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_walk_forward_ga(
    df: pd.DataFrame,
    ga_runner: Callable[[pd.DataFrame], list],
    engine: BacktestEngine,
    train_bars: int = 504,
    test_bars: int = 126,
    step_bars: int = 126,
    normalization_window: int = 252,
    warmup_bars: int = 252,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
    position_size_mult: Optional[float] = None,
) -> WalkForwardResult:
    """Run walk-forward GA across all rolling windows.

    For each window:
    1. Slice the training portion of df (warmup + train bars)
    2. Call ga_runner(train_df) → best_individual for that window
    3. Build indicator cache from the full window's data
    4. Run backtest on the test slice with the returned individual
    5. Record OOS PF and profitability

    Args:
        df:                   Full OHLCV DataFrame (must include warmup rows).
        ga_runner:            Callable(train_df) → 13-gene chromosome list.
                              Receives the training slice (warmup included)
                              and returns the best individual found.
        engine:               BacktestEngine implementation.
        train_bars:           Training window length (post-warmup bars).
        test_bars:            Test window length.
        step_bars:            Stride between windows (= test_bars for pure WF).
        normalization_window: Rolling indicator normalisation window.
        warmup_bars:          Bars to discard at start of each slice.
        stop_loss_pct:        Override SL% (default: individual gene 10).
        take_profit_pct:      Override TP% (default: individual gene 11).
        position_size_mult:   Override size mult (default: individual gene 12).

    Returns:
        WalkForwardResult with per-window details and aggregate pass/fail.
    """
    window_specs = _build_windows(len(df), warmup_bars, train_bars, test_bars, step_bars)

    wf_windows: List[WalkForwardWindow] = []

    for idx, (tr_s, tr_e, te_s, te_e) in enumerate(window_specs):
        # Training slice: warmup + train_bars rows of raw df
        train_df = df.iloc[: warmup_bars + tr_e].reset_index(drop=True)

        # Get best individual for this window
        individual = ga_runner(train_df)

        sl_pct   = stop_loss_pct      if stop_loss_pct      is not None else float(individual[IDX_STOP_LOSS_PCT])
        tp_pct   = take_profit_pct    if take_profit_pct    is not None else float(individual[IDX_TAKE_PROFIT_PCT])
        pos_mult = position_size_mult if position_size_mult is not None else float(individual[IDX_POSITION_SIZE_MULT])

        # Build indicator cache from entire window (warmup + train + test)
        full_slice_df = df.iloc[: warmup_bars + te_e].reset_index(drop=True)
        cache_full = build_indicator_cache(full_slice_df, normalization_window=normalization_window)

        # Post-warmup test prices
        test_prices = full_slice_df["close"].values[warmup_bars + te_s : warmup_bars + te_e].astype(np.float32)

        if len(test_prices) < 10:
            wf_windows.append(WalkForwardWindow(
                window_idx=idx,
                train_start_bar=tr_s, train_end_bar=tr_e,
                test_start_bar=te_s, test_end_bar=te_e,
                best_individual=individual,
                test_profit_factor=0.0, test_total_pnl=0.0,
                n_test_trades=0, profitable=False,
            ))
            continue

        # Signals for the test slice only
        test_cache = {k: v[warmup_bars + te_s : warmup_bars + te_e] for k, v in cache_full.items()}
        signals = generate_signals_weighted_sum(individual, test_cache)

        result: BacktestResult = engine.run(signals, test_prices, sl_pct, tp_pct, pos_mult)

        wf_windows.append(WalkForwardWindow(
            window_idx=idx,
            train_start_bar=tr_s, train_end_bar=tr_e,
            test_start_bar=te_s, test_end_bar=te_e,
            best_individual=individual,
            test_profit_factor=result.profit_factor,
            test_total_pnl=result.total_pnl,
            n_test_trades=result.n_trades,
            profitable=result.profit_factor >= PROFITABLE_PF,
        ))

    n_profitable = sum(w.profitable for w in wf_windows)
    n_total = len(wf_windows)
    avg_pf = float(np.mean([w.test_profit_factor for w in wf_windows])) if wf_windows else 0.0
    fraction = (n_profitable / n_total) if n_total > 0 else 0.0

    return WalkForwardResult(
        windows=wf_windows,
        n_profitable_windows=n_profitable,
        n_total_windows=n_total,
        avg_test_pf=avg_pf,
        passed_mvp=fraction >= MVP_MIN_FRACTION,
        passed_production=fraction >= PRODUCTION_MIN_FRACTION,
    )
