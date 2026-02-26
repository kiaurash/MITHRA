"""Tests for src/indicators/ (registry, calculator, signal_generator)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.indicators.registry import INDICATOR_REGISTRY, N_INDICATORS, IndicatorSpec
from src.indicators.calculator import (
    build_indicator_cache,
    compute_raw_indicator,
)
from src.indicators.signal_generator import generate_signals_weighted_sum, get_entry_signals


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 700) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    prices = 100 + np.cumsum(rng.normal(0, 0.5, n))
    prices = np.clip(prices, 1.0, None)  # keep positive
    return pd.DataFrame(
        {
            "date":   pd.date_range("2010-01-04", periods=n, freq="B"),
            "open":   prices,
            "high":   prices * (1 + rng.uniform(0, 0.01, n)),
            "low":    prices * (1 - rng.uniform(0, 0.01, n)),
            "close":  prices,
            "volume": rng.integers(500_000, 2_000_000, n).astype(float),
        }
    )


def _make_individual(
    ind1_type=0, ind1_period=14, ind1_weight=1.0,
    ind2_type=1, ind2_period=20, ind2_weight=0.5,
    ind3_type=7, ind3_period=10, ind3_weight=0.5,
    entry_threshold=20.0,
    stop_loss_pct=0.05,
    take_profit_pct=0.10,
    position_size_mult=1.0,
) -> list:
    return [
        ind1_type, ind1_period, ind1_weight,
        ind2_type, ind2_period, ind2_weight,
        ind3_type, ind3_period, ind3_weight,
        entry_threshold, stop_loss_pct, take_profit_pct, position_size_mult,
    ]


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_n_indicators_is_15(self):
        assert N_INDICATORS == 15

    def test_ids_are_0_to_14(self):
        assert set(INDICATOR_REGISTRY.keys()) == set(range(15))

    def test_all_entries_are_indicator_spec(self):
        for spec in INDICATOR_REGISTRY.values():
            assert isinstance(spec, IndicatorSpec)

    def test_obv_period_is_zero(self):
        spec = INDICATOR_REGISTRY[12]
        assert spec.min_period == 0 and spec.max_period == 0

    def test_macd_period_range(self):
        spec = INDICATOR_REGISTRY[5]
        assert spec.min_period == 8 and spec.max_period == 20

    def test_all_non_obv_have_positive_periods(self):
        for ind_id, spec in INDICATOR_REGISTRY.items():
            if ind_id == 12:  # OBV
                continue
            assert spec.min_period > 0, f"ID {ind_id} has zero min_period"
            assert spec.max_period >= spec.min_period


# ---------------------------------------------------------------------------
# compute_raw_indicator tests
# ---------------------------------------------------------------------------

class TestComputeRawIndicator:
    def setup_method(self):
        df = _make_ohlcv(400)
        self.close = df["close"].values
        self.high = df["high"].values
        self.low = df["low"].values
        self.volume = df["volume"].values
        self.n = len(self.close)

    def test_output_length_equals_input(self):
        for ind_id in range(15):
            spec = INDICATOR_REGISTRY[ind_id]
            period = spec.min_period
            out = compute_raw_indicator(ind_id, period, self.close, self.high, self.low, self.volume)
            assert len(out) == self.n, f"ID {ind_id} length mismatch"

    def test_output_is_float64(self):
        for ind_id in range(15):
            spec = INDICATOR_REGISTRY[ind_id]
            period = spec.min_period
            out = compute_raw_indicator(ind_id, period, self.close, self.high, self.low, self.volume)
            assert out.dtype == np.float64, f"ID {ind_id} not float64"

    def test_warmup_bars_are_nan(self):
        """First bar should be NaN for every indicator except OBV."""
        for ind_id in range(15):
            if ind_id == 12:  # OBV starts at bar 0 (no warm-up)
                continue
            spec = INDICATOR_REGISTRY[ind_id]
            out = compute_raw_indicator(ind_id, spec.min_period, self.close, self.high, self.low, self.volume)
            assert np.isnan(out[0]), f"ID {ind_id}: bar 0 should be NaN"

    def test_eventually_non_nan(self):
        """Each indicator must produce at least one non-NaN value."""
        for ind_id in range(15):
            spec = INDICATOR_REGISTRY[ind_id]
            out = compute_raw_indicator(ind_id, spec.min_period, self.close, self.high, self.low, self.volume)
            assert np.any(~np.isnan(out)), f"ID {ind_id} never produces a non-NaN value"

    def test_rsi_bounded_0_to_100(self):
        out = compute_raw_indicator(0, 14, self.close, self.high, self.low, self.volume)
        valid = out[~np.isnan(out)]
        assert np.all(valid >= 0.0 - 1e-9) and np.all(valid <= 100.0 + 1e-9)

    def test_stoch_bounded_0_to_100(self):
        out = compute_raw_indicator(2, 14, self.close, self.high, self.low, self.volume)
        valid = out[~np.isnan(out)]
        assert np.all(valid >= 0.0 - 1e-9) and np.all(valid <= 100.0 + 1e-9)

    def test_adx_bounded_0_to_100(self):
        out = compute_raw_indicator(3, 14, self.close, self.high, self.low, self.volume)
        valid = out[~np.isnan(out)]
        assert np.all(valid >= 0.0 - 1e-9) and np.all(valid <= 100.0 + 1e-9)

    def test_willr_bounded_neg100_to_0(self):
        out = compute_raw_indicator(8, 14, self.close, self.high, self.low, self.volume)
        valid = out[~np.isnan(out)]
        assert np.all(valid >= -100.0 - 1e-9) and np.all(valid <= 0.0 + 1e-9)

    def test_mfi_bounded_0_to_100(self):
        out = compute_raw_indicator(13, 14, self.close, self.high, self.low, self.volume)
        valid = out[~np.isnan(out)]
        assert np.all(valid >= 0.0 - 1e-9) and np.all(valid <= 100.0 + 1e-9)

    def test_obv_no_warmup_nan(self):
        """OBV starts from bar 0 — no NaN at beginning."""
        out = compute_raw_indicator(12, 0, self.close, self.high, self.low, self.volume)
        assert not np.isnan(out[0])

    def test_invalid_indicator_id_raises(self):
        with pytest.raises(ValueError, match="Unknown indicator_id"):
            compute_raw_indicator(99, 14, self.close, self.high, self.low, self.volume)

    def test_macd_period_is_fast_span(self):
        """MACD with fast=8 → slow=22; should produce values eventually."""
        out = compute_raw_indicator(5, 8, self.close, self.high, self.low, self.volume)
        assert np.any(~np.isnan(out))


# ---------------------------------------------------------------------------
# build_indicator_cache tests
# ---------------------------------------------------------------------------

class TestBuildIndicatorCache:
    def setup_method(self):
        self.df = _make_ohlcv(700)

    def test_returns_dict(self):
        cache = build_indicator_cache(self.df, normalization_window=50)
        assert isinstance(cache, dict)

    def test_cache_has_expected_keys(self):
        cache = build_indicator_cache(self.df, normalization_window=50)
        # OBV key
        assert "12_0" in cache
        # RSI with period 5 (min for RSI)
        assert "0_5" in cache
        # RSI with period 50 (max for RSI)
        assert "0_50" in cache

    def test_cache_arrays_are_float32(self):
        cache = build_indicator_cache(self.df, normalization_window=50)
        for key, arr in cache.items():
            assert arr.dtype == np.float32, f"Key {key}: expected float32"

    def test_cache_array_lengths_match_data(self):
        cache = build_indicator_cache(self.df, normalization_window=50)
        n = len(self.df)
        for key, arr in cache.items():
            assert len(arr) == n, f"Key {key}: length {len(arr)} != {n}"

    def test_normalized_values_bounded(self):
        """Normalized values must be in [-100, 100]."""
        cache = build_indicator_cache(self.df, normalization_window=50)
        for key, arr in cache.items():
            valid = arr[~np.isnan(arr)]
            if len(valid) == 0:
                continue
            assert np.all(valid >= -100.0 - 1e-4), f"Key {key}: below -100"
            assert np.all(valid <= 100.0 + 1e-4), f"Key {key}: above +100"

    def test_no_obv_with_nonzero_period(self):
        """OBV should only have key '12_0', not '12_1', '12_2' etc."""
        cache = build_indicator_cache(self.df, normalization_window=50)
        obv_keys = [k for k in cache if k.startswith("12_")]
        assert obv_keys == ["12_0"], f"Unexpected OBV keys: {obv_keys}"

    def test_number_of_cache_entries(self):
        """Total entries = sum of (max-min+1) for each indicator + 1 for OBV."""
        cache = build_indicator_cache(self.df, normalization_window=50)
        expected = 0
        for spec in INDICATOR_REGISTRY.values():
            if spec.min_period == 0 and spec.max_period == 0:
                expected += 1  # OBV
            else:
                expected += spec.max_period - spec.min_period + 1
        assert len(cache) == expected, f"Expected {expected} entries, got {len(cache)}"


# ---------------------------------------------------------------------------
# generate_signals_weighted_sum tests
# ---------------------------------------------------------------------------

class TestGenerateSignals:
    def setup_method(self):
        df = _make_ohlcv(700)
        self.cache = build_indicator_cache(df, normalization_window=50)
        self.n = len(df)
        self.individual = _make_individual()

    def test_output_length_equals_data(self):
        out = generate_signals_weighted_sum(self.individual, self.cache)
        assert len(out) == self.n

    def test_output_is_float64(self):
        out = generate_signals_weighted_sum(self.individual, self.cache)
        assert out.dtype == np.float64

    def test_nan_where_any_indicator_nan(self):
        """Any bar where at least one indicator is NaN → composite is NaN."""
        out = generate_signals_weighted_sum(self.individual, self.cache)
        # The first bar should be NaN because RSI/CCI have warm-up
        assert np.isnan(out[0])

    def test_eventually_non_nan(self):
        out = generate_signals_weighted_sum(self.individual, self.cache)
        assert np.any(~np.isnan(out))

    def test_zero_weights_produce_zero_signal(self):
        ind = _make_individual(ind1_weight=0.0, ind2_weight=0.0, ind3_weight=0.0)
        out = generate_signals_weighted_sum(ind, self.cache)
        valid = out[~np.isnan(out)]
        assert np.allclose(valid, 0.0)

    def test_wrong_gene_count_raises(self):
        with pytest.raises(ValueError, match="13 genes"):
            generate_signals_weighted_sum([1, 2, 3], self.cache)

    def test_missing_cache_key_raises(self):
        bad_ind = _make_individual(ind1_type=99, ind1_period=14)
        with pytest.raises(KeyError):
            generate_signals_weighted_sum(bad_ind, self.cache)

    def test_obv_slot_works(self):
        """OBV uses period=0; signal generation must handle it."""
        ind = _make_individual(ind1_type=12, ind1_period=0, ind1_weight=1.0)
        out = generate_signals_weighted_sum(ind, self.cache)
        assert np.any(~np.isnan(out))


# ---------------------------------------------------------------------------
# get_entry_signals tests
# ---------------------------------------------------------------------------

class TestGetEntrySignals:
    def test_returns_bool_array(self):
        composite = np.array([10.0, 25.0, np.nan, 5.0, 30.0])
        out = get_entry_signals(composite, entry_threshold=20.0)
        assert out.dtype == bool

    def test_length_preserved(self):
        composite = np.array([1.0, 2.0, 3.0])
        out = get_entry_signals(composite, entry_threshold=0.0)
        assert len(out) == 3

    def test_nan_bars_produce_false(self):
        composite = np.array([np.nan, 100.0, np.nan])
        out = get_entry_signals(composite, entry_threshold=50.0)
        assert not out[0] and not out[2]

    def test_above_threshold_is_true(self):
        composite = np.array([30.0, 5.0, 25.0])
        out = get_entry_signals(composite, entry_threshold=20.0)
        assert out[0] and not out[1] and out[2]

    def test_equal_to_threshold_is_false(self):
        """Strict > threshold, not >=."""
        composite = np.array([20.0])
        out = get_entry_signals(composite, entry_threshold=20.0)
        assert not out[0]
