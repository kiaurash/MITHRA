"""Tests for src/data/normalizer.py."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data.normalizer import normalize_indicator, train_test_split_timeseries


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv_df(n: int = 600) -> pd.DataFrame:
    dates = pd.date_range("2010-01-04", periods=n, freq="B")
    prices = 100 + np.cumsum(np.random.default_rng(42).normal(0, 1, n))
    return pd.DataFrame(
        {
            "date":   dates,
            "open":   prices,
            "high":   prices + 1,
            "low":    prices - 1,
            "close":  prices,
            "volume": [1_000_000] * n,
        }
    )


def _linear_series(n: int = 500) -> pd.Series:
    """Strictly increasing series — easy to reason about normalisation."""
    return pd.Series(np.arange(float(n)), name="test")


# ---------------------------------------------------------------------------
# normalize_indicator
# ---------------------------------------------------------------------------


class TestNormalizeIndicator:
    def test_first_251_bars_are_nan(self):
        # rolling(window=252, min_periods=252) first produces a value at index 251
        # (the 252nd bar, 1-indexed). So bars 0-250 (251 bars) are NaN.
        s = _linear_series(500)
        result = normalize_indicator(s, window=252)
        assert result.iloc[:251].isna().all(), "First 251 bars must be NaN (warm-up)"
        assert not pd.isna(result.iloc[251]), "Bar 251 should be the first non-NaN value"

    def test_bars_after_warmup_are_not_nan(self):
        s = _linear_series(500)
        result = normalize_indicator(s, window=252)
        assert result.iloc[252:].notna().all(), "Bars after warm-up must not be NaN"

    def test_values_bounded_minus100_to_100(self):
        rng = np.random.default_rng(0)
        s = pd.Series(rng.normal(0, 10, 600))
        result = normalize_indicator(s, window=252)
        valid = result.dropna()
        assert (valid >= -100.0 - 1e-9).all(), "Values must be >= -100"
        assert (valid <= 100.0 + 1e-9).all(), "Values must be <= +100"

    def test_linear_series_reaches_100_at_window_end(self):
        """Last bar of the first complete window should be +100 (max of window)."""
        s = _linear_series(300)
        result = normalize_indicator(s, window=252)
        # At bar 251 (0-indexed), the value is the max of bars [0..251]
        assert abs(result.iloc[251] - 100.0) < 1e-6

    def test_flat_series_produces_nan_not_zero(self):
        """When rolling_max == rolling_min, result should be NaN, not 0."""
        s = pd.Series([50.0] * 300)
        result = normalize_indicator(s, window=252)
        # All values within the window are identical → denom = 0 → NaN
        assert result.iloc[252:].isna().all(), "Flat series should produce NaN, not 0"

    def test_output_length_matches_input(self):
        s = _linear_series(400)
        result = normalize_indicator(s, window=252)
        assert len(result) == len(s)

    def test_series_name_preserved(self):
        s = pd.Series(np.arange(300.0), name="RSI_14")
        result = normalize_indicator(s)
        assert result.name == "RSI_14"

    def test_custom_window(self):
        """Window=10: first 9 bars are NaN; bar 9 is first non-NaN."""
        s = _linear_series(50)
        result = normalize_indicator(s, window=10)
        assert result.iloc[:9].isna().all()
        assert result.iloc[9:].notna().all()


# ---------------------------------------------------------------------------
# train_test_split_timeseries
# ---------------------------------------------------------------------------


class TestTrainTestSplit:
    def test_basic_split_sizes(self):
        df = _make_ohlcv_df(n=600)
        train, test = train_test_split_timeseries(df, train_ratio=0.4, warmup_bars=252)
        post_warmup = 600 - 252  # 348
        expected_train = int(post_warmup * 0.4)  # 139
        assert len(train) == expected_train
        assert len(test) == post_warmup - expected_train

    def test_temporal_ordering(self):
        df = _make_ohlcv_df(n=600)
        train, test = train_test_split_timeseries(df)
        assert train["date"].iloc[-1] < test["date"].iloc[0], "Train must end before test starts"

    def test_warmup_bars_trimmed(self):
        df = _make_ohlcv_df(n=600)
        train, test = train_test_split_timeseries(df, warmup_bars=252)
        # First bar in train must be after the warmup period
        first_valid_date = df["date"].iloc[252]
        assert train["date"].iloc[0] == first_valid_date

    def test_no_overlap_between_train_and_test(self):
        df = _make_ohlcv_df(n=600)
        train, test = train_test_split_timeseries(df)
        train_dates = set(train["date"])
        test_dates = set(test["date"])
        assert train_dates.isdisjoint(test_dates), "Train and test must not share dates"

    def test_train_plus_test_equals_post_warmup(self):
        df = _make_ohlcv_df(n=600)
        train, test = train_test_split_timeseries(df, warmup_bars=252)
        assert len(train) + len(test) == 600 - 252

    def test_reset_index(self):
        df = _make_ohlcv_df(n=600)
        train, test = train_test_split_timeseries(df)
        assert list(train.index) == list(range(len(train)))
        assert list(test.index) == list(range(len(test)))

    def test_raises_when_not_enough_data(self):
        df = _make_ohlcv_df(n=100)  # less than warmup_bars=252
        with pytest.raises(ValueError, match="Not enough data"):
            train_test_split_timeseries(df, warmup_bars=252)

    def test_raises_when_zero_test_bars(self):
        # n=300, warmup=252 → 48 remaining. train_ratio=1.0 → n_train=48, n_test=0
        df = _make_ohlcv_df(n=300)
        with pytest.raises(ValueError):
            train_test_split_timeseries(df, train_ratio=1.0, warmup_bars=252)
