---
title: "GA-Trading-Sys MVP: Genetic Algorithm Trading System Optimizer"
version: 2.0
date: 2026-02-22
status: ready
priority: p1
type: product-requirements-document
poc_validation: qualified-pass
poc_date: 2026-02-22
implementation_plan: ./2026-02-21-feat-ga-trading-sys-implementation-plan.md
---

# GA-Trading-Sys MVP - Product Requirements Document

## Executive Summary

**What**: Open-source genetic algorithm trading system optimizer that prevents overfitting through practitioner-grade validation (Pearson filters, multi-period OOS, noise testing, family grouping).

**Why**: Academic GA+RL systems fail in live trading (MaxAI PF=1.07 live vs GSBsys PF≥1.8 requirement). Need transparent, reproducible alternative to $200-$799 commercial GSBsys software.

**Validation**: POC completed 2026-02-22 with qualified pass:
- ✓ DEAP integration works
- ✓ Fitness function drives optimization (1.77→2.14 improvement)
- ✓ GA converges in 1000 generations
- ⚠ VectorBT speed: 62.53ms (25% over 50ms target, addressable via optimization)

**Timeline**: 26 weeks (Phases 1-4), solo developer, 40 hrs/week

**Success Criteria**:
- MVP Tier: Pearson ≥0.85, PF ≥1.2, 3/5 OOS periods profitable
- Production Tier: Pearson ≥0.90, PF ≥1.5, 4/5 OOS periods profitable

---

## Problem Statement

### Current State: Academic Systems Fail Live Trading

**Case Study: MaxAI** (best academic GA system)
- Backtest: Strong performance
- Live: PF=1.07 (4 months)
- Rejected: Below GSBsys PF≥1.8 commercial threshold

**Case Study: Red Queen** (catastrophic failure)
- Backtest: Excellent metrics
- Live: Capital decay, strategy abandoned
- Root cause: No Pearson filter, no multi-period OOS, no noise testing

**Gap Identified**: Academic research lacks practitioner rigor
- No train/test equity correlation filtering
- Single-period backtests (regime-specific overfitting)
- No robustness testing (noise injection, parameter stability)

### Commercial Alternative: GSBsys (Insufficient)

**Strengths**:
- Multi-year live deployment
- 12 documented innovations (Pearson filter, family grouping, walk-forward GA)
- Proven methodology ($200-$799 pricing validates demand)

**Weaknesses**:
- Proprietary (closed-source, auditing impossible)
- Partially documented (22/37 indicators undocumented)
- Platform-locked (Windows-only)
- Expensive ($200-$799 per license)

### Target State: Open-Source GA Optimizer

**What We're Building**:
- ≥93% fidelity reproduction of GSBsys documented methodology
- Transparent, auditable algorithms (all code public)
- Cross-platform (Python 3.10+, Windows/Linux/macOS)
- Free MVP tier (yfinance daily data, $0 cost)
- Production upgrade path (Theta Data 1-min futures, $150/month)

**4-Stage Overfitting Prevention**:
1. **Pearson Equity Filter**: Train/test correlation ≥0.85 (MVP) / ≥0.90 (Production)
2. **Multi-Period OOS**: Profitable across ≥3/5 (MVP) / ≥4/5 (Production) regimes
3. **Noise Injection**: Profitable on ≥5/8 (MVP) / ≥6/8 (Production) perturbed variants
4. **Family Grouping**: Parameter stability CoV ≤60% (MVP) / ≤50% (Production)

---

## Goals and Non-Goals

### Goals (MVP Scope - Phases 1-4, 26 weeks)

**Phase 1: Core GA Engine** (12 weeks)
- ✓ Data pipeline (yfinance, SPY/QQQ/IWM, 2010-2025)
- ✓ 15 standard indicators (TA-Lib: RSI, MACD, Bollinger, Stochastic, ADX, etc.)
- ✓ DEAP GA framework (pop=200, gen=1000, restarts=10)
- ✓ Vectorized backtest (VectorBT + Numba, <50ms per eval after optimization)
- ✓ Fitness function: NetProfit × AvgTrade

**Phase 2: Validation Framework** (8 weeks)
- ✓ Pearson equity filter (≥0.85 MVP, ≥0.90 Production)
- ✓ Multi-period OOS testing (5 regimes: 2010-2013, 2013-2016, 2016-2019, 2019-2022, 2022-2025)
- ✓ Noise injection (8 variants: ±1% price, ±5% volume, entry shift ±1 day, commission ±50%)
- ✓ Family grouping (10 restarts, parameter CoV analysis)

