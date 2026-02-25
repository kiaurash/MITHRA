"""Tests for src/ga/fitness.py."""

from __future__ import annotations

from typing import Tuple
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.backtesting.engine import BacktestResult
from src.ga.fitness import (
    _MIN_TRADES,
    _MIN_PF,
    _PEARSON_THRESHOLD,
    evaluate_individual,
)
from src.ga.chromosome import GENE_NAMES, N_GENES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_prices(n: int = 400, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    prices = 100.0 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n)))
    return prices.astype(np.float32)


def _make_individual(
    ind1_type=0, ind1_period=14, ind1_weight=1.0,
    ind2_type=7, ind2_period=10, ind2_weight=0.5,
    ind3_type=9, ind3_period=10, ind3_weight=0.5,
    entry_threshold=10.0,
    stop_loss_pct=0.06,
    take_profit_pct=0.12,
    position_size_mult=1.0,
) -> list:
    return [
        ind1_type, ind1_period, ind1_weight,
        ind2_type, ind2_period, ind2_weight,
        ind3_type, ind3_period, ind3_weight,
        entry_threshold, stop_loss_pct, take_profit_pct, position_size_mult,
    ]


def _mock_result(
    n_trades: int = 20,
    total_pnl: float = 500.0,
    profit_factor: float = 1.5,
    equity_len: int = 100,
) -> BacktestResult:
    avg_pnl = total_pnl / n_trades if n_trades > 0 else 0.0
    curve = np.linspace(100_000, 100_000 + total_pnl, equity_len).astype(np.float32)
    trades = np.full(n_trades, avg_pnl / 100_000.0, dtype=np.float32)
    return BacktestResult(
        sharpe_ratio=1.0,
        profit_factor=profit_factor,
        n_trades=n_trades,
        total_pnl=total_pnl,
        avg_trade_pnl=avg_pnl,
        equity_curve=curve,
        returns=trades,
    )


class _MockEngine:
    """Configurable mock engine for unit tests."""

    def __init__(self, train_result: BacktestResult, test_result: BacktestResult):
        self._train = train_result
        self._test  = test_result
        self._call_count = 0

    def run(self, signals, prices, stop_loss_pct, take_profit_pct, position_size_mult):
        self._call_count += 1
        # First call = train, second = test
        if self._call_count % 2 == 1:
            return self._train
        return self._test


def _make_tiny_cache(n: int) -> dict:
    """Minimal cache stub with enough keys for the default test individual."""
    # ind1=RSI(0_14), ind2=ROC(7_10), ind3=MOM(9_10)
    arr = np.zeros(n, dtype=np.float32)
    return {"0_14": arr, "7_10": arr, "9_10": arr}


# ---------------------------------------------------------------------------
# Basic interface
# ---------------------------------------------------------------------------

class TestEvaluateIndividual:
    def setup_method(self):
        n = 300
        n_train = 120
        self.n_train = n_train
        self.train_prices = _make_prices(n_train, seed=1)
        self.test_prices  = _make_prices(n - n_train, seed=2)
        self.cache = _make_tiny_cache(n)
        self.individual = _make_individual()

    def _run(self, engine):
        return evaluate_individual(
            self.individual,
            self.train_prices,
            self.test_prices,
            self.n_train,
            self.cache,
            engine,
        )

    def test_returns_tuple(self):
        engine = _MockEngine(_mock_result(), _mock_result())
        result = self._run(engine)
        assert isinstance(result, tuple) and len(result) == 1

    def test_returns_float(self):
        engine = _MockEngine(_mock_result(), _mock_result())
        result = self._run(engine)
        assert isinstance(result[0], float)

    def test_fitness_non_negative(self):
        engine = _MockEngine(_mock_result(), _mock_result())
        result = self._run(engine)
        assert result[0] >= 0.0

    def test_engine_called_twice(self):
        engine = _MockEngine(_mock_result(), _mock_result())
        self._run(engine)
        assert engine._call_count == 2


# ---------------------------------------------------------------------------
# Fast-exit logic
# ---------------------------------------------------------------------------

class TestFastExit:
    def setup_method(self):
        n = 300
        self.n_train = 120
        self.train_prices = _make_prices(120, seed=3)
        self.test_prices  = _make_prices(180, seed=4)
        self.cache = _make_tiny_cache(n)
        self.individual = _make_individual()

    def _run(self, engine):
        return evaluate_individual(
            self.individual, self.train_prices, self.test_prices,
            self.n_train, self.cache, engine,
        )

    def test_zero_train_trades_returns_zero(self):
        engine = _MockEngine(
            _mock_result(n_trades=0),
            _mock_result(n_trades=20),
        )
        assert self._run(engine) == (0.0,)

    def test_zero_test_trades_returns_zero(self):
        engine = _MockEngine(
            _mock_result(n_trades=20),
            _mock_result(n_trades=0),
        )
        assert self._run(engine) == (0.0,)

    def test_few_train_trades_returns_zero(self):
        engine = _MockEngine(
            _mock_result(n_trades=_MIN_TRADES - 1),
            _mock_result(n_trades=20),
        )
        assert self._run(engine) == (0.0,)

    def test_few_test_trades_returns_zero(self):
        engine = _MockEngine(
            _mock_result(n_trades=20),
            _mock_result(n_trades=_MIN_TRADES - 1),
        )
        assert self._run(engine) == (0.0,)

    def test_exactly_min_trades_not_fast_exit(self):
        engine = _MockEngine(
            _mock_result(n_trades=_MIN_TRADES),
            _mock_result(n_trades=_MIN_TRADES),
        )
        result = self._run(engine)
        # Should proceed past fast-exit (fitness may still be 0 due to penalties)
        assert isinstance(result[0], float)


