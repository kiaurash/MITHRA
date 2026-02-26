"""Indicator normalization and train/test splitting.

Normalization maps indicator values to [-100, +100] using a 252-bar
(~1 trading year) rolling window.  The first 252 bars are NaN — this is
intentional and correct.  Do NOT fillna(0): that would introduce lookahead
bias by implying the indicator was at the midpoint of its range.

Train/test split is strictly sequential (time-ordered).  Random shuffling
would leak future information into training data (lookahead bias).
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


def normalize_indicator(series: pd.Series, window: int = 252) -> pd.Series:
    """Normalize a raw indicator series to [-100, +100] via rolling window.

    Uses rolling Highest–Lowest normalization:
        normalized = 2 × (value − rolling_min) / (rolling_max − rolling_min) − 1
        scaled     = normalized × 100

    Properties:
    - First ``window - 1`` bars are NaN (warm-up period — caller must trim).
      Bar at index ``window - 1`` is the first non-NaN value.
    - Values are bounded to [-100, 100] when min≠max within the window
    - When rolling_max == rolling_min (flat region), result is NaN (not 0)

    Args:
        series: Raw indicator values as a pandas Series.
        window: Rolling window size in bars. Default 252 (~1 trading year).

    Returns:
        Series of same length, dtype float64, values in [-100, 100] or NaN.
    """
    rolling_min = series.rolling(window=window, min_periods=window).min()
    rolling_max = series.rolling(window=window, min_periods=window).max()

    denom = rolling_max - rolling_min
    # Where denom == 0 (perfectly flat), keep NaN rather than 0
    safe_denom = denom.where(denom != 0, other=np.nan)

    normalized = 2.0 * (series - rolling_min) / safe_denom - 1.0
    return (normalized * 100.0).rename(series.name)


def train_test_split_timeseries(
    df: pd.DataFrame,
    train_ratio: float = 0.4,
    warmup_bars: int = 252,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split OHLCV data into train and test sets after trimming warm-up bars.

    Steps:
    1. Discard the first ``warmup_bars`` rows (indicator warm-up period)
    2. Split remaining rows sequentially: first ``train_ratio`` → train,
       remainder → test

    Args:
        df: OHLCV DataFrame with a ``date`` column.  Must be sorted by date.
        train_ratio: Fraction of post-warmup bars allocated to training.
            Default 0.4 → 40% train / 60% test.
        warmup_bars: Number of leading bars to discard. Default 252.

    Returns:
        Tuple of (train_df, test_df), each with reset integer index.

    Raises:
        ValueError: If the trimmed DataFrame has fewer than 2 rows, or if
            the temporal ordering assertion fails (train end ≥ test start).
    """
    if len(df) <= warmup_bars:
        raise ValueError(
            f"DataFrame has {len(df)} rows but warmup_bars={warmup_bars}. "
            "Not enough data after warm-up trim."
        )

    trimmed = df.iloc[warmup_bars:].reset_index(drop=True)
    n = len(trimmed)

    if n < 2:
        raise ValueError(f"Only {n} bar(s) remain after warmup trim — cannot split.")

    n_train = max(1, int(n * train_ratio))
    n_test = n - n_train

    if n_test < 1:
        raise ValueError(
            f"train_ratio={train_ratio} leaves 0 test bars from {n} total."
        )

    train = trimmed.iloc[:n_train].reset_index(drop=True)
    test = trimmed.iloc[n_train:].reset_index(drop=True)

    # Strict temporal ordering guard — catches misconfigured splits
    if "date" in train.columns and "date" in test.columns:
        last_train = train["date"].iloc[-1]
        first_test = test["date"].iloc[0]
        if last_train >= first_test:
            raise ValueError(
                f"Temporal ordering violated: last train date {last_train} "
                f">= first test date {first_test}."
            )

    return train, test
