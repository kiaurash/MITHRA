# GSBsys Development Methodology

## Overview

GSBsys follows a structured 5-part methodology (Parts A-E) for developing robust trading systems. The process emphasizes out-of-sample validation, walk-forward testing, and systematic filtering to identify stable, generalizable systems.

---

## Part A: Baseline Establishment

**Objective:** Create a performance baseline for comparison

### Process

```
1. Build 50,000 systems
2. Rank by F-F metric (fitness function)
3. Select top 250 systems
4. Apply walk-forward testing
5. Filter through:
   - Anchored Stability Course → 90 systems
   - VSS (Visual System Selector) → 91 systems
6. Record performance statistics across 3 time periods
```

### Data Periods

**In-Sample:**
- Start: 2007-01-01 (or earlier depending on market)
- End: 2017-02-28

**Out-of-Sample Windows:**
- Statistics B: 2017-03-01 to 2018-02-28
- Statistics C: 2018-03-01 to 2019-02-28
- Statistics D: 2019-03-01 to 2020-02-28
- Statistics E: 2020-03-01 to 2021-02-28
- Statistics F: 2021-03-01+

### Key Metrics Tracked

- Net Profit
- Average Trade
- Profit Factor
- Pearson Correlation (R-F field)
- Anchored Stability (Astab) score
- NP/DD ratio (Net Profit / Drawdown)

---

## Part B: Indicator Identification

**Objective:** Identify the most effective indicators for the target market

### Process

```
1. Build 20,000 systems using SINGLE indicators
2. Rank all ~75 available indicators
3. Select top 10,000 systems
4. Identify 9-11 most effective indicators
```

**Macro M1 Execution:**
- Automated indicator ranking process
- "The top 10 indicators will be chosen"
- Based on frequency in top-performing systems

### Validation Test (Proving Methodology)

**Scale:** 50,000 systems on ES futures, 30-minute bars

**Configuration:**
- 20 indicators tested
- Settings optimized for 30-minute timeframe
- Training data: Pre-20150630
- OOS Period 1: 20150630-20180228
- OOS Period 2: 20180229-20190301

**Selection Criteria:**
- Filter top ~2,000 systems
- Remove lowest 1,000 by Pearson correlation
- Apply walk-forward parameters from pre-June 2015 data only

**Key Finding:**
> "In all cases the WF parameters are better in EVERY metric in all 3 tests."

Systems with **Astab ≥ 40** showed improved out-of-sample results.

---

## Part C: Reduced Indicator Testing

**Objective:** Validate that reduced indicator set improves performance

### Process

```
1. Rebuild systems using only 9-12 selected indicators (from Part B)
2. Use same filtering approach as Part A:
   - Top 250 by F-F metric
   - Astab-C filter
   - VSS filter
3. Compare to baseline (Part A) using identical statistics
```

**Expected Outcome:**
- Improved baseline results
- Better out-of-sample consistency
- Faster optimization (reduced search space)

**Search Space Reduction:**
- Original: C(75, 5) = 17+ million combinations
- Reduced: C(10, 5) = 252 combinations
- Speedup: ~67,000x fewer combinations

---

## Part D: Optimization Parameters (Optional)

**Objective:** Fine-tune configuration settings for marginal gains

### Tested Parameters

1. **Normalization Modes**
   - HighestLowest (default)
   - Alternative mode (unspecified)

2. **Indicator Quantity**
   - Test 2, 3, 4, or 5 indicators
   - More indicators = more complexity + more WF tests needed

3. **Secondary Data Streams**
   - Daily bars
   - Multiple timeframes

4. **Entry Types**
   - Compare1
   - Alternative entry modes

### Configuration Guidance

**For 3 indicators:**
- WF Generations: 120
- WF Population: 120
- Total WF tests: 14,400

**For 4-5 indicators:**
- WF Generations: 150+
- WF Population: 150+
- Total WF tests: 22,500+

**With Adaptive MA:**
- Requires "many more tests" due to 3 parameters per adaptive indicator
- Recommend 150×150 minimum

---

## Part E: Final System Selection

**Objective:** Select production-ready systems for trading

### Family Grouping

Systems are organized into **families** — groups with similar indicator combinations but different parameter values.

**Example Family:**
```
Family: TrueRange + GSB_CCI + DMIPlus
  Member 1: TrueRange(1500), CCI(1700), DMI(2000)
  Member 2: TrueRange(1450), CCI(1720), DMI(1980)
  Member 3: TrueRange(1520), CCI(1680), DMI(2020)
```

### Selection Criteria

1. **Family Quality:**
   - "Ideally you want at least 3 members in a family group"
   - "Most or all members have good out of sample results"
   - Low variance between members indicates stability

2. **Filter Selection:**
   - Choose best-performing filter: Astab-C or VSS
   - Typically both produce similar results

3. **Member Selection:**
   - "The top families and the top member of the family (first entry)"
   - Walk-forward test selected members

### High-Variance Warning

> "High variance between family members indicates excessive sensitivity to parameters"

This suggests overfitting — avoid families where small parameter changes drastically alter performance.

---

## Walk-Forward Testing

### Configuration (from Screenshots)

**WF Parameters:**
- Generations: 100-150 (depends on indicator count)
- Population: 100-150
- Optimization Type: GeneticAlgorithm

**Data Split:**
- Training %: 40 (conservative)
- Test %: 60 (majority reserved for OOS)
- Test @ Beginning: False (test on most recent data)

### Validation Evidence

