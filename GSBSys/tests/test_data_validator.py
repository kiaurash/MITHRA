"""Tests for src/data/validator.py."""

from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.data.validator import validate_ohlcv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_df(n: int = 5) -> pd.DataFrame:
    """Minimal valid OHLCV DataFrame."""
    dates = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.DataFrame(
        {
            "date": dates,
            "open":   [100.0] * n,
            "high":   [102.0] * n,
            "low":    [98.0]  * n,
            "close":  [101.0] * n,
            "volume": [1_000_000] * n,
        }
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_dataframe_passes():
    validate_ohlcv(_valid_df())  # must not raise


def test_valid_with_varying_prices():
    df = _valid_df(10)
    df["open"]   = [100 + i for i in range(10)]
    df["high"]   = [103 + i for i in range(10)]
    df["low"]    = [97  + i for i in range(10)]
    df["close"]  = [101 + i for i in range(10)]
    validate_ohlcv(df)


# ---------------------------------------------------------------------------
# Missing columns
# ---------------------------------------------------------------------------


def test_missing_column_raises():
    df = _valid_df().drop(columns=["volume"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_ohlcv(df)


def test_missing_multiple_columns_raises():
    df = _valid_df().drop(columns=["high", "low"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_ohlcv(df)


# ---------------------------------------------------------------------------
# NaN checks
# ---------------------------------------------------------------------------


def test_nan_in_close_raises():
    df = _valid_df()
    df.loc[2, "close"] = float("nan")
    with pytest.raises(ValueError, match="NaN values"):
        validate_ohlcv(df)


def test_nan_in_volume_raises():
    df = _valid_df()
    df.loc[0, "volume"] = float("nan")
    with pytest.raises(ValueError, match="NaN values"):
        validate_ohlcv(df)


def test_nan_in_high_raises():
    df = _valid_df()
    df.loc[1, "high"] = float("nan")
    with pytest.raises(ValueError, match="NaN values"):
        validate_ohlcv(df)


# ---------------------------------------------------------------------------
# OHLCV constraint checks
# ---------------------------------------------------------------------------


def test_high_less_than_low_raises():
    df = _valid_df()
    df.loc[1, "high"] = 97.0  # below low=98
    with pytest.raises(ValueError, match="High < Low"):
        validate_ohlcv(df)


def test_high_less_than_open_raises():
    df = _valid_df()
    df.loc[0, "high"] = 99.0  # below open=100
    with pytest.raises(ValueError, match="High < Open"):
        validate_ohlcv(df)


def test_low_greater_than_open_raises():
    df = _valid_df()
    df.loc[0, "low"] = 101.0  # above open=100
    with pytest.raises(ValueError, match="Low > Open"):
        validate_ohlcv(df)


def test_zero_volume_raises():
    df = _valid_df()
    df.loc[2, "volume"] = 0
    with pytest.raises(ValueError, match="Non-positive volume"):
        validate_ohlcv(df)


def test_negative_volume_raises():
    df = _valid_df()
    df.loc[2, "volume"] = -500
    with pytest.raises(ValueError, match="Non-positive volume"):
        validate_ohlcv(df)


# ---------------------------------------------------------------------------
# Date checks
# ---------------------------------------------------------------------------


def test_duplicate_dates_raises():
    df = _valid_df(5)
    df.loc[2, "date"] = df.loc[1, "date"]  # duplicate
    with pytest.raises(ValueError, match="Duplicate dates"):
        validate_ohlcv(df)


def test_non_monotonic_dates_raises():
    df = _valid_df(5)
    # Swap two dates to break ordering
    df.loc[1, "date"], df.loc[3, "date"] = df.loc[3, "date"], df.loc[1, "date"]
    with pytest.raises(ValueError, match="monotonically"):
        validate_ohlcv(df)


# ---------------------------------------------------------------------------
# Edge: close outside open range is OK (overnight gap)
# ---------------------------------------------------------------------------


def test_close_above_high_does_not_raise():
    """Close can be above High in theory (adjusted prices) — we don't reject it."""
    df = _valid_df()
    df.loc[0, "close"] = 200.0  # way above high=102
    # Validator only checks High>=Open and Low<=Open, not High>=Close
    validate_ohlcv(df)  # must not raise
