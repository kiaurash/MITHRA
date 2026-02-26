# GSBsys Website Documentation Index

## Overview

This document catalogs all successfully accessed pages from https://trademaid.info/gsbhelp/ and summarizes their content for reproduction purposes.

**Last Updated:** February 19, 2026

---

## Successfully Accessed Pages

### 1. GSBArchitecture1.html ✅

**URL:** https://trademaid.info/gsbhelp/GSBArchitecture1.html

**Content:**
- **Signal Combination Formula:** `result = indicator1 * indicator2 * indicator3`
- **Weighted Variant:** `result = indicator1^weight1 * indicator2^weight2 * indicator3^weight3`
- **Secondary Filter:** `close - close[1]` or `close / high_daily[1]` (crude oil)
- **Entry Logic:**
  ```
  IF secondary_filter > 0 AND result > EntryLevel THEN Buy
  IF secondary_filter < 0 AND result < EntryLevel THEN Sell
  ```
- **Indicator Range:** -100 to +100 (normalized)
- **Multiplication Problem:** Acknowledges 2 negatives × 1 positive = false positive signal

**Links to:**
- Process.html
- BeforeweBegin.html
- GSB2PassIndicatorMethod.html
- Families.html

**Reproduction Value:** ⭐⭐⭐⭐⭐ (Essential - core algorithm)

---

### 2. BeforeweBegin.html ✅

**URL:** https://trademaid.info/gsbhelp/BeforeweBegin.html

**Content:**
- **Process Overview:** 7-step methodology
- **Key Principle:** "Change only one thing at a time"
- **Consistency Testing:** Repeat tests up to 4 times to validate robustness
- **Evaluation Focus:** Groups of systems, not individual systems
- **Initial Phase:** Focus on robust system groups before selecting top families

**Links to:**
- Methodology.html
- CLVideoInstructions.html
- Process.html

**Reproduction Value:** ⭐⭐⭐ (Useful - methodology context)

---

### 3. GSB2PassIndicatorMethod.html ⚠️

**URL:** https://trademaid.info/gsbhelp/GSB2PassIndicatorMethod.html

**Content:**
- **Status:** Navigation page only, no algorithm details
- **References:** In-sample and out-of-sample dates
- **Actual Method:** Not documented on this page

**Reproduction Value:** ⭐ (Limited - navigation only)

---

### 4. Families.html ✅

**URL:** https://trademaid.info/gsbhelp/Families.html

**Content:**
- **Definition:** "Families are a group of systems that have the same indicators but are not identical"
- **Robustness Indicator:** "A family with many members means the systems are robust regardless of the parameters"
- **Selection Criterion:** Prefer families where most/all members have good OOS results

**Missing:**
- Specific algorithms for creating families
- Quantitative thresholds
- Implementation procedures

**Reproduction Value:** ⭐⭐ (Conceptual understanding, no implementation details)

---

### 5. EntryModes.html ✅

**URL:** https://trademaid.info/gsbhelp/EntryModes.html

**Content:**

**AIC (Any Indicators Cross)** - Recommended for ES/NQ:
```
If any indicator crosses > 0 then buy
If any indicator crosses < 0 then Sell short
```

**NCC (No Conflict Cross):**
- Long: Indicator crosses above 0 without conflicting downward crosses
- Short: Indicator crosses below 0 without conflicting upward crosses

**Compare2:**
```
If result > entryLevel And result[1] > entryLevel then buy
If result < entryLevel And result[1] < entryLevel then sell
```

**Also Listed:**
- Cross (standard crossover)
- Compare1 (simple threshold)
- CrossSingleLevel (not recommended)

**Critical Note:** AIC and NCC do NOT use EntryLevel or weights. Optimize with ranges -90 to 90 in 5-step increments.

**Reproduction Value:** ⭐⭐⭐⭐⭐ (Essential - specific algorithms provided)

---

### 6. Methodology.html ✅

**URL:** https://trademaid.info/gsbhelp/Methodology.html

**Content:**