**Methodology Update (May 6, 2019):**
- Changed from multiplication to addition operators for weight adjustments
- Timing changed: adjustments occur relative to walk-forward completion

**Performance:**
- Walk-forward systems consistently outperformed static systems
- Validated across multiple timeframes (30-min, 15-min, daily)
- Markets tested: ES, NQ, DOW, NG, CL, GC, DAX

---

## Data Verification

### Noise Injection Testing

**Method:** Add randomized noise to data streams

**Purpose:** Verify systems aren't overfitting to specific data quirks

**Process:**
```
1. Select winning systems
2. Create 8 versions with different random noise added
3. Re-run backtests on noisy data
4. Systems that remain profitable = robust
5. Systems that fail = data-specific overfitting
```

This is an anti-overfitting validation technique not mentioned in academic GA+RL research.

---

## Building Nasdaq/SP500/Dow Systems

### 6-7 Step Process

**Step 1: Indicator Selection**
- Run Macro M1 on 20,000 systems
- Identify top 10 indicators
- Specific to target market (ES, NQ, or YM)

**Step 2: System Generation**
- Build 20,000 systems (optimal volume per documentation)
- "Systems build twice as fast as indicators"
- Filter to top 300 performers

**Step 3: Categorization**
- Organize into Favorites B, C, D
- Based on out-of-sample performance across multiple periods (Statistics B-F)

**Step 4: Family Grouping**
- Group by indicator combination
- Minimum 3 members per family

**Step 5: Walk-Forward Testing**
- Test selected family members
- WF parameters from pre-2017 data

**Step 6: Validation**
- Verify across Statistics B-F periods (2017-2021+)
- Ensure consistency across market regimes

**Step 7: Deployment**
- Export to TradeStation, MultiCharts, or NinjaTrader
- Use tick-based volume settings
- Align to exchange time

---

## Critical Configuration Parameters

### Session Settings (Updated July 2022)

**Market Data:**
- Use @ES, @NQ (not @ES.D, @NQ.D)
- Start time: 8:00 AM
- Earliest trade: 9:00 AM

**Data Requirements:**
- Multiple years of historical data
- Consistent data source
- Verified tick/volume accuracy

### Optimization Scale

**Recommended:**
- 20,000 systems = optimal build volume
- Larger builds don't improve results proportionally
- "Systems build twice as fast as indicators"

**Resource Management:**
- Submit large jobs to GSB cloud/workers
- Local processing lacks RAM protection
- 16 GB RAM minimum for standalone

---

## Quality Filters

### Pearson Correlation

**Threshold:** ≥ 0.95 (R-F field)

**Purpose:** Ensure training and test equity curves have consistent shape

**Interpretation:**
- 0.95+ = Very consistent behavior across in-sample and OOS
- < 0.95 = System behaves differently on new data (reject)

### Profit Factor

**Training/Test:** ≥ 1.2
**Validation:** ≥ 1.8

**Calculation:** Gross Profit / Gross Loss

**Example:**
- Gross Profit: $100k
- Gross Loss: $50k
- Profit Factor: 100/50 = 2.0 ✓ (passes validation threshold)

### Net Profit / Drawdown Ratio

**Selection Range:** 25-20 (top 1,000 systems from 50,000)

**Purpose:** Balance profitability against risk

**Example:**
- Net Profit: $100k
- Max Drawdown: $10k
- NP/DD: 10 (marginal)

vs.

- Net Profit: $80k
- Max Drawdown: $3k
- NP/DD: 26.7 (excellent)

---

## Methodology Evolution

### Continuous Improvement

**Regular Updates:**
- May 6, 2019: Changed operator logic (multiply → add)
- July 2022: Session settings update
- Ongoing refinements to swing trading systems

**Documentation Version:**
- GSB version 1.0.68.92 / 2025-05-05
- "Last updated 5-May-2025"

### Community Integration

**Support Resources:**
- Active forum discussions
- Video tutorials (13+ documented)
- Advanced parameter combination guidance

**NDA Distribution:**
- Suggests proprietary techniques not fully disclosed
- Commercial users may access additional methodology details

---

## Key Methodological Innovations

1. **Multi-Stage Filtering:** 50,000 → 2,000 → 1,000 → families → final selection
2. **Walk-Forward as Separate GA Stage:** Independent optimization of WF parameters
3. **Noise Injection Validation:** Robustness testing through randomized data perturbation
4. **Anchored Stability Metric:** Proprietary measure of parameter sensitivity
5. **Family Grouping:** Parameter stability verification through member comparison
6. **Conservative OOS Split:** 40/60 train/test (opposite of academic standard)
7. **Multi-Period Validation:** 5+ distinct OOS windows spanning different market regimes

---

## Comparison to Academic Practice

| Aspect | Academic GA+RL | GSBsys Methodology |
|--------|---------------|-------------------|
| Scale | 2k-10k evaluations | 2M evaluations (100x more) |
| OOS validation | Often single period | 5+ distinct periods |
| Walk-forward | Conceptual | Dedicated GA stage |
| Noise testing | Not mentioned | Systematic verification |
| Parameter stability | Not assessed | Family grouping + Astab metric |
| Train/test split | 60/40 typical | 40/60 (conservative) |
| Pearson threshold | Not used | ≥ 0.95 required |
| Profit Factor floor | Rarely enforced | 1.2 train, 1.8 validation |

GSBsys methodology prioritizes **robustness over optimization** — directly addressing the overfitting concerns that destroyed systems like Red Queen (arXiv:2512.15732).
