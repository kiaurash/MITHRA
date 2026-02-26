# GA-Trading-Sys Product Requirements Document

**Version:** 1.1
**Date:** February 21, 2026
**Status:** Draft - Revised
**Author:** AI Strategy Builder Team
**Revision Notes:** Incorporated technical review feedback - added data acquisition, position sizing, commission model, team resources, tiered validation, expanded WF-GA spec

---

## Executive Summary

GA-Trading-Sys is an open-source pure genetic algorithm trading system optimization framework inspired by GSBsys (commercial system with multi-year deployment validation). This system aims to provide researchers and practitioners with a production-grade GA trading optimizer that implements proven practitioner innovations not found in academic GA+RL research.

**Key Differentiators:**
- Pure GA architecture (no RL complexity overhead)
- 12 practitioner innovations from GSBsys analysis
- 85-90% reproducible from documented specifications
- Focus on robustness over maximum backtest performance
- Comprehensive validation framework preventing Red Queen-style failures

---

## 1. Product Vision & Goals

### 1.1 Vision

Create the **definitive open-source baseline** for genetic algorithm trading system optimization, bridging the gap between academic research (which lacks practitioner rigor) and commercial systems (which lack transparency).

### 1.2 Primary Goals

1. **Reproducibility:** Implement all documented GSBsys components with ≥90% fidelity
2. **Transparency:** Open-source all algorithms, parameters, and methodology
3. **Validation:** Prevent overfitting through multi-stage robustness testing
4. **Performance:** Match or exceed GSBsys validation thresholds (PF ≥ 1.8, Pearson ≥ 0.95)
5. **Extensibility:** Enable researchers to experiment with GA variants and fitness functions

### 1.3 Success Metrics (Tiered Validation)

**MVP Tier (Proof of Concept):**
| Metric | Target | Rationale |
|--------|--------|-----------|
| Reproduction Fidelity | ≥85% | Core components functional |
| Validation Profit Factor | ≥1.2 | System profitable on OOS data |
| Equity Curve Pearson | ≥0.85 | Basic train/test consistency |
| Multi-Period OOS Pass Rate | 60% (3/5 periods) | Multiple regime validation |
| Noise Test Pass Rate | ≥62.5% (5/8 variants) | Robustness to data perturbations |
| Parameter Stability (CoV) | ≤60% | Acceptable parameter sensitivity |

**Production Tier (Commercial Grade - GSBsys Standard):**
| Metric | Target | Rationale |
|--------|--------|-----------|
| Reproduction Fidelity | ≥90% | Tier 1+2 gaps filled |
| Validation Profit Factor | ≥1.5 | Strong OOS performance (relaxed from GSBsys 1.8) |
| Equity Curve Pearson | ≥0.90 | High train/test consistency (relaxed from 0.95) |
| Multi-Period OOS Pass Rate | 80% (4/5 periods) | Regime robustness (allows 1 failure) |
| Noise Test Pass Rate | ≥75% (6/8 variants) | Data quirk independence |
| Parameter Stability (CoV) | ≤50% | Low parameter sensitivity |

---

## 2. Background & Context

### 2.1 GSBsys Analysis Summary

**Commercial Validation:**
- Multi-year deployment with NDA-protected customers
- Pricing: $200-$799 (indicates sustained practitioner confidence)
- Markets: ES, NQ, YM, NG, CL, GC, DAX (multi-market generalization)

**Key Technical Specifications:**
- Population: 200, Generations: 1,000, Restarts: 10
- Crossover: 95%, Mutation: 5%, Mutation Strength: 25%
- Fitness: Net Profit × Average Trade + floors
- Train/Test: 40/60 (conservative split)
- Total Evaluations: 20 million per development cycle

### 2.2 Gap Analysis vs. Academic Research

**MaxAI (Best Academic GA+RL System):**
- Live Validation: 4 months, Profit Factor: 1.07
- **Would be REJECTED by GSBsys** (PF < 1.8 threshold)

**Red Queen (Failed GA+RL System):**
- Catastrophic live capital decay despite excellent backtest
- **Would be flagged by Pearson filter** (equity curve divergence)

**GSBsys provides 12 innovations not in academic research:**
1. Net Profit × Avg Trade fitness (anti-overtrading)
2. Pearson ≥ 0.95 equity filter (curve consistency)
3. 40/60 conservative train/test split
4. 10-restart diversity mechanism
5. Two-stage GA (development + walk-forward)
6. Bounded stop loss optimization
7. Indicator pre-filtering (75 → 10)
8. Multi-period OOS validation (5+ windows)
9. Noise injection robustness testing
10. Family grouping (parameter stability)
11. Crossover-dominant GA (95/5 with restarts)
12. Commercial deployment grade evidence

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GA-Trading-Sys                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │  Data Pipeline  │─────>│ Indicator Engine│             │
│  └─────────────────┘      └─────────────────┘             │
│           │                        │                        │
│           v                        v                        │
│  ┌─────────────────────────────────────────┐               │
│  │     Development GA Engine               │               │
│  │  - Population Management                │               │
│  │  - Fitness Evaluation                   │               │
│  │  - Genetic Operators                    │               │
│  │  - Multi-Restart Coordinator            │               │
│  └─────────────────────────────────────────┘               │
│           │                                                 │
│           v                                                 │
│  ┌─────────────────────────────────────────┐               │
│  │     Validation Framework                │               │
│  │  - Pearson Equity Filter                │               │
│  │  - Multi-Period OOS Tester              │               │
│  │  - Noise Injection Tester               │               │
│  │  - Family Grouping Analyzer             │               │
│  └─────────────────────────────────────────┘               │
│           │                                                 │
│           v                                                 │
│  ┌─────────────────────────────────────────┐               │
│  │     Walk-Forward GA Engine              │               │
│  │  - Retraining Schedule Optimization     │               │
│  │  - Parameter Update Strategy            │               │
│  └─────────────────────────────────────────┘               │
│           │                                                 │
│           v                                                 │
│  ┌─────────────────────────────────────────┐               │
│  │     Deployment Pipeline                 │               │
│  │  - Code Generation (EasyLanguage/Python)│               │
│  │  - Performance Monitoring               │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Component Specifications

#### 3.2.1 Data Pipeline
- **Input:** OHLCV time series (futures/stocks)
- **Normalization:** HighestLowest to [-100, +100] range
- **Train/Test Split:** 40% training, 60% out-of-sample
- **Multi-Period Windowing:** 5+ distinct OOS periods

#### 3.2.2 Indicator Engine
- **Standard Indicators:** 15 (RSI, CCI, Stochastic, ADX, ATR, etc.)
- **Custom Indicators:** Open architecture for user-defined indicators
- **Pre-Filtering:** Rank all indicators, select top 10 for main GA
- **Signal Combination:** Two formulations supported (configurable)

**Signal Combination Methods:**

**Option 1 - Weighted Sum (Recommended for MVP):**
```python
# Normalized indicators in range [-100, +100]
signal = w1 * norm(indicator1) + w2 * norm(indicator2) + ... + wN * norm(indicatorN)
entry_threshold = 0  # GA-optimized
long_entry = signal > entry_threshold
short_entry = signal < -entry_threshold
```

**Advantages:**
- Simple, robust, no division-by-zero issues
- Weights interpretable (positive = bullish, negative = bearish)
- Linear combination proven in academic research

**Option 2 - Multiplicative (GSBsys-Style, Research Phase):**
```python
# Transform to positive range to avoid exponentiation issues
# Method: Shift normalized indicators from [-100, +100] to [0, 200]
signal = 1.0
for i, weight in enumerate(weights):
    shifted_indicator = (norm(indicator[i]) + 100)  # Now in [0, 200]
    signal *= (shifted_indicator / 100) ** weight  # Normalized to ~1.0 baseline

# Or alternative GSBsys interpretation:
signal = (1 + norm(ind1)/100)^w1 * (1 + norm(ind2)/100)^w2 * ...
# Ensures all terms positive, signal ≈ 1.0 baseline, >1.0 = bullish, <1.0 = bearish
entry_threshold = 1.0  # GA-optimized
long_entry = signal > entry_threshold
```

**Advantages:**
- Faithful to GSBsys documentation (indicator^weight formula)
- Non-linear interactions between indicators
- May capture synergies that linear combination misses

**Disadvantages:**
- More complex, potential numerical issues
- Harder to interpret weights
- Requires normalization transformation

**Implementation Plan:**
- **Phase 1 (MVP)**: Implement weighted sum (simple, proven)
- **Phase 3 (Research)**: Implement multiplicative, compare performance
- **Configuration**: `signal_method: "weighted_sum"` or `"multiplicative"` in YAML

#### 3.2.3 Development GA Engine
- **Chromosome Encoding:** Hybrid discrete-continuous
  - Discrete: Indicator selection (2-5 indicators from top 10)
  - Continuous: Indicator parameters, weights, stop loss values
- **Population:** 200 individuals
- **Generations:** 1,000 per restart
- **Restarts:** 10 independent runs with new random seeds
- **Selection:** Tournament (k=3)
- **Crossover:** Simulated Binary Crossover (SBX), rate=95%
- **Mutation:** Gaussian, rate=5%, strength=25%
- **Fitness Function:**
  ```
  Primary: NetProfit × AverageTrade
  Floors: Pearson(train_equity, test_equity) ≥ 0.95
          ProfitFactor(train) ≥ 1.2
          ProfitFactor(test) ≥ 1.2
  ```

