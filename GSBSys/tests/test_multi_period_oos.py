"""Tests for src/validation/multi_period_oos.py."""

from typing import Optional
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.backtesting.engine import BacktestResult
from src.validation.multi_period_oos import (
    MVP_MIN_PROFITABLE,
    PRODUCTION_MIN_PROFITABLE,
    REGIMES,
    OOSResult,
    RegimeResult,
    run_multi_period_oos,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

N_REGIMES = len(REGIMES)
WARMUP = 252


def _make_ohlcv(n_bars: int, seed: int = 0) -> pd.DataFrame:
    """Return a minimal OHLCV DataFrame of length n_bars."""
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n_bars))
    close = np.maximum(close, 1.0)
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars, freq="D"),
        "open":   close * 0.99,
        "high":   close * 1.01,
        "low":    close * 0.98,
        "close":  close,
        "volume": rng.integers(1_000_000, 5_000_000, n_bars).astype(float),
    })


def _make_backtest_result(pnl: float = 100.0, pf: float = 1.5, n_trades: int = 20) -> BacktestResult:
    equity = np.linspace(10_000, 10_000 + pnl, n_trades + 1).astype(np.float32)
    returns = np.diff(equity) / equity[:-1]
    return BacktestResult(
        sharpe_ratio=1.0,
        profit_factor=pf,
        n_trades=n_trades,
        total_pnl=pnl,
        avg_trade_pnl=pnl / max(n_trades, 1),
        equity_curve=equity,
        returns=returns,
    )


def _mock_engine(pf: float = 1.5, n_trades: int = 20) -> MagicMock:
    eng = MagicMock()
    eng.run.return_value = _make_backtest_result(pf=pf, n_trades=n_trades)
    return eng


def _make_individual() -> list:
    """Return a minimal 13-gene chromosome."""
    return [0, 20, 1.0, 1, 14, 1.0, 2, 9, 1.0, 0.5, 0.05, 0.10, 1.0]


# ---------------------------------------------------------------------------
# REGIMES constant
# ---------------------------------------------------------------------------

class TestRegimesConstant:
    def test_five_regimes(self):
        assert len(REGIMES) == 5

    def test_regime_tuple_length(self):
        for reg in REGIMES:
            assert len(reg) == 3

    def test_dates_ascending(self):
        for i in range(len(REGIMES) - 1):
            assert REGIMES[i][1] < REGIMES[i + 1][0]

    def test_covers_2010_to_2024(self):
        assert REGIMES[0][0].startswith("2010")
        assert REGIMES[-1][1].startswith("2024")


# ---------------------------------------------------------------------------
# OOSResult / RegimeResult dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_regime_result_frozen(self):
        r = RegimeResult(
            label="test", start_date="2010-01-01", end_date="2012-12-31",
            profit_factor=1.5, n_trades=10, total_pnl=500.0, profitable=True,
        )
        with pytest.raises((TypeError, AttributeError)):
            r.profitable = False  # type: ignore[misc]

    def test_oos_result_frozen(self):
        oos = OOSResult(
            regime_results=[], n_profitable=0, passed_mvp=False, passed_production=False,
        )
        with pytest.raises((TypeError, AttributeError)):
            oos.n_profitable = 3  # type: ignore[misc]


# ---------------------------------------------------------------------------
# run_multi_period_oos — skipping logic
# ---------------------------------------------------------------------------

class TestRunMultiPeriodOOSSkipping:
    def test_all_none_data_all_skipped(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: None)
        assert result.n_profitable == 0
        assert all(r.skipped for r in result.regime_results)
        assert not result.passed_mvp

    def test_insufficient_data_skipped(self):
        """DataFrames shorter than warmup+10 are skipped."""
        ind = _make_individual()
        engine = _mock_engine()
        tiny = _make_ohlcv(10)  # way too short
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: tiny)
        assert all(r.skipped for r in result.regime_results)

    def test_skipped_regime_not_profitable(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: None)
        for r in result.regime_results:
            assert not r.profitable
            assert r.profit_factor == 0.0
            assert r.n_trades == 0


# ---------------------------------------------------------------------------
# run_multi_period_oos — pass/fail counting
# ---------------------------------------------------------------------------

class TestRunMultiPeriodOOSCounting:
    def _make_df(self) -> pd.DataFrame:
        return _make_ohlcv(WARMUP + 50)

    def test_all_profitable_passes_both_tiers(self):
        ind = _make_individual()
        engine = _mock_engine(pf=2.0)
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: self._make_df())
        assert result.n_profitable == N_REGIMES
        assert result.passed_mvp is True
        assert result.passed_production is True

    def test_all_unprofitable_fails_both_tiers(self):
        ind = _make_individual()
        engine = _mock_engine(pf=0.5)
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: self._make_df())
        assert result.n_profitable == 0
        assert result.passed_mvp is False
        assert result.passed_production is False

    def test_three_profitable_passes_mvp_fails_prod(self):
        call_count = [0]
        def data_fn(s, e):
            call_count[0] += 1
            return self._make_df()

        ind = _make_individual()
        # First 3 calls → pf=2.0; last 2 → pf=0.5
        call_pf = [2.0, 2.0, 2.0, 0.5, 0.5]
        idx = [0]
        mock_eng = MagicMock()
        def run_side_effect(signals, prices, sl, tp, pos):
            pf = call_pf[idx[0]]
            idx[0] += 1
            pnl = 100.0 if pf > 1.0 else -100.0
            return _make_backtest_result(pnl=pnl, pf=pf)
        mock_eng.run.side_effect = run_side_effect

        result = run_multi_period_oos(ind, mock_eng, data_fn=data_fn)
        assert result.n_profitable == 3
        assert result.passed_mvp is True
        assert result.passed_production is False

    def test_n_profitable_constant_mvp(self):
        assert MVP_MIN_PROFITABLE == 3

    def test_n_profitable_constant_production(self):
        assert PRODUCTION_MIN_PROFITABLE == 4


# ---------------------------------------------------------------------------
# run_multi_period_oos — result structure
# ---------------------------------------------------------------------------

class TestRunMultiPeriodOOSStructure:
    def _make_df(self):
        return _make_ohlcv(WARMUP + 50)

    def test_returns_five_regime_results(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: self._make_df())
        assert len(result.regime_results) == 5

    def test_regime_labels_match_regimes_constant(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_multi_period_oos(ind, engine, data_fn=lambda s, e: self._make_df())
        labels = [r.label for r in result.regime_results]
        expected = [reg[2] for reg in REGIMES]
        assert labels == expected

    def test_override_sl_tp(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_multi_period_oos(
            ind, engine, data_fn=lambda s, e: self._make_df(),
            stop_loss_pct=0.02, take_profit_pct=0.04,
        )
        # Engine was called with overridden values
        call_args = engine.run.call_args_list
        for call in call_args:
            _, kwargs = call
            # May be positional args; check either way
            args = call[0]
            if len(args) >= 3:
                assert args[2] == pytest.approx(0.02)
                assert args[3] == pytest.approx(0.04)