**Part A - Establish Baseline:**
- Build 50,000 systems
- Select top 250 by F-F metric
- Apply walk-forward testing
- Filter through Astab-C (90 systems) and VSS (91 systems)
- Record statistics across multiple periods

**Part B - Identify Indicators:**
- Build 20,000 systems with single indicators
- Select top 10,000 by F-F metric
- Identify 9-11 best indicators

**Part C - Rebuild with Reduced Set:**
- Build 50,000 systems using only top 9-11 indicators
- Apply same filtering as Part A
- Compare to baseline

**Part D - Optimize Parameters:**
- Test normalization modes
- Test indicator counts
- Test secondary data streams
- Test entry types

**Part E - Select Trading Systems:**
- Choose best filter (Astab-C or VSS)
- Organize into families
- Select top members

**Time Periods Referenced:**
- 2000-2015 (baseline)
- 2015-2018 (OOS1)
- 2018-2019 (OOS2)

**Reproduction Value:** ⭐⭐⭐⭐⭐ (Essential - complete workflow)

---

### 7. GeneticAlgorithm.html ✅

**URL:** https://trademaid.info/gsbhelp/GeneticAlgorithm.html

**Content:**
- **Population:** 200 systems
- **Generations:** 1,000
- **Restarts:** 100 (with 200,000 iterations × 100)
- **Total Combinations:** 20 million (1000 × 200 × 10)
- **Random Seed:** Optional for reproducibility
- **Max Crossover Attempts:** Timeout to prevent stalling
- **Early-Stop Reset-and-Restart:** Auto-restart if GA stops improving before N% completion

**Missing:**
- Crossover type
- Mutation rate (found in screenshots: 5%)
- Selection method
- Elitism strategy

**Reproduction Value:** ⭐⭐⭐⭐ (High - key parameters, some gaps)

---

### 8. Stoploss.html ✅

**URL:** https://trademaid.info/gsbhelp/Stoploss.html

**Content:**

**Stop Loss Types:**
1. Genetically chosen (range determined by stop value)
2. Trailing Stop (for overnight systems)
3. ATR Trailing Stop
4. Plock Break Even (move to BE after profit target hit)
5. Plock Variable (lock in fixed profit after target)
6. Fixed Stop (user-defined)

**Performance Notes:**
- Plock Break Even: "very worth while using"
- ATR Variable + Plock Variable: "significantly worse OOS results"

**All Values:** Genetically chosen within user-defined ranges

**Reproduction Value:** ⭐⭐⭐⭐ (Useful - stop types and performance guidance)

---

### 9. Optimization.html ⚠️

**URL:** https://trademaid.info/gsbhelp/Optimization.html

**Content:**
- **Optimizer Types:** GeneticAlgorithm & ExhaustiveSearch
- **Recommended:** "We only use GeneticAlgorithm"
- **Test @ Beginning:** Option to use bars at beginning for OOS test
- **Advanced Features:** "highlighted in Red" (not shown in excerpt)

**Missing:** Detailed optimization parameters, settings

**Reproduction Value:** ⭐⭐ (Limited - basic info only)

---

### 10. GAGenerationsGAPopulation.html ✅

**URL:** https://trademaid.info/gsbhelp/GAGenerationsGAPopulation.html

**Content:**

**Recommended Configurations:**
- **Standard:** 100 × 100 (10,000 WF tests)
- **3 indicators:** 120 × 120
- **4-5 indicators:** 150 × 150 or higher

**Formula:** `WF Tests = WF Generations × WF Population`

**Performance Guidance:**
- Too few tests → unstable WF curves
- Adaptive MA indicators → need many more tests (3 parameters)
- "Genetic will work better than random space"

**Cloud Workers:** Recommended for large populations to prevent RAM exhaustion

**Reproduction Value:** ⭐⭐⭐⭐ (Important - WF-GA parameter guidance)

---

### 11. 15GSBSetupandOperation.html ✅

**URL:** https://trademaid.info/gsbhelp/15GSBSetupandOperation.html

**Content:**

