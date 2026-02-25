"""Multi-period out-of-sample validation — Phase 2, Layer 2.

Tests the best chromosome from Phase 1 across 5 fixed market regime windows
covering 15 years of data (2010–2024).  Each regime is an independent
backtest.  Systems that survive diverse market conditions are more likely
to be robust strategies rather than overfit artefacts.

Pass criteria (from PRD Section 3.3):
  MVP tier:        >= 3/5 regime windows profitable (PF >= 1.0)
  Production tier: >= 4/5 regime windows profitable

Each window uses its own indicator cache built from that window's data.
The warm-up period (252 bars) is always trimmed before backtesting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.backtesting.engine import BacktestEngine, BacktestResult
from src.ga.chromosome import IDX_STOP_LOSS_PCT, IDX_TAKE_PROFIT_PCT, IDX_POSITION_SIZE_MULT
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum

#: Five market regime windows (start_date, end_date, label).
REGIMES: List[Tuple[str, str, str]] = [
    ("2010-01-01", "2012-12-31", "post-crisis-recovery"),
    ("2013-01-01", "2015-12-31", "stable-growth"),
    ("2016-01-01", "2018-12-31", "pre-covid-bull"),
    ("2019-01-01", "2021-12-31", "covid-crash-recovery"),
    ("2022-01-01", "2024-12-31", "rate-hikes-sideways"),
]

#: Minimum profit factor to consider a regime window "profitable".
PROFITABLE_PF: float = 1.0

#: MVP pass threshold (regimes must be profitable out of 5).
MVP_MIN_PROFITABLE: int = 3

#: Production pass threshold.
PRODUCTION_MIN_PROFITABLE: int = 4

#: Warm-up bars to discard at the start of each regime window.
_WARMUP_BARS: int = 252

#: Normalization window for indicator cache within each regime.
_NORM_WINDOW: int = 252


@dataclass(frozen=True)
class RegimeResult:
    """Backtest result for one regime window.

    Attributes:
        label:         Human-readable regime name.
        start_date:    Start of the regime window.
        end_date:      End of the regime window.
        profit_factor: PF from the backtest (1.0 = break-even).
        n_trades:      Number of completed trades.
        total_pnl:     Net dollar P&L.
        profitable:    True if profit_factor >= PROFITABLE_PF.
        skipped:       True if the window had insufficient data.
    """

    label: str
    start_date: str
    end_date: str
    profit_factor: float
    n_trades: int
    total_pnl: float
    profitable: bool
    skipped: bool = False


@dataclass(frozen=True)
class OOSResult:
    """Result of the full multi-period OOS validation.

    Attributes:
        regime_results:     One RegimeResult per regime window.
        n_profitable:       Count of profitable (PF >= 1.0) windows.
        passed_mvp:         True if n_profitable >= 3.
        passed_production:  True if n_profitable >= 4.
    """

    regime_results: List[RegimeResult]
    n_profitable: int
    passed_mvp: bool
    passed_production: bool


def run_multi_period_oos(
    individual: list,
    engine: BacktestEngine,
    data_fn: Callable[[str, str], Optional[pd.DataFrame]],
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
    position_size_mult: Optional[float] = None,
    normalization_window: int = _NORM_WINDOW,
    warmup_bars: int = _WARMUP_BARS,
) -> OOSResult:
    """Run the chromosome across all 5 regime windows.

    For each regime:
    1. Fetch OHLCV data via data_fn (returns None if unavailable → skip)
    2. Build indicator cache for this window's data
    3. Trim warm-up bars
    4. Generate signals and run backtest
    5. Record PF and profitability

    Args:
        individual:           13-gene chromosome list.
        engine:               Any BacktestEngine implementation.
        data_fn:              Callable(start_date, end_date) → DataFrame or None.
                              Must return sorted OHLCV with columns
                              [date, open, high, low, close, volume].
        stop_loss_pct:        Override SL% (default: use individual gene 10).
        take_profit_pct:      Override TP% (default: use individual gene 11).
        position_size_mult:   Override size mult (default: use individual gene 12).
        normalization_window: Rolling normalization window (default 252).
        warmup_bars:          Bars to discard per window (default 252).

    Returns:
        OOSResult with per-regime details and overall pass/fail.
    """
    sl_pct   = stop_loss_pct      if stop_loss_pct      is not None else float(individual[IDX_STOP_LOSS_PCT])
    tp_pct   = take_profit_pct    if take_profit_pct    is not None else float(individual[IDX_TAKE_PROFIT_PCT])
    pos_mult = position_size_mult if position_size_mult is not None else float(individual[IDX_POSITION_SIZE_MULT])

    regime_results: List[RegimeResult] = []

    for start, end, label in REGIMES:
        df = data_fn(start, end)

        # Skip if data unavailable or insufficient
        if df is None or len(df) <= warmup_bars + 10:
            regime_results.append(RegimeResult(
                label=label, start_date=start, end_date=end,
                profit_factor=0.0, n_trades=0, total_pnl=0.0,
                profitable=False, skipped=True,
            ))
            continue

        # Build per-regime indicator cache
        cache = build_indicator_cache(df, normalization_window=normalization_window)

        # Trim warm-up and slice cache + prices accordingly
        post_warmup_df = df.iloc[warmup_bars:].reset_index(drop=True)
        if len(post_warmup_df) < 10:
            regime_results.append(RegimeResult(
                label=label, start_date=start, end_date=end,
                profit_factor=0.0, n_trades=0, total_pnl=0.0,
                profitable=False, skipped=True,
            ))
            continue

        sliced_cache = {k: v[warmup_bars:] for k, v in cache.items()}
        prices = post_warmup_df["close"].values.astype(np.float32)

        signals = generate_signals_weighted_sum(individual, sliced_cache)

        result: BacktestResult = engine.run(
            signals, prices, sl_pct, tp_pct, pos_mult,
        )

        profitable = result.profit_factor >= PROFITABLE_PF
        regime_results.append(RegimeResult(
            label=label,
            start_date=start,
            end_date=end,
            profit_factor=result.profit_factor,
            n_trades=result.n_trades,
            total_pnl=result.total_pnl,
            profitable=profitable,
            skipped=False,
        ))

    n_profitable = sum(r.profitable for r in regime_results)
    return OOSResult(
        regime_results=regime_results,
        n_profitable=n_profitable,
        passed_mvp=n_profitable >= MVP_MIN_PROFITABLE,
        passed_production=n_profitable >= PRODUCTION_MIN_PROFITABLE,
    )
