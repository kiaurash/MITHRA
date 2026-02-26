"""Indicator registry — 15 standard indicators for GA-Trading-Sys Phase 1.

Each indicator has:
- A unique integer ID (0–14) used as the gene value in the chromosome
- A period range [min_period, max_period] that bounds the ``period`` gene
- Notes on multi-output handling (STOCH, MACD, BBANDS)

Period encoding for special indicators:
- MACD (ID 5): ``period`` = fast EMA span; slow = period + 14; signal = 9 (fixed)
- STOCH (ID 2): ``period`` = fastk window; slowk = 3-bar SMA of fastk (fixed)
- OBV  (ID 12): no period — cache key uses period=0 as sentinel
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorSpec:
    """Metadata for one indicator."""

    id: int
    name: str
    min_period: int
    max_period: int
    description: str = ""


#: Registry of all 15 Phase 1 indicators.
#: Key = indicator ID (matches gene value in chromosome).
INDICATOR_REGISTRY: dict[int, IndicatorSpec] = {
    0:  IndicatorSpec(0,  "RSI",    5,   50,  "Relative Strength Index (Wilder)"),
    1:  IndicatorSpec(1,  "CCI",    10,  100, "Commodity Channel Index"),
    2:  IndicatorSpec(2,  "STOCH",  5,   50,  "Stochastic Oscillator (slowk)"),
    3:  IndicatorSpec(3,  "ADX",    10,  30,  "Average Directional Index"),
    4:  IndicatorSpec(4,  "ATR",    10,  50,  "Average True Range (normalised)"),
    5:  IndicatorSpec(5,  "MACD",   8,   20,  "MACD line (fast period; slow=fast+14)"),
    6:  IndicatorSpec(6,  "BBANDS", 10,  30,  "Bollinger Bands %B"),
    7:  IndicatorSpec(7,  "ROC",    5,   50,  "Rate of Change (%)"),
    8:  IndicatorSpec(8,  "WILLR",  10,  30,  "Williams %R"),
    9:  IndicatorSpec(9,  "MOM",    5,   50,  "Momentum (price difference)"),
    10: IndicatorSpec(10, "EMA",    10,  100, "EMA spread (close - EMA)"),
    11: IndicatorSpec(11, "SMA",    10,  100, "SMA spread (close - SMA)"),
    12: IndicatorSpec(12, "OBV",    0,   0,   "On-Balance Volume (no period; use 0)"),
    13: IndicatorSpec(13, "MFI",    10,  50,  "Money Flow Index"),
    14: IndicatorSpec(14, "DMI",    10,  30,  "Directional Movement Index (DX)"),
}

#: Total number of indicators.
N_INDICATORS: int = len(INDICATOR_REGISTRY)
