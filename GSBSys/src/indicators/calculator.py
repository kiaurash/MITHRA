"""Indicator calculator — pure NumPy/pandas implementations for all 15 Phase 1 indicators.

No TA-Lib dependency: all indicators are implemented with NumPy/pandas.

Special encoding notes (matches registry.py):
- MACD (ID 5): ``period`` = fast EMA span; slow = fast + 14; signal = 9 (fixed)
- STOCH (ID 2): ``period`` = fastk window; slowk = 3-bar SMA of fastk
- OBV  (ID 12): no period — cache key uses period=0 as sentinel
- BBANDS (ID 6): returns %B = (close - lower) / (upper - lower)

Cache key format: f"{indicator_id}_{period}"
  Example: RSI-14 → "0_14", OBV → "12_0"

``build_indicator_cache`` pre-computes and normalizes ALL indicators for ALL
valid periods in the registry before the GA loop starts.  This is the
performance-critical path: O(n_indicators × n_periods) upfront, then O(1)
per fitness evaluation.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from src.indicators.registry import INDICATOR_REGISTRY


# ---------------------------------------------------------------------------
# Individual indicator implementations (return raw float64 arrays, same
# length as input, NaN where warm-up data is insufficient).
# ---------------------------------------------------------------------------


def _rsi(close: np.ndarray, period: int) -> np.ndarray:
    """Wilder's RSI — bounded [0, 100]."""
    n = len(close)
    out = np.full(n, np.nan)
    if n <= period:
        return out

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    # Seed with simple average
    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])

    for i in range(period, n - 1):
        avg_gain = (avg_gain * (period - 1) + gain[i]) / period
        avg_loss = (avg_loss * (period - 1) + loss[i]) / period
        if avg_loss == 0.0:
            out[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i + 1] = 100.0 - 100.0 / (1.0 + rs)

    # Fill the first complete window
    if avg_loss == 0.0:
        out[period] = 100.0
    else:
        rs = np.mean(gain[:period]) / np.mean(loss[:period]) if np.mean(loss[:period]) != 0 else np.inf
        out[period] = 100.0 - 100.0 / (1.0 + rs) if not np.isinf(rs) else 100.0

    return out


