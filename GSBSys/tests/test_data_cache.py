"""Tests for src/data/cache.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.data.cache import DataCache


def _sample_df(n: int = 5) -> pd.DataFrame:
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


def test_load_returns_none_when_not_cached(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    assert cache.load("SPY", "2020-01-01", "2020-12-31") is None


def test_exists_false_when_not_cached(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    assert not cache.exists("SPY", "2020-01-01", "2020-12-31")


def test_save_and_load_roundtrip(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    df = _sample_df()
    cache.save(df, "SPY", "2020-01-01", "2020-12-31")
    loaded = cache.load("SPY", "2020-01-01", "2020-12-31")
    assert loaded is not None
    pd.testing.assert_frame_equal(df, loaded)


def test_exists_true_after_save(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    cache.save(_sample_df(), "SPY", "2020-01-01", "2020-12-31")
    assert cache.exists("SPY", "2020-01-01", "2020-12-31")


def test_different_tickers_separate_files(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    df_spy = _sample_df()
    df_qqq = _sample_df()
    df_qqq["close"] = 300.0

    cache.save(df_spy, "SPY", "2020-01-01", "2020-12-31")
    cache.save(df_qqq, "QQQ", "2020-01-01", "2020-12-31")

    assert cache.load("SPY", "2020-01-01", "2020-12-31")["close"].iloc[0] == 101.0
    assert cache.load("QQQ", "2020-01-01", "2020-12-31")["close"].iloc[0] == 300.0


def test_different_date_ranges_separate_files(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    df1 = _sample_df(3)
    df2 = _sample_df(7)

    cache.save(df1, "SPY", "2010-01-01", "2015-12-31")
    cache.save(df2, "SPY", "2015-01-01", "2020-12-31")

    assert len(cache.load("SPY", "2010-01-01", "2015-12-31")) == 3
    assert len(cache.load("SPY", "2015-01-01", "2020-12-31")) == 7


def test_invalidate_removes_file(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    cache.save(_sample_df(), "SPY", "2020-01-01", "2020-12-31")
    cache.invalidate("SPY", "2020-01-01", "2020-12-31")
    assert not cache.exists("SPY", "2020-01-01", "2020-12-31")
    assert cache.load("SPY", "2020-01-01", "2020-12-31") is None


def test_invalidate_noop_when_not_cached(tmp_path):
    cache = DataCache(str(tmp_path / "cache"))
    cache.invalidate("SPY", "2020-01-01", "2020-12-31")  # must not raise


def test_cache_dir_created_automatically(tmp_path):
    deep = tmp_path / "a" / "b" / "c"
    cache = DataCache(str(deep))
    assert deep.exists()