#### 3.2.4 Validation Framework
- **Pearson Equity Filter:** Compute correlation between in-sample and OOS equity curves
- **Multi-Period OOS:** Test across 5 distinct market regime windows
- **Noise Injection:** Generate 8 randomized data variants (±0.5% price perturbation)
- **Family Grouping:** Generate 5-10 parameter variants (±5%), measure performance variance

#### 3.2.5 Walk-Forward GA Engine (Full Specification)

**Purpose:** Optimize WHEN and HOW to retrain the main GA as markets evolve, preventing performance degradation over time.

**Two-Stage Optimization:**
```
Stage 1: Development GA
  - Optimize trading system parameters (indicators, weights, stops)
  - Output: Best trading system for historical period

Stage 2: Walk-Forward GA (THIS COMPONENT)
  - Optimize retraining schedule for that system
  - Output: When to retrain, how to update parameters
```

**Chromosome Encoding:**
```yaml
wf_chromosome:
  # How often to retrain the system
  retrain_frequency: [30, 60, 90, 120, 180]  # days (discrete gene)

  # How much historical data to use for retraining
  data_window: [180, 365, 730, 1095]  # days (discrete gene)

  # How to update system when retraining
  update_method: ["replace", "ensemble", "parameter_blend"]  # discrete gene

  # If parameter_blend: how much weight to new vs. old system
  blend_weight_new: [0.3, 0.4, 0.5, 0.6, 0.7]  # continuous gene

  # Whether to use additive or multiplicative parameter updates
  update_operator: ["additive", "multiplicative"]  # discrete gene
```

**Example Chromosome:**
```
[retrain_freq=90, data_window=365, update_method="parameter_blend",
 blend_weight=0.6, operator="multiplicative"]

Interpretation:
- Retrain every 90 days
- Use last 365 days of data
- Blend new parameters with 60% weight to new, 40% to old
- Update using: param_new = param_old × param_optimized^0.6
```

**Fitness Function:**
```python
def wf_fitness(wf_chromosome):
    """
    Evaluate WF schedule by simulating retraining on historical OOS periods.
    """
    # Parse chromosome
    retrain_freq = wf_chromosome.retrain_frequency
    data_window = wf_chromosome.data_window
    update_method = wf_chromosome.update_method

    # Simulate walk-forward on 3 OOS periods
    oos_periods = [
        ("2020-01-01", "2020-12-31"),  # Year 1
        ("2021-01-01", "2021-12-31"),  # Year 2
        ("2022-01-01", "2022-12-31"),  # Year 3
    ]

    sharpe_ratios = []
    for start, end in oos_periods:
        # Start with base system (from Development GA)
        current_system = base_system.copy()

        # Walk forward through period with retraining
        performance = []
        current_date = parse_date(start)
        end_date = parse_date(end)

        while current_date < end_date:
            # Trade for retrain_freq days
            trade_end = current_date + timedelta(days=retrain_freq)
            pnl = backtest(current_system, current_date, trade_end)
            performance.append(pnl)

            # Retrain system using last data_window days
            retrain_start = current_date - timedelta(days=data_window)
            new_system = run_development_ga(data[retrain_start:current_date])

            # Update current_system based on update_method
            if update_method == "replace":
                current_system = new_system
            elif update_method == "ensemble":
                current_system = ensemble([current_system, new_system])
            elif update_method == "parameter_blend":
                current_system = blend_parameters(
                    current_system, new_system,
                    wf_chromosome.blend_weight_new
                )

            current_date = trade_end

        # Calculate Sharpe for this OOS period
        sharpe = calculate_sharpe(performance)
        sharpe_ratios.append(sharpe)

    # Fitness = average Sharpe across 3 OOS periods
    return mean(sharpe_ratios)
```

**GA Parameters:**
- **Population**: 120 individuals (smaller than development GA)
- **Generations**: 120 (WF parameter space smaller than system space)
- **Restarts**: 1 (WF optimization less critical than development)
- **Selection**: Tournament (k=3)
- **Crossover**: Uniform crossover (discrete genes) + SBX (continuous)
- **Mutation**: Random gene replacement (discrete) + Gaussian (continuous)

**Output & Application:**
```python
# After WF-GA completes, best chromosome is:
best_wf_schedule = {
    'retrain_frequency': 90,  # days
    'data_window': 365,
    'update_method': 'parameter_blend',
    'blend_weight_new': 0.6,
    'update_operator': 'multiplicative'
}

# Deploy system with this schedule:
# 1. Run development GA on initial period (e.g., 2015-2016)
# 2. Trade live for 90 days
# 3. After 90 days, retrain using last 365 days
# 4. Blend new parameters: param = param_old × param_new^0.6
# 5. Repeat every 90 days
```

**Validation Evidence (from GSBsys documentation):**
> "In all cases the WF parameters are better in EVERY metric in all 3 tests."

**Success Criteria:**
- WF-optimized schedule outperforms baseline (no retraining) on ≥2/3 OOS periods
- Average Sharpe improvement ≥10% over baseline
- Parameters are stable (low variance across restarts)

**Dependencies:**
- Requires Development GA to complete first (Stage 1)
- Requires ≥3 years historical data (for 3 OOS periods)
- Computationally expensive: each WF chromosome requires multiple Development GA runs

#### 3.2.6 Entry/Exit Logic
- **Entry Modes:**
  - **AIC (Any Indicators Cross):** Enter when any weighted indicator crosses threshold
  - **NCC (No Conflict Cross):** Enter only when no opposing signals
  - **Compare2:** Enter when signal strength exceeds two-indicator baseline
- **Exit Modes:**
  - Fixed stop loss (GA-optimized within user bounds)
  - Trailing stop (GA-optimized activation and trail distance)
  - Time-based exit (optional)

---

## 4. Functional Requirements

### 4.1 Core Functionality

| ID | Requirement | Priority | Tier |
|----|-------------|----------|------|
| FR-01 | Load OHLCV data from CSV/Parquet/database | MUST | 1 |
| FR-02 | Compute 15+ standard technical indicators | MUST | 1 |
| FR-03 | Normalize indicators to [-100, +100] range | MUST | 1 |
| FR-04 | Perform indicator pre-filtering (rank and select top 10) | MUST | 1 |
| FR-05 | Initialize random GA population (200 individuals) | MUST | 1 |
| FR-06 | Evaluate fitness: Net Profit × Avg Trade | MUST | 1 |
| FR-07 | Apply Pearson ≥ 0.95 equity curve filter | MUST | 1 |
| FR-08 | Perform tournament selection (k=3) | MUST | 1 |
| FR-09 | Apply SBX crossover (rate=95%) | MUST | 1 |
| FR-10 | Apply Gaussian mutation (rate=5%, strength=25%) | MUST | 1 |
| FR-11 | Perform 10 independent GA restarts | MUST | 1 |
| FR-12 | Test systems across 5+ OOS periods | MUST | 1 |
| FR-13 | Generate 8 noise-perturbed datasets | MUST | 2 |
| FR-14 | Perform noise robustness testing (6/8 pass threshold) | MUST | 2 |
| FR-15 | Generate family grouping variants (±5% parameters) | MUST | 2 |
| FR-16 | Calculate family performance variance (CoV ≤ 50%) | MUST | 2 |
| FR-17 | Optimize walk-forward schedule via WF-GA | SHOULD | 2 |
| FR-18 | Export systems to EasyLanguage code | SHOULD | 3 |
| FR-19 | Export systems to Python/pandas backtest code | SHOULD | 3 |
| FR-20 | Visualize equity curves (train vs. test alignment) | SHOULD | 2 |
| FR-21 | Generate performance reports (Sharpe, PF, DD, trades) | MUST | 1 |
| FR-22 | Support bounded parameter optimization (user-defined ranges) | MUST | 1 |
| FR-23 | Log all GA runs for reproducibility | SHOULD | 2 |

### 4.2 User Interface Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| UI-01 | CLI interface for configuration and execution | MUST |
| UI-02 | YAML/JSON configuration file support | MUST |
| UI-03 | Real-time progress display (generation, fitness, best system) | SHOULD |
| UI-04 | Web dashboard for result visualization (optional) | COULD |
| UI-05 | Export results to CSV/JSON for external analysis | SHOULD |

### 4.3 Data Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| DR-01 | Support 1-minute to daily bar intervals | MUST |
| DR-02 | Handle missing data (forward-fill or skip) | MUST |
| DR-03 | Support continuous futures contracts (rollover adjustment) | SHOULD |
| DR-04 | Support stock data with split/dividend adjustments | SHOULD |
| DR-05 | Validate data quality (no duplicates, sorted timestamps) | MUST |
| DR-06 | Data provider selection and acquisition | MUST |
| DR-07 | Position sizing strategy | MUST |
| DR-08 | Commission and slippage model | MUST |

#### DR-06: Data Provider Selection (MUST, Tier 1)

