"""Performance report builder — text table and CSV persistence.

Build a PerformanceReport from a BacktestResult, render as a human-readable
table, and save/load as CSV.

Usage::

    from src.export.reporter import build_report, format_text, save_csv, load_csv
    report = build_report(backtest_result)
    print(format_text(report))
    save_csv(report, "results/report.csv")
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, astuple, fields
from pathlib import Path
from typing import Union

import numpy as np

from src.backtesting.engine import BacktestResult


@dataclass(frozen=True)
class PerformanceReport:
    """Aggregated strategy performance metrics.

    Attributes:
        profit_factor:    Gross profit / gross loss (≥1.0 is profitable).
        total_pnl:        Net dollar P&L over all trades.
        n_trades:         Total completed trades.
        avg_trade_pnl:    total_pnl / n_trades (0 if no trades).
        sharpe_ratio:     Annualised Sharpe ratio.
        max_drawdown_pct: Maximum drawdown as percentage (0–100).
        win_rate_pct:     Fraction of winning trades × 100.
        expectancy:       Average P&L per trade (alias for avg_trade_pnl).
    """

    profit_factor:    float
    total_pnl:        float
    n_trades:         int
    avg_trade_pnl:    float
    sharpe_ratio:     float
    max_drawdown_pct: float
    win_rate_pct:     float
    expectancy:       float


def _max_drawdown(equity: np.ndarray) -> float:
    """Maximum drawdown as percentage from equity curve."""
    if len(equity) < 2:
        return 0.0
    peak = np.maximum.accumulate(equity)
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = np.where(peak > 0, (equity - peak) / peak * 100.0, 0.0)
    return float(np.min(dd))  # negative value; we return the magnitude below


def _win_rate(returns: np.ndarray) -> float:
    """Fraction of positive returns × 100."""
    if len(returns) == 0:
        return 0.0
    wins = float(np.sum(returns > 0))
    return wins / len(returns) * 100.0


def build_report(result: BacktestResult) -> PerformanceReport:
    """Build a PerformanceReport from a BacktestResult.

    Args:
        result: Populated BacktestResult from a backtest run.

    Returns:
        Frozen PerformanceReport with all metrics computed.
    """
    avg_pnl = result.avg_trade_pnl if result.n_trades > 0 else 0.0
    max_dd  = abs(_max_drawdown(result.equity_curve))
    wr      = _win_rate(result.returns)

    return PerformanceReport(
        profit_factor    = result.profit_factor,
        total_pnl        = result.total_pnl,
        n_trades         = result.n_trades,
        avg_trade_pnl    = avg_pnl,
        sharpe_ratio     = result.sharpe_ratio,
        max_drawdown_pct = max_dd,
        win_rate_pct     = wr,
        expectancy       = avg_pnl,
    )


def format_text(report: PerformanceReport) -> str:
    """Render report as a human-readable fixed-width table.

    Args:
        report: PerformanceReport to format.

    Returns:
        Multi-line string with aligned columns.
    """
    rows = [
        ("Profit Factor",      f"{report.profit_factor:.4f}"),
        ("Total P&L",          f"${report.total_pnl:,.2f}"),
        ("Trades",             f"{report.n_trades}"),
        ("Avg Trade P&L",      f"${report.avg_trade_pnl:,.2f}"),
        ("Sharpe Ratio",       f"{report.sharpe_ratio:.4f}"),
        ("Max Drawdown",       f"{report.max_drawdown_pct:.2f}%"),
        ("Win Rate",           f"{report.win_rate_pct:.1f}%"),
        ("Expectancy",         f"${report.expectancy:,.2f}"),
    ]
    header = "=" * 36
    lines = [header, "  Strategy Performance Report", header]
    for label, value in rows:
        lines.append(f"  {label:<22} {value:>10}")
    lines.append(header)
    return "\n".join(lines)


_FIELDNAMES = [f.name for f in fields(PerformanceReport)]


def save_csv(report: PerformanceReport, path: Union[str, Path]) -> None:
    """Save a PerformanceReport to a CSV file.

    Args:
        report: Report to serialise.
        path:   Destination path (parent dirs created if needed).
    """
    path = Path(path)
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerow({f: getattr(report, f) for f in _FIELDNAMES})


def load_csv(path: Union[str, Path]) -> PerformanceReport:
    """Load a PerformanceReport from a CSV file.

    Args:
        path: Path written by :func:`save_csv`.

    Returns:
        Reconstructed PerformanceReport.

    Raises:
        FileNotFoundError: If *path* does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Report CSV not found: {path}")
    with open(path, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        row = next(reader)
    return PerformanceReport(
        profit_factor    = float(row["profit_factor"]),
        total_pnl        = float(row["total_pnl"]),
        n_trades         = int(row["n_trades"]),
        avg_trade_pnl    = float(row["avg_trade_pnl"]),
        sharpe_ratio     = float(row["sharpe_ratio"]),
        max_drawdown_pct = float(row["max_drawdown_pct"]),
        win_rate_pct     = float(row["win_rate_pct"]),
        expectancy       = float(row["expectancy"]),
    )
