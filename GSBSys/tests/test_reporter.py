"""Tests for src/export/reporter.py."""

from __future__ import annotations

import numpy as np
import pytest

from src.backtesting.engine import BacktestResult
from src.export.reporter import (
    PerformanceReport,
    build_report,
    format_text,
    load_csv,
    save_csv,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_result(
    n: int = 100,
    profit: float = 500.0,
    n_trades: int = 20,
    sharpe: float = 1.2,
    seed: int = 0,
) -> BacktestResult:
    rng = np.random.default_rng(seed)
    equity = 10_000 + np.cumsum(rng.normal(0, 50, n + 1)).astype(np.float32)
    equity[0] = 10_000.0
    returns = np.diff(equity) / equity[:-1]
    return BacktestResult(
        sharpe_ratio=sharpe,
        profit_factor=1.5,
        n_trades=n_trades,
        total_pnl=profit,
        avg_trade_pnl=profit / n_trades if n_trades > 0 else 0.0,
        equity_curve=equity,
        returns=returns,
    )


# ---------------------------------------------------------------------------
# PerformanceReport
# ---------------------------------------------------------------------------

class TestPerformanceReport:
    def test_frozen(self):
        r = PerformanceReport(
            profit_factor=1.5, total_pnl=500.0, n_trades=20,
            avg_trade_pnl=25.0, sharpe_ratio=1.2,
            max_drawdown_pct=5.0, win_rate_pct=60.0, expectancy=25.0,
        )
        with pytest.raises((TypeError, AttributeError)):
            r.profit_factor = 2.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# build_report
# ---------------------------------------------------------------------------

class TestBuildReport:
    def test_returns_performance_report(self):
        r = build_report(_make_result())
        assert isinstance(r, PerformanceReport)

    def test_profit_factor_copied(self):
        result = _make_result()
        report = build_report(result)
        assert report.profit_factor == result.profit_factor

    def test_total_pnl_copied(self):
        result = _make_result(profit=1234.5)
        report = build_report(result)
        assert report.total_pnl == pytest.approx(1234.5)

    def test_n_trades_copied(self):
        result = _make_result(n_trades=15)
        report = build_report(result)
        assert report.n_trades == 15

    def test_sharpe_copied(self):
        result = _make_result(sharpe=2.1)
        report = build_report(result)
        assert report.sharpe_ratio == pytest.approx(2.1)

    def test_max_drawdown_non_negative(self):
        report = build_report(_make_result())
        assert report.max_drawdown_pct >= 0.0

    def test_win_rate_in_range(self):
        report = build_report(_make_result())
        assert 0.0 <= report.win_rate_pct <= 100.0

    def test_expectancy_equals_avg_trade_pnl(self):
        report = build_report(_make_result(profit=200.0, n_trades=10))
        assert report.expectancy == pytest.approx(report.avg_trade_pnl)

    def test_zero_trades(self):
        result = _make_result(n_trades=0, profit=0.0)
        result = BacktestResult(
            sharpe_ratio=0.0, profit_factor=1.0, n_trades=0,
            total_pnl=0.0, avg_trade_pnl=0.0,
            equity_curve=np.full(101, 10_000.0, dtype=np.float32),
            returns=np.zeros(100, dtype=np.float32),
        )
        report = build_report(result)
        assert report.n_trades == 0
        assert report.avg_trade_pnl == pytest.approx(0.0)

    def test_monotone_equity_zero_drawdown(self):
        equity = np.linspace(10_000, 11_000, 101).astype(np.float32)
        returns = np.diff(equity) / equity[:-1]
        result = BacktestResult(
            sharpe_ratio=2.0, profit_factor=2.0, n_trades=10,
            total_pnl=1000.0, avg_trade_pnl=100.0,
            equity_curve=equity, returns=returns,
        )
        report = build_report(result)
        assert report.max_drawdown_pct == pytest.approx(0.0, abs=0.01)

    def test_all_positive_returns_win_rate_100(self):
        equity = np.linspace(10_000, 11_000, 101).astype(np.float32)
        returns = np.diff(equity) / equity[:-1]
        result = BacktestResult(
            sharpe_ratio=2.0, profit_factor=2.0, n_trades=10,
            total_pnl=1000.0, avg_trade_pnl=100.0,
            equity_curve=equity, returns=returns,
        )
        report = build_report(result)
        assert report.win_rate_pct == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

class TestFormatText:
    def test_returns_string(self):
        r = build_report(_make_result())
        text = format_text(r)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_contains_profit_factor(self):
        r = build_report(_make_result())
        text = format_text(r)
        assert "Profit Factor" in text

    def test_contains_sharpe_ratio(self):
        r = build_report(_make_result())
        text = format_text(r)
        assert "Sharpe" in text

    def test_contains_trades(self):
        result = _make_result(n_trades=42)
        text = format_text(build_report(result))
        assert "42" in text


# ---------------------------------------------------------------------------
# save_csv / load_csv
# ---------------------------------------------------------------------------

class TestCsvRoundtrip:
    def test_roundtrip(self, tmp_path):
        result = _make_result(profit=750.0, n_trades=25, sharpe=1.8)
        report = build_report(result)
        path = tmp_path / "report.csv"
        save_csv(report, str(path))
        loaded = load_csv(str(path))
        assert loaded.profit_factor == pytest.approx(report.profit_factor)
        assert loaded.total_pnl == pytest.approx(report.total_pnl)
        assert loaded.n_trades == report.n_trades
        assert loaded.sharpe_ratio == pytest.approx(report.sharpe_ratio)
        assert loaded.max_drawdown_pct == pytest.approx(report.max_drawdown_pct)
        assert loaded.win_rate_pct == pytest.approx(report.win_rate_pct)

    def test_save_creates_parent_dirs(self, tmp_path):
        report = build_report(_make_result())
        path = tmp_path / "nested" / "dir" / "report.csv"
        save_csv(report, str(path))
        assert path.exists()

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_csv("nonexistent_report.csv")

    def test_csv_has_header(self, tmp_path):
        report = build_report(_make_result())
        path = tmp_path / "r.csv"
        save_csv(report, str(path))
        content = path.read_text()
        assert "profit_factor" in content
