"""Tests for src/backtesting/ and src/utils/stats.py."""

from __future__ import annotations

import numpy as np
import pytest

from src.backtesting.engine import BacktestResult
from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
from src.backtesting.metrics import calculate_metrics, max_drawdown
from src.utils.stats import pearsonr_fast


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENGINE = NumbaBacktestEngine(
    starting_capital=100_000.0,
    risk_per_trade=0.02,
    slippage_bps=0.0005,
)


def _rising_prices(n: int = 200, start: float = 100.0, step: float = 0.5) -> np.ndarray:
    """Steadily rising prices."""
    return (np.arange(n) * step + start).astype(np.float32)


def _flat_prices(n: int = 200, price: float = 100.0) -> np.ndarray:
    return np.full(n, price, dtype=np.float32)


def _signal_at(n: int, entry_bar: int, value: float = 1.0) -> np.ndarray:
    """Single entry signal at one bar, zeros elsewhere."""
    sig = np.zeros(n, dtype=np.float32)
    sig[entry_bar] = value
    return sig


def _all_signals(n: int, value: float = 1.0) -> np.ndarray:
    """Signal on every bar."""
    return np.full(n, value, dtype=np.float32)


# ---------------------------------------------------------------------------
# BacktestResult protocol / dataclass
# ---------------------------------------------------------------------------

class TestBacktestResult:
    def test_is_frozen(self):
        r = BacktestResult(
            sharpe_ratio=1.0, profit_factor=1.5, n_trades=10,
            total_pnl=500.0, avg_trade_pnl=50.0,
            equity_curve=np.ones(10, dtype=np.float32),
            returns=np.ones(10, dtype=np.float32) * 0.01,
        )
        with pytest.raises((AttributeError, TypeError)):
            r.n_trades = 99  # type: ignore[misc]

    def test_fields_accessible(self):
        r = BacktestResult(
            sharpe_ratio=0.5, profit_factor=1.2, n_trades=5,
            total_pnl=100.0, avg_trade_pnl=20.0,
            equity_curve=np.zeros(5, dtype=np.float32),
            returns=np.zeros(5, dtype=np.float32),
        )
        assert r.sharpe_ratio == 0.5
        assert r.profit_factor == 1.2
        assert r.n_trades == 5


# ---------------------------------------------------------------------------
# NumbaBacktestEngine — basic behaviour
# ---------------------------------------------------------------------------

