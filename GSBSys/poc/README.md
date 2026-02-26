# GA Trading System - Proof of Concept

This POC validates the core assumptions before committing to the full 32-week MVP implementation.

## Objectives

Validate that:

1. **VectorBT Speed**: Backtesting achieves <50ms per fitness evaluation on daily data
2. **DEAP Integration**: Genetic algorithm framework integrates correctly with fitness function
3. **Fitness Function**: NetProfit × AvgTrade produces sensible optimization behavior
4. **Convergence**: Single-indicator optimization converges within 1000 generations

## Structure

```
poc/
├── config.py              # Configuration constants
├── data_loader.py         # yfinance data loading (SPY 2010-2025)
├── indicators.py          # RSI calculation and normalization
├── backtest.py           # VectorBT backtesting wrapper
├── fitness.py            # Fitness function with Pearson penalty
├── ga_engine.py          # DEAP GA setup and evolution
├── main_poc.py           # Main POC runner with benchmarks
├── requirements.txt      # Minimal dependencies
└── README.md            # This file
```

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: TA-Lib requires manual installation on some systems. See [TA-Lib installation guide](https://github.com/mrjbq7/ta-lib#installation).

## Usage

### Run Full POC

```bash
python main_poc.py
```

This will:
1. Load SPY data (2010-2025)
2. Benchmark fitness function performance
3. Run 1000-generation GA evolution
4. Report pass/fail on all validation criteria

### Test Individual Modules

Each module can be tested independently:

```bash
python data_loader.py    # Test data loading
python indicators.py     # Test RSI calculation
python backtest.py      # Test VectorBT backtesting
python fitness.py       # Test fitness function
python ga_engine.py     # Test DEAP GA (dummy fitness)
```

## Expected Results

### Performance Benchmark
- **Target**: <50ms per fitness evaluation
- **Test**: 100 random individuals evaluated
- **Pass Criteria**: Average time < 50ms

### Convergence Test
- **Population**: 100 individuals
- **Generations**: 1000
- **Pass Criteria**: Max fitness improves from generation 0 to 1000

### Individual Genome

Each individual encodes 5 parameters:
```python
[rsi_buy, rsi_sell, stop_loss, take_profit, position_size]
```

- `rsi_buy`: RSI threshold for buy signal (-100 to 100)
- `rsi_sell`: RSI threshold for sell signal (-100 to 100)
- `stop_loss`: Stop loss percentage (1% to 20%)
- `take_profit`: Take profit percentage (1% to 50%)
- `position_size`: Position size as fraction of equity (1% to 20%)

### Fitness Function

```
fitness = NetProfit × AvgTrade

With penalties:
- Pearson correlation < 0.85
- Profit factor < 1.2
- Number of trades < 30
```

Where:
- `NetProfit ≈ Sharpe × sqrt(N_trades)`
- `AvgTrade ≈ Sharpe / sqrt(N_trades)`

## Decision Criteria

**PASS** → Proceed with full 32-week MVP implementation

**FAIL** → Investigate failures:
- If speed fails: Optimize VectorBT usage or reduce data size
- If convergence fails: Adjust fitness function or GA parameters

## Next Steps

If POC passes:
1. Review implementation plan
2. Setup full project structure
3. Begin Phase 1: Core GA Engine (Week 1-12)

If POC fails:
1. Document failure modes
2. Propose alternatives (different backtest engine, modified fitness)
3. Decide whether to pivot or refine approach
