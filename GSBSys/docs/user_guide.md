# GA Trading System — User Guide

## Overview

GA-Trading-Sys uses a genetic algorithm to optimise a multi-indicator trading strategy on historical OHLCV data. The optimiser searches a 13-gene chromosome space and produces a validated, backtested strategy.

---

## 1. Install

```bash
pip install -e .
```

Dependencies: `pydantic`, `click`, `numpy`, `pandas`, `yfinance`, `numba`, `deap`, `scipy`, `matplotlib`, `pyyaml`.

---

## 2. Configure

Write a config template:

```bash
ga-trading-sys init --output config.yaml
```

Edit `config.yaml`:

```yaml
data:
  ticker: SPY
  start_date: "2010-01-01"
  end_date: "2024-12-31"
  cache_dir: data/cache

ga:
  population_size: 200    # individuals per generation
  n_generations: 1000     # GA generations per restart
  n_restarts: 10          # independent restarts

backtest:
  warmup_bars: 252        # bars discarded for indicator warm-up
  train_fraction: 0.40    # 40% train / 60% test

output:
  dir: results
  save_code: true
  save_plots: true
  save_reports: true
```

---

## 3. Optimise

```bash
ga-trading-sys optimize --config config.yaml --output results/
```

The command validates the config and displays run parameters. Full GA optimisation requires the GA runner from Phase 1–2.

---

## 4. Validate Results

After optimisation, inspect saved results:

```bash
ga-trading-sys validate --results results/
```

To validate a specific individual:

```bash
ga-trading-sys validate --results results/ --individual results/individual.yaml
```

---

## 5. Replay a Strategy

Re-run a saved individual and print a performance report:

```bash
ga-trading-sys backtest --individual results/individual.yaml
ga-trading-sys backtest --individual results/individual.yaml --config config.yaml
```

Output:

```
====================================
  Strategy Performance Report
====================================
  Profit Factor            1.5200
  Total P&L           $1,200.00
  Trades                       42
  Avg Trade P&L           $28.57
  Sharpe Ratio             1.2400
  Max Drawdown              8.35%
  Win Rate                  61.9%
  Expectancy              $28.57
====================================
```

---

## 6. Python API

```python
from src.config import load_config
from src.export.codegen import export_strategy_yaml, load_strategy_yaml
from src.export.reporter import build_report, format_text, save_csv
from src.export.visualizer import plot_equity_curves

# Load config
cfg = load_config("config.yaml")

# Save / load an individual
export_strategy_yaml(individual, "results/individual.yaml")
individual = load_strategy_yaml("results/individual.yaml")

# Performance report
report = build_report(backtest_result)
print(format_text(report))
save_csv(report, "results/report.csv")

# Visualise
plot_equity_curves(train_equity, test_equity, save_path="results/equity.png")
```

---

## 7. Chromosome Format

The 13-gene chromosome encodes a 3-slot multi-indicator strategy:

| Index | Gene              | Type  | Range       |
|-------|-------------------|-------|-------------|
| 0     | ind1_type         | int   | 0–14        |
| 1     | ind1_period       | int   | 5–100       |
| 2     | ind1_weight       | float | -1.0–2.0    |
| 3     | ind2_type         | int   | 0–14        |
| 4     | ind2_period       | int   | 5–100       |
| 5     | ind2_weight       | float | -1.0–2.0    |
| 6     | ind3_type         | int   | 0–14        |
| 7     | ind3_period       | int   | 5–100       |
| 8     | ind3_weight       | float | -1.0–2.0    |
| 9     | entry_threshold   | float | 0.0–50.0    |
| 10    | stop_loss_pct     | float | 0.01–0.20   |
| 11    | take_profit_pct   | float | 0.01–0.50   |
| 12    | position_size_mult| float | 0.5–2.0     |

---

## 8. Project Structure

```
src/
├── config.py           # Pydantic v2 config schema
├── backtesting/        # Backtest engine (NumbaBacktestEngine)
├── ga/                 # Chromosome, fitness, operators, evolution
├── indicators/         # 15 indicators + signal generator
├── validation/         # Pearson, OOS, noise, family grouping
├── robustness/         # Walk-forward, sensitivity, regime testing
├── export/             # Code generation, reports, visualisation
└── cli/                # Click CLI commands
```
