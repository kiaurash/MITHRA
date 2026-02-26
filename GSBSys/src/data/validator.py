"""OHLCV data quality validation.

Raises ``ValueError`` on the first detected problem so callers can handle
bad data explicitly rather than propagating NaNs silently.

Key design note — we check ``High >= Open`` and ``Low <= Open``, NOT
``High >= Close`` / ``Low <= Close``.  Overnight gaps can legitimately place
Close outside the Open range of the *next* bar, so using Close as the
reference would produce false positives.  Open is always within the bar's
High–Low range by definition.
"""

from __future__ import annotations

import pandas as pd

_REQUIRED_COLUMNS = {"date", "open", "high", "low", "close", "volume"}


def validate_ohlcv(df: pd.DataFrame) -> None:
    """Validate an OHLCV DataFrame in-place (raises on first violation).

    Checks performed (in order):
    1. Required columns present
    2. No NaN in any OHLCV column
    3. High ≥ Low
    4. High ≥ Open  (use Open, not Close — see module docstring)
    5. Low  ≤ Open
    6. Volume > 0
    7. Dates monotonically increasing
    8. No duplicate dates

    Args:
        df: DataFrame with at minimum columns [date, open, high, low, close, volume].

    Raises:
        ValueError: Describing the first constraint that is violated.
    """
    # 1. Required columns
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    ohlcv_cols = ["open", "high", "low", "close", "volume"]

    # 2. No NaN in OHLCV
    nan_counts = df[ohlcv_cols].isnull().sum()
    bad = nan_counts[nan_counts > 0]
    if not bad.empty:
        raise ValueError(f"NaN values in columns: {bad.to_dict()}")

    # 3. High >= Low
    bad_hl = df["high"] < df["low"]
    if bad_hl.any():
        n = bad_hl.sum()
        raise ValueError(f"High < Low on {n} row(s). First: {df.loc[bad_hl, 'date'].iloc[0]}")

    # 4. High >= Open
    bad_ho = df["high"] < df["open"]
    if bad_ho.any():
        n = bad_ho.sum()
        raise ValueError(f"High < Open on {n} row(s). First: {df.loc[bad_ho, 'date'].iloc[0]}")

    # 5. Low <= Open
    bad_lo = df["low"] > df["open"]
    if bad_lo.any():
        n = bad_lo.sum()
        raise ValueError(f"Low > Open on {n} row(s). First: {df.loc[bad_lo, 'date'].iloc[0]}")

    # 6. Volume > 0
    bad_vol = df["volume"] <= 0
    if bad_vol.any():
        n = bad_vol.sum()
        raise ValueError(f"Non-positive volume on {n} row(s). First: {df.loc[bad_vol, 'date'].iloc[0]}")

    # 7. Monotonically increasing dates
    if not df["date"].is_monotonic_increasing:
        raise ValueError("Dates are not monotonically increasing")

    # 8. No duplicate dates
    dupes = df["date"].duplicated()
    if dupes.any():
        n = dupes.sum()
        raise ValueError(f"Duplicate dates found: {n} duplicate(s)")
