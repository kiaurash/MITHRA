# GSBsys Technical Specifications

Complete reference for all parameters, settings, and configuration values.

---

## Genetic Algorithm Parameters

### Core GA Settings

| Parameter | Value | Source |
|-----------|-------|--------|
| **Population Size** | 200 | Screenshot 3, Website |
| **Generations** | 1,000 | Screenshot 3, Website |
| **Restarts** | 10 (default, adjustable) | Website |
| **Crossover Rate** | 95% | Screenshot 3 |
| **Mutation Rate** | 5% | Screenshot 3 |
| **Mutation Strength** | 25% | Screenshot 3 |
| **Random Seed** | Blank (random) or user-defined | Website |
| **Max Crossover Attempts** | User-configurable | Website |
| **Early-Stop Reset %** | User-configurable | Website |

### Derived Metrics

```
Total Evaluations per Restart:
  Generations × Population = 1,000 × 200 = 200,000

Total Evaluations (Max):
  200,000 × 10 restarts = 2,000,000

Total Combinations Tested:
  1000 × 200 × 10 = 20,000,000
```

---

## Walk-Forward GA Parameters

| Indicator Count | WF Generations | WF Population | Total WF Tests |
|----------------|----------------|---------------|----------------|
| 3 indicators | 120 | 120 | 14,400 |
| 4-5 indicators | 150 | 150 | 22,500 |
| With Adaptive MA | 150+ | 150+ | 22,500+ |
| Minimum (fast) | 100 | 100 | 10,000 |

**Formula:** `WF Tests = WF Generations × WF Population`

**Guidance:** "Genetic will work better than random space"

---

## Data Split Configuration

### Development Phase

| Parameter | Development | Production | Source |
|-----------|------------|-----------|--------|
| **Training %** | 100 | 40 | Screenshot 2 |
| **Test %** | 0 | 60 | Screenshot 2 |
| **Test @ Beginning** | False | False | Screenshot 2 |
| **Validation %** | 0 | Variable | Screenshot 2 |

**Recommended:** "A Training % between 30% and 50% is recommended"

**Default Production:** 40% training, 60% out-of-sample

---

## Fitness Function Components

### Primary Metric

```
Fitness = NetProfit × AverageTrade
```

### Hard Floor Filters

| Metric | Training/Test | Validation | Reject if Below |
|--------|--------------|------------|-----------------|
| **Pearson Correlation** | ≥ 0.95 | - | < 0.95 |
| **Profit Factor** | ≥ 1.2 | ≥ 1.8 | Below threshold |
| **Net Profit** | > 0 | > 0 | ≤ 0 |

### Selection Thresholds (from 50k System Test)

- **Top by F-F metric:** 250 systems
- **Astab Course:** 90 systems
- **VSS Filter:** 91 systems
- **NP/DD Ratio:** 25-20 range

**Anchored Stability:** Systems with **Astab ≥ 40** show improved OOS results

---

## Indicator Configuration

### Indicator Pool

| Category | Count | Examples |
|----------|-------|----------|
| **Built-In Indicators** | 37 | TrueRange, GSB_SS_Stochastic, ADX, CCI |
| **Custom Indicators** | 0 (SF: 0) | User can add via API |
| **Secondary Filters** | ~5 | CloseLessPrevCloseD, GeneticAlgorithm |

### Indicator Selection

| Parameter | Value | Range |
|-----------|-------|-------|
| **# of Indicators** | 3 (typical) | 2-5 |
| **Indicator Weights** | Genetically optimized | -1 to +2 |
| **Normalization Length** | 100 bars | Fixed |
| **Normalization Range** | -100 to +100 | Fixed |

---

## Normalization Settings

| Setting | Value | Status |
|---------|-------|--------|
| **Normalization Modes** | 2 of 2 enabled | Active |
| **Mode 1** | HighestLowest | Confirmed |
| **Mode 2** | Unknown | Enabled but not specified |
| **Normalization Length** | 100 | Fixed |

---

## Entry/Exit Parameters

### Entry Settings

| Parameter | Type | Typical Value | Range |
|-----------|------|---------------|-------|
| **EntryLevel** | Continuous | 450-500 | GA optimized |
| **Secondary Filter** | Discrete | GeneticAlgorithm | Fixed rule or GA |
| **Entry Modes** | Discrete | 3 of 3 enabled | Compare1 + 2 others |