**MVP Approach - Free Data Sources:**
- **Primary**: yfinance (Yahoo Finance Python API)
  - **Coverage**: Daily bars for stocks/ETFs (SPY, QQQ, IWM, DIA)
  - **Limitation**: No 1-minute futures data
  - **Workaround**: Use stock proxies (SPY ≈ ES, QQQ ≈ NQ, DIA ≈ YM)
  - **Cost**: Free
  - **Data Range**: 2010-present (15+ years)

- **Alternative Free**: AlphaVantage (API key required)
  - **Coverage**: Intraday (1-min, 5-min) for stocks (limited history: 30 days rolling)
  - **Limitation**: Rate limits (5 calls/min, 500 calls/day)
  - **Cost**: Free tier

**Production Upgrade Path - Paid Sources:**
- **Theta Data** ($150/month recommended)
  - Coverage: 1-min futures 2015-present (ES, NQ, YM, CL, GC, etc.)
  - Format: REST API + Parquet downloads
  - Quality: Tick-level, cleaned, back-adjusted

- **NinjaTrader Lifetime** (~$1000 one-time)
  - Coverage: Live + historical futures/stocks
  - Format: Export to CSV
  - Quality: Professional-grade

**MVP Data Strategy:**
```
Phase 1-2 (MVP): Daily stock data (SPY, QQQ) via yfinance
Phase 3-4 (Production): Upgrade to Theta Data for 1-min futures
```

**Data Format:**
- Input: CSV with columns [Date, Open, High, Low, Close, Volume]
- Storage: Parquet for fast access (pandas.to_parquet)
- Rollover method (futures): Panama method (back-adjusted continuous contracts)

#### DR-07: Position Sizing Strategy (MUST, Tier 1)

**Method**: Fixed fractional risk per trade

**Formula:**
```python
risk_per_trade = starting_capital * 0.02  # 2% of capital
contracts = floor(risk_per_trade / stop_loss_dollars)
contracts = max(1, min(contracts, max_contracts))

# Where:
# stop_loss_dollars = GA-optimized stop loss value
# max_contracts = floor(capital / margin_requirement)
```

**Parameters:**
- **Risk percentage**: 2% of starting capital per trade
- **Starting capital**: $50,000 (configurable)
- **Margin requirement** (futures):
  - ES: $13,000 per contract
  - NQ: $17,000 per contract
  - YM: $9,000 per contract
- **Margin requirement** (stocks): None (assume full capital available)

**Constraints:**
- Minimum: 1 contract (no fractional contracts)
- Maximum: floor(capital / margin_requirement)
- Rebalance: Daily (capital updated with realized P&L)

**Rationale:**
- Fixed fractional risk ensures consistent exposure across trades
- 2% is conservative (prevents account blowup on losing streaks)
- Stops are GA-optimized, so position size adapts to volatility

#### DR-08: Commission & Slippage Model (MUST, Tier 1)

**Futures (Production - when using Theta Data):**
- **Commission**: $2.50 per round-trip (conservative estimate)
  - Interactive Brokers: $0.85 per side = $1.70 RT
  - Budget brokers: $0.50 per side = $1.00 RT
  - Using $2.50 as safety margin
- **Slippage**: 1.5 ticks per side = 3 ticks RT
  - ES: 0.25 point tick = $12.50 × 3 = $37.50
  - NQ: 0.25 point tick = $5.00 × 3 = $15.00
  - YM: 1 point tick = $5.00 × 3 = $15.00
- **Total cost per RT**: $2.50 + slippage (varies by instrument)

**Stocks (MVP - when using yfinance):**
- **Commission**: $0 (most brokers zero-commission for stocks)
- **Slippage**: 0.05% of entry price (half bid-ask spread)
  - SPY @ $450: $450 × 0.0005 = $0.225 per share × 100 shares = $22.50 per side
  - Total RT: $45 for 100 shares
- **Alternative**: Use actual bid-ask spread if available

**Application in Backtest:**
```python
def apply_costs(entry_price, exit_price, contracts, instrument):
    # Entry cost
    entry_commission = 2.50  # per contract
    entry_slippage = get_slippage_ticks(instrument) * tick_value(instrument)
    entry_cost = (entry_commission + entry_slippage) * contracts

    # Exit cost (same)
    exit_cost = entry_cost

    # Gross P&L
    gross_pnl = (exit_price - entry_price) * point_value(instrument) * contracts

    # Net P&L
    net_pnl = gross_pnl - entry_cost - exit_cost
    return net_pnl
```

**Validation:**
- Report both gross and net Profit Factor
- Expect 10-20% degradation from costs
- If net PF < 1.0, system unprofitable after costs (REJECT)

---

## 5. Technical Requirements

### 5.1 GA Parameters (Baseline Configuration)

```yaml
ga_config:
  development:
    population_size: 200
    generations: 1000
    restarts: 10
    crossover_rate: 0.95
    mutation_rate: 0.05
    mutation_strength: 0.25
    tournament_size: 3
    elitism: 2  # preserve top 2 individuals

  walk_forward:
    population_size: 120
    generations: 120
    restarts: 1
    crossover_rate: 0.90
    mutation_rate: 0.10

  chromosome:
    indicator_count: [2, 3, 4, 5]  # discrete gene
    indicator_ids: [0, 1, 2, ..., 9]  # from pre-filtered set
    indicator_params: [10, 5000]  # continuous range
    indicator_weights: [-1.0, 2.0]  # continuous range
    stop_loss_range: [200, 2000]  # user-bounded range (dollars)
    trailing_stop_range: [100, 1000]  # user-bounded range (dollars)

  fitness:
    primary: "net_profit * avg_trade"
    signal_method: "weighted_sum"  # or "multiplicative" (Phase 3)

    # Tiered validation thresholds
    mvp_tier:
      pearson_floor: 0.85
      profit_factor_train_floor: 1.2
      profit_factor_test_floor: 1.2
      profit_factor_validation_floor: 1.2
      min_trades: 30
      max_drawdown_pct: 30

    production_tier:
      pearson_floor: 0.90
      profit_factor_train_floor: 1.2
      profit_factor_test_floor: 1.2
      profit_factor_validation_floor: 1.5
      min_trades: 50
      max_drawdown_pct: 25

  validation:
    train_test_split: [0.4, 0.6]
    oos_periods: 5

    noise_testing:
      enabled: true
      variants: 8
      noise_level: 0.005  # ±0.5% price perturbation
      mvp_pass_threshold: 0.625  # 5/8 variants
      production_pass_threshold: 0.75  # 6/8 variants

    family_grouping:
      enabled: true
      variants: 10
      perturbation: 0.05  # ±5%
      mvp_cov_threshold: 0.60
      production_cov_threshold: 0.50
```

### 5.2 Indicator Specifications

#### 5.2.1 Standard Indicators (Tier 1 - Immediate Implementation)

| Indicator | Parameters | Formula Source |
|-----------|-----------|----------------|
| RSI | Period | Standard (Wilder) |
| CCI | Period | Standard (Lambert) |
| Stochastic | K, D, Smooth | Standard (Lane) |
| ADX | Period | Standard (Wilder) |
| ATR | Period | Standard (Wilder) |
| MACD | Fast, Slow, Signal | Standard (Appel) |
| Bollinger Bands | Period, StdDev | Standard (Bollinger) |
| ROC | Period | Standard (rate of change) |
| Williams %R | Period | Standard (Williams) |
| Momentum | Period | Standard (price difference) |
| EMA | Period | Standard (exponential MA) |
| SMA | Period | Standard (simple MA) |
| Volume | N/A | Raw volume |
| OBV | N/A | Standard (on-balance volume) |
| DMI | Period | Standard (directional movement) |

#### 5.2.2 Custom Indicators (Tier 2 - Research-Based Approximations)

Implement approximations for GSBsys proprietary indicators:
- **TrueRange-based indicators:** Use ATR variants with different smoothing
- **CCI variants:** Multi-timeframe CCI combinations
- **DMI variants:** Different period DMI with threshold logic
- **Range-based indicators:** High-Low range with normalization

### 5.3 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Core Language | Python 3.10+ | NumPy/Pandas ecosystem, GA libraries |
| GA Framework | DEAP (Distributed Evolutionary Algorithms in Python) | Mature, flexible, well-documented |
| Data Handling | Pandas, Polars | OHLCV manipulation, performance |
| Indicators | TA-Lib, pandas-ta | Battle-tested implementations |
| Backtesting | **VectorBT** (Phase 1-2), Backtrader (Phase 5 optional) | Vectorized backtesting for GA speed |
| Visualization | Matplotlib, Plotly | Equity curves, GA convergence |
| Configuration | PyYAML, Pydantic | Type-safe config validation |
| CLI | Click or Typer | User-friendly command interface |
| Testing | Pytest | Unit/integration tests |
| Documentation | Sphinx | API and methodology docs |

**Backtesting Engine Decision Rationale:**

