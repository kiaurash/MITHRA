"""
GA Trading System - Proof of Concept

This package validates core assumptions for the GA Trading System:
1. VectorBT backtesting speed (<50ms per fitness evaluation)
2. DEAP genetic algorithm integration
3. Fitness function correctness (NetProfit × AvgTrade)
4. Convergence within 1000 generations

To run the POC:
    python main_poc.py

Individual modules can be tested:
    python data_loader.py
    python indicators.py
    python backtest.py
    python fitness.py
    python ga_engine.py
"""

__version__ = "0.1.0"
__author__ = "AI Product Development"

from . import config
from . import data_loader
from . import indicators
from . import backtest
from . import fitness
from . import ga_engine

__all__ = [
    "config",
    "data_loader",
    "indicators",
    "backtest",
    "fitness",
    "ga_engine"
]