class TestNumbaEngine:
    def test_no_signals_returns_zero_trades(self):
        sig = np.zeros(100, dtype=np.float32)
        pri = _flat_prices(100)
        result = _ENGINE.run(sig, pri, 0.06, 0.10, 1.0)
        assert result.n_trades == 0

    def test_result_is_backtest_result(self):
        sig = _all_signals(100)
        pri = _rising_prices(100)
        result = _ENGINE.run(sig, pri, 0.06, 0.10, 1.0)
        assert isinstance(result, BacktestResult)

    def test_equity_curve_length_equals_input(self):
        n = 150
        sig = _signal_at(n, 10)
        pri = _rising_prices(n)
        result = _ENGINE.run(sig, pri, 0.06, 0.10, 1.0)
        assert len(result.equity_curve) == n

    def test_equity_curve_starts_at_capital(self):
        sig = np.zeros(100, dtype=np.float32)
        pri = _flat_prices(100)
        result = _ENGINE.run(sig, pri, 0.06, 0.10, 1.0)
        assert result.equity_curve[0] == pytest.approx(100_000.0, rel=1e-4)

    def test_take_profit_exit(self):
        """Price rises 15% → TP at 10% should trigger with 1 trade."""
        n = 50
        prices = np.zeros(n, dtype=np.float32)
        prices[:] = 100.0
        prices[20:] = 115.0  # 15% jump → TP at 10% should fire
        sig = _signal_at(n, 5)
        result = _ENGINE.run(sig, prices, 0.06, 0.10, 1.0)
        assert result.n_trades >= 1

    def test_stop_loss_exit(self):
        """Price drops 10% → SL at 6% should trigger."""
        n = 50
        prices = np.zeros(n, dtype=np.float32)
        prices[:] = 100.0
        prices[15:] = 89.0  # 11% drop → SL at 6% fires
        sig = _signal_at(n, 5)
        result = _ENGINE.run(sig, prices, 0.06, 0.10, 1.0)
        assert result.n_trades >= 1

    def test_rising_market_positive_pnl(self):
        """All-signals on a steadily rising market → positive total_pnl."""
        sig = _all_signals(300)
        pri = _rising_prices(300)
        result = _ENGINE.run(sig, pri, 0.01, 0.20, 1.0)
        assert result.total_pnl > 0

    def test_flat_market_near_zero_pnl(self):
        """Flat prices → slippage only, near-zero or slightly negative P&L."""
        sig = _all_signals(100)
        pri = _flat_prices(100)
        result = _ENGINE.run(sig, pri, 0.01, 0.20, 1.0)
        # P&L should be small (only slippage cost)
        assert abs(result.total_pnl) < 10_000.0

    def test_profit_factor_gte_1_on_rising(self):
        sig = _all_signals(300)
        pri = _rising_prices(300)
        result = _ENGINE.run(sig, pri, 0.01, 0.20, 1.0)
        if result.n_trades > 0:
            assert result.profit_factor >= 1.0

    def test_nan_signals_treated_as_zero(self):
        """NaN signals must not cause a trade entry."""
        sig = np.full(100, np.nan, dtype=np.float32)
        pri = _flat_prices(100)
        result = _ENGINE.run(sig, pri, 0.06, 0.10, 1.0)
        assert result.n_trades == 0

    def test_returns_array_length_equals_n_trades(self):
        sig = _all_signals(200)
        pri = _rising_prices(200)
        result = _ENGINE.run(sig, pri, 0.02, 0.05, 1.0)
        assert len(result.returns) == result.n_trades

    def test_avg_trade_pnl_consistent(self):
        sig = _all_signals(200)
        pri = _rising_prices(200)
        result = _ENGINE.run(sig, pri, 0.01, 0.15, 1.0)
        if result.n_trades > 0:
            expected = result.total_pnl / result.n_trades
            assert result.avg_trade_pnl == pytest.approx(expected, rel=1e-4)

    def test_slippage_reduces_pnl(self):
        """High slippage engine should have lower P&L than no-slippage."""
        sig = _all_signals(200)
        pri = _rising_prices(200)
        eng_no_slip = NumbaBacktestEngine(slippage_bps=0.0)
        eng_slip = NumbaBacktestEngine(slippage_bps=0.01)  # 100 bps
        r_no = eng_no_slip.run(sig, pri, 0.01, 0.20, 1.0)
        r_sl = eng_slip.run(sig, pri, 0.01, 0.20, 1.0)
        if r_no.n_trades > 0 and r_sl.n_trades > 0:
            assert r_no.total_pnl >= r_sl.total_pnl

    def test_position_size_mult_scales_pnl(self):
        """2× position_size_mult → roughly 2× P&L (all else equal)."""
        sig = _all_signals(200)
        pri = _rising_prices(200)
        r1 = _ENGINE.run(sig, pri, 0.06, 0.20, 1.0)
        r2 = _ENGINE.run(sig, pri, 0.06, 0.20, 2.0)
        if r1.n_trades > 0 and r1.total_pnl > 0:
            assert r2.total_pnl > r1.total_pnl


# ---------------------------------------------------------------------------
# warmup_jit
# ---------------------------------------------------------------------------

