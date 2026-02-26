"""
Backtesting engine module for GA Trading System POC

Implements VectorBT-based backtesting with performance targets:
- <50ms per fitness evaluation on daily data
- Vectorized execution for speed
"""

import pandas as pd
import numpy as np
import vectorbt as vbt
from typing import NamedTuple
from config import INITIAL_CASH, COMMISSION


class BacktestResult(NamedTuple):
    """Results from a backtest run"""
    equity_curve: np.ndarray
    total_return: float
    sharpe_ratio: float
    profit_factor: float
    n_trades: int
    win_rate: float
    max_drawdown: float


def run_backtest(
    signals: pd.Series,
    prices: pd.Series,
    stop_loss: float = 0.05,
    take_profit: float = 0.10,
    position_size: float = 0.10,
    initial_cash: float = INITIAL_CASH,
    commission: float = COMMISSION
) -> BacktestResult:
    """
    Run vectorized backtest using VectorBT.

    Args:
        signals: Trading signals (1=buy, -1=sell, 0=hold)
        prices: Price series for execution
        stop_loss: Stop loss percentage (e.g., 0.05 = 5%)
        take_profit: Take profit percentage (e.g., 0.10 = 10%)
        position_size: Position size as fraction of equity (e.g., 0.10 = 10%)
        initial_cash: Starting cash
        commission: Commission rate (e.g., 0.0005 = 0.05%)

    Returns:
        BacktestResult with performance metrics
    """
    # Convert signals to entries/exits
    # Entry when signal changes from 0 to 1 or -1
    # Exit when signal returns to 0 or reverses
    entries = (signals == 1) & (signals.shift(1) != 1)
    exits = (signals == 0) & (signals.shift(1) == 1)

    # Handle short positions (signal == -1)
    short_entries = (signals == -1) & (signals.shift(1) != -1)
    short_exits = (signals == 0) & (signals.shift(1) == -1)

    # For POC, we'll only do long positions to simplify
    # (Short positions would require different VectorBT setup)

    # Create portfolio
    pf = vbt.Portfolio.from_signals(
        close=prices,
        entries=entries,
        exits=exits,
        init_cash=initial_cash,
        size=position_size,  # Fraction of equity
        size_type='percent',
        fees=commission,
        freq='1D',  # Daily frequency
        sl_stop=stop_loss,  # Stop loss
        tp_stop=take_profit  # Take profit
    )

    # Extract metrics
    try:
        equity_curve = pf.value().values
        total_return = pf.total_return()
        sharpe = pf.sharpe_ratio()
        n_trades = pf.trades.count()

        # Profit factor calculation
        gross_profit = pf.trades.winning.pnl.sum() if pf.trades.winning.count() > 0 else 0
        gross_loss = abs(pf.trades.losing.pnl.sum()) if pf.trades.losing.count() > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Win rate
        win_rate = pf.trades.win_rate() if n_trades > 0 else 0

        # Max drawdown
        max_dd = pf.max_drawdown()

        return BacktestResult(
            equity_curve=equity_curve,
            total_return=total_return,
            sharpe_ratio=sharpe if not np.isnan(sharpe) else 0.0,
            profit_factor=profit_factor if not np.isnan(profit_factor) else 0.0,
            n_trades=n_trades,
            win_rate=win_rate if not np.isnan(win_rate) else 0.0,
            max_drawdown=max_dd if not np.isnan(max_dd) else 0.0
        )

    except Exception as e:
        # Return zeroed result if backtest fails
        print(f"Backtest failed: {e}")
        return BacktestResult(
            equity_curve=np.array([initial_cash] * len(prices)),
            total_return=0.0,
            sharpe_ratio=0.0,
            profit_factor=0.0,
            n_trades=0,
            win_rate=0.0,
            max_drawdown=0.0
        )


if __name__ == "__main__":
    # Test backtest engine
    from data_loader import load_market_data, train_test_split_timeseries
    from indicators import calculate_normalized_rsi, generate_signals

    print("Loading data...")
    data = load_market_data()
    train, test = train_test_split_timeseries(data)

    print("\nCalculating indicators...")
    train_rsi = calculate_normalized_rsi(train['Close'])
    test_rsi = calculate_normalized_rsi(test['Close'])

    print("\nGenerating signals...")
    train_signals = generate_signals(train_rsi, buy_threshold=-60, sell_threshold=60)
    test_signals = generate_signals(test_rsi, buy_threshold=-60, sell_threshold=60)

    print("\nRunning backtests...")
    train_result = run_backtest(
        train_signals,
        train['Close'],
        stop_loss=0.05,
        take_profit=0.10,
        position_size=0.10
    )

    test_result = run_backtest(
        test_signals,
        test['Close'],
        stop_loss=0.05,
        take_profit=0.10,
        position_size=0.10
    )

    print("\n--- Train Results ---")
    print(f"Total Return: {train_result.total_return:.2%}")
    print(f"Sharpe Ratio: {train_result.sharpe_ratio:.3f}")
    print(f"Profit Factor: {train_result.profit_factor:.3f}")
    print(f"Number of Trades: {train_result.n_trades}")
    print(f"Win Rate: {train_result.win_rate:.2%}")
    print(f"Max Drawdown: {train_result.max_drawdown:.2%}")

    print("\n--- Test Results ---")
    print(f"Total Return: {test_result.total_return:.2%}")
    print(f"Sharpe Ratio: {test_result.sharpe_ratio:.3f}")
    print(f"Profit Factor: {test_result.profit_factor:.3f}")
    print(f"Number of Trades: {test_result.n_trades}")
    print(f"Win Rate: {test_result.win_rate:.2%}")
    print(f"Max Drawdown: {test_result.max_drawdown:.2%}")
