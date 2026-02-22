"""Parquet-based OHLCV data cache.

Avoids re-downloading 4,000 bars on every run.  Cache keys are derived from
(ticker, start, end) so different date ranges are stored separately.

Parquet is preferred over SQLite for OHLCV:
- Columnar format → fast reads for price/indicator arrays
- Built-in compression via pyarrow
- No schema management required
- pd.read_parquet / df.to_parquet are one-liners
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class DataCache:
    """Persistent Parquet cache for OHLCV DataFrames.

    Args:
        cache_dir: Directory where ``.parquet`` files are stored.
            Created automatically if it does not exist.

    Example::

        cache = DataCache("data/cache")
        df = cache.load("SPY", "2010-01-01", "2025-12-31")
        if df is None:
            df = load_market_data("SPY", "2010-01-01", "2025-12-31")
            cache.save(df, "SPY", "2010-01-01", "2025-12-31")
    """

    def __init__(self, cache_dir: str = "data/cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, ticker: str, start: str, end: str) -> pd.DataFrame | None:
        """Return cached DataFrame or ``None`` if not cached.

        Args:
            ticker: Ticker symbol, e.g. "SPY".
            start: Start date string "YYYY-MM-DD".
            end: End date string "YYYY-MM-DD".

        Returns:
            Cached DataFrame with OHLCV columns, or ``None``.
        """
        path = self._cache_path(ticker, start, end)
        if path.exists():
            return pd.read_parquet(path)
        return None

    def save(self, df: pd.DataFrame, ticker: str, start: str, end: str) -> None:
        """Persist *df* to the Parquet cache.

        Args:
            df: OHLCV DataFrame to cache.
            ticker: Ticker symbol.
            start: Start date string.
            end: End date string.
        """
        path = self._cache_path(ticker, start, end)
        df.to_parquet(path, index=False)

    def exists(self, ticker: str, start: str, end: str) -> bool:
        """Return True if a cached file exists for this key."""
        return self._cache_path(ticker, start, end).exists()

    def invalidate(self, ticker: str, start: str, end: str) -> None:
        """Delete the cached file for this key (no-op if not cached)."""
        path = self._cache_path(ticker, start, end)
        if path.exists():
            path.unlink()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cache_path(self, ticker: str, start: str, end: str) -> Path:
        """Deterministic cache file path from (ticker, start, end)."""
        key = f"{ticker}_{start}_{end}"
        return self.cache_dir / f"{key}.parquet"