def test_warmup_jit_runs_without_error():
    warmup_jit()  # must not raise


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class TestMetrics:
    def _make_result(self, n_trades: int = 10, pnl: float = 100.0) -> BacktestResult:
        trades = np.full(n_trades, pnl / n_trades, dtype=np.float32)
        equity = np.cumsum(trades) + 100_000.0
        equity = np.concatenate([[100_000.0], equity]).astype(np.float32)
        return BacktestResult(
            sharpe_ratio=1.0, profit_factor=1.5, n_trades=n_trades,
            total_pnl=pnl, avg_trade_pnl=pnl / n_trades,
            equity_curve=equity, returns=trades / 100_000.0,
        )

    def test_calculate_metrics_returns_dict(self):
        r = self._make_result()
        m = calculate_metrics(r)
        assert isinstance(m, dict)

    def test_required_keys_present(self):
        r = self._make_result()
        m = calculate_metrics(r)
        required = {"sharpe_ratio", "profit_factor", "n_trades", "total_pnl",
                    "avg_trade_pnl", "max_drawdown_pct", "win_rate",
                    "avg_win", "avg_loss", "expectancy"}
        assert required.issubset(m.keys())

    def test_win_rate_all_winners(self):
        r = self._make_result(pnl=500.0)  # all positive trades
        m = calculate_metrics(r)
        assert m["win_rate"] == pytest.approx(1.0)

    def test_win_rate_all_losers(self):
        r = self._make_result(pnl=-500.0)  # all negative trades
        m = calculate_metrics(r)
        assert m["win_rate"] == pytest.approx(0.0)

    def test_zero_trades(self):
        r = BacktestResult(
            sharpe_ratio=0.0, profit_factor=1.0, n_trades=0,
            total_pnl=0.0, avg_trade_pnl=0.0,
            equity_curve=np.ones(10, dtype=np.float32) * 100_000.0,
            returns=np.zeros(1, dtype=np.float32),
        )
        m = calculate_metrics(r)
        assert m["win_rate"] == 0.0
        assert m["n_trades"] == 0.0

    def test_max_drawdown_flat(self):
        equity = np.ones(100, dtype=np.float32) * 100_000.0
        assert max_drawdown(equity) == pytest.approx(0.0, abs=1e-6)

    def test_max_drawdown_negative(self):
        equity = np.array([100.0, 110.0, 90.0, 95.0], dtype=np.float32)
        dd = max_drawdown(equity)
        # Peak was 110, drops to 90 → drawdown = (90-110)/110 ≈ -0.1818
        assert dd == pytest.approx(-0.1818, rel=1e-3)

    def test_max_drawdown_monotone_rising(self):
        equity = np.arange(1.0, 101.0, dtype=np.float32)
        assert max_drawdown(equity) == pytest.approx(0.0, abs=1e-6)


# ---------------------------------------------------------------------------
# pearsonr_fast
# ---------------------------------------------------------------------------

class TestPearsonrFast:
    def test_perfect_positive_correlation(self):
        a = np.arange(100.0)
        assert pearsonr_fast(a, a) == pytest.approx(1.0, abs=1e-9)

    def test_perfect_negative_correlation(self):
        a = np.arange(100.0)
        assert pearsonr_fast(a, -a) == pytest.approx(-1.0, abs=1e-9)

    def test_uncorrelated_random(self):
        rng = np.random.default_rng(0)
        a = rng.normal(0, 1, 1000)
        b = rng.normal(0, 1, 1000)
        r = pearsonr_fast(a, b)
        assert abs(r) < 0.1  # should be near 0 for large uncorrelated samples

    def test_against_numpy_corrcoef(self):
        rng = np.random.default_rng(42)
        a = rng.normal(0, 1, 500)
        b = 0.7 * a + 0.3 * rng.normal(0, 1, 500)
        fast = pearsonr_fast(a, b)
        expected = float(np.corrcoef(a, b)[0, 1])
        assert fast == pytest.approx(expected, abs=1e-9)

    def test_constant_array_near_zero(self):
        a = np.ones(100)
        b = np.arange(100.0)
        r = pearsonr_fast(a, b)
        assert abs(r) < 1e-6

    def test_mismatched_length_raises(self):
        with pytest.raises(ValueError, match="equal length"):
            pearsonr_fast(np.ones(10), np.ones(20))

    def test_result_bounded(self):
        rng = np.random.default_rng(7)
        a = rng.normal(0, 1, 300)
        b = rng.normal(0, 1, 300)
        r = pearsonr_fast(a, b)
        assert -1.0 <= r <= 1.0