| Feature | VectorBT | Backtrader | Decision |
|---------|----------|------------|----------|
| **Speed** | Fast (vectorized NumPy) | Slow (event-driven Python loops) | VectorBT wins (100x faster) |
| **Fitness Evals** | <300ms for 200k bars | >5000ms for 200k bars | Critical for GA (200k evals needed) |
| **Entry/Exit Logic** | Medium flexibility (array operations) | High flexibility (custom Python) | VectorBT sufficient for AIC/NCC |
| **Indicators** | Built-in (TA-Lib integration) | Manual implementation | VectorBT easier |
| **Learning Curve** | Moderate (NumPy knowledge) | Steep (event-driven paradigm) | VectorBT faster onboarding |
| **Use Case** | GA optimization (many backtests) | Strategy prototyping (single backtest) | VectorBT fits our need |

**Phase 1-2 (MVP):** VectorBT exclusively
- Rationale: Speed critical (200k× 1000 gen × 10 restarts = 2 billion operations)
- Trade-off: May require creative solutions for Compare2 entry mode

**Phase 5 (Optional):** Backtrader for complex logic
- If Compare2 or custom entry modes too difficult in VectorBT
- Performance acceptable for code generation validation (not GA loop)

### 5.4 Performance Requirements (Revised - Realistic Targets)

| Metric | Target | Notes |
|--------|--------|-------|
| Single Fitness Evaluation | <300ms | VectorBT on 200k bars (realistic for daily data 2010-present) |
| Full GA Run (1 restart) | ~16 hours | 200 pop × 1000 gen × 300ms = 60,000 sec = 16.7 hours |
| 10-Restart Development Cycle (parallel) | ~16 hours wall-time | **Assumes 10-core parallelization** (10 restarts concurrent) |
| 10-Restart Development Cycle (sequential) | ~160 hours (7 days) | If parallelization unavailable (fallback) |
| Memory Footprint | <16GB RAM | GSBsys minimum spec (per restart) |
| Disk Space | <1GB | Per dataset/results |

**Performance Scaling:**

**Daily bars (MVP with yfinance stock data):**
- SPY 2010-2025: 15 years × 252 days = **3,780 bars**
- Single backtest: ~10-20ms (VectorBT vectorized)
- **Full GA run**: 200 × 1000 × 20ms = **4,000 sec = 1.1 hours**
- **10 restarts parallel**: **1.1 hours wall-time** ✓ Meets target

**1-minute bars (Production with Theta Data futures):**
- NQ 2017-2024: 7 years × 252 × 6.5 hours × 60 min = **682,000 bars**
- Single backtest: ~300-500ms (complex entry logic)
- **Full GA run**: 200 × 1000 × 400ms = **80,000 sec = 22 hours**
- **10 restarts parallel**: **22 hours wall-time**
- **10 restarts sequential**: **220 hours (9 days)**

**Parallelization Implementation:**
```python
from multiprocessing import Pool

def run_ga_restart(seed):
    np.random.seed(seed)
    return genetic_algorithm(population=200, generations=1000)

# Parallel execution
with Pool(processes=10) as pool:
    results = pool.map(run_ga_restart, range(10))

best_system = max(results, key=lambda x: x.fitness)
```

**Mitigation if Performance Insufficient:**
1. Reduce population to 100 (GSBsys uses 200, but 100 may suffice)
2. Reduce generations to 500 (if convergence faster than expected)
3. Use daily bars instead of 1-minute (MVP strategy)
4. Optimize VectorBT usage (cache indicator calculations, vectorize more)
5. GPU acceleration (future Phase 5)

### 5.5 GA Hyperparameter Sensitivity Analysis

**Problem:** GSBsys parameters (Pop=200, Gen=1000, CR=95%, MR=5%) are optimized for futures data with proprietary indicators. Our system uses different data (stocks vs futures) and different indicators (standard vs proprietary), so parameters may need tuning.

**Tuning Protocol (Before Full Optimization):**

**Step 1: Baseline Run**
```python
# Run pilot GA with GSBsys defaults
baseline_config = {
    'population_size': 200,
    'generations': 1000,
    'crossover_rate': 0.95,
    'mutation_rate': 0.05
}
baseline_results = run_ga(baseline_config, restarts=3)
baseline_fitness = baseline_results.best_fitness
baseline_convergence_gen = baseline_results.convergence_generation
```

**Step 2: Population Size Sweep**
```python
# Test if smaller population sufficient (faster iterations)
for pop_size in [100, 150, 200, 250]:
    results = run_ga(population_size=pop_size, generations=1000, restarts=3)
    fitness_at_gen1000 = results.best_fitness
    convergence_gen = results.convergence_generation

    # Select smallest population that:
    # - Achieves ≥95% of baseline fitness
    # - Converges by generation 1000
```

**Step 3: Crossover Rate Sweep**
```python
for crossover_rate in [0.85, 0.90, 0.95, 0.98]:
    results = run_ga(crossover_rate=crossover_rate, restarts=3)
    # Select rate with best final fitness
```

**Step 4: Mutation Rate Sweep**
```python
for mutation_rate in [0.03, 0.05, 0.07, 0.10]:
    results = run_ga(mutation_rate=mutation_rate, restarts=3)
    # Select rate with best diversity × fitness product
```

**Acceptance Criteria:**
- If GSBsys defaults within **5% of tuned parameters** → Use defaults (simplicity)
- If tuned parameters improve fitness by **>10%** → Document tuned params per dataset
- Document tuning results in `config/tuning_results_[dataset].yaml`

**Example Output:**
```yaml
# config/tuning_results_SPY_daily.yaml
dataset: "SPY daily 2010-2025"
baseline:
  population_size: 200
  best_fitness: 1250.5
  convergence_gen: 780

tuned:
  population_size: 150  # 5% faster, 98% of fitness
  crossover_rate: 0.95  # No improvement, keep default
  mutation_rate: 0.07  # +3% fitness vs 0.05
  best_fitness: 1287.3  # +2.9% improvement
  recommendation: "Use tuned params (small but consistent improvement)"
```

**When to Run Tuning:**
- Once per dataset type (daily stocks, 1-min futures, etc.)
- When switching markets (ES vs NQ may have different optimal params)
- If GA not converging within 1000 generations (diagnostic)

**Cost:**
- ~5-10 GA runs (vs 1 run for production optimization)
- Adds 5-10 hours to initial setup
- Pays off if running multiple optimizations on same dataset

---

## 6. Non-Functional Requirements

### 6.1 Reliability

- **Reproducibility:** Fixed random seeds for all GA runs, logged for replication
- **Validation:** All systems must pass multi-stage validation before deployment recommendation
- **Error Handling:** Graceful handling of data errors, invalid configs, fitness eval failures

### 6.2 Maintainability

- **Modular Architecture:** Clear separation of data, indicators, GA, validation, export
- **Extensibility:** Plugin architecture for custom indicators and fitness functions
- **Documentation:** Inline code comments, API docs, methodology docs, user guides

### 6.3 Usability

- **Configuration:** YAML-based config files with sensible defaults
- **Logging:** Comprehensive logs with INFO/DEBUG levels
- **Progress Tracking:** Real-time feedback on GA convergence and validation progress
- **Error Messages:** Clear, actionable error messages for common failure modes

### 6.4 Portability

- **Platform:** Cross-platform (Windows, Linux, macOS)
- **Python Version:** Python 3.10+ (leveraging type hints)
- **Dependencies:** Minimal external dependencies, all pip-installable

### 6.5 Security

- **Data Privacy:** All processing local (no cloud uploads without explicit user consent)
- **Code Generation:** Sandboxed execution of generated trading code
- **Configuration Validation:** Schema validation prevents code injection via config

---

## 7. Implementation Phases (Solo Developer - 1 FTE)

**Team Composition:** 1 full-time developer with skills in:
- Python (advanced: NumPy, Pandas, DEAP)
- Genetic algorithms (theory + implementation)
- Financial data (OHLCV, indicators, backtesting)
- Software engineering (testing, documentation, Git)

**Timeline Basis:** Estimates assume 40 hours/week, solo developer, no blockers

### Phase 1: Core GA Engine (Tier 1 - 12 weeks, solo)

**Deliverables:**
- Data pipeline (yfinance integration, CSV/Parquet, normalization) - 1 week
- 15 standard indicators (TA-Lib integration) - 1 week
- Position sizing (fixed fractional risk) - 0.5 week
- Commission/slippage model - 0.5 week
- Basic GA engine (DEAP framework) - 3 weeks
  - Population initialization
  - Tournament selection
  - SBX crossover
  - Gaussian mutation
  - Fitness evaluation (Net Profit × Avg Trade)
- 40/60 train/test split - 0.5 week
- VectorBT backtest engine integration - 2 weeks
- Performance reporting (Sharpe, PF, drawdown, trade count) - 1 week
- Testing & debugging - 2 weeks
- Documentation (setup, usage) - 1 week

**Success Criteria:**
- Run single GA optimization on SPY daily data (2010-2025)
- Generate trading system with MVP validation (PF ≥ 1.2 on test set)
- Reproduce GSBsys GA parameter settings (200 pop, 1000 gen)
- Single fitness eval <50ms (daily bars)

**Reproducibility:** ~60% (core GA architecture, standard indicators, basic validation)

**Timeline Breakdown:** 12 weeks (solo), 6 weeks (2 FTE team)

---

### Phase 2: Validation Framework (Tier 1+2 - 8 weeks, solo)