def _cci(close: np.ndarray, high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
    """Commodity Channel Index."""
    n = len(close)
    out = np.full(n, np.nan)
    typical = (high + low + close) / 3.0

    for i in range(period - 1, n):
        window = typical[i - period + 1 : i + 1]
        mean_tp = np.mean(window)
        mean_dev = np.mean(np.abs(window - mean_tp))
        if mean_dev != 0.0:
            out[i] = (typical[i] - mean_tp) / (0.015 * mean_dev)

    return out


def _stoch_slowk(close: np.ndarray, high: np.ndarray, low: np.ndarray, fastk_period: int) -> np.ndarray:
    """Stochastic Oscillator — slowK = 3-bar SMA of fastK."""
    n = len(close)
    fastk = np.full(n, np.nan)

    for i in range(fastk_period - 1, n):
        h = np.max(high[i - fastk_period + 1 : i + 1])
        l = np.min(low[i - fastk_period + 1 : i + 1])
        if h != l:
            fastk[i] = 100.0 * (close[i] - l) / (h - l)

    # slowK = 3-bar SMA of fastK
    slowk = np.full(n, np.nan)
    for i in range(fastk_period + 1, n):
        window = fastk[i - 2 : i + 1]
        if not np.any(np.isnan(window)):
            slowk[i] = np.mean(window)

    return slowk


def _adx(close: np.ndarray, high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
    """Average Directional Index [0, 100]."""
    n = len(close)
    out = np.full(n, np.nan)
    if n < period * 2:
        return out

    # True Range
    tr = np.full(n, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))

    # Directional movement
    plus_dm = np.zeros(n)
    minus_dm = np.zeros(n)
    for i in range(1, n):
        up = high[i] - high[i - 1]
        down = low[i - 1] - low[i]
        plus_dm[i] = up if up > down and up > 0 else 0.0
        minus_dm[i] = down if down > up and down > 0 else 0.0

    # Smooth with Wilder's
    atr = np.full(n, np.nan)
    plus_di = np.full(n, np.nan)
    minus_di = np.full(n, np.nan)

    atr[period] = np.mean(tr[1 : period + 1])
    plus_di[period] = np.mean(plus_dm[1 : period + 1])
    minus_di[period] = np.mean(minus_dm[1 : period + 1])

    for i in range(period + 1, n):
        atr[i] = atr[i - 1] * (period - 1) / period + tr[i]
        plus_di[i] = plus_di[i - 1] * (period - 1) / period + plus_dm[i]
        minus_di[i] = minus_di[i - 1] * (period - 1) / period + minus_dm[i]

    # DI+/DI- as percentages, then DX
    dx = np.full(n, np.nan)
    for i in range(period, n):
        if atr[i] != 0.0:
            pdi = 100.0 * plus_di[i] / atr[i]
            mdi = 100.0 * minus_di[i] / atr[i]
            s = pdi + mdi
            if s != 0.0:
                dx[i] = 100.0 * abs(pdi - mdi) / s

    # ADX = Wilder's smoothing of DX
    first_valid = period * 2 - 1
    if first_valid >= n:
        return out
    out[first_valid] = np.nanmean(dx[period : first_valid + 1])
    for i in range(first_valid + 1, n):
        if not np.isnan(dx[i]):
            out[i] = (out[i - 1] * (period - 1) + dx[i]) / period

    return out


def _atr_normalized(close: np.ndarray, high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
    """ATR normalized by close price (ATR / close × 100)."""
    n = len(close)
    out = np.full(n, np.nan)
    if n < period + 1:
        return out

    tr = np.full(n, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))

    atr = np.full(n, np.nan)
    atr[period - 1] = np.mean(tr[:period])
    for i in range(period, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

    for i in range(period - 1, n):
        if close[i] != 0.0:
            out[i] = atr[i] / close[i] * 100.0

    return out


def _macd_line(close: np.ndarray, fast_period: int) -> np.ndarray:
    """MACD line = EMA(fast) - EMA(slow), where slow = fast + 14."""
    slow_period = fast_period + 14
    n = len(close)
    out = np.full(n, np.nan)
    if n < slow_period:
        return out

    series = pd.Series(close)
    ema_fast = series.ewm(span=fast_period, min_periods=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, min_periods=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    out[:] = macd.values
    return out


def _bbands_pctb(close: np.ndarray, period: int, num_std: float = 2.0) -> np.ndarray:
    """Bollinger Bands %B = (close - lower) / (upper - lower)."""
    n = len(close)
    out = np.full(n, np.nan)
    series = pd.Series(close)
    mid = series.rolling(window=period, min_periods=period).mean()
    std = series.rolling(window=period, min_periods=period).std(ddof=0)
    upper = mid + num_std * std
    lower = mid - num_std * std
    band_width = upper - lower
    # Only compute where band_width > 0
    mask = band_width > 0
    out[mask] = ((series[mask] - lower[mask]) / band_width[mask]).values
    return out


def _roc(close: np.ndarray, period: int) -> np.ndarray:
    """Rate of Change (%)."""
    n = len(close)
    out = np.full(n, np.nan)
    for i in range(period, n):
        if close[i - period] != 0.0:
            out[i] = (close[i] - close[i - period]) / close[i - period] * 100.0
    return out


def _willr(close: np.ndarray, high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
    """Williams %R — values in [-100, 0]."""
    n = len(close)
    out = np.full(n, np.nan)
    for i in range(period - 1, n):
        h = np.max(high[i - period + 1 : i + 1])
        l = np.min(low[i - period + 1 : i + 1])
        if h != l:
            out[i] = -100.0 * (h - close[i]) / (h - l)
    return out


def _momentum(close: np.ndarray, period: int) -> np.ndarray:
    """Momentum = close[t] - close[t - period]."""
    n = len(close)
    out = np.full(n, np.nan)
    out[period:] = close[period:] - close[:-period]
    return out


def _ema_spread(close: np.ndarray, period: int) -> np.ndarray:
    """EMA spread = close - EMA(period)."""
    series = pd.Series(close)
    ema = series.ewm(span=period, min_periods=period, adjust=False).mean()
    spread = series - ema
    out = spread.values.copy()
    out[ema.isna()] = np.nan
    return out


def _sma_spread(close: np.ndarray, period: int) -> np.ndarray:
    """SMA spread = close - SMA(period)."""
    series = pd.Series(close)
    sma = series.rolling(window=period, min_periods=period).mean()
    spread = series - sma
    out = spread.values.copy()
    out[sma.isna()] = np.nan
    return out


def _obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
    """On-Balance Volume."""
    n = len(close)
    out = np.zeros(n)
    for i in range(1, n):
        if close[i] > close[i - 1]:
            out[i] = out[i - 1] + volume[i]
        elif close[i] < close[i - 1]:
            out[i] = out[i - 1] - volume[i]
        else:
            out[i] = out[i - 1]
    return out


def _mfi(close: np.ndarray, high: np.ndarray, low: np.ndarray, volume: np.ndarray, period: int) -> np.ndarray:
    """Money Flow Index [0, 100]."""
    n = len(close)
    out = np.full(n, np.nan)
    typical = (high + low + close) / 3.0
    raw_mf = typical * volume

    for i in range(period, n):
        pos_mf = 0.0
        neg_mf = 0.0
        for j in range(i - period + 1, i + 1):
            if typical[j] > typical[j - 1]:
                pos_mf += raw_mf[j]
            elif typical[j] < typical[j - 1]:
                neg_mf += raw_mf[j]
        if neg_mf == 0.0:
            out[i] = 100.0
        else:
            mfr = pos_mf / neg_mf
            out[i] = 100.0 - 100.0 / (1.0 + mfr)

    return out


def _dmi_dx(close: np.ndarray, high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
    """Directional Movement Index — raw DX (without ADX smoothing), [0, 100]."""
    n = len(close)
    out = np.full(n, np.nan)
    if n < period + 1:
        return out

    tr = np.full(n, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))

    plus_dm = np.zeros(n)
    minus_dm = np.zeros(n)
    for i in range(1, n):
        up = high[i] - high[i - 1]
        down = low[i - 1] - low[i]
        plus_dm[i] = up if up > down and up > 0 else 0.0
        minus_dm[i] = down if down > up and down > 0 else 0.0

    # Wilder smoothing
    atr_s = np.full(n, np.nan)
    plus_s = np.full(n, np.nan)
    minus_s = np.full(n, np.nan)
    atr_s[period] = np.mean(tr[1 : period + 1])
    plus_s[period] = np.mean(plus_dm[1 : period + 1])
    minus_s[period] = np.mean(minus_dm[1 : period + 1])

    for i in range(period + 1, n):
        atr_s[i] = atr_s[i - 1] * (period - 1) / period + tr[i]
        plus_s[i] = plus_s[i - 1] * (period - 1) / period + plus_dm[i]
        minus_s[i] = minus_s[i - 1] * (period - 1) / period + minus_dm[i]

    for i in range(period, n):
        if atr_s[i] != 0.0:
            pdi = 100.0 * plus_s[i] / atr_s[i]
            mdi = 100.0 * minus_s[i] / atr_s[i]
            s = pdi + mdi
            if s != 0.0:
                out[i] = 100.0 * abs(pdi - mdi) / s

    return out


# ---------------------------------------------------------------------------
# Public dispatcher
# ---------------------------------------------------------------------------


def compute_raw_indicator(
    indicator_id: int,
    period: int,
    close: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    volume: np.ndarray,
) -> np.ndarray:
    """Compute a single raw indicator array.

    Args:
        indicator_id: Integer ID from INDICATOR_REGISTRY (0–14).
        period:       Period value (ignored for OBV, use 0).
        close:        1-D float64 close prices array.
        high:         1-D float64 high prices array.
        low:          1-D float64 low prices array.
        volume:       1-D float64 volume array.

    Returns:
        float64 ndarray of same length as ``close``, NaN during warm-up.

    Raises:
        ValueError: If indicator_id is not in INDICATOR_REGISTRY.
    """
    if indicator_id not in INDICATOR_REGISTRY:
        raise ValueError(f"Unknown indicator_id {indicator_id}. Valid: 0–14.")

    dispatch = {
        0:  lambda: _rsi(close, period),
        1:  lambda: _cci(close, high, low, period),
        2:  lambda: _stoch_slowk(close, high, low, period),
        3:  lambda: _adx(close, high, low, period),
        4:  lambda: _atr_normalized(close, high, low, period),
        5:  lambda: _macd_line(close, period),
        6:  lambda: _bbands_pctb(close, period),
        7:  lambda: _roc(close, period),
        8:  lambda: _willr(close, high, low, period),
        9:  lambda: _momentum(close, period),
        10: lambda: _ema_spread(close, period),
        11: lambda: _sma_spread(close, period),
        12: lambda: _obv(close, volume),
        13: lambda: _mfi(close, high, low, volume, period),
        14: lambda: _dmi_dx(close, high, low, period),
    }
    return dispatch[indicator_id]()


# ---------------------------------------------------------------------------
# Cache builder
# ---------------------------------------------------------------------------


def build_indicator_cache(
    data: pd.DataFrame,
    normalization_window: int = 252,
) -> Dict[str, np.ndarray]:
    """Pre-compute and normalize all indicators for all valid periods.

    Iterates over every indicator in INDICATOR_REGISTRY and every period
    in [spec.min_period, spec.max_period].  For OBV (min_period=max_period=0)
    only one entry is computed, keyed as "12_0".

    Each raw indicator array is normalized to [-100, 100] via a 252-bar
    rolling Highest-Lowest window (see normalizer.py).  Arrays are stored
    as float32 to reduce memory.

    Args:
        data:                OHLCV DataFrame with columns
                             [date, open, high, low, close, volume].
                             Must be sorted by date and free of NaNs.
        normalization_window: Rolling window for normalization. Default 252.

    Returns:
        dict mapping ``f"{indicator_id}_{period}"`` → float32 ndarray.
        Arrays have the same length as ``data`` (NaN during warm-up).
    """
    from src.data.normalizer import normalize_indicator  # avoid circular import at module load

    close = data["close"].values.astype(np.float64)
    high = data["high"].values.astype(np.float64)
    low = data["low"].values.astype(np.float64)
    volume = data["volume"].values.astype(np.float64)

    cache: Dict[str, np.ndarray] = {}

    for ind_id, spec in INDICATOR_REGISTRY.items():
        if spec.min_period == 0 and spec.max_period == 0:
            # OBV — no period
            raw = compute_raw_indicator(ind_id, 0, close, high, low, volume)
            series = pd.Series(raw)
            normalized = normalize_indicator(series, window=normalization_window)
            cache[f"{ind_id}_0"] = normalized.values.astype(np.float32)
        else:
            for period in range(spec.min_period, spec.max_period + 1):
                raw = compute_raw_indicator(ind_id, period, close, high, low, volume)
                series = pd.Series(raw)
                normalized = normalize_indicator(series, window=normalization_window)
                cache[f"{ind_id}_{period}"] = normalized.values.astype(np.float32)

    return cache