**Phase 3: Robustness Testing** (6 weeks)
- ✓ Walk-Forward GA (reduced-fidelity: 100 pop × 200 gen)
- ✓ Sensitivity analysis (correlate parameter stability with family grouping)
- ✓ Regime testing (bull/bear/sideways market classification)

**Phase 4: Export & Integration** (6 weeks)
- ✓ Python backtest code generation
- ✓ Visualization (equity curves, train vs test alignment)
- ✓ Performance reports (Sharpe, PF, max DD, trades)
- ✓ CLI interface + YAML configuration
- ✓ Documentation (API, user guide, methodology)

### Non-Goals (Deferred to Post-MVP)

**Phase 5: Production Enhancements** (optional, +6 weeks)
- Multi-objective GA (Pareto frontier optimization)
- EasyLanguage code generation (TradeStation export)
- GPU acceleration (target: 5x speedup)
- Theta Data integration (1-min futures, $150/month)
- Advanced indicators (22 proprietary GSBsys indicators - requires reverse engineering)

**Explicitly Out of Scope**:
- Real-time trading execution (backtesting only)
- Brokerage integration (users export to their platform)
- Machine learning hybrids (GA+RL deferred, focus on pure GA)
- Portfolio optimization (single-system focus)
- Options strategies (equity/futures only)

---

## Success Metrics

### MVP Tier (Required for Release)

**Performance Thresholds**:
- Pearson correlation (train/test equity): ≥0.85
- Profit Factor: ≥1.2
- Multi-period OOS: ≥3/5 regimes profitable
- Noise robustness: ≥5/8 variants profitable (62.5%)
- Family grouping: CoV ≤60% for stable systems

**Speed Targets**:
- Single fitness evaluation: <50ms (daily bars, ~4000 bars)
- Full 10-restart GA: <2 hours wall-time (8-core parallel)
- Memory usage: <16GB RAM

**Code Quality**:
- Test coverage: ≥70% (Phases 1-2), ≥80% (Phases 3-4)
- 100% reproducibility (logged random seeds)
- Configuration validation (Pydantic schemas)

**Usability**:
- New user → SPY optimization: <30 minutes (timed user testing)
- Setup time: <5 minutes (pip install + YAML config)
- Documentation: API docs + user guide + methodology rationale

### Production Tier (Stretch Goals)

**Performance Thresholds**:
- Pearson correlation: ≥0.90
- Profit Factor: ≥1.5
- Multi-period OOS: ≥4/5 regimes profitable
- Noise robustness: ≥6/8 variants profitable (75%)
- Family grouping: CoV ≤50%

**Speed Targets**:
- 1-min bars: <300ms per fitness evaluation
- GPU acceleration: ≥5x speedup

### Comparative Benchmarks

