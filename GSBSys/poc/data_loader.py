"""
Data loading module for GA Trading System POC

Loads historical OHLCV data from yfinance with proper error handling
and data validation as specified in the implementation plan.
"""

import pandas as pd
import yfinance as yf
from typing import Optional
from config import TICKER, START_DATE, END_DATE, DATA_SOURCE


def load_market_data(
    ticker: str = TICKER,
    source: str = DATA_SOURCE,
    start: str = START_DATE,
    end: str = END_DATE
) -> pd.DataFrame:
    """
    Load historical market data from specified source.

    Args:
        ticker: Stock ticker symbol (default: SPY)
        source: Data source (default: yfinance)
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format

    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume

    Raises:
        ValueError: If data loading fails or data is invalid
    """
    if source == "yfinance":
        try:
            # Download data from yfinance
            df = yf.download(ticker, start=start, end=end, progress=False)

            # Handle MultiIndex columns (yfinance sometimes returns these)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

            # Reset index to make Date a column
            df = df.reset_index()

            # Ensure we have the required columns
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

            # Rename columns if needed (yfinance uses capitalized names)
            column_mapping = {
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }

            df.columns = [column_mapping.get(c.lower(), c) for c in df.columns]

            # Select only required columns
            df = df[required_cols]

            # Validate data
            if len(df) < 500:  # Need at least ~2 years for 252-day normalization
                raise ValueError(f"Insufficient data: only {len(df)} rows retrieved")

            if df[['Open', 'High', 'Low', 'Close', 'Volume']].isnull().any().any():
                raise ValueError("Data contains NaN values")

            if (df['High'] < df['Low']).any():
                raise ValueError("Data integrity error: High < Low detected")

            print(f"Loaded {len(df)} rows of data for {ticker} from {start} to {end}")
            return df

        except Exception as e:
            raise ValueError(f"Failed to load data from {source}: {str(e)}")

    else:
        raise ValueError(f"Unsupported data source: {source}")


def train_test_split_timeseries(
    data: pd.DataFrame,
    train_frac: float = 0.4
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split time series data into train and test sets sequentially.

    Args:
        data: Input DataFrame with time series data
        train_frac: Fraction of data to use for training (default: 0.4)

    Returns:
        Tuple of (train_df, test_df)
    """
    split_idx = int(len(data) * train_frac)

    train = data.iloc[:split_idx].copy()
    test = data.iloc[split_idx:].copy()

    print(f"Train: {len(train)} rows ({train['Date'].iloc[0]} to {train['Date'].iloc[-1]})")
    print(f"Test:  {len(test)} rows ({test['Date'].iloc[0]} to {test['Date'].iloc[-1]})")

    return train, test


if __name__ == "__main__":
    # Test the data loader
    data = load_market_data()
    print(f"\nData shape: {data.shape}")
    print(f"\nFirst few rows:\n{data.head()}")
    print(f"\nLast few rows:\n{data.tail()}")
    print(f"\nData types:\n{data.dtypes}")

    # Test train-test split
    print("\n--- Train-Test Split ---")
    train, test = train_test_split_timeseries(data)