### Stop Loss Configuration

| Type | Description | Status | Performance Notes |
|------|-------------|--------|-------------------|
| **Fixed Stop** | User-defined currency value | Available | Manual override option |
| **Trailing Stop** | Fixed-amount trailing | Available | For overnight systems |
| **ATR Trailing** | ATR-based trailing | Available | For overnight systems |
| **Plock Break Even** | Move to BE after profit target hit | Available | "Very worth while using" |
| **Plock Variable** | Lock in fixed profit after target | Available | "Significantly worse OOS results" |
| **StaticStop** | Genetically chosen from range | Default | Most common |

**Stop Loss Count:** 0 to 3 stops can be active simultaneously

**Units:** Currency (e.g., $800), **excluding** commissions and slippage

### Profit Target

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Max. Profit Target** | $2,000 (example) | Genetically chosen within range |
| **Units** | Currency | Excluding commissions/slippage |
| **Purpose** | Prevent curve fitting | "Reduce high gains in 2008" |

### Exit Modes

| Mode | Count | Enabled |
|------|-------|---------|
| **Total Exit Modes** | 8 | 0 enabled (disabled) |
| **Market On Day Close** | Boolean | True (for day-trading) |

---

## Trading Parameters

### Position Sizing

| Parameter | Value | Application |
|-----------|-------|-------------|
| **CapitalInvestment** | $10,000 (example) | Preferred for stocks |
| **Fixed Shares** | Alternative | Less common |

### Transaction Costs

| Cost Type | Default Value | Notes |
|-----------|---------------|-------|
| **Commission** | $13.50 per side | User-configurable |
| **Slippage** | Not pre-set | Embedded in backtest |
| **Market Impact** | Not pre-set | Not modeled separately |

### Trading Direction

| Direction | Default | Configurable |
|-----------|---------|--------------|
| **Long** | Enabled | True |
| **Short** | Enabled | True |

---

## Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 16 GB | 32+ GB for large builds |
| **CPU** | Not specified | Multi-core for parallel GA |
| **Storage** | Not specified | SSD for fast data access |
| **Network** | Optional | For cloud worker submission |

**Cloud Workers:**
- Prevents local RAM exhaustion
- Required for population sizes > 200
- Submission queue management

---

## Data Requirements

### Session Settings (Updated July 2022)

| Setting | ES/NQ | Notes |
|---------|-------|-------|
| **Contract Symbols** | @ES, @NQ | NOT @ES.D, @NQ.D |
| **Market Start Time** | 8:00 AM | Exchange time |
| **Earliest Trade Time** | 9:00 AM | Avoid illiquid hours |
| **Timeframe** | 30-minute bars | Typical for intraday |

### Historical Data

**In-Sample Period:**
- Start: 2007-01-01 (or earlier)
- End: 2017-02-28

**Out-of-Sample Periods:**
- Statistics B: 2017-03-01 to 2018-02-28
- Statistics C: 2018-03-01 to 2019-02-28
- Statistics D: 2019-03-01 to 2020-02-28
- Statistics E: 2020-03-01 to 2021-02-28
- Statistics F: 2021-03-01 onwards

**Validation Windows (Proving Methodology Test):**
- Pre-20150630 (training)
- 20150630-20180228 (OOS1)
- 20180229-20190301 (OOS2)

---

## Optimizer Settings

### Optimizer Type

| Type | Status | Usage |
|------|--------|-------|
| **GeneticAlgorithm** | Active | "We only use GeneticAlgorithm" |
| **ExhaustiveSearch** | Available | Not recommended |

### Parallel Processing

| Setting | Value | Source |
|---------|-------|--------|
| **Is Parallel** | True | Screenshot 2 |
| **Periods Mode** | Percent | Screenshot 2 |

---

## Operators Configuration

| Operator | Status | Purpose |
|----------|--------|---------|
| **Add** | Disabled | Alternative combination method |
| **Multiply** | Enabled | Primary signal combination |
| **Compare1** | Enabled | Entry logic comparison |

**Active Operators:** 1 of 3

