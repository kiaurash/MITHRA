"""Market data loader — yfinance with MultiIndex flattening.

Usage::

    df = load_market_data("SPY", "2010-01-01", "2025-12-31")
    # Returns DataFrame with columns: date, open, high, low, close, volume
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def load_market_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance via yfinance.

    Handles the MultiIndex column format that newer yfinance versions return
    for single-ticker downloads. Flattens columns BEFORE any downstream
    processing to prevent silent data corruption.

    Args:
        ticker: Yahoo Finance ticker symbol (e.g. "SPY", "QQQ", "IWM").
        start: Start date string, inclusive, format "YYYY-MM-DD".
        end: End date string, exclusive, format "YYYY-MM-DD".

    Returns:
        DataFrame with columns [date, open, high, low, close, volume].
        ``date`` is a plain column (not the index), dtype datetime64.
        Prices are adjusted for splits and dividends (auto_adjust=True).

    Raises:
        ValueError: If the download returns no data (bad ticker / date range).
    """
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

    if raw.empty:
        raise ValueError(f"No data returned for ticker={ticker!r} ({start} → {end})")

    # --- Flatten MultiIndex columns (yfinance ≥0.2.x for single tickers) ----
    # Example before: ("Close", "SPY"), ("Open", "SPY"), ...
    # Example after:  "Close", "Open", ...
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [col[0] for col in raw.columns]

    # --- Normalise column names to lowercase with underscores ----------------
    raw = raw.reset_index()
    raw.columns = [str(c).replace(" ", "_").lower() for c in raw.columns]

    # Rename "price_date" → "date" if yfinance emits that variant
    if "price_date" in raw.columns:
        raw = raw.rename(columns={"price_date": "date"})

    # Select and return only the standard OHLCV columns
    return raw[["date", "open", "high", "low", "close", "volume"]].copy()
