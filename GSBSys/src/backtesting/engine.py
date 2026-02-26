"""BacktestResult dataclass and BacktestEngine Protocol.

The Protocol pattern enables dependency injection: production code uses
NumbaBacktestEngine; tests use a lightweight MockBacktestEngine that returns
fixed results without running a simulation.

SL/TP design note:
  stop_loss_pct and take_profit_pct are fractions of position value (e.g.
  0.06 = 6%).  This is percentage-based, not dollar-based, so risk sizing
  scales correctly across tickers at different price levels (SPY ≈ $500,
  IWM ≈ $200).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class BacktestResult:
    """Immutable result from a single backtest run.

    Attributes:
        sharpe_ratio:   Annualised Sharpe ratio of per-trade returns.
        profit_factor:  Gross profit / gross loss (≥1.0 is profitable).
        n_trades:       Total number of completed trades.
        total_pnl:      Net dollar P&L summed over all trades.
        avg_trade_pnl:  total_pnl / n_trades (pre-computed for fitness).
        equity_curve:   float32 array of equity value at each bar.
        returns:        float32 array of per-trade returns (total_pnl/capital).
    """

    sharpe_ratio: float
    profit_factor: float
    n_trades: int
    total_pnl: float
    avg_trade_pnl: float
    equity_curve: np.ndarray
    returns: np.ndarray


class BacktestEngine(Protocol):
    """Protocol for any backtest engine implementation.

    Implementations must accept percentage-based SL/TP (not dollar amounts)
    so risk sizing is consistent across tickers at different price levels.
    """

    def run(
        self,
        signals: np.ndarray,
        prices: np.ndarray,
        stop_loss_pct: float,
        take_profit_pct: float,
        position_size_mult: float,
    ) -> BacktestResult:
        """Run a backtest over the given bar range.

        Args:
            signals:            float32 array of length T. Non-NaN, non-zero
                                values trigger entries. Positive = long entry.
            prices:             float32 close price array of length T.
            stop_loss_pct:      Exit loss threshold as fraction of entry price
                                (e.g. 0.06 = exit when price drops 6%).
            take_profit_pct:    Exit profit threshold as fraction of entry
                                price (e.g. 0.10 = exit when up 10%).
            position_size_mult: Multiplier applied to base position size.

        Returns:
            BacktestResult with all fields populated.
        """
        ...
