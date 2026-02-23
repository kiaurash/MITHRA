"""Tests for src/validation/noise_injection.py."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.backtesting.engine import BacktestResult
from src.validation.noise_injection import (
    MVP_MIN_PROFITABLE,
    NOISE_VARIANTS,
    PRODUCTION_MIN_PROFITABLE,
    NoiseResult,
    VariantResult,
    _perturb_prices,
    _perturb_volume,
    _shift_signals,
    run_noise_injection,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

WARMUP = 252


def _make_ohlcv(n_bars: int = WARMUP + 50, seed: int = 0) -> pd.DataFrame:
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


def _make_backtest_result(pnl: float = 100.0, pf: float = 1.5, n_trades: int = 10) -> BacktestResult:
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


def _mock_engine(pf: float = 1.5) -> MagicMock:
    eng = MagicMock()
    eng.run.return_value = _make_backtest_result(pf=pf)
    return eng


def _make_individual() -> list:
    return [0, 20, 1.0, 1, 14, 1.0, 2, 9, 1.0, 0.5, 0.05, 0.10, 1.0]


# ---------------------------------------------------------------------------
# NOISE_VARIANTS constant
# ---------------------------------------------------------------------------

class TestNoiseVariantsConstant:
    def test_eight_variants(self):
        assert len(NOISE_VARIANTS) == 8

    def test_variant_tuple_length(self):
        for v in NOISE_VARIANTS:
            assert len(v) == 5, f"Variant {v} does not have 5 elements"

    def test_unique_names(self):
        names = [v[0] for v in NOISE_VARIANTS]
        assert len(names) == len(set(names))

    def test_unique_seeds(self):
        seeds = [v[4] for v in NOISE_VARIANTS]
        assert len(seeds) == len(set(seeds))

    def test_price_and_volume_and_shift_variants_present(self):
        names = [v[0] for v in NOISE_VARIANTS]
        assert any("price" in n for n in names)
        assert any("volume" in n for n in names)
        assert any("entry_shift" in n for n in names)


# ---------------------------------------------------------------------------
# _perturb_prices
# ---------------------------------------------------------------------------

class TestPerturbPrices:
    def test_zero_noise_returns_same_data(self):
        df = _make_ohlcv()
        out = _perturb_prices(df, 0.0, seed=42)
        pd.testing.assert_frame_equal(out, df)

    def test_positive_noise_increases_prices(self):
        df = _make_ohlcv()
        out = _perturb_prices(df, +0.01, seed=42)
        assert (out["close"] >= df["close"]).all()

    def test_negative_noise_decreases_prices(self):
        df = _make_ohlcv()
        out = _perturb_prices(df, -0.01, seed=42)
        assert (out["close"] <= df["close"]).all()

    def test_high_ge_low_after_perturbation(self):
        df = _make_ohlcv()
        for noise in [+0.02, -0.02]:
            out = _perturb_prices(df, noise, seed=42)
            assert (out["high"] >= out["low"]).all()

    def test_volume_unchanged(self):
        df = _make_ohlcv()
        out = _perturb_prices(df, +0.01, seed=42)
        pd.testing.assert_series_equal(out["volume"], df["volume"])

    def test_reproducible_with_same_seed(self):
        df = _make_ohlcv()
        out1 = _perturb_prices(df, +0.01, seed=7)
        out2 = _perturb_prices(df, +0.01, seed=7)
        pd.testing.assert_frame_equal(out1, out2)

    def test_different_seeds_give_different_results(self):
        df = _make_ohlcv()
        out1 = _perturb_prices(df, +0.01, seed=7)
        out2 = _perturb_prices(df, +0.01, seed=8)
        assert not (out1["close"] == out2["close"]).all()


# ---------------------------------------------------------------------------
# _perturb_volume
# ---------------------------------------------------------------------------

class TestPerturbVolume:
    def test_zero_noise_unchanged(self):
        df = _make_ohlcv()
        out = _perturb_volume(df, 0.0, seed=42)
        pd.testing.assert_frame_equal(out, df)

    def test_positive_noise_increases_volume(self):
        df = _make_ohlcv()
        out = _perturb_volume(df, +0.10, seed=42)
        assert (out["volume"] >= df["volume"]).all()

    def test_volume_minimum_1(self):
        df = _make_ohlcv()
        df = df.copy()
        df["volume"] = 0.1  # near-zero
        out = _perturb_volume(df, -0.50, seed=42)
        assert (out["volume"] >= 1.0).all()

    def test_prices_unchanged(self):
        df = _make_ohlcv()
        out = _perturb_volume(df, +0.10, seed=42)
        pd.testing.assert_series_equal(out["close"], df["close"])


# ---------------------------------------------------------------------------
# _shift_signals
# ---------------------------------------------------------------------------

class TestShiftSignals:
    def test_zero_shift_unchanged(self):
        sig = np.array([0, 1, 0, 1, 1, 0], dtype=np.float32)
        out = _shift_signals(sig, 0)
        np.testing.assert_array_equal(out, sig)

    def test_positive_shift_delays_signals(self):
        sig = np.array([1, 0, 0, 0, 0], dtype=np.float32)
        out = _shift_signals(sig, 1)
        # Signal at index 0 should appear at index 1
        assert out[1] == 1
        assert out[0] == 0

    def test_negative_shift_advances_signals(self):
        sig = np.array([0, 0, 0, 0, 1], dtype=np.float32)
        out = _shift_signals(sig, -1)
        # Signal at index 4 should appear at index 3
        assert out[3] == 1
        assert out[4] == 0

    def test_shape_preserved(self):
        sig = np.ones(100, dtype=np.float32)
        for shift in [-2, -1, 0, 1, 2]:
            out = _shift_signals(sig, shift)
            assert out.shape == sig.shape


# ---------------------------------------------------------------------------
# run_noise_injection — constants
# ---------------------------------------------------------------------------

class TestNoiseConstants:
    def test_mvp_threshold(self):
        assert MVP_MIN_PROFITABLE == 5

    def test_production_threshold(self):
        assert PRODUCTION_MIN_PROFITABLE == 6


# ---------------------------------------------------------------------------
# run_noise_injection — pass/fail
# ---------------------------------------------------------------------------

class TestRunNoiseInjection:
    def test_all_profitable_passes_both_tiers(self):
        ind = _make_individual()
        engine = _mock_engine(pf=2.0)
        result = run_noise_injection(ind, _make_ohlcv(), engine)
        assert result.n_profitable == 8
        assert result.passed_mvp is True
        assert result.passed_production is True

    def test_all_unprofitable_fails_both_tiers(self):
        ind = _make_individual()
        engine = _mock_engine(pf=0.5)
        result = run_noise_injection(ind, _make_ohlcv(), engine)
        assert result.n_profitable == 0
        assert result.passed_mvp is False
        assert result.passed_production is False

    def test_five_profitable_passes_mvp_fails_prod(self):
        ind = _make_individual()
        call_pf = [2.0, 2.0, 2.0, 2.0, 2.0, 0.5, 0.5, 0.5]
        idx = [0]
        mock_eng = MagicMock()
        def run_side(signals, prices, sl, tp, pos):
            pf = call_pf[idx[0]]
            idx[0] += 1
            return _make_backtest_result(pf=pf)
        mock_eng.run.side_effect = run_side

        result = run_noise_injection(ind, _make_ohlcv(), mock_eng)
        assert result.n_profitable == 5
        assert result.passed_mvp is True
        assert result.passed_production is False

    def test_eight_variant_results_returned(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_noise_injection(ind, _make_ohlcv(), engine)
        assert len(result.variant_results) == 8

    def test_variant_names_match_noise_variants(self):
        ind = _make_individual()
        engine = _mock_engine()
        result = run_noise_injection(ind, _make_ohlcv(), engine)
        expected_names = [v[0] for v in NOISE_VARIANTS]
        actual_names = [r.name for r in result.variant_results]
        assert actual_names == expected_names

    def test_too_short_df_all_skip(self):
        """Very short df → all variants skipped (n_trades=0, not profitable)."""
        ind = _make_individual()
        engine = _mock_engine()
        tiny = _make_ohlcv(5)  # fewer than warmup+10
        result = run_noise_injection(ind, tiny, engine, warmup_bars=252)
        assert result.n_profitable == 0
        assert all(r.n_trades == 0 for r in result.variant_results)

    def test_variant_result_frozen(self):
        vr = VariantResult(
            name="test", profit_factor=1.5, n_trades=10, total_pnl=100.0, profitable=True
        )
        with pytest.raises((TypeError, AttributeError)):
            vr.profitable = False  # type: ignore[misc]

    def test_noise_result_frozen(self):
        nr = NoiseResult(
            variant_results=[], n_profitable=0, passed_mvp=False, passed_production=False
        )
        with pytest.raises((TypeError, AttributeError)):
            nr.n_profitable = 5  # type: ignore[misc]

    def test_engine_called_eight_times(self):
        ind = _make_individual()
        engine = _mock_engine()
        run_noise_injection(ind, _make_ohlcv(), engine)
        assert engine.run.call_count == 8
