# GSBsys Reproduction Guide

## Overview

This document identifies what information is **available** vs. **missing** from the GSBsys documentation for reproducing the system.

**Key Finding:** The official documentation (https://trademaid.info/gsbhelp/) is **user-facing**, not developer-facing. Most low-level implementation details are proprietary and not documented.

---

## What IS Documented (Reproducible)

### 1. High-Level Architecture

**Source:** https://trademaid.info/gsbhelp/GSBArchitecture1.html

```python
# Signal Combination Formula
result = indicator1 * indicator2 * indicator3

# With Weights
result = indicator1**weight1 * indicator2**weight2 * indicator3**weight3

# Entry Logic
if secondary_filter > 0 and result > entry_level:
    buy()
elif secondary_filter < 0 and result < entry_level:
    sell_short()
```

**Parameters:**
- Indicators normalized to [-100, +100] range
- Weights range: -1 to +2 (from screenshots)
- EntryLevel: threshold value (user-configurable)

**Secondary Filter Options:**
```python
# Standard
secondary_filter = close - close[1]

# Crude Oil variant
secondary_filter = close / high_daily[1]

# Or: Genetically selected indicator
```

---

### 2. Entry Mode Algorithms

**Source:** https://trademaid.info/gsbhelp/EntryModes.html

**AIC (Any Indicators Cross)** - Recommended for ES/NQ:
```python
# Long entry
if any(indicator > 0 for indicator in indicators):
    buy()

# Short entry
if any(indicator < 0 for indicator in indicators):
    sell_short()
```

**NCC (No Conflict Cross):**
```python
# Long entry
if indicator crosses above 0 and no_conflicting_downward_crosses:
    buy()

# Short entry
if indicator crosses below 0 and no_conflicting_upward_crosses:
    sell_short()
```

**Compare2:**
```python
if result > entry_level and result[1] > entry_level:
    buy()
if result < entry_level and result[1] < entry_level:
    sell_short()
```

**Critical:** AIC and NCC modes **do not use EntryLevel or weights**. These parameters should be optimized with ranges -90 to 90 in 5-step increments instead.

---

### 3. 5-Part Methodology

**Source:** https://trademaid.info/gsbhelp/Methodology.html, https://trademaid.info/gsbhelp/BeforeweBegin.html

**Part A: Establish Baseline**
```
1. Build 50,000 systems
2. Rank by F-F metric (fitness function)
3. Select top 250 systems
4. Apply walk-forward testing
5. Filter through Astab-C (90 systems) and VSS (91 systems)
6. Record statistics across multiple periods
```

**Part B: Identify Top Indicators**
```
1. Build 20,000 systems using single indicators
2. Select top 10,000 by F-F metric
3. Identify 9-11 best-performing indicators
```

**Part C: Rebuild with Reduced Set**
```
1. Build 50,000 systems using only top 9-11 indicators
2. Apply same filtering as Part A
3. Compare to baseline performance
```

**Part D: Optimize Parameters (optional)**
```
1. Test normalization modes
2. Test indicator counts (2-5)
3. Test secondary data streams
4. Test entry types
```

**Part E: Select Trading Systems**
```
1. Choose best filter approach (Astab-C or VSS)
2. Organize into families
3. Select top family members for trading
```

**Key Principle:** "Change only one thing at a time" to isolate improvement sources

---

### 4. GA Parameters (from Screenshots)

**Confirmed Values:**
- Population: 200
- Generations: 1,000
- Restarts: 10 (default, adjustable)
- Crossover Rate: 95%
- Mutation Rate: 5%
- Mutation Strength: 25%

**Derived:**
- Total evaluations per restart: 200,000
- Max total evaluations: 2,000,000
- Total combinations tested: 20,000,000

---

### 5. Configuration Parameters (from Screenshots & Website)

**Optimization:**
- Optimizer Type: GeneticAlgorithm (exhaustive search not recommended)
- Training %: 40 (recommended 30-50%)
- Test %: 60
- Test @ Beginning: False

**Strategy:**
- Number of Indicators: 2-5 (3 typical)
- Built-In Indicators: 37 available
- Normalization Modes: 2 enabled (HighestLowest confirmed)
- Normalization Length: 100 bars

**Walk-Forward:**
- WF Generations × Population: 100×100 to 150×150
- 3 indicators: 120×120 minimum
- 4-5 indicators: 150×150 minimum

**Trading:**
- Commission: $13.50 per side (example)
- Position Sizing: CapitalInvestment preferred over fixed shares

---

### 6. Validation Thresholds

**From Website & Screenshots:**
- Pearson Correlation (train/test): ≥ 0.95
- Profit Factor (train/test): ≥ 1.2
- Profit Factor (validation): ≥ 1.8
- Anchored Stability: ≥ 40 (improved OOS results)
- NP/DD Ratio: 25-20 range for top systems

---

### 7. Family Grouping

**Source:** https://trademaid.info/gsbhelp/Families.html

**Definition:** "Families are a group of systems that have the same indicators but are not identical"

**Principle:** "A family with many members means the systems are robust regardless of the parameters"

**Selection:** Prefer families where "most or all members have good out of sample results"

**Warning:** High variance between family members indicates parameter sensitivity (overfitting)

**Minimum:** Ideally 3+ members per family

---

## What is NOT Documented (Requires Reverse Engineering)

### 1. Indicator Formulas ❌

**Missing:**
- Mathematical formulas for all 37 built-in indicators
- Calculation methods for proprietary GSB_ indicators
- Normalization algorithm specifics
- Parameter ranges for each indicator

**What we know:**
- Indicator names (TrueRange, CCI, DMI, etc.)
- Performance rankings (from screenshots)
- Normalized output range: [-100, +100]

**To reproduce:** Would need to:
- Implement standard indicators (TrueRange, ADX, RSI) from public specifications
- Reverse-engineer proprietary GSB_ indicators from behavior
- Determine normalization formula (likely: `(raw - min) / (max - min) * 200 - 100`)

---

### 2. Fitness Function (F-F Metric) ❌

**Missing:**
- Exact formula for F-F metric
- How Net Profit × Average Trade is calculated
- Whether transaction costs are included in fitness
- How multiple objectives are weighted

**What we know:**
- Primary metric: Net Profit × Average Trade (from screenshots)
- Floor filters: Pearson ≥ 0.95, PF ≥ 1.2 (train), PF ≥ 1.8 (validation)
- Systems ranked by F-F metric

**To reproduce:** Possible implementation:
```python
def fitness_function(system, backtest_results):
    # Calculate metrics
    net_profit = backtest_results.total_profit - backtest_results.total_loss
    avg_trade = net_profit / backtest_results.num_trades
    profit_factor = backtest_results.total_profit / backtest_results.total_loss
    pearson = correlation(backtest_results.equity_train, backtest_results.equity_test)

    # Apply hard filters
    if pearson < 0.95:
        return -np.inf
    if profit_factor < 1.2:
        return -np.inf

    # Calculate fitness
    fitness = net_profit * avg_trade

    return fitness
```

---

### 3. GA Selection Method ❌

**Missing:**
- Selection algorithm (tournament? roulette? rank?)
- Tournament size (if tournament selection)
- Elitism strategy (how many top individuals preserved?)
- Selection pressure

**What we know:**
- Population: 200
- Max Crossover Attempts exists (suggests selection can produce similar parents)

**To reproduce:** Standard options:
```python
# Tournament selection (likely)
def tournament_selection(population, fitness_scores, tournament_size=3):
    tournament = random.sample(zip(population, fitness_scores), tournament_size)
    return max(tournament, key=lambda x: x[1])[0]

# Or: Roulette wheel selection
# Or: Rank-based selection
```

---

### 4. Crossover Operator ❌

**Missing:**
- Crossover type (single-point? two-point? uniform? blend?)
- How discrete genes (indicator IDs) are recombined
- How continuous genes (parameters, weights) are recombined
- Crossover points selection

**What we know:**
- Crossover Rate: 95%
- Max Crossover Attempts parameter exists
- Hybrid discrete-continuous chromosome

**To reproduce:** Likely implementation:
```python
def crossover(parent1, parent2):
    child = {}

    # Discrete genes (indicator IDs): uniform crossover
    child['indicator_ids'] = []
    for i in range(num_indicators):
        child['indicator_ids'].append(
            random.choice([parent1['indicator_ids'][i],
                          parent2['indicator_ids'][i]])
        )

    # Continuous genes (parameters, weights): blend crossover
    alpha = 0.5  # blend parameter
    for param in ['weights', 'entry_level', 'stop_loss']:
        child[param] = alpha * parent1[param] + (1 - alpha) * parent2[param]

    return child
```

---

### 5. Mutation Operator ❌

**Missing:**
- Mutation type (Gaussian? Uniform? Polynomial?)
- How 25% mutation strength is applied
- Whether discrete and continuous genes mutate differently
- Mutation probability per gene vs. per individual

**What we know:**
- Mutation Rate: 5%
- Mutation Strength: 25%

**To reproduce:** Possible implementation:
```python
def mutate(individual, mutation_strength=0.25):
    if random.random() < 0.05:  # 5% mutation rate
        # For continuous genes
        for param in ['weights', 'entry_level', 'stop_loss']:
            param_range = param_max - param_min
            individual[param] += random.uniform(-mutation_strength, mutation_strength) * param_range
            individual[param] = clip(individual[param], param_min, param_max)

        # For discrete genes (indicator IDs)
        if random.random() < 0.05:
            idx = random.randint(0, len(individual['indicator_ids']) - 1)
            individual['indicator_ids'][idx] = random.choice(available_indicators)

    return individual
```

---

### 6. Anchored Stability (Astab) Metric ❌

**Missing:**
- Complete formula
- How stability is quantified
- What "anchored" means algorithmically
- Calculation method

**What we know:**
- Astab ≥ 40 shows improved OOS results
- Used to filter systems (90 systems pass Astab-C)
- Proprietary metric

**To reproduce:** Hypothesis (requires testing):
```python
def anchored_stability(system, multiple_test_periods):
    # Possible approach: variance of performance across OOS periods
    performances = []
    for period in multiple_test_periods:
        perf = backtest(system, period)
        performances.append(perf.sharpe_ratio)

    # Lower variance = higher stability
    stability = 100 - (np.std(performances) * scaling_factor)
    return stability
```

---

### 7. VSS (Vertical System Stability) Metric ❌

**Missing:**
- Complete formula
- Calculation method
- What "vertical" means in this context

**What we know:**
- Used to filter systems (91 systems pass VSS)
- Alternative to Astab-C
- Proprietary metric

**To reproduce:** Unknown - would require access to VSS-selected systems to reverse-engineer.

---

### 8. Walk-Forward Anchoring Algorithm ❌

**Missing:**
- How walk-forward parameters are anchored to historical data
- What gets optimized in the WF-GA stage
- How weights are updated (additive vs. multiplicative mentioned but not detailed)
- When adjustments occur relative to WF completion

**What we know:**
- WF parameters validated on pre-2017 data
- "WF parameters better in EVERY metric in all 3 tests"
- May 2019 update changed from multiplication to addition operators

**To reproduce:** Standard walk-forward with unknown anchoring:
```python
def walk_forward(system, data, wf_window_size, wf_step_size):
    results = []
    for i in range(0, len(data) - wf_window_size, wf_step_size):
        train_data = data[i:i+wf_window_size]
        test_data = data[i+wf_window_size:i+wf_window_size+wf_step_size]

        # Optimize system on train_data
        optimized = ga_optimize(system, train_data)

        # Test on test_data
        result = backtest(optimized, test_data)
        results.append(result)

        # ??? Unknown: How to "anchor" for next iteration

    return results
```

---

### 9. Noise Injection Testing ❌

**Missing:**
- Noise generation method
- Noise magnitude (what % of typical bar range?)
- How many noise variants (document says 8)
- Pass/fail criteria (6/8? 7/8?)

**What we know:**
- Creates 8 randomized data variants
- Systems must remain profitable across variants
- Purpose: catch data-specific overfitting

**To reproduce:** Hypothesis:
```python
def noise_injection_test(system, data, num_variants=8, noise_level=0.005):
    results = []
    for _ in range(num_variants):
        noisy_data = data.copy()
        noisy_data['close'] *= (1 + np.random.uniform(-noise_level, noise_level, len(data)))
        noisy_data['high'] *= (1 + np.random.uniform(-noise_level, noise_level, len(data)))
        noisy_data['low'] *= (1 + np.random.uniform(-noise_level, noise_level, len(data)))

        result = backtest(system, noisy_data)
        results.append(result.net_profit > 0)

    # Pass if profitable on at least 6/8 variants
    return sum(results) >= 6
```

---

### 10. Normalization Modes ❌

**Missing:**
- HighestLowest formula specifics
- Second normalization mode formula
- How modes interact with indicators

**What we know:**
- 2 modes enabled
- Mode 1: HighestLowest (confirmed)
- Mode 2: Unknown
- Normalization Length: 100 bars

**To reproduce:** Standard HighestLowest normalization:
```python
def normalize_highest_lowest(indicator_values, length=100):
    normalized = []
    for i in range(len(indicator_values)):
        if i < length:
            window = indicator_values[:i+1]
        else:
            window = indicator_values[i-length+1:i+1]

        highest = max(window)
        lowest = min(window)

        if highest == lowest:
            norm = 0
        else:
            norm = (indicator_values[i] - lowest) / (highest - lowest) * 200 - 100

        normalized.append(norm)

    return normalized
```

---

### 11. Backtesting Engine ❌

**Missing:**
- Order execution logic
- Slippage model
- Commission calculation method
- Position sizing algorithm
- Risk management implementation
- Profit target / stop loss execution logic

**What we know:**
- Commission: $13.50 per side (example)
- Slippage: embedded but method unknown
- Stop loss types: Fixed, Trailing, ATR, Plock variants
- Market-on-close execution for day trading

**To reproduce:** Standard backtesting framework needed with proper execution simulation.

---

### 12. Early-Stop Reset-and-Restart Logic ❌

**Missing:**
- How "stopped improving" is detected
- What % threshold triggers restart
- Whether best-so-far is preserved across restarts
- How random seed is reset

**What we know:**
- If GA stops before N% of total tests, auto-restart
- Each restart gets new random seed
- Up to 10 restarts total

**To reproduce:** Hypothesis:
```python
def ga_with_restarts(population_size=200, generations=1000, max_restarts=10):
    best_overall = None

    for restart in range(max_restarts):
        # New random seed
        np.random.seed(int(time.time() * 1000) + restart)

        # Initialize population
        population = initialize_population(population_size)

        # Run GA
        best_this_run = None
        no_improvement_count = 0
        for gen in range(generations):
            population, best = evolve_generation(population)

            if best_this_run is None or best.fitness > best_this_run.fitness:
                best_this_run = best
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            # Early stop if no improvement for 20% of generations?
            if no_improvement_count > generations * 0.2:
                print(f"Early stop at generation {gen}, restarting...")
                break

        # Track best across all restarts
        if best_overall is None or best_this_run.fitness > best_overall.fitness:
            best_overall = best_this_run

    return best_overall
```

---

## Data Requirements

### Available Information

**Data Format:**
- Source: @ES, @NQ (not @ES.D or @NQ.D)
- Timeframes: 30-minute bars typical, 15-minute for diversification
- Start time: 8:00 AM
- Earliest trade: 9:00 AM

**Historical Periods:**
- In-sample: 2007-2018 typical
- OOS periods: 2017-2021+ (5+ distinct windows)

### Missing Information

**Data Structure:**
- File format (CSV? Binary?)
- Required fields (OHLCV? Additional?)
- Date/time format
- How to handle gaps, missing data
- Contract rollover handling for futures

---

## Reproduction Strategy

### What You CAN Reproduce

**Tier 1 - High Confidence:**
1. ✅ Signal combination architecture (multiplication, weights)
2. ✅ Entry mode algorithms (AIC, NCC, Compare2)
3. ✅ 5-part methodology workflow
4. ✅ GA parameters (population, generations, crossover/mutation rates)
5. ✅ Configuration settings (train/test split, etc.)
6. ✅ Validation thresholds (Pearson, PF)
7. ✅ Family grouping concept

**Tier 2 - Moderate Confidence (requires standard implementations):**
1. ⚠️ Standard indicators (TrueRange, RSI, ADX, etc.) - use TA-Lib or similar
2. ⚠️ Normalization (HighestLowest likely standard)
3. ⚠️ Basic fitness function (Net Profit × Avg Trade)
4. ⚠️ Standard GA operators (tournament selection, blend crossover, Gaussian mutation)
5. ⚠️ Walk-forward testing (standard rolling window)

### What You CANNOT Reproduce

**Tier 3 - Proprietary / Reverse Engineering Required:**
1. ❌ Proprietary GSB_ indicators (22 of 37 indicators)
2. ❌ Exact F-F metric formula
3. ❌ Anchored Stability (Astab) calculation
4. ❌ VSS (Vertical System Stability) calculation
5. ❌ Walk-forward anchoring algorithm
6. ❌ Noise injection specifics
7. ❌ Second normalization mode
8. ❌ Early-stop restart trigger logic
9. ❌ Exact selection/crossover/mutation implementations

---

## Recommended Approach

### Phase 1: Core System (Reproducible)

```python
# 1. Implement signal combination
def calculate_signal(indicators, weights):
    result = 1
    for indicator, weight in zip(indicators, weights):
        result *= indicator ** weight
    return result

# 2. Implement entry logic
def check_entry(signal, secondary_filter, entry_level):
    if secondary_filter > 0 and signal > entry_level:
        return "BUY"
    elif secondary_filter < 0 and signal < -entry_level:
        return "SELL"
    return "HOLD"

# 3. Implement GA with known parameters
ga = GeneticAlgorithm(
    population_size=200,
    generations=1000,
    crossover_rate=0.95,
    mutation_rate=0.05,
    mutation_strength=0.25,
    restarts=10
)

# 4. Implement fitness with known floors
def fitness(system, data):
    train_result = backtest(system, data[:40%])
    test_result = backtest(system, data[40%:])

    pearson = correlation(train_result.equity, test_result.equity)
    if pearson < 0.95:
        return -np.inf

    pf = test_result.gross_profit / test_result.gross_loss
    if pf < 1.2:
        return -np.inf

    return test_result.net_profit * test_result.avg_trade
```

### Phase 2: Standard Indicators (TA-Lib)

```python
import talib

# Implement normalization
def normalize_indicator(values, length=100):
    normalized = []
    for i in range(len(values)):
        window = values[max(0, i-length+1):i+1]
        high = max(window)
        low = min(window)
        norm = (values[i] - low) / (high - low) * 200 - 100 if high != low else 0
        normalized.append(norm)
    return np.array(normalized)

# Use standard indicators
indicators = {
    'TrueRange': normalize_indicator(talib.TRANGE(high, low, close)),
    'RSI': normalize_indicator(talib.RSI(close)),
    'ADX': normalize_indicator(talib.ADX(high, low, close)),
    'CCI': normalize_indicator(talib.CCI(high, low, close)),
    # etc.
}
```

### Phase 3: Proprietary Components (Best-Effort)

```python
# For proprietary indicators, try to infer from behavior:
# 1. Run GSBsys if available
# 2. Export signals for proprietary indicators
# 3. Reverse-engineer formulas from output
# 4. Validate against known patterns

# For metrics (Astab, VSS), use proxies:
def proxy_anchored_stability(system, oos_periods):
    # Use coefficient of variation as stability proxy
    performances = [backtest(system, period).sharpe for period in oos_periods]
    cv = np.std(performances) / np.mean(performances) if np.mean(performances) != 0 else np.inf
    return 100 - cv * 100  # Scale to Astab-like metric
```

### Phase 4: Validation

```python
# Test reproduction against GSBsys output:
# 1. Generate same systems in both
# 2. Compare rankings
# 3. Measure correlation of fitness scores
# 4. Validate family groupings match
# 5. Compare OOS performance

# Acceptance criteria:
# - Top 100 systems overlap >= 70%
# - Fitness correlation >= 0.90
# - OOS performance within ±15%
```

---

## Critical Gaps Summary

**To fully reproduce GSBsys, you would need:**

1. **Proprietary indicator formulas** - 22 of 37 indicators are GSB-specific
2. **Exact fitness function** - We know components but not exact formula
3. **Stability metrics** - Astab and VSS calculations are proprietary
4. **Walk-forward anchoring** - Algorithm unclear
5. **Noise testing specifics** - Magnitude, pass/fail criteria
6. **GA operator details** - Selection, crossover, mutation specifics

**Without these, best approach:**
- Implement what IS documented (60-70% of system)
- Use standard algorithms for missing pieces
- Validate by comparing results to GSBsys output
- Iterate on proxies until performance matches

**Or:** Purchase GSBsys ($200-$799) and use it as intended, rather than attempting full reproduction.

---

## Conclusion

The GSBsys documentation provides:
- ✅ **High-level architecture** (fully documented)
- ✅ **Methodology workflow** (fully documented)
- ✅ **GA parameters** (confirmed from screenshots)
- ✅ **Validation criteria** (thresholds documented)
- ⚠️ **Standard algorithms** (implementable with common libraries)
- ❌ **Proprietary components** (not documented, reverse engineering required)

**Reproduction feasibility: 60-70%** - Core system reproducible, proprietary components require either:
1. Reverse engineering from GSBsys output
2. Best-effort proxies with validation
3. Purchase of actual software
