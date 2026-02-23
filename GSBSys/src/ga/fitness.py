"""Fitness function for the GA Trading System.

Fitness = NetProfit × AvgTrade (real dollar P&L, not Sharpe² approximation).

Design rationale vs POC:
  POC used sharpe² which penalises high-trade/low-sharpe systems and rewards
  few-trade/high-sharpe systems — the opposite of what GSBsys needs.
  Phase 1 uses total_pnl × avg_trade_pnl which:
    - Rewards systems that make money AND make it consistently per trade
    - Penalises lucky one-trade winners (avg_trade large but total_pnl small)
    - Penalises churning systems (total_pnl large but avg_trade tiny)

Penalties are scaled by base_magnitude = max(|fitness|, 1.0) so they remain
proportionally significant as the GA discovers higher-fitness solutions.

Fast-exit: return (0.0,) immediately if n_trades < 5 on either split —
avoids wasting time computing Pearson on degenerate chromosomes.
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np

from src.backtesting.engine import BacktestEngine
from src.indicators.signal_generator import generate_signals_weighted_sum
from src.utils.stats import pearsonr_fast

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Penalty thresholds (from plan research insights)
# ---------------------------------------------------------------------------
_MIN_TRADES = 5          # fast-exit threshold (both train + test)
_DESIRED_TRADES = 30     # soft penalty below this
_MIN_PF = 1.2            # profit factor threshold for scaled penalty
_PEARSON_THRESHOLD = 0.85  # train/test equity curve correlation minimum


def evaluate_individual(
    individual: list,
    train_prices: np.ndarray,
    test_prices: np.ndarray,
    n_train: int,
    cache: Dict[str, np.ndarray],
    engine: BacktestEngine,
) -> Tuple[float, ...]:
    """Evaluate a single GA chromosome and return its fitness as a 1-tuple.

    The chromosome encodes 3 indicator slots (type, period, weight) plus
    global risk parameters.  Signals are generated from the full price array,
    then split into train/test portions before backtesting.

    Args:
        individual:   List of 13 gene values (see chromosome.py).
        train_prices: float32 close prices for the training split.
        test_prices:  float32 close prices for the test split.
        n_train:      Length of the training split (= len(train_prices)).
                      Used to slice the composite signal array.
        cache:        Pre-computed indicator cache from build_indicator_cache().
                      Keys: f"{indicator_id}_{period}", values: float32 arrays.
        engine:       Any BacktestEngine implementation (NumbaBacktestEngine
                      in production, MockBacktestEngine in tests).

    Returns:
        (fitness,) — 1-tuple of float ≥ 0.0.  Returns (0.0,) on fast-exit.
    """
    stop_loss_pct      = float(individual[10])
    take_profit_pct    = float(individual[11])
    position_size_mult = float(individual[12])

    # Generate composite signals from the full cache (length = train + test)
    # NaN bars are treated as zero (no entry) by the engine
    signals = generate_signals_weighted_sum(individual, cache)

    # Split signals to match price arrays
    train_signals = signals[:n_train]
    test_signals  = signals[n_train:]

    # Guard against length mismatches (can happen with edge-case data)
    if len(train_signals) != len(train_prices) or len(test_signals) != len(test_prices):
        return (0.0,)

    train_result = engine.run(
        train_signals, train_prices,
        stop_loss_pct, take_profit_pct, position_size_mult,
    )
    test_result = engine.run(
        test_signals, test_prices,
        stop_loss_pct, take_profit_pct, position_size_mult,
    )

    # --- Fast-exit: degenerate chromosome ---
    if train_result.n_trades < _MIN_TRADES or test_result.n_trades < _MIN_TRADES:
        return (0.0,)

    # --- Primary fitness: NetProfit × AvgTrade ---
    fitness = test_result.total_pnl * test_result.avg_trade_pnl

    # --- Scaled penalties ---
    base_magnitude = max(abs(fitness), 1.0)

    # Penalty 1: train/test equity curve correlation < 0.85 (overfitting signal)
    # Pearson requires equal-length arrays; use min length to be safe
    min_len = min(len(train_result.equity_curve), len(test_result.equity_curve))
    if min_len >= 2:
        pearson = pearsonr_fast(
            train_result.equity_curve[:min_len].astype(np.float64),
            test_result.equity_curve[:min_len].astype(np.float64),
        )
        if pearson < _PEARSON_THRESHOLD:
            fitness -= ((_PEARSON_THRESHOLD - pearson) * 10.0 * base_magnitude)

    # Penalty 2: train profit factor below threshold
    if train_result.profit_factor < _MIN_PF:
        fitness -= ((_MIN_PF - train_result.profit_factor) * 5.0 * base_magnitude)

    # Penalty 3: test profit factor below threshold
    if test_result.profit_factor < _MIN_PF:
        fitness -= ((_MIN_PF - test_result.profit_factor) * 5.0 * base_magnitude)

    # Penalty 4: too few test trades (soft — linear, not scaled)
    if test_result.n_trades < _DESIRED_TRADES:
        fitness -= ((_DESIRED_TRADES - test_result.n_trades) * 0.1)

    return (max(0.0, fitness),)