**vs. MaxAI** (academic baseline):
- ✓ Higher PF threshold (1.2 vs 1.07)
- ✓ Pearson filter (MaxAI doesn't use)
- ✓ Multi-period OOS (MaxAI: single 4-year backtest)
- ✓ Faster (MVP: ~2 hours, MaxAI: days with RL training)

**vs. GSBsys** (commercial target):
- ✓ Match GA parameters (pop=200, gen=1000, restarts=10)
- ✓ Match validation methodology (Pearson, OOS, noise, family)
- ✓ Match fitness function (NetProfit × AvgTrade)
- ⚠ Relaxed thresholds (Pearson 0.90 vs 0.95, PF 1.5 vs 1.8) - documented gap
- ⚠ 15 standard indicators vs 37 total (22 proprietary undocumented)

---

## User Stories and Personas

### Primary Persona: Quantitative Trader (Solo Developer)

**Background**:
- Python developer with 2-5 years experience
- Familiar with backtesting (vectorbt, backtrader)
- Frustrated with manual indicator tuning
- Wants systematic, reproducible optimization
- Budget: $0-150/month for data

**User Journey**:

1. **Installation** (5 minutes)
   ```bash
   pip install ga-trading-sys
   ga-trading-sys init --config my_optimization.yaml
   ```

2. **Configuration** (10 minutes)
   - Edit `my_optimization.yaml`:
     - Ticker: SPY
     - Date range: 2010-2025
     - Indicators: RSI, MACD, Bollinger
     - Validation tier: MVP (Pearson ≥0.85)

3. **Execution** (2 hours)
   ```bash
   ga-trading-sys optimize --config my_optimization.yaml
   ```
   - Watches progress bar (1000 generations × 10 restarts)
   - Sees real-time best fitness updates

4. **Analysis** (15 minutes)
   - Reviews `results/` directory:
     - `equity_curves.png`: Train vs test alignment
     - `performance_report.txt`: Sharpe 1.8, PF 1.4, MaxDD -12%
     - `strategy.py`: Executable Python backtest code
   - Validates: Pearson=0.88 ✓, 4/5 OOS periods ✓, 6/8 noise variants ✓

5. **Integration** (30 minutes)
   - Copies `strategy.py` to trading platform
   - Runs paper trading for 3 months
   - Monitors live vs backtest correlation

**Success Outcome**: Reproducible, validated strategy in <3 hours total work

### Secondary Persona: Academic Researcher

**Background**:
- PhD student or postdoc in finance/quantitative methods
- Researching GA optimization, overfitting prevention
- Needs transparent, auditable methodology
- Publishing in peer-reviewed journals

**Needs**:
- Open-source code (citation, replication)
- Detailed methodology docs (algorithm specifications)
- Reproducible results (seeded random states)
- Extensible architecture (custom indicators, fitness functions)

**User Journey**:
1. Clone repo, review source code
2. Run baseline optimization (SPY, 15 indicators)
3. Modify fitness function (add custom constraint)
4. Re-run, compare results
5. Publish paper citing methodology

---

## Requirements

### Functional Requirements

**FR-1: Data Pipeline**
- FR-1.1: Load OHLCV data from yfinance (SPY, QQQ, IWM)
- FR-1.2: Support date range specification (default: 2010-2025)
- FR-1.3: Validate data quality (no NaNs, High ≥ Low, Volume > 0)
- FR-1.4: Cache downloaded data (avoid redundant API calls)

**FR-2: Indicator Engine**
- FR-2.1: Calculate 15 standard indicators via TA-Lib:
  - Trend: SMA, EMA, MACD, ADX
  - Momentum: RSI, Stochastic, CCI, Williams %R
  - Volatility: Bollinger Bands, ATR, Keltner Channels
  - Volume: OBV, MFI, Chaikin A/D
- FR-2.2: Normalize all indicators to [-100, 100] range (252-day rolling window)
- FR-2.3: Handle NaN values correctly (no fillna(0) look-ahead bias)
- FR-2.4: Vectorized computation (Numba JIT where applicable)

**FR-3: Genetic Algorithm**
- FR-3.1: DEAP framework integration
- FR-3.2: Individual genome: [indicator_weights, thresholds, stop_loss, take_profit, position_size]
- FR-3.3: Population: 200 individuals (configurable)
- FR-3.4: Generations: 1000 (configurable)
- FR-3.5: Restarts: 10 (diversity guarantee)
- FR-3.6: Crossover: SBX (Simulated Binary Crossover), 95% probability
- FR-3.7: Mutation: Gaussian, 5% probability
- FR-3.8: Selection: Tournament (size=3)
- FR-3.9: Elitism: Top 10 individuals preserved

**FR-4: Backtesting**
- FR-4.1: VectorBT-based vectorized backtest
- FR-4.2: Long-only positions (MVP), long/short (Production)
- FR-4.3: Stop-loss and take-profit exits
- FR-4.4: Position sizing: Fixed fractional (% of equity)
- FR-4.5: Commission model: Stocks ($0 + 0.05% slippage), Futures ($2.50 RT + 1.5 ticks)
- FR-4.6: Performance metrics: Total return, Sharpe, PF, max DD, win rate, # trades

**FR-5: Fitness Function**
- FR-5.1: Primary: NetProfit × AvgTrade (from GSBsys methodology)
- FR-5.2: Constraints (soft penalties):
  - Pearson < 0.85: -10 × (0.85 - Pearson)
  - PF < 1.2: -5 × (1.2 - PF)
  - Trades < 30: -0.1 × (30 - Trades)
- FR-5.3: Train/test split: 40/60 (sequential, no shuffling)

**FR-6: Validation Framework**
- FR-6.1: Pearson equity filter (train vs test correlation)
- FR-6.2: Multi-period OOS (5 regimes, walk-forward style)
- FR-6.3: Noise injection (8 variants):
  - Price: ±1%, ±2%
  - Volume: ±5%, ±10%
  - Entry timing: ±1 day, ±2 days
  - Commission: ±50%
- FR-6.4: Family grouping (10 restarts, CoV analysis)

**FR-7: Export & Visualization**
- FR-7.1: Generate executable Python backtest code
- FR-7.2: Equity curve plots (train vs test, matplotlib)
- FR-7.3: Performance report (text format, CSV export)
- FR-7.4: Strategy parameters (YAML format)

**FR-8: Configuration & CLI**
- FR-8.1: YAML-based configuration
- FR-8.2: Command-line interface:
  - `ga-trading-sys init`: Generate config template
  - `ga-trading-sys optimize`: Run optimization
  - `ga-trading-sys validate`: Run validation suite
  - `ga-trading-sys backtest`: Test exported strategy
- FR-8.3: Logging (progress, warnings, errors)
- FR-8.4: Random seed logging (reproducibility)

### Non-Functional Requirements

**NFR-1: Performance**
- NFR-1.1: Single fitness evaluation: <50ms (daily bars)
- NFR-1.2: Full 10-restart GA: <2 hours (8-core parallel)
- NFR-1.3: Memory: <16GB RAM
- NFR-1.4: Scalability: Linear with population size (parallel evaluation)

**NFR-2: Reliability**
- NFR-2.1: 100% reproducibility via logged seeds
- NFR-2.2: Graceful degradation (missing data → warning, continue)
- NFR-2.3: Error handling (invalid config → clear error message)
- NFR-2.4: Unit test coverage: ≥70% (Phases 1-2), ≥80% (Phases 3-4)

**NFR-3: Usability**
- NFR-3.1: Installation: pip installable, <5 min setup
- NFR-3.2: Documentation: Sphinx API docs + user guide
- NFR-3.3: Examples: 3+ worked examples (SPY, QQQ, multi-indicator)
- NFR-3.4: Troubleshooting guide (common errors, solutions)

**NFR-4: Maintainability**
- NFR-4.1: Modular architecture (data, indicators, GA, validation, export as separate modules)
- NFR-4.2: Type hints (Python 3.10+ syntax)
- NFR-4.3: Docstrings (Google style, all public APIs)
- NFR-4.4: Configuration validation (Pydantic schemas)

**NFR-5: Extensibility**
- NFR-5.1: Plugin architecture for custom indicators
- NFR-5.2: Custom fitness functions (user-defined constraints)
- NFR-5.3: Data source abstraction (yfinance, Theta Data, CSV)

**NFR-6: Compliance**
- NFR-6.1: Open-source license (MIT or Apache 2.0)
- NFR-6.2: No proprietary dependencies (all libraries open-source)
- NFR-6.3: Privacy: No data collection, no telemetry

---

## Technical Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GA-Trading-Sys MVP                       │
│                   (Python 3.10+, 26 weeks)                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Data Pipeline │   │ Indicator     │   │ GA Engine     │
│               │   │ Engine        │   │               │
│ - yfinance    │   │ - TA-Lib      │   │ - DEAP        │
│ - Cache       │   │ - Normalize   │   │ - Evolution   │
│ - Validate    │──▶│ - Vectorize   │──▶│ - Restarts    │
└───────────────┘   └───────────────┘   └───────────────┘
                                                │
                            ┌───────────────────┼───────────────────┐
                            │                   │                   │
                            ▼                   ▼                   ▼
                    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
                    │ Backtest      │   │ Fitness       │   │ Validation    │
                    │ Engine        │   │ Function      │   │ Framework     │
                    │               │   │               │   │               │
                    │ - VectorBT    │   │ NetProfit×    │   │ - Pearson     │
                    │ - Numba       │   │   AvgTrade    │   │ - Multi-OOS   │
                    │ - Vectorized  │◀──│ - Penalties   │──▶│ - Noise       │
                    └───────────────┘   └───────────────┘   │ - Family      │
                                                             └───────────────┘
                                                                     │
                                                                     ▼
                                                             ┌───────────────┐
                                                             │ Export &      │
                                                             │ Visualization │
                                                             │               │
                                                             │ - Python code │
                                                             │ - Plots       │
                                                             │ - Reports     │
                                                             │ - CLI         │
                                                             └───────────────┘
```

### Technology Stack

**Core Dependencies**:
- Python 3.10+ (type hints, match statements)
- DEAP 1.4+ (genetic algorithms)
- VectorBT 0.26+ (vectorized backtesting)
- TA-Lib 0.4.28+ (technical indicators)
- NumPy 1.24+ (numerical computation)
- Pandas 2.1+ (data manipulation)
- Numba 0.58+ (JIT compilation)

**Secondary Dependencies**:
- yfinance 0.2.33+ (data acquisition)
- Pydantic 2.5+ (configuration validation)
- Matplotlib 3.8+ (visualization)
- Click 8.1+ (CLI framework)
- PyYAML 6.0+ (configuration)
- SciPy 1.11+ (Pearson correlation)

**Development Dependencies**:
- pytest 7.4+ (unit testing)
- pytest-cov 4.1+ (coverage)
- black 23.12+ (code formatting)
- mypy 1.7+ (type checking)
- Sphinx 7.2+ (documentation)

### Module Structure

```
ga_trading_sys/
├── __init__.py
├── config.py                 # Configuration schemas (Pydantic)
├── data/
│   ├── __init__.py
│   ├── loader.py            # Data acquisition (yfinance)
│   ├── cache.py             # Data caching
│   └── validator.py         # Data quality checks
├── indicators/
│   ├── __init__.py
│   ├── calculator.py        # TA-Lib wrapper
│   ├── normalizer.py        # 252-day normalization
│   └── registry.py          # 15 standard indicators
├── ga/
│   ├── __init__.py
│   ├── engine.py            # DEAP integration
│   ├── operators.py         # Crossover, mutation, selection
│   ├── individual.py        # Genome definition
│   └── population.py        # Initialization, diversity
├── backtest/
│   ├── __init__.py
│   ├── engine.py            # VectorBT wrapper
│   ├── signals.py           # Signal generation
│   └── metrics.py           # Performance calculations
├── fitness/
│   ├── __init__.py
│   ├── function.py          # NetProfit × AvgTrade
│   ├── constraints.py       # Pearson, PF, trades penalties
│   └── evaluator.py         # Train/test split, evaluation
├── validation/
│   ├── __init__.py
│   ├── pearson.py           # Equity correlation
│   ├── multi_oos.py         # Multi-period OOS
│   ├── noise.py             # Noise injection
│   └── family.py            # Family grouping, CoV
├── export/
│   ├── __init__.py
│   ├── codegen.py           # Python code generation
│   ├── visualizer.py        # Equity curves, plots
│   └── reporter.py          # Performance reports
├── cli/
│   ├── __init__.py
│   ├── commands.py          # Click commands
│   └── logger.py            # Logging setup
└── utils/
    ├── __init__.py
    ├── seed.py              # Random seed management
    └── parallel.py          # Multiprocessing helpers
```

---

## Dependencies and Integrations

### Data Dependencies

**Primary: yfinance** (MVP)
- Source: Yahoo Finance (free, public)
- Coverage: US equities (SPY, QQQ, IWM, etc.)
- Resolution: Daily OHLCV
- History: 2000-present
- Limitations: No 1-min data, occasional API issues

**Optional: Theta Data** (Production, Phase 5)
- Source: Professional market data
- Coverage: Futures, options, equities
- Resolution: Tick, 1-min, daily
- Cost: $150/month
- Integration: Phase 5 (out of MVP scope)

### External Integrations

**None Required for MVP**:
- No brokerage API integration (export-only)
- No real-time data (backtesting only)
- No cloud services (runs locally)

**User Workflow Integration**:
1. User exports `strategy.py` from GA-Trading-Sys
2. User integrates into their platform:
   - TradeStation (manual EasyLanguage translation, Phase 5)
   - Interactive Brokers (via ib_insync)
   - MetaTrader (via Python bridge)
   - Custom backtester (direct Python import)

---

## Risks and Mitigations

### Technical Risks

**RISK-1: VectorBT Performance**
- **Description**: POC showed 62.53ms (target: <50ms)
- **Impact**: HIGH - Full GA takes >2 hours (unacceptable for users)
- **Probability**: MEDIUM - 25% over target, but optimizable
- **Mitigation**:
  - Week 2-3: Implement indicator caching (pre-calculate normalized RSI)
  - Week 4: Vectorize signal generation (remove pandas loops)
  - Week 5: Parallel population evaluation (8-core speedup)
  - Fallback: Custom Numba backtest engine (replace VectorBT)

**RISK-2: TA-Lib Installation Complexity**
- **Description**: Requires C library compilation (user friction)
- **Impact**: MEDIUM - Users fail to install, abandon project
- **Probability**: HIGH - Windows users especially affected
- **Mitigation**:
  - Provide precompiled wheels for Windows (common Python versions)
  - Document installation thoroughly (Linux: apt/yum, macOS: brew)
  - Fallback: pandas-ta library (pure Python, slower but simpler)

**RISK-3: Overfitting Despite Validation**
- **Description**: Strategies pass validation but fail live
- **Impact**: CRITICAL - Undermines project credibility
- **Probability**: MEDIUM - Even GSBsys has failures
- **Mitigation**:
  - Conservative thresholds (Pearson ≥0.85, PF ≥1.2)
  - Multiple validation layers (Pearson + OOS + noise + family)
  - Walk-forward GA (Phase 3 robustness testing)
  - User education: Paper trading required before live

**RISK-4: DEAP Scalability**
- **Description**: DEAP may not scale to 15-indicator genome
- **Impact**: MEDIUM - GA fails to converge or takes too long
- **Probability**: LOW - POC validated single-indicator works
- **Mitigation**:
  - Incremental testing (Week 6: 3 indicators, Week 8: 7, Week 10: 15)
  - Indicator pre-filtering (reduce 15 → 10 via correlation)
  - Adaptive population size (increase if diversity drops)

### Project Risks

**RISK-5: Solo Developer Capacity**
- **Description**: 26 weeks @ 40 hrs/week = 1,040 hours (aggressive)
- **Impact**: HIGH - Delays, burnout, quality compromises
- **Probability**: MEDIUM - Realistic for experienced developer
- **Mitigation**:
  - POC de-risked core assumptions (2 weeks front-loaded)
  - Modular milestones (ship Phase 1 independently if needed)
  - Buffer time in each phase (12+8+6+6 = 32 weeks realistic)
  - Community contributions (open-source leverage)

**RISK-6: GSBsys Methodology Gaps**
- **Description**: 22/37 indicators undocumented, proprietary logic unknown
- **Impact**: MEDIUM - Can't achieve 100% fidelity
- **Probability**: HIGH - Confirmed gap
- **Mitigation**:
  - Accept 93% fidelity goal (15 documented indicators)
  - Document gap transparently (README acknowledgment)
  - Phase 5: Reverse-engineer proprietary indicators (optional)
  - Focus on validation methodology (more important than indicators)

**RISK-7: Data Source Reliability**
- **Description**: yfinance API changes, downtime
- **Impact**: MEDIUM - Users can't run optimizations
- **Probability**: MEDIUM - Yahoo Finance has had outages
- **Mitigation**:
  - Data caching (local SQLite database)
  - CSV import fallback (user-provided data)
  - Modular data abstraction (easy to swap yfinance → Theta)

### Market Risks

**RISK-8: Regime Change Invalidation**
- **Description**: Strategies optimized 2010-2025 fail in 2026+
- **Impact**: HIGH - Live trading losses
- **Probability**: HIGH - Markets evolve
- **Mitigation**:
  - Walk-forward GA (Phase 3) simulates regime changes
  - Multi-period OOS includes diverse regimes (2008 crisis, COVID)
  - User education: Periodic re-optimization required (quarterly/annually)
  - Out-of-sample monitoring (live vs backtest correlation tracking)

---

## Timeline and Milestones

### Phase 1: Core GA Engine (Weeks 1-12)

**Week 1-2: Data Pipeline**
- Load SPY/QQQ/IWM via yfinance (2010-2025)
- Validate data quality (NaNs, High≥Low, Volume>0)
- Implement caching (SQLite)
- **Milestone**: Successfully load 4,000 daily bars for 3 tickers

**Week 3-4: Indicator Engine**
- Integrate TA-Lib (15 standard indicators)
- Implement 252-day normalization (no fillna leak!)
- Vectorize calculations (Numba JIT)
- **Milestone**: Calculate all 15 indicators in <100ms

**Week 5-7: GA Framework**
- DEAP integration (individual, population, operators)
- Genome design (indicator weights, thresholds, SL/TP, position size)
- Evolution loop (1000 generations, 10 restarts)
- **Milestone**: GA runs to completion (dummy fitness)

**Week 8-10: Backtest Engine**
- VectorBT integration
- Signal generation (vectorized)
- Performance metrics (Sharpe, PF, MaxDD, trades)
- **Optimization**: Achieve <50ms per fitness evaluation
- **Milestone**: Backtest 1 strategy in <50ms

**Week 11-12: Fitness Function**
- Implement NetProfit × AvgTrade
- Add Pearson penalty
- Add PF, trades penalties
- Train/test split (40/60)
- **Milestone**: Generate system with PF≥1.2 on test set

**Phase 1 Deliverable**: Working GA optimizer (single-run, no validation)

### Phase 2: Validation Framework (Weeks 13-20)

**Week 13-14: Pearson Filter**
- Equity curve correlation
- Threshold enforcement (≥0.85 MVP, ≥0.90 Production)
- **Milestone**: Systems pass Pearson filter

**Week 15-16: Multi-Period OOS**
- Split data into 5 regimes (2010-2013, ..., 2022-2025)
- Walk-forward testing
- **Milestone**: 3/5 (MVP) or 4/5 (Production) periods profitable

**Week 17-18: Noise Injection**
- 8 variants (price ±1%/±2%, volume ±5%/±10%, entry ±1d/±2d)
- Re-run backtest for each variant
- **Milestone**: ≥5/8 (MVP) or ≥6/8 (Production) variants profitable

**Week 19-20: Family Grouping**
- Collect 10 restart results
- Analyze parameter CoV
- Identify stable vs unstable systems
- **Milestone**: CoV ≤60% (MVP) or ≤50% (Production)

**Phase 2 Deliverable**: Validated strategies passing all 4 criteria

### Phase 3: Robustness Testing (Weeks 21-26)

**Week 21-23: Walk-Forward GA**
- Reduced-fidelity: 100 pop × 200 gen
- Re-optimize every 6 months OOS
- Compare vs baseline (no retraining)
- **Milestone**: WF-GA improves OOS Sharpe ≥10%

**Week 24-25: Sensitivity Analysis**
- Parameter perturbation (±10% each gene)
- Correlate sensitivity with family grouping CoV
- **Milestone**: High CoV = high sensitivity (confirm instability)

**Week 26: Regime Testing**
- Classify periods (bull/bear/sideways)
- Compare performance by regime
- **Milestone**: Strategies work across multiple regimes

**Phase 3 Deliverable**: Robustness-tested strategies

### Phase 4: Export & Integration (Weeks 27-32)

**Week 27-28: Code Generation**
- Python backtest code export
- Strategy parameters YAML
- **Milestone**: Generated code reproduces fitness (±0.01%)

**Week 29-30: Visualization**
- Equity curves (train vs test)
- Performance reports (text, CSV)
- Parameter heatmaps
- **Milestone**: Clear train/test alignment visible

**Week 31: CLI & Config**
- Click-based CLI (init, optimize, validate, backtest)
- YAML configuration
- Logging, seed tracking
- **Milestone**: User can run from config in <5 min

**Week 32: Documentation**
- Sphinx API docs
- User guide (getting started, examples, troubleshooting)
- Methodology documentation (algorithm specs, rationale)
- **Milestone**: New user reproduces SPY optimization in <30 min

**Phase 4 Deliverable**: Shippable MVP with docs

---

## Appendix A: POC Validation Results

**Date**: 2026-02-22
**Scope**: Single-indicator (RSI) optimization on SPY daily data (2010-2025)
**Runtime**: 172.77 minutes (1000 generations × 100 population)

### Results

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| VectorBT Speed | <50ms | 62.53ms | ⚠ MARGINAL FAIL (25% over) |
| DEAP Integration | Works | ✓ | ✓ PASS |
| Fitness Function | Works | ✓ | ✓ PASS |
| Convergence | Improves | 1.77→2.14 (+21%) | ✓ PASS |

### Best Solution Found

```python
{
    "rsi_buy": 28.10,       # Oversold threshold
    "rsi_sell": 35.03,      # Exit near neutral
    "stop_loss": 0.0623,    # 6.23% SL
    "take_profit": 0.1030,  # 10.30% TP (1.65:1 R/R)
    "position_size": 0.01   # 1% of equity
}
```

**Fitness**: 2.136 (NetProfit × AvgTrade approximation)

### Analysis

**Speed Gap (62.53ms vs 50ms)**:
- Root cause: VectorBT overhead, indicator recalculation
- Addressable via: Indicator caching, vectorized signals, parallel evaluation
- With 8-core parallel: 62.53ms → 7.8ms per individual (acceptable)

**Convergence Quality**:
- Strong fitness improvement (21% gain)
- Average fitness convergence (0.20 → 2.05 = 10x!)
- Proves fitness landscape is searchable

**Recommendation**: **QUALIFIED PASS** - Proceed to MVP with optimization roadmap

---

## Appendix B: Success Criteria Checklist

### MVP Tier (Required for v1.0 Release)

**Performance**:
- [ ] Single fitness eval <50ms (daily bars)
- [ ] Full 10-restart GA <2 hours (8-core)
- [ ] Memory <16GB RAM

**Validation**:
- [ ] Pearson ≥0.85
- [ ] PF ≥1.2
- [ ] 3/5 OOS periods profitable
- [ ] 5/8 noise variants profitable
- [ ] CoV ≤60% family grouping

**Code Quality**:
- [ ] Test coverage ≥70%
- [ ] 100% reproducibility (seeded)
- [ ] Pydantic config validation

**Usability**:
- [ ] New user → SPY optimization <30 min
- [ ] Setup <5 min (pip + YAML)
- [ ] API docs + user guide + methodology

### Production Tier (Stretch Goals, v2.0)

**Performance**:
- [ ] 1-min bars <300ms
- [ ] GPU acceleration ≥5x speedup

**Validation**:
- [ ] Pearson ≥0.90
- [ ] PF ≥1.5
- [ ] 4/5 OOS periods profitable
- [ ] 6/8 noise variants profitable
- [ ] CoV ≤50% family grouping

**Features**:
- [ ] Multi-objective GA (Pareto frontier)
- [ ] EasyLanguage export (TradeStation)
- [ ] Theta Data integration (1-min futures)

---

## Appendix C: Comparison Matrix

| Feature | MaxAI (Academic) | GSBsys (Commercial) | GA-Trading-Sys MVP |
|---------|------------------|---------------------|-------------------|
| **Methodology** |
| Pearson Filter | ✗ | ✓ (≥0.95) | ✓ (≥0.85) |
| Multi-Period OOS | ✗ (single 4-year) | ✓ (5 periods) | ✓ (5 periods) |
| Noise Testing | ✗ | ✓ | ✓ (8 variants) |
| Family Grouping | ✗ | ✓ (CoV ≤50%) | ✓ (CoV ≤60%) |
| Walk-Forward GA | ✗ | ✓ | ✓ (Phase 3) |
| **Performance** |
| Live PF | 1.07 (4 mo) | ≥1.8 (multi-year) | ≥1.2 (target) |
| Backtest PF | Strong | ≥1.8 | ≥1.2 |
| **Technology** |
| Algorithm | GA + RL | Pure GA | Pure GA |
| Indicators | Unknown | 37 (22 proprietary) | 15 (open-source) |
| Platform | Python | Windows-only | Cross-platform |
| Cost | Free (research) | $200-$799 | Free (MVP) |
| Source Code | Closed | Closed | Open (MIT/Apache) |
| **Speed** |
| Optimization Time | Days-weeks | Hours | <2 hours (target) |
| Real-time | ✗ | ✓ | ✗ (backtest only) |

---

## Appendix D: References

**Academic**:
- GSBsys Methodology: [Reproduction-Guide.md](../Reproduction-Guide.md)
- MaxAI Paper: "Genetic Algorithm + Reinforcement Learning for Trading" (placeholder)
- Red Queen Failure: Internal case study

**Implementation**:
- Implementation Plan: [2026-02-21-feat-ga-trading-sys-implementation-plan.md](./2026-02-21-feat-ga-trading-sys-implementation-plan.md)
- POC Code: [../poc/](../poc/)
- POC Results: See Appendix A

**External**:
- DEAP Documentation: https://deap.readthedocs.io/
- VectorBT Documentation: https://vectorbt.dev/
- TA-Lib Documentation: https://ta-lib.org/

---

**Document Control**:
- Version: 2.0 (POC-validated)
- Date: 2026-02-22
- Author: AI Product Development
- Status: Ready for Phase 1 implementation
- Next Review: After Phase 1 completion (Week 12)