# ---------------------------------------------------------------------------
# Penalty logic
# ---------------------------------------------------------------------------

class TestPenalties:
    def setup_method(self):
        n = 300
        self.n_train = 120
        self.train_prices = _make_prices(120, seed=5)
        self.test_prices  = _make_prices(180, seed=6)
        self.cache = _make_tiny_cache(n)
        self.individual = _make_individual()

    def _run(self, train_result, test_result):
        engine = _MockEngine(train_result, test_result)
        return evaluate_individual(
            self.individual, self.train_prices, self.test_prices,
            self.n_train, self.cache, engine,
        )[0]

    def test_high_pf_no_penalty_gives_positive_fitness(self):
        """Good PF on both splits → positive fitness."""
        fit = self._run(
            _mock_result(n_trades=50, total_pnl=2000.0, profit_factor=2.0),
            _mock_result(n_trades=50, total_pnl=2000.0, profit_factor=2.0),
        )
        assert fit > 0.0

    def test_negative_pnl_still_clamped_to_zero(self):
        """Fitness is clamped to 0 even if penalties push it negative."""
        fit = self._run(
            _mock_result(n_trades=10, total_pnl=-500.0, profit_factor=0.5),
            _mock_result(n_trades=10, total_pnl=-500.0, profit_factor=0.5),
        )
        assert fit == 0.0

    def test_low_pf_reduces_fitness(self):
        """Low PF result should score lower than high PF result."""
        good = self._run(
            _mock_result(n_trades=30, total_pnl=1000.0, profit_factor=2.0),
            _mock_result(n_trades=30, total_pnl=1000.0, profit_factor=2.0),
        )
        bad = self._run(
            _mock_result(n_trades=30, total_pnl=1000.0, profit_factor=0.8),
            _mock_result(n_trades=30, total_pnl=1000.0, profit_factor=0.8),
        )
        assert good >= bad

    def test_few_test_trades_soft_penalty(self):
        """Low n_trades applies soft penalty — same avg_trade_pnl, fewer trades → lower score.

        Hold avg_trade_pnl = 20.0 constant; vary n_trades so total_pnl also varies.
        Primary fitness = total_pnl × avg_trade_pnl is lower for fewer trades,
        and the soft penalty reduces it further.
        """
        # many: 50 trades × $20 = $1000 total; fitness ≈ 1000 × 20 = 20000
        many = self._run(
            _mock_result(n_trades=50, total_pnl=1000.0, profit_factor=2.0),
            _mock_result(n_trades=50, total_pnl=1000.0, profit_factor=2.0),
        )
        # few: 6 trades × $20 = $120 total; fitness ≈ 120 × 20 = 2400 minus soft penalty
        few = self._run(
            _mock_result(n_trades=50, total_pnl=1000.0, profit_factor=2.0),
            _mock_result(n_trades=6, total_pnl=120.0, profit_factor=2.0),
        )
        assert many >= few


# ---------------------------------------------------------------------------
# Entry threshold wiring
# ---------------------------------------------------------------------------

class TestEntryThreshold:
    """entry_threshold gene (index 9) must gate signals before they reach the engine."""

    def _run_capture(self, entry_threshold: float):
        """Return total entry-signal count seen by the engine across both splits."""
        n = 200
        n_train = 100
        # Constant cache values of 10.0 → composite = 1.0*10 + 0.5*10 + 0.5*10 = 20.0
        arr = np.full(n, 10.0, dtype=np.float32)
        cache = {"0_14": arr, "7_10": arr, "9_10": arr}
        individual = _make_individual(entry_threshold=entry_threshold)
        train_prices = _make_prices(n_train, seed=11)
        test_prices  = _make_prices(n - n_train, seed=12)

        captured: list = []

        class _CapturingEngine:
            def run(self, signals, prices, sl, tp, pos):
                captured.append(np.array(signals, dtype=float).copy())
                return _mock_result(n_trades=20)

        evaluate_individual(individual, train_prices, test_prices, n_train, cache, _CapturingEngine())
        return sum(int(np.sum(s > 0)) for s in captured)

    def test_zero_threshold_passes_all_positive_signals(self):
        """threshold=0.0: composite 20.0 > 0.0 → all bars produce entry signals."""
        entries = self._run_capture(entry_threshold=0.0)
        assert entries > 0

    def test_high_threshold_suppresses_all_entries(self):
        """threshold=50.0: composite 20.0 < 50.0 → no bar produces an entry signal."""
        entries = self._run_capture(entry_threshold=50.0)
        assert entries == 0

    def test_entry_threshold_reduces_signal_count(self):
        """Raising the threshold must strictly reduce the number of entry signals."""
        low  = self._run_capture(entry_threshold=0.0)
        high = self._run_capture(entry_threshold=50.0)
        assert low > high


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

class TestReproducibility:
    def test_same_inputs_same_output(self):
        n = 300
        n_train = 120
        train_prices = _make_prices(120, seed=7)
        test_prices  = _make_prices(180, seed=8)
        cache = _make_tiny_cache(n)
        individual = _make_individual()

        engine1 = _MockEngine(_mock_result(30, 1000.0, 1.8), _mock_result(30, 1000.0, 1.8))
        engine2 = _MockEngine(_mock_result(30, 1000.0, 1.8), _mock_result(30, 1000.0, 1.8))

        r1 = evaluate_individual(individual, train_prices, test_prices, n_train, cache, engine1)
        r2 = evaluate_individual(individual, train_prices, test_prices, n_train, cache, engine2)
        assert r1 == r2