**Deliverables:**
- Pearson equity curve filter (train vs test correlation) - 1 week
- Multi-period OOS validation (5 distinct regime windows) - 1.5 weeks
- 10-restart multi-start GA (parallelization) - 1 week
- Indicator pre-filtering (rank indicators, select top 10) - 1.5 weeks
- Family grouping (±5% parameter variants, CoV calculation) - 1.5 weeks
- Bounded parameter optimization (user-defined ranges) - 0.5 week
- Tiered validation thresholds (MVP vs Production) - 0.5 week
- Comprehensive logging (random seeds, all runs) - 0.5 week
- Testing & integration - 1 week

**Success Criteria:**
- Systems pass MVP tier: Pearson ≥ 0.85, PF ≥ 1.2, 3/5 OOS periods
- Production tier: Pearson ≥ 0.90, PF ≥ 1.5, 4/5 OOS periods
- Family grouping identifies stable (CoV ≤ 60%) vs unstable systems
- 10 restarts produce diverse solutions (diversity >20%)
- All runs reproducible via logged seeds

**Reproducibility:** ~80% (core + validation without noise testing)

**Timeline Breakdown:** 8 weeks (solo), 4 weeks (2 FTE team)

---

### Phase 3: Robustness Testing (Tier 2 - 6 weeks, solo)

**Deliverables:**
- Noise injection testing (8 perturbed datasets, ±0.5% price) - 1.5 weeks
- Monte Carlo robustness tests (reshuffle, resample, permutation) - 1 week
- Walk-Forward GA engine (full specification from Section 3.2.5) - 2.5 weeks
- Parameter sensitivity analysis (aligns with family grouping) - 1 week

**Success Criteria:**
- MVP tier: Systems profitable on ≥5/8 noise variants (62.5%)
- Production tier: Systems profitable on ≥6/8 noise variants (75%)
- Walk-forward improves OOS Sharpe by ≥10% vs baseline (no retraining)
- Sensitivity analysis correlates with family grouping (high CoV = unstable)

**Reproducibility:** ~85% (core + validation + robustness)

**Timeline Breakdown:** 6 weeks (solo), 3 weeks (2 FTE team)

---

### Phase 4: Export & Integration (Tier 3 - 6 weeks, solo)

**Deliverables:**
- Python backtest code generator (pandas reproduction) - 1.5 weeks
- Result visualization (equity curves, GA convergence plots) - 1 week
- CLI polish (progress bars, colored output, help text) - 1 week
- Comprehensive documentation (user guide, API reference, Sphinx) - 2 weeks
- Hyperparameter tuning protocol implementation - 0.5 week

**Success Criteria:**
- Generated Python code reproduces fitness metrics (±0.01% tolerance)
- Users can run full GA optimization from YAML config in <5 min setup
- Documentation enables new user to reproduce SPY optimization in <30 min
- Visualization shows train vs test equity alignment clearly

**Reproducibility:** ~90% (all documented components implemented)

**EasyLanguage Code Generation:** **Deferred to Phase 5** (complexity underestimated)
- Requires TradeStation SDK research (2 weeks)
- Bar-by-bar translation non-trivial (2 weeks)
- TradeStation subscription for testing ($99/month)

**Timeline Breakdown:** 6 weeks (solo), 3 weeks (2 FTE team)

---

### Phase 5: Advanced Features (Optional - 8 weeks, solo)

**Deliverables:**
- EasyLanguage code generator (TradeStation/MultiCharts) - 4 weeks
- Backtrader integration (for complex entry/exit logic) - 1 week
- Multi-objective fitness (Pareto frontier: return vs risk) - 1 week
- Adaptive mutation (anneal mutation rate by generation) - 0.5 week
- GPU acceleration (CUDA/JAX for parallel fitness evals) - 1 week
- Theta Data integration (1-min futures upgrade path) - 0.5 week

**Success Criteria:**
- Generated EasyLanguage code compiles in TradeStation
- EasyLanguage backtest reproduces Python fitness (±1% tolerance)
- Multi-objective GA produces Pareto frontier (10+ non-dominated solutions)
- GPU acceleration achieves ≥5x speedup (realistic, not 10x)
- Theta Data integration enables 1-min futures optimization

**Reproducibility:** >90% (exceeds GSBsys with novel features)

**Timeline Breakdown:** 8 weeks (solo), 4 weeks (2 FTE team)

---

**Total MVP Timeline (Phases 1-4):**
- **Solo developer**: 12 + 8 + 6 + 6 = **32 weeks (~8 months)**
- **2 FTE team**: 6 + 4 + 3 + 3 = **16 weeks (~4 months)**
- **With Phase 5 (optional)**: +8 weeks solo = **40 weeks (~10 months)**

---

## 8. Success Criteria

### 8.1 Functional Success (Tiered Criteria)

**MVP Tier (Proof of Concept - Phase 1-2):**
- [ ] System generates trading strategies on historical stock data (SPY daily 2010-2025)
- [ ] All 15 standard indicators compute correctly (validated against TA-Lib)
- [ ] GA converges within 1,000 generations (fitness improvement >10%)
- [ ] 10 restarts produce diverse solutions (population diversity >15%)
- [ ] Systems pass Pearson ≥ 0.85 filter on train/test equity curves
- [ ] Systems achieve PF ≥ 1.2 on both train and test sets
- [ ] Systems achieve PF ≥ 1.2 on independent validation set
- [ ] Multi-period OOS validation shows 60% pass rate (3/5 periods PF > 1.0)
- [ ] Noise testing passes ≥62.5% threshold (5/8 variants profitable)
- [ ] Family grouping identifies stable systems (CoV ≤ 60%)

**Production Tier (Commercial Grade - Phase 3-4):**
- [ ] Systems pass Pearson ≥ 0.90 filter (higher train/test consistency)
- [ ] Systems achieve PF ≥ 1.5 on independent validation set
- [ ] Multi-period OOS validation shows 80% pass rate (4/5 periods PF > 1.0)
- [ ] Noise testing passes ≥75% threshold (6/8 variants profitable)
- [ ] Family grouping identifies stable systems (CoV ≤ 50%)
- [ ] Walk-forward optimization improves OOS Sharpe by ≥10%

### 8.2 Non-Functional Success

**MVP Tier (Daily Stock Data):**
- [ ] Single fitness evaluation completes in <50ms (daily bars, ~4000 bars)
- [ ] Full 10-restart GA cycle completes in ~1.5 hours wall-time (parallel execution)
- [ ] Memory usage remains <8GB RAM throughout execution
- [ ] Configuration via YAML file with schema validation (Pydantic)
- [ ] CLI provides real-time progress bars (tqdm) and clear error messages
- [ ] All GA runs are reproducible via logged random seeds
- [ ] Documentation enables new user to run SPY optimization in <30 minutes setup
- [ ] Code coverage ≥70% (unit + integration tests)

**Production Tier (1-min Futures Data):**
- [ ] Single fitness evaluation completes in <300ms (1-min bars, ~700k bars)
- [ ] Full 10-restart GA cycle completes in ~22 hours wall-time (parallel execution)
- [ ] Memory usage remains <16GB RAM (GSBsys spec)
- [ ] Code coverage ≥80%
- [ ] Sphinx documentation with API reference

### 8.3 Comparison to Academic Baselines

