"""Tests for src/robustness/walk_forward.py."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.backtesting.engine import BacktestResult
from src.robustness.walk_forward import (
    MVP_MIN_FRACTION,
    PRODUCTION_MIN_FRACTION,
    WalkForwardResult,
    WalkForwardWindow,
    _build_windows,
    run_walk_forward_ga,
)

WARMUP = 252


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n_bars: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n_bars))
    close = np.maximum(close, 1.0)
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars, freq="D"),
        "open":   close * 0.99,
        "high":   close * 1.01,
        "low":    close * 0.98,
        "close":  close.astype(np.float32),
        "volume": rng.integers(1_000_000, 5_000_000, n_bars).astype(float),
    })


def _make_backtest_result(pf: float = 1.5, n_trades: int = 10) -> BacktestResult:
    pnl = 100.0 if pf >= 1.0 else -50.0
    equity = np.linspace(10_000, 10_000 + pnl, n_trades + 1).astype(np.float32)
    returns = np.diff(equity) / equity[:-1]
    return BacktestResult(
        sharpe_ratio=1.0, profit_factor=pf, n_trades=n_trades,
        total_pnl=pnl, avg_trade_pnl=pnl / max(n_trades, 1),
        equity_curve=equity, returns=returns,
    )


def _mock_engine(pf: float = 1.5) -> MagicMock:
    eng = MagicMock()
    eng.run.return_value = _make_backtest_result(pf=pf)
    return eng


def _make_individual() -> list:
    return [0, 20, 1.0, 1, 14, 1.0, 2, 9, 1.0, 0.5, 0.05, 0.10, 1.0]


def _ga_runner(df: pd.DataFrame) -> list:
    return _make_individual()


# ---------------------------------------------------------------------------
# _build_windows
# ---------------------------------------------------------------------------

class TestBuildWindows:
    def test_no_windows_if_data_too_short(self):
        # Only 10 bars available after warmup, need 504+126=630
        windows = _build_windows(WARMUP + 10, WARMUP, 504, 126, 126)
        assert windows == []

    def test_one_window_exact_fit(self):
        # exactly warmup + train + test
        n = WARMUP + 504 + 126
        windows = _build_windows(n, WARMUP, 504, 126, 126)
        assert len(windows) == 1
        tr_s, tr_e, te_s, te_e = windows[0]
        assert tr_s == 0
        assert tr_e == 504
        assert te_s == 504
        assert te_e == 630

    def test_two_windows_with_step(self):
        n = WARMUP + 504 + 2 * 126
        windows = _build_windows(n, WARMUP, 504, 126, 126)
        assert len(windows) == 2

    def test_window_start_advances_by_step(self):
        n = WARMUP + 504 + 3 * 126
        windows = _build_windows(n, WARMUP, 504, 126, 126)
        assert len(windows) == 3
        for i in range(1, len(windows)):
            assert windows[i][0] == windows[i - 1][0] + 126


# ---------------------------------------------------------------------------
# WalkForwardWindow / WalkForwardResult dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_walk_forward_window_frozen(self):
        w = WalkForwardWindow(
            window_idx=0, train_start_bar=0, train_end_bar=504,
            test_start_bar=504, test_end_bar=630,
            best_individual=_make_individual(),
            test_profit_factor=1.5, test_total_pnl=100.0,
            n_test_trades=10, profitable=True,
        )
        with pytest.raises((TypeError, AttributeError)):
            w.profitable = False  # type: ignore[misc]

    def test_walk_forward_result_frozen(self):
        r = WalkForwardResult(
            windows=[], n_profitable_windows=0, n_total_windows=0,
            avg_test_pf=0.0, passed_mvp=False, passed_production=False,
        )
        with pytest.raises((TypeError, AttributeError)):
            r.n_total_windows = 5  # type: ignore[misc]


# ---------------------------------------------------------------------------
# run_walk_forward_ga — no windows
# ---------------------------------------------------------------------------

class TestRunWalkForwardNoWindows:
    def test_too_short_returns_empty(self):
        df = _make_ohlcv(WARMUP + 10)
        engine = _mock_engine()
        result = run_walk_forward_ga(
            df, _ga_runner, engine,
            train_bars=504, test_bars=126, step_bars=126,
        )
        assert result.n_total_windows == 0
        assert result.n_profitable_windows == 0
        assert not result.passed_mvp
        assert not result.passed_production


# ---------------------------------------------------------------------------
# run_walk_forward_ga — with windows
# ---------------------------------------------------------------------------

class TestRunWalkForwardWithWindows:
    def _make_full_df(self, n_windows: int = 3) -> pd.DataFrame:
        n = WARMUP + 504 + n_windows * 126
        return _make_ohlcv(n)

    def test_correct_number_of_windows(self):
        df = self._make_full_df(3)
        engine = _mock_engine(pf=1.5)
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        assert result.n_total_windows == 3

    def test_all_profitable_passes_both_tiers(self):
        df = self._make_full_df(5)
        engine = _mock_engine(pf=2.0)
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        assert result.n_profitable_windows == result.n_total_windows
        assert result.passed_mvp is True
        assert result.passed_production is True

    def test_all_unprofitable_fails_both_tiers(self):
        df = self._make_full_df(5)
        engine = _mock_engine(pf=0.5)
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        assert result.n_profitable_windows == 0
        assert result.passed_mvp is False
        assert result.passed_production is False

    def test_avg_test_pf_computed(self):
        df = self._make_full_df(3)
        engine = _mock_engine(pf=1.8)
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        assert abs(result.avg_test_pf - 1.8) < 1e-3

    def test_window_indices_sequential(self):
        df = self._make_full_df(3)
        engine = _mock_engine()
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        for i, w in enumerate(result.windows):
            assert w.window_idx == i

    def test_ga_runner_called_once_per_window(self):
        df = self._make_full_df(3)
        engine = _mock_engine()
        call_count = [0]
        def counting_runner(train_df):
            call_count[0] += 1
            return _make_individual()
        run_walk_forward_ga(df, counting_runner, engine,
                            train_bars=504, test_bars=126, step_bars=126)
        assert call_count[0] == 3

    def test_window_test_ranges_non_overlapping(self):
        df = self._make_full_df(3)
        engine = _mock_engine()
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        for i in range(1, len(result.windows)):
            prev = result.windows[i - 1]
            curr = result.windows[i]
            assert curr.test_start_bar >= prev.test_end_bar

    def test_profitable_flag_consistent_with_pf(self):
        df = self._make_full_df(3)
        engine = _mock_engine(pf=1.5)
        result = run_walk_forward_ga(df, _ga_runner, engine,
                                     train_bars=504, test_bars=126, step_bars=126)
        for w in result.windows:
            assert w.profitable == (w.test_profit_factor >= 1.0)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_mvp_fraction(self):
        assert MVP_MIN_FRACTION == pytest.approx(0.60)

    def test_production_fraction(self):
        assert PRODUCTION_MIN_FRACTION == pytest.approx(0.70)
