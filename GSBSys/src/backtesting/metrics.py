"""Post-backtest performance metrics.

Operates on BacktestResult objects or raw arrays.  Not used in the hot path
(fitness function uses the metrics already embedded in BacktestResult);
intended for post-run reporting and experiment notebooks.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from src.backtesting.engine import BacktestResult


def calculate_metrics(result: BacktestResult) -> Dict[str, float]:
    """Compute a comprehensive performance metrics dict from a BacktestResult.

    Args:
        result: BacktestResult from any BacktestEngine implementation.

    Returns:
        Dict with keys:
          sharpe_ratio, profit_factor, n_trades, total_pnl, avg_trade_pnl,
          max_drawdown_pct, win_rate, avg_win, avg_loss, expectancy
    """
    metrics: Dict[str, float] = {
        "sharpe_ratio":   result.sharpe_ratio,
        "profit_factor":  result.profit_factor,
        "n_trades":       float(result.n_trades),
        "total_pnl":      result.total_pnl,
        "avg_trade_pnl":  result.avg_trade_pnl,
    }

    metrics["max_drawdown_pct"] = max_drawdown(result.equity_curve)

    if result.n_trades > 0:
        returns = result.returns
        wins  = returns[returns > 0]
        losses = returns[returns < 0]
        metrics["win_rate"]  = float(len(wins)) / result.n_trades
        metrics["avg_win"]   = float(np.mean(wins))   if len(wins)   > 0 else 0.0
        metrics["avg_loss"]  = float(np.mean(losses)) if len(losses) > 0 else 0.0
        metrics["expectancy"] = (
            metrics["win_rate"] * metrics["avg_win"]
            + (1.0 - metrics["win_rate"]) * metrics["avg_loss"]
        )
    else:
        metrics["win_rate"]   = 0.0
        metrics["avg_win"]    = 0.0
        metrics["avg_loss"]   = 0.0
        metrics["expectancy"] = 0.0

    return metrics


def max_drawdown(equity_curve: np.ndarray) -> float:
    """Maximum drawdown as a fraction of peak equity (negative float).

    Returns 0.0 if the equity curve never drops below its running peak.

    Args:
        equity_curve: 1-D array of equity values (any dtype).

    Returns:
        Float in (-1, 0].  E.g. -0.15 means a 15% drawdown.
    """
    curve = np.asarray(equity_curve, dtype=np.float64)
    if len(curve) == 0:
        return 0.0
    peak = np.maximum.accumulate(curve)
    drawdowns = np.where(peak > 0, (curve - peak) / peak, 0.0)
    return float(np.min(drawdowns))