**Strategy Settings:**
- Number of indicators: 3-5 (5 may be optimal)
- Secondary-Filter Indicator: CloseLessPrevCloseD or GeneticAlgorithm

**Optimization:**
- Training %: 30-50% recommended (40% default)
- Restarts: 10 (adjustable)
- Total combinations: 20 million (1000 × 200 × 10)

**Trading Parameters:**
- Capital investment preferred over fixed shares
- Commission: $13.50 per side
- Market On Day Close: True (for day trading)
- Both long and short enabled by default

**Performance Metrics:**
- Fitness: "Net Profit times Average Trade"
- Pearson: 0.95 minimum (train/test)
- Profit Factor: 1.2 (train/test), 1.8 (validation)

**System Requirements:**
- **Minimum RAM: 16 GB**

**Reproduction Value:** ⭐⭐⭐⭐⭐ (Essential - complete configuration spec)

---

### 12. GSBGuidefortheBeginners.html ✅

**URL:** https://trademaid.info/gsbhelp/GSBGuidefortheBeginners.html

**Content:**

**Overview:**
- Genetic System Builder for algorithmic trading
- Version 64.45 discussed (current: 1.0.68.92)
- Regular updates available to purchasers

**Workflow:**
1. Data Preparation
2. Configuration
3. System Generation
4. Performance Analysis
5. Verification
6. Platform Export

**Supported Platforms:**
- TradeStation
- MultiCharts
- NinjaTrader

**Video Tutorials:** 13+ YouTube videos listed

**Reproduction Value:** ⭐⭐⭐ (Overview - good for understanding workflow)

---

### 13. 11GSBFamiliarisationGSBStandalon.html ⚠️

**URL:** https://trademaid.info/gsbhelp/11GSBFamiliarisationGSBStandalon.html

**Content:**
- GSB application types: Standalone, Manager, Worker
- Hardware requirements
- Cloud worker setup
- Configuration settings

**Missing:** GA implementation details, algorithms

**Reproduction Value:** ⭐ (Infrastructure info, not algorithms)

---

### 14. Provingthemethodology.html ✅

**URL:** https://trademaid.info/gsbhelp/Provingthemethodology.html

**Content:**

**Validation Test:**
- **Scale:** 50,000 systems on ES futures, 30-minute bars
- **Data Configuration:** 20 indicators
- **Selection:** Top ~2,000 systems → remove lowest 1,000 by Pearson correlation

**Walk-Forward Testing:**
- WF parameters from pre-June 2015 data only
- Performance tested across 3 periods:
  - Pre-20150630 (in-sample)
  - 20150630-20180228 (OOS1)
  - 20180229-20190301 (OOS2)

**Key Finding:**
> "In all cases the WF parameters are better in EVERY metric in all 3 tests"

**Performance Factor:**
- Systems with **Astab ≥ 40** showed improved OOS results

**Methodology Change (May 6, 2019):**
- Changed from multiplication to addition operators
- Timing changed for weight adjustments relative to WF completion

**Reproduction Value:** ⭐⭐⭐⭐ (Validation evidence - important for methodology validation)

---

### 15. BuildingNasdaqSP500orDowsystems.html ✅

**URL:** https://trademaid.info/gsbhelp/BuildingNasdaqSP500orDowsystems.html

**Content:**

**6-7 Step Process:**

1. **Indicator Selection:** Run Macro M1 on 20,000 systems → identify top 10 indicators
2. **System Generation:** Build 20,000 systems (optimal volume), filter to top 300
3. **Categorization:** Organize into Favorites B, C, D by OOS performance
4. **Family Grouping:** Minimum 3 members per family
5. **Walk-Forward Testing:** Test selected family members
6. **Validation:** Verify across Statistics B-F periods (2017-2021)
7. **Deployment:** Export to TradeStation/MultiCharts/NinjaTrader

**Configuration (Updated July 2022):**
- In-sample: 2007-01-01 to 2017-02-28
- OOS windows: Statistics B-F (2017-2021)
- Market data: @ES, @NQ (not @ES.D, @NQ.D)
- Start time: 8:00 AM
- Earliest trade: 9:00 AM

