"""Tests for src/data/loader.py.

Unit tests use mock yfinance responses — no network calls.
Integration tests (marked @pytest.mark.integration) hit the real Yahoo Finance API.
Run only unit tests by default: pytest tests/test_data_loader.py -m "not integration"
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.data.loader import load_market_data


# ---------------------------------------------------------------------------
# Helpers — build synthetic yfinance responses
# ---------------------------------------------------------------------------

def _make_flat_df(n: int = 10) -> pd.DataFrame:
    """Synthetic DataFrame mimicking yfinance flat-column response (older API)."""
    dates = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": [100.0 + i for i in range(n)],
            "High": [102.0 + i for i in range(n)],
            "Low": [98.0 + i for i in range(n)],
            "Close": [101.0 + i for i in range(n)],
            "Volume": [1_000_000 + i * 1000 for i in range(n)],
        }
    ).set_index("Date")


def _make_multiindex_df(ticker: str = "SPY", n: int = 10) -> pd.DataFrame:
    """Synthetic DataFrame mimicking yfinance MultiIndex response (newer API)."""
    flat = _make_flat_df(n)
    flat.columns = pd.MultiIndex.from_tuples(
        [(col, ticker) for col in flat.columns]
    )
    return flat


# ---------------------------------------------------------------------------
# loader.py — unit tests
# ---------------------------------------------------------------------------


class TestLoadMarketDataColumns:
    def test_returns_standard_columns_flat(self):
        with patch("src.data.loader.yf.download", return_value=_make_flat_df()):
            df = load_market_data("SPY", "2020-01-01", "2020-12-31")
        assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]

    def test_returns_standard_columns_multiindex(self):
        with patch("src.data.loader.yf.download", return_value=_make_multiindex_df("SPY")):
            df = load_market_data("SPY", "2020-01-01", "2020-12-31")
        assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]

    def test_multiindex_flattened_before_downstream(self):
        """MultiIndex must be flattened — if not, column names would be tuples."""
        with patch("src.data.loader.yf.download", return_value=_make_multiindex_df("QQQ")):
            df = load_market_data("QQQ", "2020-01-01", "2020-12-31")
        for col in df.columns:
            assert isinstance(col, str), f"Column {col!r} is not a string — MultiIndex not flattened"


class TestLoadMarketDataTypes:
    def test_date_column_is_datetime(self):
        with patch("src.data.loader.yf.download", return_value=_make_flat_df()):
            df = load_market_data("SPY", "2020-01-01", "2020-12-31")
        assert pd.api.types.is_datetime64_any_dtype(df["date"]), "date column must be datetime64"

    def test_price_columns_are_numeric(self):
        with patch("src.data.loader.yf.download", return_value=_make_flat_df()):
            df = load_market_data("SPY", "2020-01-01", "2020-12-31")
        for col in ["open", "high", "low", "close"]:
            assert pd.api.types.is_numeric_dtype(df[col]), f"{col} must be numeric"

    def test_row_count_preserved(self):
        with patch("src.data.loader.yf.download", return_value=_make_flat_df(n=20)):
            df = load_market_data("SPY", "2020-01-01", "2020-12-31")
        assert len(df) == 20

    def test_date_is_plain_column_not_index(self):
        with patch("src.data.loader.yf.download", return_value=_make_flat_df()):
            df = load_market_data("SPY", "2020-01-01", "2020-12-31")
        assert "date" in df.columns
        assert df.index.name != "date"


class TestLoadMarketDataErrors:
    def test_raises_on_empty_response(self):
        empty = pd.DataFrame()
        with patch("src.data.loader.yf.download", return_value=empty):
            with pytest.raises(ValueError, match="No data returned"):
                load_market_data("INVALID", "2020-01-01", "2020-12-31")

    def test_passes_auto_adjust_true(self):
        """Verify auto_adjust=True is forwarded to yf.download."""
        mock_dl = MagicMock(return_value=_make_flat_df())
        with patch("src.data.loader.yf.download", mock_dl):
            load_market_data("SPY", "2020-01-01", "2020-12-31")
        _, kwargs = mock_dl.call_args
        assert kwargs.get("auto_adjust") is True, "auto_adjust=True must be passed to yf.download"

    def test_passes_progress_false(self):
        """progress=False suppresses the tqdm bar."""
        mock_dl = MagicMock(return_value=_make_flat_df())
        with patch("src.data.loader.yf.download", mock_dl):
            load_market_data("SPY", "2020-01-01", "2020-12-31")
        _, kwargs = mock_dl.call_args
        assert kwargs.get("progress") is False
