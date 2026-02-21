"""
Fitness function module for GA Trading System POC

Implements the fitness function from the implementation plan:
fitness = NetProfit × AvgTrade

With penalties for:
- Pearson correlation < 0.85
- Profit factor < 1.2
- Number of trades < 30
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from typing import Tuple
from backtest import run_backtest, BacktestResult
from indicators import calculate_normalized_rsi, generate_signals
from data_loader import train_test_split_timeseries
from config import MIN_PEARSON, MIN_PROFIT_FACTOR, MIN_TRADES, TRAIN_FRACTION


def calculate_pearson(equity1: np.ndarray, equity2: np.ndarray) -> float:
    """
    Calculate Pearson correlation between two equity curves.

    Both curves are normalized to percentage returns from initial value
    to ensure correlation measures strategy consistency, not absolute scale.

    Args:
        equity1: First equity curve
        equity2: Second equity curve

    Returns:
        Pearson correlation coefficient (0 if calculation fails)
    """
    try:
        # Normalize to percentage returns
        if len(equity1) > 0 and equity1[0] != 0:
            norm1 = (equity1 / equity1[0] - 1) * 100
        else:
            return 0.0

        if len(equity2) > 0 and equity2[0] != 0:
            norm2 = (equity2 / equity2[0] - 1) * 100
        else:
            return 0.0

        # Handle length mismatch (shouldn't happen but be defensive)
        min_len = min(len(norm1), len(norm2))
        if min_len < 10:  # Need at least 10 points for meaningful correlation
            return 0.0

        # Calculate Pearson correlation
        correlation, _ = pearsonr(norm1[:min_len], norm2[:min_len])

        return correlation if not np.isnan(correlation) else 0.0

    except Exception as e:
        print(f"Pearson calculation failed: {e}")
        return 0.0


def evaluate_individual(
    individual: list,
    data: pd.DataFrame
) -> Tuple[float]:
    """
    Evaluate fitness of a GA individual (strategy parameters).

    Individual genome structure:
    [rsi_buy, rsi_sell, stop_loss, take_profit, position_size]

    Fitness formula: NetProfit × AvgTrade (on test set)
    With soft penalties for constraint violations.

    Args:
        individual: List of strategy parameters
        data: Full dataset (will be split into train/test)

    Returns:
        Tuple containing single fitness value (required by DEAP)
    """
    try:
        # Unpack individual
        rsi_buy, rsi_sell, stop_loss, take_profit, position_size = individual

        # Validate basic constraints
        if rsi_buy >= rsi_sell:  # Buy threshold must be below sell
            return (0.0,)
        if stop_loss >= take_profit:  # SL must be tighter than TP
            return (0.0,)

        # Split data
        train, test = train_test_split_timeseries(data, TRAIN_FRACTION)

        # Calculate indicators
        train_rsi = calculate_normalized_rsi(train['Close'])
        test_rsi = calculate_normalized_rsi(test['Close'])

        # Generate signals
        train_signals = generate_signals(train_rsi, rsi_buy, rsi_sell)
        test_signals = generate_signals(test_rsi, rsi_buy, rsi_sell)

        # Run backtests
        train_result = run_backtest(
            train_signals,
            train['Close'],
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size
        )

        test_result = run_backtest(
            test_signals,
            test['Close'],
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size
        )

        # Calculate Pearson correlation
        pearson = calculate_pearson(train_result.equity_curve, test_result.equity_curve)

        # Calculate fitness components (using test results)
        if test_result.n_trades > 0:
            net_profit_approx = test_result.sharpe_ratio * np.sqrt(test_result.n_trades)
            avg_trade_approx = test_result.sharpe_ratio / np.sqrt(test_result.n_trades)
            fitness = net_profit_approx * avg_trade_approx
        else:
            fitness = 0.0

        # Apply penalties (soft constraints)
        if pearson < MIN_PEARSON:
            fitness -= (MIN_PEARSON - pearson) * 10

        if train_result.profit_factor < MIN_PROFIT_FACTOR:
            fitness -= (MIN_PROFIT_FACTOR - train_result.profit_factor) * 5

        if test_result.profit_factor < MIN_PROFIT_FACTOR:
            fitness -= (MIN_PROFIT_FACTOR - test_result.profit_factor) * 5

        if test_result.n_trades < MIN_TRADES:
            fitness -= (MIN_TRADES - test_result.n_trades) * 0.1

        # Ensure non-negative
        fitness = max(0.0, fitness)

        return (fitness,)

    except Exception as e:
        print(f"Fitness evaluation failed: {e}")
        return (0.0,)


if __name__ == "__main__":
    # Test fitness function
    from data_loader import load_market_data

    print("Loading data...")
    data = load_market_data()

    # Test individual: [rsi_buy, rsi_sell, stop_loss, take_profit, position_size]
    test_individual = [-60, 60, 0.05, 0.10, 0.10]

    print(f"\nEvaluating test individual: {test_individual}")
    fitness = evaluate_individual(test_individual, data)
    print(f"Fitness: {fitness[0]:.6f}")

    # Test a few more individuals
    test_cases = [
        [-70, 70, 0.03, 0.15, 0.15],  # More aggressive
        [-50, 50, 0.07, 0.08, 0.05],  # More conservative
        [-80, 80, 0.02, 0.20, 0.20],  # Very aggressive
    ]

    print("\n--- Additional Test Cases ---")
    for i, ind in enumerate(test_cases, 1):
        fitness = evaluate_individual(ind, data)
        print(f"Case {i} {ind}: Fitness = {fitness[0]:.6f}")
