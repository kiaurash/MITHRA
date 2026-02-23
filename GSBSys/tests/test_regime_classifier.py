"""Tests for src/robustness/regime_classifier.py."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.backtesting.engine import BacktestResult
from src.robustness.regime_classifier import (
    RegimeLabel,
    RegimePerformance,
    RegimeTestResult,
    _make_regime_performance,
    _regime_pf,
    classify_regimes,
    run_regime_testing,
)

WARMUP = 252


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n_bars: int = WARMUP + 300, seed: int = 0) -> pd.DataFrame:
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


def _make_backtest_result(n: int = 200) -> BacktestResult:
    equity = np.linspace(10_000, 10_500, n + 1).astype(np.float32)
    returns = np.diff(equity) / equity[:-1]
    return BacktestResult(
        sharpe_ratio=1.0, profit_factor=1.5, n_trades=20,
        total_pnl=500.0, avg_trade_pnl=25.0,
        equity_curve=equity, returns=returns,
    )


def _mock_engine(n_returns: int = 299) -> MagicMock:
    eng = MagicMock()
    eng.run.return_value = _make_backtest_result(n=n_returns)
    return eng


def _make_individual() -> list:
    return [0, 20, 1.0, 1, 14, 1.0, 2, 9, 1.0, 0.5, 0.05, 0.10, 1.0]


# ---------------------------------------------------------------------------
# classify_regimes
# ---------------------------------------------------------------------------

class TestClassifyRegimes:
    def test_output_length_matches_input(self):
        prices = np.linspace(100, 120, 200)
        labels = classify_regimes(prices, window=63)
        assert len(labels) == 200

    def test_first_window_bars_are_sideways(self):
        prices = np.linspace(100, 120, 200)
        labels = classify_regimes(prices, window=63)
        assert all(l == RegimeLabel.SIDEWAYS for l in labels[:63])

    def test_strong_uptrend_classified_as_bull(self):
        # 200 bars: linear 100 → 200 (+100%); 63-bar return ≈ +20% > bull_threshold=0.10
        prices = np.linspace(100, 200, 200)
        labels = classify_regimes(prices, window=63, bull_threshold=0.10)
        post_warmup = labels[63:]
        bull_fraction = sum(1 for l in post_warmup if l == RegimeLabel.BULL) / len(post_warmup)
        assert bull_fraction > 0.5

    def test_strong_downtrend_classified_as_bear(self):
        # 200 bars: linear 100 → 50 (-50%); 63-bar return ≈ -20% < bear_threshold=-0.10
        prices = np.linspace(100, 50, 200)
        labels = classify_regimes(prices, window=63, bear_threshold=-0.10)
        post_warmup = labels[63:]
        bear_fraction = sum(1 for l in post_warmup if l == RegimeLabel.BEAR) / len(post_warmup)
        assert bear_fraction > 0.8

    def test_flat_prices_all_sideways(self):
        prices = np.full(200, 100.0)
        labels = classify_regimes(prices, window=63)
        assert all(l == RegimeLabel.SIDEWAYS for l in labels)

    def test_regime_labels_are_regime_label_instances(self):
        prices = np.linspace(100, 120, 100)
        labels = classify_regimes(prices)
        valid = {RegimeLabel.BULL, RegimeLabel.BEAR, RegimeLabel.SIDEWAYS}
        for label in labels:
            assert label in valid

    def test_list_input_accepted(self):
        prices = list(np.linspace(100, 120, 100))
        labels = classify_regimes(prices)
        assert len(labels) == 100

    def test_returns_list(self):
        prices = np.linspace(100, 120, 100)
        labels = classify_regimes(prices)
        assert isinstance(labels, list)


# ---------------------------------------------------------------------------
# _regime_pf
# ---------------------------------------------------------------------------

class TestRegimePf:
    def test_all_positive_returns_infinite_pf(self):
        returns = np.array([0.01, 0.02, 0.03])
        pf = _regime_pf(returns)
        assert pf == float("inf")

    def test_all_negative_returns_zero_pf(self):
        returns = np.array([-0.01, -0.02])
        pf = _regime_pf(returns)
        assert pf == pytest.approx(0.0)

    def test_equal_profit_loss_pf_one(self):
        returns = np.array([0.10, -0.10])
        pf = _regime_pf(returns)
        assert pf == pytest.approx(1.0)

    def test_2x_profit_vs_1x_loss_pf_two(self):
        returns = np.array([0.20, -0.10])
        pf = _regime_pf(returns)
        assert pf == pytest.approx(2.0)

    def test_empty_returns_pf_one(self):
        pf = _regime_pf(np.array([]))
        assert pf == 1.0


# ---------------------------------------------------------------------------
# RegimePerformance / RegimeTestResult dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_regime_performance_frozen(self):
        rp = RegimePerformance(
            label=RegimeLabel.BULL, n_bars=100,
            profit_factor=1.5, total_return_pct=10.0, profitable=True,
        )
        with pytest.raises((TypeError, AttributeError)):
            rp.profitable = False  # type: ignore[misc]

    def test_regime_test_result_frozen(self):
        rp = RegimePerformance(
            label=RegimeLabel.SIDEWAYS, n_bars=50,
            profit_factor=1.0, total_return_pct=0.0, profitable=True,
        )
        rt = RegimeTestResult(
            bull=rp, bear=rp, sideways=rp,
            dominant_regime=RegimeLabel.SIDEWAYS,
            best_regime=RegimeLabel.SIDEWAYS,
            worst_regime=RegimeLabel.SIDEWAYS,
        )
        with pytest.raises((TypeError, AttributeError)):
            rt.dominant_regime = RegimeLabel.BULL  # type: ignore[misc]


# ---------------------------------------------------------------------------
# run_regime_testing — structure
# ---------------------------------------------------------------------------

class TestRunRegimeTesting:
    def _df(self):
        return _make_ohlcv(WARMUP + 300)

    def test_returns_regime_test_result(self):
        result = run_regime_testing(
            _make_individual(), self._df(), _mock_engine(299)
        )
        assert isinstance(result, RegimeTestResult)

    def test_bull_bear_sideways_present(self):
        result = run_regime_testing(
            _make_individual(), self._df(), _mock_engine(299)
        )
        assert isinstance(result.bull, RegimePerformance)
        assert isinstance(result.bear, RegimePerformance)
        assert isinstance(result.sideways, RegimePerformance)

    def test_dominant_regime_is_valid_label(self):
        result = run_regime_testing(
            _make_individual(), self._df(), _mock_engine(299)
        )
        assert result.dominant_regime in (RegimeLabel.BULL, RegimeLabel.BEAR, RegimeLabel.SIDEWAYS)

    def test_best_regime_is_valid_label(self):
        result = run_regime_testing(
            _make_individual(), self._df(), _mock_engine(299)
        )
        assert result.best_regime in (RegimeLabel.BULL, RegimeLabel.BEAR, RegimeLabel.SIDEWAYS)

    def test_worst_regime_is_valid_label(self):
        result = run_regime_testing(
            _make_individual(), self._df(), _mock_engine(299)
        )
        assert result.worst_regime in (RegimeLabel.BULL, RegimeLabel.BEAR, RegimeLabel.SIDEWAYS)

    def test_n_bars_sum_equals_post_warmup_minus_one(self):
        """Total bars across regimes should match returns length."""
        df = self._df()
        n_returns = len(df) - WARMUP - 1  # returns = prices[1:] - prices[:-1]
        result = run_regime_testing(
            _make_individual(), df, _mock_engine(n_returns)
        )
        total_bars = result.bull.n_bars + result.bear.n_bars + result.sideways.n_bars
        assert total_bars == n_returns

    def test_engine_called_once(self):
        engine = _mock_engine(299)
        run_regime_testing(_make_individual(), self._df(), engine)
        assert engine.run.call_count == 1

    def test_profitable_flag_consistent_with_pf(self):
        result = run_regime_testing(
            _make_individual(), self._df(), _mock_engine(299)
        )
        for perf in [result.bull, result.bear, result.sideways]:
            assert perf.profitable == (perf.profit_factor >= 1.0)


# ---------------------------------------------------------------------------
# RegimeLabel enum
# ---------------------------------------------------------------------------

class TestRegimeLabelEnum:
    def test_values(self):
        assert RegimeLabel.BULL.value == "bull"
        assert RegimeLabel.BEAR.value == "bear"
        assert RegimeLabel.SIDEWAYS.value == "sideways"

    def test_is_str(self):
        assert isinstance(RegimeLabel.BULL, str)