---

## Export Settings

### Platform Support

| Platform | Export Format | Status |
|----------|---------------|--------|
| **TradeStation** | EasyLanguage | Supported |
| **MultiCharts** | EasyLanguage compatible | Supported |
| **NinjaTrader** | C# code | Supported |

### Export Configuration

- Use tick-based volume settings
- Align to exchange time (not broker time)
- Verify data alignment before live deployment

---

## Performance Thresholds

### System Selection Criteria

| Metric | Minimum | Ideal | Reject Below |
|--------|---------|-------|--------------|
| **Profit Factor (Train)** | 1.2 | 1.5+ | < 1.2 |
| **Profit Factor (Valid)** | 1.8 | 2.0+ | < 1.8 |
| **Pearson R (Train/Test)** | 0.95 | 0.98+ | < 0.95 |
| **NP/DD Ratio** | 20 | 25+ | < 15 |
| **Astab Score** | 40 | 60+ | < 40 |
| **Family Members** | 3 | 5+ | < 2 |

### Trade Metrics (Example System)

| Metric | Example Value |
|--------|---------------|
| **Total Trades** | 4,014 (MaxAI comparison) |
| **Net Profit** | $132,412 (MaxAI comparison) |
| **Average Trade** | $33 |
| **Win Rate** | Not specified |
| **Max Drawdown** | Not specified as hard limit |

---

## Version Information

| Component | Version | Date |
|-----------|---------|------|
| **GSB Software** | 1.0.68.92 | 2025-05-05 |
| **Documentation** | Latest | 2025-05-05 |
| **Methodology** | Evolved | 2019-05-06 update |

---

## Computational Benchmarks

### Evaluation Speed

**Per-Individual Fitness:**
- Rule-based system: **Milliseconds** per evaluation
- Deep RL (comparison): **Hours** per evaluation

**Total Time Estimates:**
```
Best case (1 successful run):
  200,000 evals × 0.001 sec = 200 seconds (3-4 minutes)

Typical case (3-5 restarts):
  600k-1M evals × 0.001 sec = 600-1,000 seconds (10-17 minutes)

Worst case (10 restarts):
  2M evals × 0.001 sec = 2,000 seconds (33 minutes)
```

**Note:** Actual time depends on:
- Data size (years × bars per day)
- Number of indicators
- Hardware specifications
- Parallel processing capability

---

## Recommended Configurations

### Fast Development (Prototype)

```
Population: 100
Generations: 500
Restarts: 5
Training %: 50
Test %: 50
WF Gen × Pop: 100 × 100

Total Time: ~5-10 minutes
Total Evals: 250,000
```

### Standard Production (Robust)

```
Population: 200
Generations: 1000
Restarts: 10
Training %: 40
Test %: 60
WF Gen × Pop: 120 × 120

Total Time: ~30-60 minutes
Total Evals: 2,000,000
```

### High-Quality (Maximum Robustness)

```
Population: 200
Generations: 1000
Restarts: 10
Training %: 30
Test %: 70
WF Gen × Pop: 150 × 150
Noise Injection: 8 variants

Total Time: ~2-4 hours
Total Evals: 2,000,000+
```

---

## Comparison to Academic Systems

| Specification | GSBsys | MaxAI (Academic) | Red Queen (Failed) |
|---------------|--------|------------------|-------------------|
| Population | 200 | ~20-100 (est) | 500 |
| Generations | 1,000 | Unknown | Unknown |
| Total Evals | 2,000,000 | ~2,000-10,000 | Unknown (massive) |
| Eval Speed | Milliseconds | Hours (RL training) | Hours (LSTM training) |
| Wall-Clock Time | 30-60 min | Days-weeks | Weeks-months |
| Crossover Rate | 95% | Unknown | Unknown |
| Mutation Rate | 5% | Unknown | Unknown |
| Train/Test Split | 40/60 | 60/40 | Unknown |
| Profit Factor Min | 1.8 (validation) | 1.07 (actual) | N/A (failed) |
| Pearson Threshold | 0.95 | Not used | Not used |
| Live Validation | Multi-year | 4 months | Catastrophic failure |

**Key Advantage:** 100-1000x more evaluations feasible due to fast fitness computation