**Performance:**
- 20,000 systems = optimal build volume
- Systems build 2x faster than indicators

**Selection:**
- Target families where most/all members have good OOS results
- High variance between family members = parameter sensitivity (reject)

**Reproduction Value:** ⭐⭐⭐⭐⭐ (Essential - complete build process for specific markets)

---

### 16. UpdatedAsOf.html ⚠️

**URL:** https://trademaid.info/gsbhelp/UpdatedAsOf.html

**Content:**
- GSB version: 1.0.68.92 / 2025-05-05
- Last updated: 5-May-2025
- Navigation links: Introduction, Summary, GSB Guide for Beginners, Process

**Missing:** Detailed version history, changelogs

**Reproduction Value:** ⭐ (Version info only)

---

### 17. StopLossProfitTarget.html ✅

**URL:** https://trademaid.info/gsbhelp/StopLossProfitTarget.html

**Content:**

**Purpose:** Exit mechanisms for swing trading (overnight systems)

**Stop Loss:**
- **Max Stop Loss:** Currency units, excluding commissions/slippage
- **Types:** Fixed trailing, ATR trailing

**Profit Target:**
- **Example:** $2,000
- **Units:** Currency, excluding commissions/slippage
- **Purpose:** "Reduce high gains in 2008 that may cause the system to curve fit for 2008"

**Additional Exits:**
- Time-based (specific times of day)
- Market-on-close (MOC)
- Position-based (after losing trades)
- Price-based (compare to previous close)

**Reproduction Value:** ⭐⭐⭐ (Useful - exit parameter specifications)

---

## Pages That Return 404 (Not Available)

The following pages were attempted but do not exist on the site:

- Contents.html
- API.html
- Implementation.html
- CustomIndicators.html
- Introduction.html
- Process.html
- Summary.html
- IndicatorParameters.html
- Indicators.html
- StrategyConfiguration.html
- DataFormat.html
- Exports.html
- NormalizationModes.html
- Weights.html
- FitnessFunction.html
- WalkForward.html
- SecondaryData.html
- PerformanceMetrics.html
- BacktestingEngine.html
- AnchoredStability.html
- VSS.html
- FFMetric.html

**Implication:** These implementation-specific pages either don't exist or use different URLs. Core implementation details are likely proprietary and not publicly documented.

---

## Information Extracted from Screenshots

### Screenshot 1: Indicator Rankings
**File:** GSB-Indicator-screenshot.png

**Content:**
- **37 indicators ranked by RatioGd/bd**
- Top performer: **TrueRange (2.71)**
- Second: **GSB_SS_Stochastic (1.53)**
- Third: **GSB_AverageFC (1.28)**
- Good indicators: 21
- Bad indicators: 20

**Value:** ⭐⭐⭐⭐⭐ (Essential - indicator performance rankings)

---

### Screenshot 2: Main Application Interface
**File:** GSB-Indicator-screenshot2.png

**Content:**
- **Strategy:** GSB
- **Number of indicators:** 2
- **Built-in indicators:** 38 (SF: 1) / 40 indicators total
- **Normalization Modes:** 2 of 2 enabled (HighestLowest confirmed)
- **Normalization Length:** 100
- **Operators:** 1 of 3 enabled (Multiply enabled)
- **Entry Modes:** 3 of 3 enabled
- **Optimizer Type:** GeneticAlgorithm
- **Is Parallel:** True
- **Training %:** 100 (development setting)
- **Test %:** 0 (development setting)

**Full indicator list visible with Top/Bottom/Ratio columns**

**Value:** ⭐⭐⭐⭐⭐ (Essential - configuration interface, all indicators listed)

---

### Screenshot 3: GA Parameter Settings
**File:** GSB-Indicator-screenshot3.png

