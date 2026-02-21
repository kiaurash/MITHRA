"""
Configuration constants for GA Trading System POC

This module contains all configuration parameters for the proof-of-concept
validation of core assumptions: VectorBT speed, DEAP integration, and fitness function.
"""

# Data Configuration
TICKER = "SPY"
START_DATE = "2010-01-01"
END_DATE = "2025-12-31"
DATA_SOURCE = "yfinance"

# Indicator Configuration
RSI_PERIOD = 14
NORMALIZATION_WINDOW = 252  # Trading days in a year

# GA Configuration
POPULATION_SIZE = 100
GENERATIONS = 1000
CXPB = 0.7  # Crossover probability
MUTPB = 0.2  # Mutation probability
INDPB = 0.2  # Individual gene mutation probability

# Individual Genome Structure
# [rsi_threshold_buy, rsi_threshold_sell, stop_loss_pct, take_profit_pct, position_size_pct]
GENE_BOUNDS = {
    'rsi_buy': (-100, 100),      # Normalized RSI buy threshold
    'rsi_sell': (-100, 100),     # Normalized RSI sell threshold
    'stop_loss': (0.01, 0.20),   # 1-20% stop loss
    'take_profit': (0.01, 0.50), # 1-50% take profit
    'position_size': (0.01, 0.20) # 1-20% position size
}

# Backtest Configuration
TRAIN_FRACTION = 0.4  # 40% train, 60% test (as per implementation plan)
INITIAL_CASH = 10000
COMMISSION = 0.0005  # 0.05% slippage for stocks

# Fitness Function Configuration
MIN_PEARSON = 0.85      # Minimum train-test equity correlation
MIN_PROFIT_FACTOR = 1.2 # Minimum profit factor for both train and test
MIN_TRADES = 30         # Minimum number of trades

# Performance Targets (from implementation plan)
TARGET_FITNESS_TIME_MS = 50  # <50ms per fitness evaluation for daily data
