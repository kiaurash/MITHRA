"""
Technical indicators module for GA Trading System POC

Implements RSI calculation and 252-day normalization as specified
in the implementation plan. Uses TA-Lib for indicator calculations.
"""

import pandas as pd
import numpy as np
import talib
from config import RSI_PERIOD, NORMALIZATION_WINDOW


def calculate_rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """
    Calculate Relative Strength Index using TA-Lib.

    Args:
        close: Series of closing prices
        period: RSI period (default: 14)

    Returns:
        Series of RSI values (0-100 range, with NaN for first `period` values)
    """
    rsi = talib.RSI(close.values, timeperiod=period)
    return pd.Series(rsi, index=close.index)


def normalize_indicator(
    indicator: pd.Series,
    window: int = NORMALIZATION_WINDOW
) -> pd.Series:
    """
    Normalize indicator to [-100, 100] range using rolling window.

    CRITICAL: Returns NaN for first (window-1) observations.
    Do NOT fillna(0) as this introduces look-ahead bias.

    Formula: 200 * (value - rolling_min) / (rolling_max - rolling_min + epsilon) - 100

    Args:
        indicator: Raw indicator values
        window: Normalization window in days (default: 252 trading days = 1 year)

    Returns:
        Normalized indicator in [-100, 100] range
    """
    rolling_high = indicator.rolling(window, min_periods=window).max()
    rolling_low = indicator.rolling(window, min_periods=window).min()

    # Avoid division by zero with small epsilon
    normalized = 200 * (indicator - rolling_low) / (rolling_high - rolling_low + 1e-10) - 100

    return normalized


def calculate_normalized_rsi(
    close: pd.Series,
    rsi_period: int = RSI_PERIOD,
    norm_window: int = NORMALIZATION_WINDOW
) -> pd.Series:
    """
    Calculate RSI and normalize it in one step.

    Args:
        close: Series of closing prices
        rsi_period: RSI calculation period
        norm_window: Normalization window

    Returns:
        Normalized RSI values in [-100, 100] range
    """
    # Calculate raw RSI
    rsi = calculate_rsi(close, rsi_period)

    # Normalize RSI
    normalized_rsi = normalize_indicator(rsi, norm_window)

    return normalized_rsi


def generate_signals(
    normalized_rsi: pd.Series,
    buy_threshold: float,
    sell_threshold: float
) -> pd.Series:
    """
    Generate trading signals based on normalized RSI thresholds.

    Signal logic:
    - Buy (1) when normalized_rsi crosses below buy_threshold
    - Sell (-1) when normalized_rsi crosses above sell_threshold
    - Hold (0) otherwise

    Args:
        normalized_rsi: Normalized RSI values in [-100, 100] range
        buy_threshold: Threshold for buy signal (typically negative)
        sell_threshold: Threshold for sell signal (typically positive)

    Returns:
        Series of signals: 1 (buy), -1 (sell), 0 (hold)
    """
    signals = pd.Series(0, index=normalized_rsi.index)

    # Buy when RSI crosses below threshold (oversold)
    signals[normalized_rsi < buy_threshold] = 1

    # Sell when RSI crosses above threshold (overbought)
    signals[normalized_rsi > sell_threshold] = -1

    return signals


if __name__ == "__main__":
    # Test indicators with sample data
    from data_loader import load_market_data

    data = load_market_data()

    # Calculate normalized RSI
    print("Calculating normalized RSI...")
    norm_rsi = calculate_normalized_rsi(data['Close'])

    print(f"\nNormalized RSI shape: {norm_rsi.shape}")
    print(f"First valid index: {norm_rsi.first_valid_index()}")
    print(f"NaN count: {norm_rsi.isna().sum()}")
    print(f"\nNormalized RSI statistics:\n{norm_rsi.describe()}")

    # Generate sample signals
    print("\n--- Generating Signals ---")
    signals = generate_signals(norm_rsi, buy_threshold=-50, sell_threshold=50)
    print(f"Buy signals: {(signals == 1).sum()}")
    print(f"Sell signals: {(signals == -1).sum()}")
    print(f"Hold signals: {(signals == 0).sum()}")