**Content:**
- **Crossover Rate:** **95%**
- **Mutation Rate:** **5%**
- **Mutation Strength:** **25%**
- **Generations:** 1000
- **Population:** 200
- **Random Seed:** (blank)
- **Number of indicators:** 5
- **Built-in indicators:** 37 (SF: 37)
- **Secondary-Filter Indicator:** Enabled = True, Force-Use = False
- **Training %:** 40
- **Test %:** 60

**Indicator Enabled Collection Editor** showing enabled indicators with Force-Use settings

**Value:** ⭐⭐⭐⭐⭐ (CRITICAL - reveals previously undocumented GA parameters)

---

## Summary of Reproduction Information

### Fully Documented (Can Reproduce) ✅

1. **Signal Combination Architecture** - Complete formula and entry logic
2. **Entry Modes** - All modes with specific algorithms
3. **5-Part Methodology** - Complete workflow
4. **GA Parameters** - Population, generations, crossover, mutation (from screenshots)
5. **Configuration Settings** - Train/test split, all parameter values
6. **Validation Thresholds** - Pearson, PF minimums
7. **Build Process** - Step-by-step for ES/NQ/YM
8. **Stop Loss Types** - All types with performance notes
9. **Walk-Forward Parameters** - WF-GA generation/population guidance

### Partially Documented (Can Implement with Standard Methods) ⚠️

1. **Indicator Normalization** - Method name (HighestLowest) but not exact formula
2. **Fitness Function** - Components known (NP × AvgTrade) but exact formula missing
3. **Walk-Forward Testing** - Concept clear, anchoring algorithm unclear
4. **Family Grouping** - Concept clear, selection algorithm unclear
5. **Noise Injection** - Mentioned but specifics (magnitude, pass/fail) missing

### Not Documented (Proprietary) ❌

1. **37 Indicator Formulas** - Names known, 22 are proprietary GSB_ variants
2. **Anchored Stability (Astab)** - Calculation method not disclosed
3. **VSS (Vertical System Stability)** - Calculation method not disclosed
4. **F-F Metric** - Exact formula not disclosed
5. **GA Selection Method** - Not specified
6. **GA Crossover Type** - Not specified
7. **GA Mutation Algorithm** - Not specified
8. **Second Normalization Mode** - Not named or explained
9. **Early-Stop Trigger Logic** - Threshold not specified
10. **Backtesting Engine** - Order execution, slippage model not disclosed

---

## Recommendations for Reproduction

### Tier 1: Use Official Documentation ✅
- Implement signal combination architecture exactly as specified
- Use documented entry modes (AIC, NCC, Compare2)
- Follow 5-part methodology workflow
- Apply exact GA parameters from screenshots
- Use validation thresholds (Pearson ≥ 0.95, PF ≥ 1.2/1.8)

### Tier 2: Use Standard Implementations ⚠️
- Standard indicators: Use TA-Lib (TrueRange, RSI, ADX, CCI, etc.)
- Normalization: Implement standard HighestLowest formula
- Fitness: Implement Net Profit × Avg Trade with floor filters
- GA operators: Use tournament selection, blend crossover, Gaussian mutation
- Walk-forward: Use standard rolling window with periodic reoptimization

### Tier 3: Reverse Engineer or Substitute ❌
- **Proprietary indicators:** Either purchase GSBsys or create best-effort proxies
- **Astab/VSS:** Use proxy metrics (coefficient of variation, performance consistency)
- **Exact fitness:** Test variations until results match GSBsys output
- **GA internals:** Use standard GA library, tune parameters empirically

---

## Final Assessment

**Documentation Quality:** ⭐⭐⭐ (3/5)
- Excellent high-level methodology
- Good configuration specifications
- Missing low-level implementation details

**Reproduction Feasibility:** 60-70%
- Core architecture: 100% reproducible
- Methodology: 100% reproducible
- Standard components: 80% reproducible
- Proprietary components: 0% reproducible without reverse engineering

**Recommendation:**
- For research/learning: Implement Tier 1 + Tier 2, use proxies for Tier 3
- For production trading: Purchase GSBsys software ($200-$799)
- For academic comparison: Document what's reproducible, note proprietary gaps in methodology