**vs. MaxAI (Best Academic GA+RL System):**
- [ ] Achieve Profit Factor ≥ MaxAI's 1.07 ✓ (our MVP target: 1.2, Production: 1.5)
- [ ] Pass Pearson equity filter ✓ (MaxAI doesn't use, we require ≥0.85-0.90)
- [ ] Validate across ≥5 OOS periods ✓ (MaxAI uses single 4-year backtest, we use 5 regime windows)
- [ ] Complete faster ✓ (MVP: ~1.5 hours, MaxAI: estimated days-weeks with RL training)
- [ ] Simpler architecture ✓ (pure GA vs GA+RL hybrid)
- [ ] Lower computational cost ✓ (CPU-only vs GPU required)

**vs. GSBsys (Commercial Pure-GA System - our inspiration):**
- [ ] Match GA parameters ✓ (Pop=200, Gen=1000, Restarts=10, CR=95%, MR=5%)
- [ ] Match validation methodology ✓ (Pearson, multi-period OOS, noise, family grouping)
- [ ] Fitness function ✓ (Net Profit × Avg Trade)
- [ ] **Relaxed thresholds** (Pearson 0.90 vs 0.95, PF 1.5 vs 1.8) - more forgiving for public data
- [ ] **Missing proprietary indicators** (15 standard vs 37 total) - documented gap
- [ ] **Free data (MVP)** vs commercial futures data

**vs. Red Queen (Failed GA+RL System):**
- [ ] Pearson filter prevents training/live divergence ✓ (Red Queen lacked this → catastrophic failure)
- [ ] Noise testing catches data-specific overfitting ✓ (Red Queen lacked this)
- [ ] Multi-period OOS prevents regime-specific optimization ✓ (Red Queen lacked this)
- [ ] Simpler architecture prevents mode collapse ✓ (10 restarts vs complex diversity preservation)

### 8.4 Reproduction Fidelity

**Target: ≥90% of documented GSBsys components implemented**

**Fidelity Scoring Methodology:**
- **✓ (Full match)**: Component implemented exactly as documented in GSBsys → 100% credit
- **~✓ (Adapted)**: Core concept implemented but parameters/approach differ → 70% credit
- **✗ (Missing/Approximated)**: Not implemented or significantly different → 0% credit

| Component | GSBsys Spec | GA-Trading-Sys Implementation | Match Type | Score |
|-----------|-------------|------------------------------|------------|-------|
| GA Parameters | Pop=200, Gen=1000, Restarts=10 | Exact match | ✓ | 100% |
| Crossover/Mutation | 95/5, Strength=25% | Exact match | ✓ | 100% |
| Fitness Function | NP × AvgTrade + floors | Exact match | ✓ | 100% |
| Train/Test Split | 40/60 | Exact match | ✓ | 100% |
| Pearson Filter | ≥0.95 | ≥0.90 (relaxed for robustness) | ~✓ | 70% |
| Indicator Pre-Filter | 75 indicators→10 | 15 indicators→10 (limited indicators) | ~✓ | 70% |
| Multi-Period OOS | 5 periods | 5 periods (same regime coverage) | ✓ | 100% |
| Noise Testing | 8 variants | 8 variants | ✓ | 100% |
| Family Grouping | CoV threshold | CoV threshold | ✓ | 100% |
| Walk-Forward GA | Separate stage, 120-150 pop/gen | Exact match (Section 3.2.5 spec) | ✓ | 100% |
| Signal Combination | Multiplicative (ind^weight) | Weighted sum (MVP), multiplicative (Phase 3) | ~✓ | 70% |
| Position Sizing | Fixed fractional | Fixed fractional (2% risk) | ✓ | 100% |
| Commission/Slippage | Modeled ($13.50/side + slippage) | Modeled ($2.50 RT + 1.5 ticks) | ✓ | 100% |
| **Total Components** | **13** | **13** | | |
| **Total Score** | **1300 points** | **1210 points** | | **93% fidelity** |

**Calculation:**
- 10 full matches × 100% = 1000 points
- 3 adapted (Pearson, Indicator Pre-Filter, Signal Combination) × 70% = 210 points
- **Total: 1210 / 1300 = 93%** ✓ **Exceeds 90% target**

**What We're NOT Reproducing (Accepted Gaps):**
1. **Proprietary indicators** (22 GSB_* indicators): Using 15 standard indicators instead
2. **Anchored Stability metric** (Astab): Proprietary formula undocumented
3. **Vertical System Stability** (VSS): Proprietary formula undocumented
4. **F-F fitness metric**: Exact formula undocumented (we use NP × AvgTrade as documented)
5. **1-minute futures data** (MVP): Using daily stock data (yfinance free), upgrade path to Theta Data

**These gaps are DOCUMENTED and do not prevent system functionality** - see [Reproduction-Guide.md](../Reproduction-Guide.md) for full analysis.

---

## 9. Acceptance Tests

### 9.1 End-to-End Integration Test

**Test Case:** Reproduce GSBsys-style optimization on NASDAQ E-mini (NQ) futures

**Setup:**
- Historical NQ data: 2017-2024 (7 years)
- Train: 2017-2019 (40%)
- Test: 2020-2021 (30%)
- Validation: 2022-2024 (30%)

**Procedure:**
1. Load NQ data, normalize indicators
2. Run indicator pre-filtering (rank 15 standard indicators, select top 10)
3. Run 10-restart GA with 200 population, 1000 generations
4. Apply Pearson ≥ 0.95 filter
5. Validate across 5 OOS periods (2020-Q1, 2020-Q2, 2021, 2022, 2023-2024)
6. Noise test with 8 variants (±0.5% price perturbation)
7. Family grouping with 10 parameter variants (±5%)

**Expected Results:**
- At least 1 system passes all validation filters
- System achieves PF ≥ 1.8 on validation set (2022-2024)
- Pearson(train_equity, test_equity) ≥ 0.95
- Noise test: profitable on ≥6/8 variants
- Family CoV ≤ 50%
- Total runtime <10 hours

**Pass Criteria:** All expected results met

---

### 9.2 Pearson Filter Test

**Test Case:** Verify Pearson filter prevents training/live divergence

**Setup:**
- Generate synthetic trading system with intentional train/test divergence
- Train equity: smooth exponential curve
- Test equity: same endpoint, but volatile path (Pearson ~0.60)

**Procedure:**
1. Compute Pearson correlation between train and test equity curves
2. Apply ≥0.95 threshold
3. System should be REJECTED

**Expected Results:**
- Pearson = 0.60 < 0.95 → System rejected
- Log message: "System failed Pearson filter (train/test equity divergence)"

**Pass Criteria:** System correctly rejected

---

### 9.3 Multi-Period OOS Test

**Test Case:** Ensure systems perform consistently across market regimes

**Setup:**
- 5 distinct OOS periods representing different regimes:
  - 2020-Q1: COVID crash (high volatility, downtrend)
  - 2020-Q2-Q4: Recovery (uptrend, moderate volatility)
  - 2021: Retail surge (uptrend, high volume)
  - 2022: Rate hikes (downtrend, moderate volatility)
  - 2023-2024: Sideways (low volatility, range-bound)

**Procedure:**
1. Backtest winning system on each period independently
2. Calculate Profit Factor for each period
3. Require PF > 1.0 in all 5 periods

**Expected Results:**
- System profitable in 5/5 periods (PF > 1.0)
- If any period shows PF < 1.0, system is regime-specific (REJECT)

**Pass Criteria:** 5/5 periods pass PF > 1.0 threshold

---

### 9.4 Noise Robustness Test

**Test Case:** Verify systems aren't overfitting to data quirks

**Setup:**
- Generate 8 noise-perturbed datasets:
  - For each bar: price_noisy = price_original × (1 + random(-0.005, +0.005))
  - 8 different random seeds

**Procedure:**
1. Backtest winning system on all 8 noisy datasets
2. Count how many variants remain profitable (PF > 1.0)
3. Require ≥6/8 pass

**Expected Results:**
- System profitable on ≥6/8 noise variants
- If <6/8, system is data-specific (REJECT)

**Pass Criteria:** ≥6/8 variants pass PF > 1.0 threshold

---

### 9.5 Family Grouping Test

**Test Case:** Ensure parameter stability (low variance across parameter perturbations)

**Setup:**
- Generate 10 parameter variants of winning system
- Perturb each continuous parameter by ±5% (10 different random perturbations)

**Procedure:**
1. Backtest all 10 family members
2. Calculate Sharpe ratio for each
3. Compute Coefficient of Variation: CoV = stddev(Sharpe) / mean(Sharpe)
4. Require CoV ≤ 50%

**Expected Results:**
- Family mean Sharpe: 1.2
- Family stddev Sharpe: ≤0.6 (so CoV = 0.6/1.2 = 50%)
- If CoV > 50%, system is parameter-sensitive (HIGH RISK)

**Pass Criteria:** CoV ≤ 50%

---

### 9.6 Indicator Pre-Filtering Test

**Test Case:** Verify indicator ranking reduces search space correctly

**Setup:**
- 15 standard indicators on ES futures 2017-2019

**Procedure:**
1. Build 10,000 single-indicator systems (random parameters)
2. Rank indicators by median Profit Factor
3. Select top 10 indicators
4. Run GA using only top 10 (not full 15)

**Expected Results:**
- Top 10 indicators identified (e.g., CCI, RSI, DMI might rank highest)
- Search space reduced: C(15,5) = 3,003 → C(10,5) = 252 (12x reduction)
- GA converges faster using top 10 vs. full 15

**Pass Criteria:**
- Top 10 selected successfully
- GA fitness improves faster with pre-filtered set vs. full set

---

### 9.7 Walk-Forward GA Test

**Test Case:** Verify WF-GA optimizes retraining schedule

**Setup:**
- Training data: 2015-2016
- Walk-forward periods: 2017, 2018, 2019 (3 OOS periods)

**Procedure:**
1. Run development GA on 2015-2016 → System A
2. Run walk-forward GA to optimize:
   - Retraining frequency (monthly? quarterly?)
   - Data window size (6 months? 1 year?)
   - Parameter update method (additive? multiplicative?)
3. Test WF-optimized schedule on 2017-2019
4. Compare to baseline (no walk-forward)

**Expected Results:**
- WF-optimized system outperforms baseline in at least 2/3 periods
- WF parameters improve Sharpe, PF, or drawdown

**Pass Criteria:** WF-GA improves performance on ≥2/3 OOS periods

---

### 9.8 Multi-Market Generalization Test

**Test Case:** Verify GA generalizes across different markets (not just single symbol optimization)

**Setup:**
- Run full optimization on 3 stock proxies: SPY (S&P 500), QQQ (NASDAQ), IWM (Russell 2000)
- Same time periods: 2010-2025
- Same GA parameters (200 pop, 1000 gen)
- Train/test/validation: 40/30/30 split

**Procedure:**
1. Optimize each market independently (3 separate GA runs)
2. Validate: At least 1 passing system per market (MVP tier thresholds)
3. Analyze indicator selection overlap across markets
4. Cross-market test: SPY-optimized system → test on QQQ data (measure degradation)

**Expected Results:**
- **3/3 markets produce MVP-passing systems** (PF ≥ 1.2, Pearson ≥ 0.85)
- **Indicator overlap ≥50%**: Common indicators selected (e.g., RSI, CCI, ATR appear in all 3 systems)
  - If overlap <30%: Systems are market-specific (overfitting to symbol)
  - If overlap >70%: Systems capture universal patterns (robust)
- **Cross-market degradation <40%**: SPY system on QQQ achieves ≥60% of original fitness
  - Example: SPY fitness = 1000 → QQQ fitness ≥ 600

**Pass Criteria:**
- 3/3 markets produce passing systems
- Indicator overlap ≥40% (at least 2 shared indicators across all 3 systems)
- Cross-market degradation <50% (system retains ≥50% fitness on different symbol)

**Why This Matters:**
- GSBsys claims multi-market generalization (ES, NQ, YM, GC, CL, DAX)
- If our system only works on SPY, it's overfitting to that specific market microstructure
- Cross-market robustness indicates capturing fundamental price action patterns

**Future Extension (Phase 5):**
- Test on futures (ES, NQ, YM) after Theta Data integration
- Test on commodities (GC, CL) for diversification across asset classes

---

## 10. Risks & Mitigation

### 10.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GA doesn't converge within 1,000 generations | High | Medium | Increase generations to 2,000; tune crossover/mutation rates; add adaptive operators |
| Fitness evaluations too slow (>100ms each) | High | Low | Use vectorized backtesting (VectorBT); parallelize across restarts; profile and optimize hot paths |
| Indicator formulas don't match TA-Lib | Medium | Low | Validate against known test cases; use TA-Lib directly when possible |
| Pearson filter too strict (rejects all systems) | High | Medium | Tune threshold (0.90-0.95); visualize equity curves to debug divergence |
| Noise testing too strict (rejects all systems) | Medium | Medium | Tune noise level (0.1%-1%); adjust pass threshold (5/8 instead of 6/8) |
| Memory overflow with 200 population | Medium | Low | Use memory-efficient data structures; offload historical data to disk; reduce population to 100 if needed |

### 10.2 Reproducibility Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GSBsys proprietary indicators cannot be approximated | High | High | **ACCEPTED RISK** - Use 15 standard indicators, document gap as limitation |
| Random seed mismanagement breaks reproducibility | Medium | Medium | Centralize RNG seeding; log all seeds; add reproducibility tests to CI/CD |
| Floating-point precision differences across platforms | Low | Medium | Use fixed precision (np.float64); add tolerance to assertions (±0.01%) |

### 10.3 Validation Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Overfitting despite multi-stage validation | High | Low | Add additional robustness tests (Monte Carlo resampling); require longer validation periods (3+ years) |
| Systems fail in live trading despite passing validation | High | Low | **Out of scope for MVP** - Paper trading recommended before live deployment; add monitoring dashboard (future phase) |
| Market regime shift invalidates all validated systems | High | Low | Regular retraining via walk-forward; maintain diverse system portfolio; monitor performance degradation |

### 10.4 Project Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Scope creep (too many features) | Medium | High | Strict phase gating; MVP focuses on Tier 1+2 only; defer Tier 3 features to post-release |
| Insufficient testing coverage | Medium | Medium | TDD approach; target 80% code coverage; integration tests for each acceptance criterion |
| Documentation lags behind code | Low | High | Generate API docs from docstrings; update user guide each sprint; treat docs as deliverable |

---

## 11. Open Questions & Future Work

### 11.1 Research Questions

1. **Pure GA vs. GA+RL:** Can pure GA with rigorous validation match GA+RL performance?
   - Hypothesis: Yes, based on GSBsys commercial success vs. academic GA+RL failures (Red Queen)
   - Test: Compare GA-Trading-Sys to MaxAI (best academic GA+RL) on same NQ dataset

2. **Optimal Train/Test Split:** Is 40/60 always better than 60/40?
   - Hypothesis: Depends on data availability and market stability
   - Test: Sweep train/test ratios (30/70, 40/60, 50/50, 60/40), measure OOS degradation

3. **Indicator Pre-Filtering:** Does greedy single-indicator ranking miss synergistic combinations?
   - Hypothesis: Possibly, but empirical success of GSBsys suggests it's acceptable
   - Test: Compare pre-filtered GA vs. full search on small indicator set (10 vs. 15 total)

4. **Restart vs. Diversity Preservation:** Are 10 restarts better than single run with niching?
   - Hypothesis: Restarts simpler and equally effective
   - Test: Compare 10×1000-gen restarts vs. 1×10000-gen with diversity operators

### 11.2 Future Enhancements

**Post-MVP (Phase 6+):**
- Multi-objective optimization (Pareto frontier: return vs. risk)
- Adaptive mutation rates (anneal as GA converges)
- Island model GA (multiple populations with migration)
- Neural architecture search for custom indicators
- Reinforcement learning for adaptive entry/exit (GA+RL hybrid)
- Live trading connector (Interactive Brokers, Alpaca)
- Performance monitoring dashboard (track live vs. backtest divergence)

**Advanced Validation:**
- Adversarial stress testing (worst-case scenarios)
- Ensemble systems (combine multiple GA-evolved strategies)
- Regime detection (auto-switch systems based on detected market state)

---

## 12. References & Bibliography

### 12.1 GSBsys Documentation

1. **Official Website:** https://trademaid.info/gsbhelp/
2. **Key Pages:**
   - GeneticAlgorithm.html
   - Optimization.html
   - Methodology.html
   - BuildingNasdaqSP500orDowsystems.html
3. **Internal Documentation:**
   - [README.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/README.md)
   - [GA-Architecture.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/GA-Architecture.md)
   - [Indicator-System.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Indicator-System.md)
   - [Methodology.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Methodology.md)
   - [Technical-Specifications.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Technical-Specifications.md)
   - [Comparison-to-Research.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Comparison-to-Research.md)
   - [Key-Insights.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Key-Insights.md)
   - [Reproduction-Guide.md](/Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Reproduction-Guide.md)

### 12.2 Academic GA+RL Research

1. **GA+RL-Result3-FINAL.md** - Systematic review of GA+RL hybrids in finance
2. **MaxAI (C07)** - Best academic GA+RL system (4-month live validation, PF 1.07)
3. **Red Queen (C09)** - Failed GA+RL system (catastrophic live capital decay)
4. **DERL (C06)** - Nested GA+RL architecture (+58% over baseline RL)

### 12.3 Technical References

1. **DEAP:** Distributed Evolutionary Algorithms in Python (https://deap.readthedocs.io/)
2. **TA-Lib:** Technical Analysis Library (https://ta-lib.org/)
3. **VectorBT:** Fast backtesting library (https://vectorbt.dev/)
4. **Backtrader:** Event-driven backtesting (https://www.backtrader.com/)

---

## 13. Team & Resources

### 13.1 Team Composition

**MVP Team (Phases 1-4): 1 FTE Solo Developer**

| Role | FTE | Skills Required | Responsibilities |
|------|-----|-----------------|------------------|
| **Full-Stack GA Developer** | 1.0 | Python (advanced), DEAP, NumPy/Pandas, VectorBT, TA-Lib, Git, pytest, Sphinx | All development, testing, documentation |

**Required Skills (Priority Order):**
1. **Python** (advanced): NumPy, Pandas, type hints, multiprocessing
2. **Genetic Algorithms**: DEAP framework, chromosome encoding, fitness functions
3. **Financial Data**: OHLCV structure, technical indicators, backtesting concepts
4. **Backtesting**: VectorBT (vectorized backtesting), performance metrics
5. **Software Engineering**: Git, pytest (TDD), documentation (Sphinx)
6. **Domain Knowledge**: Futures trading, position sizing, commission models (nice-to-have)

**Learning Curve Estimate:**
- Python ecosystem (DEAP, VectorBT): 1-2 weeks
- Financial domain (if unfamiliar): 2-3 weeks
- GSBsys methodology: 1 week (reading documentation)

### 13.2 Hardware Requirements

**Minimum Spec (Solo Developer):**
- **CPU**: 8 cores (Intel i7/i9 or AMD Ryzen 7/9) - for parallel restarts
- **RAM**: 16 GB (GSBsys minimum spec)
- **Storage**: 100 GB SSD (data + results)
- **GPU**: Not required for MVP (CPU-only VectorBT sufficient)

**Recommended Spec (Production):**
- **CPU**: 12-16 cores (Ryzen 9 / Threadripper / Xeon) - faster parallel restarts
- **RAM**: 32 GB (enables larger datasets, future GPU work)
- **Storage**: 500 GB NVMe SSD (fast data access)
- **GPU**: NVIDIA RTX 3060+ (12GB VRAM) - Phase 5 GPU acceleration

**Cloud Alternative (Optional):**
- AWS c6i.4xlarge (16 vCPU, 32 GB RAM): $0.68/hour
- For 32-week project (5 hours/day dev work): ~$500 total
- Spot instances: 50-70% discount

### 13.3 Software Requirements

**Development Environment:**
- **OS**: Windows, macOS, or Linux (cross-platform support)
- **Python**: 3.10+ (type hints, dataclasses)
- **IDE**: VS Code, PyCharm, or Cursor (with Python extensions)
- **Git**: Version control (GitHub/GitLab for repo hosting)

**Production Dependencies:**
```bash
# Core
python>=3.10
numpy>=1.24
pandas>=2.0
deap>=1.4
pyyaml>=6.0
pydantic>=2.0

# Backtesting
vectorbt>=0.26
ta-lib>=0.4  # Requires C library installation

# Visualization
matplotlib>=3.7
plotly>=5.14

# CLI
click>=8.1 or typer>=0.9
tqdm>=4.65  # Progress bars

# Data
yfinance>=0.2  # MVP data source

# Testing
pytest>=7.3
pytest-cov>=4.1

# Documentation
sphinx>=6.2
sphinx-rtd-theme>=1.2
```

### 13.4 Data Requirements & Costs

**MVP (Phases 1-4): Free Data**
- **Source**: yfinance (Yahoo Finance)
- **Cost**: $0
- **Coverage**: Daily stock data (SPY, QQQ, IWM) 2010-present
- **Limitation**: No 1-minute futures data

**Production (Phase 5+): Paid Data**
- **Source**: Theta Data (recommended)
- **Cost**: $150/month
- **Coverage**: 1-minute futures (ES, NQ, YM, CL, GC) 2015-present
- **Alternative**: NinjaTrader Lifetime ($1000 one-time) or Interactive Brokers (free with account)

### 13.5 Budget Estimate (Solo Developer)

| Item | Cost (MVP) | Cost (Production) | Notes |
|------|------------|-------------------|-------|
| **Developer Salary** | $0 (hobby) or $40k (8 months @ $60k/year) | Same | Solo developer time |
| **Hardware** | $0 (assume existing laptop) | $2000 (if purchasing new workstation) | 16-core CPU, 32GB RAM |
| **Data** | $0 (yfinance free) | $1200 ($150/month × 8 months) | Theta Data subscription |
| **Software** | $0 (all open-source) | $0 | Python ecosystem is free |
| **Cloud** (optional) | $0 (local dev) | $500 (AWS spot instances) | If local hardware insufficient |
| **TradeStation** (Phase 5) | $0 (deferred) | $800 ($99/month × 8 months) | For EasyLanguage generation testing |
| **Total (excluding salary)** | **$0** | **$4500** | Realistic production cost |
| **Total (including salary)** | **$40k** | **$44.5k** | Freelancer/contractor rate |

### 13.6 Risk Mitigation (Solo Developer)

| Risk | Mitigation |
|------|------------|
| **Single point of failure** | Comprehensive documentation, Git version control, weekly backups |
| **Skill gaps** | Budget 3-4 weeks learning curve, leverage online resources (DEAP docs, VectorBT tutorials) |
| **Scope creep** | Strict phase gating, defer Phase 5 features to post-MVP |
| **Burnout** | 32 weeks is manageable if paced (20-30 hrs/week side project), take breaks between phases |
| **Debugging delays** | TDD approach (write tests first), extensive logging, reproducible random seeds |

### 13.7 Scaling to Team (Future)

**If scaling from 1 FTE to 2-3 FTE team:**

| Role | FTE | Focus | Timeline Impact |
|------|-----|-------|-----------------|
| GA Developer | 1.0 | Core GA engine, optimization | Primary developer |
| Backtesting Engineer | 0.5 | VectorBT, indicators, validation | Halves Phase 1-2 time |
| QA/Testing | 0.5 | pytest, integration tests, documentation | Improves quality, adds coverage |

**Timeline with 2 FTE team:**
- Phase 1: 6 weeks (vs 12 solo)
- Phase 2: 4 weeks (vs 8 solo)
- Phase 3: 3 weeks (vs 6 solo)
- Phase 4: 3 weeks (vs 6 solo)
- **Total: 16 weeks (4 months)** vs 32 weeks solo

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **AIC** | Any Indicators Cross - entry mode that triggers when any weighted indicator crosses threshold (OR logic) |
| **ATR** | Average True Range - volatility indicator measuring average price range |
| **Chromosome** | Individual solution encoding in GA (e.g., [indicator_ids, params, weights, stops]) |
| **Compare2** | Entry mode that triggers when signal strength exceeds two-indicator baseline comparison |
| **CoV** | Coefficient of Variation - stddev / mean (measures relative parameter sensitivity) |
| **Equity Curve** | Cumulative profit/loss over time plotted as line chart |
| **Fitness** | Objective function score (higher = better individual). Our fitness: Net Profit × Avg Trade |
| **GA** | Genetic Algorithm - evolutionary optimization technique mimicking natural selection |
| **Generation** | Iteration of GA (selection → crossover → mutation → fitness evaluation) |
| **HighestLowest** | Normalization method: maps indicator to [-100, +100] range using rolling highest/lowest values |
| **NCC** | No Conflict Cross - entry mode that triggers only when no opposing signals exist (AND logic) |
| **OOS** | Out-of-Sample - data not used during training (test/validation set) to measure generalization |
| **Panama Method** | Continuous futures contract rollover adjustment: back-adjusts historical prices to eliminate gaps at contract expiry |
| **Pearson** | Pearson correlation coefficient (measures linear relationship strength, -1 to +1). Used to compare equity curve shapes. |
| **PF** | Profit Factor - gross profit / gross loss (PF > 1.0 = profitable, PF < 1.0 = losing) |
| **Population** | Set of candidate solutions in GA (e.g., 200 trading systems) |
| **Regime** | Market condition characterized by trend and volatility (bull/bear/sideways, high-vol/low-vol) |
| **Restart** | Independent GA run with new random seed (diversity mechanism) |
| **RL** | Reinforcement Learning - agent-based learning via trial-and-error rewards |
| **SBX** | Simulated Binary Crossover - GA crossover operator for continuous variables (indicator params, weights) |
| **Walk-Forward** | Rolling retraining methodology: optimize on past data, test on future data, advance window, repeat |

---

## Appendix B: Configuration Example

```yaml
# ga-trading-sys-config.yaml
project:
  name: "NQ-Futures-Strategy"
  data_source: "data/NQ_1min_2017-2024.csv"
  output_dir: "results/nq_optimization"
  random_seed: 42

data:
  symbol: "NQ"
  interval: "1min"
  train_start: "2017-01-01"
  train_end: "2019-12-31"
  test_start: "2020-01-01"
  test_end: "2021-12-31"
  validation_start: "2022-01-01"
  validation_end: "2024-12-31"
  train_test_split: [0.4, 0.6]
  normalize_range: [-100, 100]

indicators:
  standard:
    - name: "RSI"
      param_range: [10, 50]
    - name: "CCI"
      param_range: [10, 100]
    - name: "Stochastic"
      param_range: [5, 50]
    - name: "ADX"
      param_range: [10, 30]
    - name: "ATR"
      param_range: [10, 50]
    - name: "MACD"
      fast_range: [8, 15]
      slow_range: [20, 30]
      signal_range: [7, 12]
  pre_filter:
    enabled: true
    top_n: 10
    ranking_metric: "profit_factor"
    single_indicator_trials: 10000

ga:
  development:
    population_size: 200
    generations: 1000
    restarts: 10
    crossover_rate: 0.95
    mutation_rate: 0.05
    mutation_strength: 0.25
    tournament_size: 3
    elitism: 2

  walk_forward:
    enabled: true
    population_size: 120
    generations: 120

  chromosome:
    indicator_count_range: [2, 5]
    indicator_weight_range: [-1.0, 2.0]
    stop_loss_range: [200, 2000]  # dollars
    trailing_stop_range: [100, 1000]  # dollars

fitness:
  primary_function: "net_profit * avg_trade"

  # Tiered validation thresholds
  mvp_tier:
    pearson_floor: 0.85
    profit_factor_train_floor: 1.2
    profit_factor_test_floor: 1.2
    profit_factor_validation_floor: 1.2
    min_trades: 30
    max_drawdown_pct: 30

  production_tier:
    pearson_floor: 0.90
    profit_factor_train_floor: 1.2
    profit_factor_test_floor: 1.2
    profit_factor_validation_floor: 1.5
    min_trades: 50
    max_drawdown_pct: 25

validation:
  oos_periods:
    - {start: "2020-01-01", end: "2020-03-31", name: "COVID Crash"}
    - {start: "2020-04-01", end: "2020-12-31", name: "Recovery"}
    - {start: "2021-01-01", end: "2021-12-31", name: "Retail Surge"}
    - {start: "2022-01-01", end: "2022-12-31", name: "Rate Hikes"}
    - {start: "2023-01-01", end: "2024-12-31", name: "Sideways"}

  noise_testing:
    enabled: true
    variants: 8
    noise_level: 0.005  # ±0.5%
    pass_threshold: 0.75  # 6/8 variants

  family_grouping:
    enabled: true
    variants: 10
    perturbation: 0.05  # ±5%
    cov_threshold: 0.50

output:
  export_formats: ["easylanguage", "python"]
  generate_reports: true
  plot_equity_curves: true
  save_population_history: true
  log_level: "INFO"

performance:
  parallel_restarts: true
  max_workers: 10
  vectorized_backtest: true
  cache_indicator_calcs: true
```

---

**END OF PRODUCT REQUIREMENTS DOCUMENT**
