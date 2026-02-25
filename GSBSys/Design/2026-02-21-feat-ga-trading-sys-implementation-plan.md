---
title: "GA-Trading-Sys: Pure Genetic Algorithm Trading System Optimizer - Implementation Plan"
type: feat
date: 2026-02-21
prd_version: 1.1
prd_path: Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Design/GA-Trading-Sys-PRD.md
status: ready
priority: p1

---

# GA-Trading-Sys Implementation Plan

## Executive Summary

Implement a production-grade, open-source genetic algorithm trading system optimizer with ≥93% fidelity to GSBsys commercial system. Target: reproduce 12 practitioner innovations (Pearson filter, multi-period OOS, noise testing, family grouping, walk-forward GA) to prevent Red Queen-style failures in live trading.

**Key Metrics:**
- **MVP Timeline**: 26 weeks (Phases 1-4, solo developer)
- **Production Tier**: +6 weeks (Phase 5, optional advanced features)
- **Performance Target**: <300ms per fitness evaluation, 2M evaluations in 16 hours (8-core parallel)
- **Validation Success**: Pearson ≥0.90, PF ≥1.5, 4/5 OOS periods pass, 6/8 noise variants profitable

**Critical Path:** Address 7 PRD gaps (data acquisition, team resources, validation thresholds, WF-GA spec, position sizing, commission model, indicator combination) → Resolve 5 spec-flow blocking questions (normalization, infeasible handling, computational cost, multi-market criteria, train/test split) → Phase 1 Core GA → Phase 2 Validation Framework → Phase 3 Robustness → Phase 4 Export/Integration.

---

## Problem Statement

### Current State

**Academic GA+RL systems fail in live trading:**
- **MaxAI** (best academic system): PF=1.07 live (4 months), rejected by GSBsys PF≥1.8 threshold
- **Red Queen** (catastrophic failure): Excellent backtest, capital decay in live trading
- **Gap**: Academic research lacks practitioner rigor (Pearson filters, multi-period OOS, noise testing)

**GSBsys provides commercial validation** (multi-year deployment, $200-$799 pricing) but is:
- Proprietary (closed-source)
- Partially documented (12 innovations identified, 22 indicators undocumented)
- Windows-only, expensive ($200-$799/license)

### Target State

**Open-source GA trading optimizer** achieving:
- ≥93% reproduction fidelity to GSBsys documented components
- Transparent methodology (all algorithms, parameters, validation public)
- Cross-platform (Python 3.10+, Windows/Linux/macOS)
- Free MVP tier (yfinance daily data, $0 cost)
- Production upgrade path (Theta Data 1-min futures, $150/month)

**Prevents overfitting via 4-stage validation:**
1. Pearson ≥0.90 equity filter (train/test consistency)
2. Multi-period OOS (4/5 regimes profitable)
3. Noise injection (6/8 perturbed variants profitable)
4. Family grouping (parameter stability CoV ≤50%)

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GA-Trading-Sys MVP                          │
│                   (Phases 1-4: 26 weeks)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ Data Pipeline    │────────>│ Indicator Engine │             │
│  │ (yfinance)       │         │ (TA-Lib 15 std)  │             │
│  └──────────────────┘         └──────────────────┘             │
│           │                            │                        │
│           v                            v                        │
│  ┌─────────────────────────────────────────────┐               │
│  │        Development GA (DEAP)                │               │
│  │  - Pop: 200, Gen: 1000, Restarts: 10       │               │
│  │  - SBX Crossover 95%, Gaussian Mutation 5% │               │
│  │  - Fitness: NetProfit × AvgTrade           │               │
│  │  - Vectorized Backtest (VectorBT/Numba)    │               │
│  └─────────────────────────────────────────────┘               │
│           │                                                     │
│           v                                                     │
│  ┌─────────────────────────────────────────────┐               │
│  │       Validation Framework                  │               │
│  │  - Pearson Equity Filter (≥0.90 MVP)       │               │
│  │  - Multi-Period OOS (4/5 regimes)          │               │
│  │  - Noise Injection (6/8 variants)          │               │
│  │  - Family Grouping (CoV ≤50%)              │               │
│  └─────────────────────────────────────────────┘               │
│           │                                                     │
│           v                                                     │
│  ┌─────────────────────────────────────────────┐               │
│  │      Export & Visualization                 │               │
│  │  - Python backtest code generation          │               │
│  │  - Equity curve plots (train vs test)      │               │
│  │  - Performance reports (Sharpe, PF, DD)    │               │
│  └─────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack (From PRD + Research)

| Component | Technology | Rationale | Version |
|-----------|-----------|-----------|---------|
| Core Language | Python 3.10+ | NumPy/Pandas ecosystem, DEAP support | 3.10+ |
| GA Framework | DEAP | Mature (10+ years), flexible, well-documented | 1.4+ |
| Backtesting | **VectorBT** | Vectorized (100x faster than loops), Numba-accelerated | 0.26+ |
| Indicators | TA-Lib | Battle-tested, C-optimized | 0.4.28+ |
| Data | yfinance (MVP), Theta Data (Phase 5) | Free daily, $150/mo 1-min futures | 0.2.30+ |
| Config | PyYAML + Pydantic | Type-safe validation | 6.0+, 2.0+ |
| Visualization | Matplotlib, Plotly | Static + interactive plots | 3.7+, 5.14+ |
| Testing | pytest + pytest-cov | TDD, 80% coverage target | 7.3+, 4.1+ |
| Parallelization | multiprocessing.Pool | Built-in, 8-core → 3x speedup | stdlib |
| JIT Compilation | Numba | <300ms backtest target | 0.58+ |

**Backtesting Engine Decision (From Research):**
- **VectorBT wins**: 100x faster than Backtrader, built-in TA-Lib, perfect for GA (2M evaluations)
- **Tradeoff**: Less flexible for complex entry logic, but weighted-sum signals (MVP) work fine
- **Fallback**: Backtrader for Phase 5 EasyLanguage validation (not GA loop)

---

## Critical Gaps Resolution (From PRD Review)

Before Phase 1 coding, resolve these 7 critical issues identified in PRD review:

### 1. Data Acquisition Strategy

**Decision:**
- **MVP (Phases 1-4)**: yfinance SPY/QQQ/IWM daily data (2010-2025, free)
- **Production (Phase 5+)**: Theta Data NQ/ES 1-min futures ($150/month)

**Implementation:**
```python
# Src/data/data_loader.py
def load_market_data(
    ticker: str = "SPY",
    source: str = "yfinance",
    start: str = "2010-01-01",
    end: str = "2025-12-31"
) -> pd.DataFrame:
    """
    Load OHLCV data from configured source.

    Args:
        ticker: Symbol (SPY, QQQ, IWM for MVP; NQ, ES for Production)
        source: "yfinance" (MVP) or "theta" (Phase 5)
        start/end: Date range

    Returns:
        pd.DataFrame with [Date, Open, High, Low, Close, Volume]
    """
    if source == "yfinance":
        import yfinance as yf
        df = yf.download(ticker, start=start, end=end, progress=False)
        df = df.reset_index()
        # Flatten MultiIndex if present
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    elif source == "theta":
        # Phase 5: Theta Data integration
        raise NotImplementedError("Theta Data integration deferred to Phase 5")
```

**Data Quality Checks (CORRECTED - Critical Fix):**
```python
import pandas as pd
import numpy as np

def validate_ohlcv_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify data integrity before backtesting.

    CRITICAL FIX: Previous version had incorrect constraints (High >= Close, Low <= Close).
    Valid OHLC bars can have Close outside [Open, High, Low] range due to gaps.

    Args:
        df: DataFrame with Date, Open, High, Low, Close, Volume columns

    Returns:
        Validated DataFrame (same as input if all checks pass)

    Raises:
        AssertionError: If data validation fails (production should use exceptions)
    """
    errors = []

    # Core OHLCV relationships
    if not df['High'].ge(df['Low']).all():
        errors.append("High < Low violation detected")
    if not df['High'].ge(df['Open']).all():
        errors.append("High < Open violation detected")
    if not df['Low'].le(df['Open']).all():
        errors.append("Low > Open violation detected")

    # Positive price validation
    if not (df['Close'] > 0).all():
        errors.append("Non-positive Close prices detected")
    if not (df['Open'] > 0).all():
        errors.append("Non-positive Open prices detected")
    if not (df['High'] > 0).all():
        errors.append("Non-positive High prices detected")
    if not (df['Low'] > 0).all():
        errors.append("Non-positive Low prices detected")

    # Volume validation
    if not df['Volume'].ge(0).all():
        errors.append("Negative volume detected")

    # NaN/inf validation
    if df.isnull().any().any():
        errors.append("NaN values detected")
    if np.isinf(df[['Open', 'High', 'Low', 'Close', 'Volume']]).any().any():
        errors.append("Inf values detected")

    # Temporal validation
    if not df['Date'].is_monotonic_increasing:
        errors.append("Non-sequential dates detected")
    if df['Date'].duplicated().any():
        errors.append("Duplicate timestamps detected")

    # Production: raise exception with all errors
    if errors:
        raise ValueError(f"Data validation failed:\n" + "\n".join(errors))

    return df
```

### 2. Team & Resource Planning

**Decision:** Solo developer (1 FTE) for MVP, optional scale to 2 FTE team

**Solo Developer Profile:**
- Python advanced (NumPy, Pandas, DEAP, multiprocessing)
- GA theory (crossover, mutation, selection, fitness landscapes)
- Financial domain (OHLCV, indicators, backtesting, position sizing)
- Timeline: 32 weeks (40 hrs/week, no blockers)

**Hardware Requirements:**
- **Minimum**: 8-core CPU, 16 GB RAM, 100 GB SSD
- **Recommended**: 12-16 core, 32 GB RAM, 500 GB NVMe (Phase 5 GPU: RTX 3060+ 12GB)

**Budget (Solo, Excluding Salary):**
| Item | MVP Cost | Production Cost |
|------|----------|-----------------|
| Data | $0 (yfinance) | $1200 (Theta $150×8 months) |
| Hardware | $0 (existing laptop) | $2000 (new workstation) |
| Software | $0 (open-source) | $0 |
| Cloud (optional) | $0 | $500 (AWS spot instances) |
| **Total** | **$0** | **$3700** |

### 3. Validation Thresholds (Relaxed from GSBsys for Public Data)

**Decision:** Two-tier validation (MVP vs Production)

**MVP Tier (Proof of Concept):**
| Metric | GSBsys Threshold | MVP Threshold | Rationale |
|--------|------------------|---------------|-----------|
| Pearson | ≥0.95 | **≥0.85** | 99.9% rejection too strict |
| PF Validation | ≥1.8 | **≥1.2** | GSBsys has proprietary data |
| Multi-Period OOS | 5/5 (100%) | **3/5 (60%)** | Allow regime failures |
| Noise Test | 6/8 (75%) | **5/8 (62.5%)** | Slight relaxation |
| Family CoV | ≤50% | **≤60%** | Higher tolerance for MVP |

**Production Tier (Commercial Grade):**
| Metric | Target | Rationale |
|--------|--------|-----------|
| Pearson | **≥0.90** | Still strict, prevents divergence |
| PF Validation | **≥1.5** | Between MVP and GSBsys |
| Multi-Period OOS | **4/5 (80%)** | 1 regime failure allowed |
| Noise Test | **6/8 (75%)** | Matches GSBsys |
| Family CoV | **≤50%** | Matches GSBsys |

**Rationale:** From my Volatility-Trader memory: "Hard CI gates incentivize p-hacking and are brittle across regimes." Use validation as REPORT RANKING, select top 10 systems, manual review.

### 4. Walk-Forward GA Specification (Full Detail)

**Decision:** Expand PRD Section 3.2.5 with complete chromosome encoding and fitness function

**Chromosome Encoding:**
```python
@dataclass
class WFChromosome:
    """Walk-Forward GA chromosome for retraining schedule optimization."""
    retrain_frequency: int  # [30, 60, 90, 120, 180] days (discrete)
    data_window: int        # [180, 365, 730, 1095] days (discrete)
    update_method: str      # ["replace", "ensemble", "parameter_blend"] (discrete)
    blend_weight_new: float # [0.3, 0.7] (continuous, only if parameter_blend)
    update_operator: str    # ["additive", "multiplicative"] (discrete)
```

**Fitness Function:**
```python
def wf_fitness(
    wf_chromosome: 'WFChromosome',
    base_system: list[float],
    oos_periods: list[tuple[datetime, datetime]]
) -> float:
    """
    Evaluate WF schedule by simulating retraining on historical OOS periods.

    Args:
        wf_chromosome: WFChromosome instance
        base_system: Best strategy from Development GA
        oos_periods: [(start, end), ...] test periods

    Returns:
        Average Sharpe ratio across OOS periods
    """
    sharpe_ratios = []

    for start, end in oos_periods:
        current_system = base_system.copy()
        performance = []
        current_date = start

        while current_date < end:
            # Trade for retrain_freq days
            trade_end = min(current_date + timedelta(days=wf_chromosome.retrain_frequency), end)
            pnl = backtest(current_system, current_date, trade_end)
            performance.append(pnl)

            # Retrain using last data_window days
            retrain_start = current_date - timedelta(days=wf_chromosome.data_window)
            new_system = run_development_ga(data[retrain_start:current_date], reduced_fidelity=True)

            # Update system based on update_method
            current_system = apply_update(current_system, new_system, wf_chromosome)
            current_date = trade_end

        sharpe_ratios.append(calculate_sharpe(performance))

    return np.mean(sharpe_ratios)
```

**Computational Cost Mitigation (From Spec-Flow Analysis):**
- **Problem**: Full-fidelity WF-GA = 96 days runtime (unusable)
- **Solution**: Reduced-fidelity retraining during WF-GA fitness evaluation
  - Development GA: 200 pop × 1000 gen = 200k evals
  - WF-GA retraining: **100 pop × 200 gen = 20k evals** (10× faster)
  - Degradation acceptable for WF schedule discovery

### 5. Position Sizing Strategy

**Decision:** Fixed fractional risk (2% per trade)

```python
def calculate_position_size(
    capital: float,
    stop_loss_dollars: float,
    risk_per_trade: float = 0.02
) -> int:
    """
    Fixed fractional position sizing.

    Args:
        capital: Current equity
        stop_loss_dollars: GA-optimized stop loss ($200-$2000)
        risk_per_trade: 2% default

    Returns:
        Number of contracts to trade
    """
    risk_amount = capital * risk_per_trade
    contracts = np.floor(risk_amount / stop_loss_dollars)
    return max(1, int(contracts))
```

**Alternative (Phase 5):** Half-Kelly criterion based on historical win rate

### 6. Commission & Slippage Model

**Decision:** Realistic costs from research

**Futures (Production - Theta Data):**
```python
COMMISSION_PER_RT = 2.50  # Dollars (conservative)
SLIPPAGE_TICKS = {
    'ES': 3 * 12.50,  # 3 ticks × $12.50 = $37.50
    'NQ': 3 * 5.00,   # 3 ticks × $5.00 = $15.00
    'YM': 3 * 5.00,   # 3 ticks × $5.00 = $15.00
}

def apply_costs_futures(gross_pnl, instrument, n_contracts):
    total_cost = (COMMISSION_PER_RT + SLIPPAGE_TICKS[instrument]) * n_contracts
    return gross_pnl - total_cost
```

**Stocks (MVP - yfinance):**
```python
COMMISSION_STOCKS = 0.0  # Zero commission (most brokers)
SLIPPAGE_BPS = 5  # 0.05% (half bid-ask spread)

def apply_costs_stocks(gross_pnl, entry_price, n_shares):
    slippage = entry_price * n_shares * SLIPPAGE_BPS / 10000
    return gross_pnl - slippage * 2  # Entry + exit
```

### 7. Indicator Combination Formula

**Decision:** Weighted sum (MVP), multiplicative (Phase 3 research)

**MVP Implementation:**
```python
def generate_signals_weighted_sum(individual, data):
    """
    Weighted sum signal combination (MVP).

    individual: [indicator_type, period, threshold, stop_loss, ...]
    """
    # Calculate indicator (normalized to [-100, +100])
    indicator = calculate_indicator_normalized(
        data['close'].values,
        indicator_type=individual[0],
        period=individual[1]
    )

    # Weighted signal
    weight = individual[2]  # Weight parameter
    signal = weight * indicator

    # Entry threshold
    threshold = individual[3]
    entry_long = signal > threshold
    entry_short = signal < -threshold

    return np.where(entry_long, 1, np.where(entry_short, -1, 0))
```

**Phase 3 Alternative (Multiplicative):**
```python
def generate_signals_multiplicative(individual, data):
    """Multiplicative signal combination (GSBsys-style)."""
    # Shift to positive range [0, 200]
    indicator_shifted = indicator_normalized + 100

    # Multiplicative combination
    signal = 1.0
    for i, weight in enumerate(weights):
        signal *= (indicator_shifted[i] / 100) ** weight

    # Entry when signal > 1.0 (bullish) or < 1.0 (bearish)
    return np.where(signal > 1.0 + threshold, 1, np.where(signal < 1.0 - threshold, -1, 0))
```

---

## Spec-Flow Blocking Questions Resolution

From SpecFlow analysis, resolve these 5 critical ambiguities:

### Q1: Normalization Window Size

**Question:** "HighestLowest to [-100, +100]" - rolling window size unspecified

**Decision:** 252-day rolling window (1 year)

```python
import pandas as pd

def normalize_indicator(indicator: pd.Series, window: int = 252) -> pd.Series:
    """
    Normalize to [-100, +100] using rolling highest/lowest.

    CRITICAL FIX: Removed fillna(0) which destroys time-series alignment.
    First (window-1) values will be NaN - caller MUST handle warm-up period.

    Args:
        indicator: Raw indicator values
        window: Rolling window size (252 = 1 year for daily data)

    Returns:
        Normalized series with NaN for first (window-1) observations

    Note:
        Caller must trim warm-up period or handle NaN appropriately.
        Do NOT fill NaN with arbitrary values (creates false signals).
    """
    rolling_high = indicator.rolling(window, min_periods=window).max()
    rolling_low = indicator.rolling(window, min_periods=window).min()

    # Normalized to [-100, +100] range
    normalized = 200 * (indicator - rolling_low) / (rolling_high - rolling_low + 1e-10) - 100

    # CRITICAL: Do NOT fill NaN - return as-is, caller handles warm-up
    return normalized


def train_test_split_timeseries(
    data: pd.DataFrame,
    train_frac: float = 0.4,
    warmup_bars: int = 252
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Sequential split for time-series with warm-up period removal.

    CRITICAL FIX: Removes first warmup_bars to avoid NaN from normalization.

    Args:
        data: Full dataset with DatetimeIndex
        train_frac: Fraction for training (0.4 = 40% train, 60% test)
        warmup_bars: Bars to trim (252 for annual normalization window)

    Returns:
        (train_df, test_df) with no NaN values

    Raises:
        AssertionError: If train/test overlap or NaN detected
    """
    # Trim warm-up period BEFORE splitting
    data_trimmed = data.iloc[warmup_bars:].copy()

    split_idx = int(len(data_trimmed) * train_frac)
    train = data_trimmed.iloc[:split_idx].copy()
    test = data_trimmed.iloc[split_idx:].copy()

    # Validation
    assert train.index[-1] < test.index[0], "Train/test temporal overlap detected"
    assert not train.isnull().any().any(), f"NaN in train set after trimming {warmup_bars} bars"
    assert not test.isnull().any().any(), f"NaN in test set after trimming {warmup_bars} bars"

    return train, test
```

### Q2: All-Infeasible Population Handling

**Question:** What if all 200 individuals fail fitness floors (Pearson < 0.90, PF < 1.2)?

**Decision:** Penalty function instead of hard rejection

```python
def fitness_with_penalty(individual, data):
    """
    Soft penalty for failed validation instead of hard rejection.

    Prevents GA selection from breaking when all individuals infeasible.
    """
    sharpe, pf_train, pf_test, pearson = evaluate_system(individual, data)

    # Base fitness
    fitness = sharpe

    # Penalties (subtractive)
    if pearson < 0.85:
        fitness -= (0.85 - pearson) * 10  # Heavy penalty
    if pf_train < 1.2:
        fitness -= (1.2 - pf_train) * 5
    if pf_test < 1.2:
        fitness -= (1.2 - pf_test) * 5

    return max(0.0, fitness),  # Floor at 0
```

**Alternative:** Adaptive threshold relaxation if population infeasible for 100+ generations

### Q3: Walk-Forward GA Computational Cost

**Resolved above in Gap #4** - Use reduced-fidelity retraining (100 pop × 200 gen)

### Q4: Multi-Market Partial Failure Interpretation

**Question:** If 2/3 markets pass, is system acceptable?

**Decision:** Tiered criteria

| Tier | Requirement | Rationale |
|------|-------------|-----------|
| MVP | 2/3 markets pass | Allow specialization |
| Production | **3/3 markets pass** | True generalization |

**Acceptance Test 9.8 Update:**
```python
def multi_market_validation(strategy, tickers=['SPY', 'QQQ', 'IWM']):
    results = []
    for ticker in tickers:
        data = load_market_data(ticker)
        pf, sharpe = backtest(strategy, data)
        passed = pf >= 1.2 and sharpe > 0
        results.append({'ticker': ticker, 'pf': pf, 'sharpe': sharpe, 'passed': passed})

    df = pd.DataFrame(results)

    # MVP: 2/3 pass, Production: 3/3 pass
    mvp_pass = df['passed'].sum() >= 2
    production_pass = df['passed'].sum() == 3

    return df, mvp_pass, production_pass
```

### Q5: Train/Test Split Method

**Question:** Sequential (time-series) vs random split?

**Decision:** **MUST be sequential** (time-series validity)

```python
def train_test_split_timeseries(data, train_frac=0.4):
    """
    Sequential split for time-series data.

    CRITICAL: Random split creates lookahead bias in backtesting.
    """
    split_idx = int(len(data) * train_frac)

    train = data.iloc[:split_idx]
    test = data.iloc[split_idx:]

    assert train.index[-1] < test.index[0], "Train/test overlap detected"

    return train, test
```

---

## Technical Approach

### Phase 1: Core GA Engine (12 weeks, solo)

**Deliverables:**
1. Data pipeline (yfinance, CSV/Parquet, normalization)
2. 15 standard indicators (TA-Lib integration)
3. Position sizing (fixed fractional risk)
4. Commission/slippage model
5. Basic GA engine (DEAP framework)
6. VectorBT backtest integration
7. Performance reporting (Sharpe, PF, drawdown)

**File Structure:**
```
GA-Trading-Sys/
├── Src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_loader.py          # yfinance integration
│   │   ├── data_validator.py       # OHLCV quality checks
│   │   └── normalization.py        # HighestLowest [-100, +100]
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── ta_lib_wrapper.py       # 15 standard indicators
│   │   └── signal_generator.py     # Weighted sum / multiplicative
│   ├── ga/
│   │   ├── __init__.py
│   │   ├── chromosome.py           # Individual encoding
│   │   ├── operators.py            # SBX crossover, Gaussian mutation
│   │   ├── fitness.py              # NetProfit × AvgTrade
│   │   └── evolution.py            # DEAP integration, 10 restarts
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── vectorized_backtest.py  # Numba-optimized (<300ms target)
│   │   └── costs.py                # Commission, slippage models
│   ├── validation/
│   │   ├── __init__.py
│   │   └── basic_validation.py     # Profit factor floors
│   └── utils/
│       ├── __init__.py
│       ├── position_sizing.py      # Fixed fractional risk
│       └── risk_metrics.py         # Sharpe, Sortino, Omega
├── tests/
│   ├── test_data_loader.py
│   ├── test_indicators.py
│   ├── test_ga_operators.py
│   ├── test_backtest.py
│   └── test_validation.py
├── experiments/
│   ├── 01_baseline_buy_hold.py
│   ├── 02_single_indicator_ga.py
│   └── results/
├── requirements.txt
├── pyproject.toml
└── README.md
```

**Week-by-Week Breakdown:**
- **Week 1-2**: Data pipeline + validation (yfinance, OHLCV checks, normalization)
- **Week 3-4**: Indicators (TA-Lib wrapper, 15 standard, signal generator)
- **Week 5-6**: Position sizing + costs (fixed fractional, commission/slippage)
- **Week 7-9**: GA engine (DEAP setup, SBX/Gaussian operators, fitness function)
- **Week 10-11**: VectorBT integration (vectorized backtest, Numba optimization)
- **Week 12**: Performance reporting + testing (Sharpe/PF/DD, pytest suite)

**Success Criteria (Phase 1):**
- [ ] Load SPY daily data 2010-2025 via yfinance
- [ ] Calculate all 15 standard indicators (TA-Lib)
- [ ] Run single GA optimization (200 pop, 1000 gen, 1 restart)
- [ ] Generate trading system with PF ≥ 1.2 on test set
- [ ] Single fitness evaluation <50ms (daily bars)
- [ ] Code coverage ≥70%

**Critical Path Items:**
1. **Numba backtest optimization** (Week 10-11) - Blocks <300ms target
2. **DEAP parallelization setup** (Week 7) - Blocks 10-restart performance
3. **TA-Lib installation** (Week 3) - Requires C library, platform-specific

**Risks & Mitigation:**
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| TA-Lib C library install fails | High | Medium | Fallback: pandas-ta (pure Python) |
| VectorBT too slow (>300ms) | High | Low | Profile, optimize hot paths, reduce data size |
| GA doesn't converge | Medium | Medium | Tune crossover/mutation rates, increase generations |

---

### Phase 2: Validation Framework (8 weeks, solo)

**Deliverables:**
1. Pearson equity curve filter (train/test correlation)
2. Multi-period OOS validation (5 regime windows)
3. 10-restart multi-start GA (parallelization)
4. Indicator pre-filtering (rank 15, select top 10)
5. Family grouping (parameter perturbation, CoV)
6. Bounded parameter optimization
7. Tiered validation thresholds (MVP vs Production)
8. Comprehensive logging (random seeds, reproducibility)

**New Files:**
```
Src/validation/
├── pearson_filter.py       # Equity curve correlation
├── multi_period_oos.py     # 5-regime testing
├── family_grouping.py      # Parameter stability (CoV)
├── indicator_filter.py     # Pre-filtering (rank top 10)
└── validation_report.py    # Comprehensive validation output
```

**Week-by-Week Breakdown:**
- **Week 13-14**: Pearson filter (train/test equity correlation, threshold validation)
- **Week 15-16**: Multi-period OOS (5 regime windows, walk-forward splits)
- **Week 17**: 10-restart GA (parallelization with multiprocessing.Pool)
- **Week 18-19**: Indicator pre-filtering (10k single-indicator trials, rank by PF)
- **Week 20-21**: Family grouping (±5% perturbation, CoV calculation)
- **Week 22**: Bounded optimization + tiered thresholds + logging

**Success Criteria (Phase 2):**
- [ ] Systems pass MVP tier: Pearson ≥0.85, PF ≥1.2, 3/5 OOS periods
- [ ] Systems pass Production tier: Pearson ≥0.90, PF ≥1.5, 4/5 OOS periods
- [ ] Family grouping identifies stable systems (CoV ≤60% MVP, ≤50% Production)
- [ ] 10 restarts produce diverse solutions (population diversity >15%)
- [ ] All runs reproducible via logged random seeds

**Critical Path Items:**
1. **Multiprocessing parallelization** (Week 17) - Blocks 10-restart performance target
2. **Regime classification logic** (Week 15) - Requires VIX-based volatility regimes
3. **Indicator pre-filter correctness** (Week 18) - Must not introduce bias

---

### Phase 3: Robustness Testing (6 weeks, solo)

**Deliverables:**
1. Noise injection testing (8 perturbed datasets, ±0.5% price)
2. Monte Carlo robustness (reshuffle, resample, permutation)
3. Walk-Forward GA engine (retraining schedule optimization)
4. Parameter sensitivity analysis (correlates with family grouping)

**New Files:**
```
Src/validation/
├── noise_injection.py      # 8 randomized variants
├── monte_carlo.py          # Reshuffle/resample tests
Src/ga/
└── walk_forward_ga.py      # WF-GA with reduced-fidelity retraining
```

**Week-by-Week Breakdown:**
- **Week 23-24**: Noise injection (±0.5% price perturbation, 8 variants, 6/8 pass threshold)
- **Week 25**: Monte Carlo tests (reshuffle bar order, resample with replacement)
- **Week 26-27**: Walk-Forward GA engine (chromosome encoding, fitness function, reduced-fidelity)
- **Week 28**: Parameter sensitivity (align with family grouping, CoV analysis)

**Success Criteria (Phase 3):**
- [ ] MVP: Systems profitable on ≥5/8 noise variants (62.5%)
- [ ] Production: Systems profitable on ≥6/8 noise variants (75%)
- [ ] WF-GA improves OOS Sharpe by ≥10% vs baseline (no retraining)
- [ ] WF-GA runtime <24 hours (reduced-fidelity: 100 pop × 200 gen)
- [ ] Sensitivity analysis correlates with family grouping (high CoV = unstable)

**Critical Path Items:**
1. **WF-GA computational cost** (Week 26-27) - Must achieve reduced-fidelity speedup
2. **Noise perturbation randomness** (Week 23) - Must be reproducible (seeded RNG)

---

### Phase 4: Export & Integration (6 weeks, solo)

**Deliverables:**
1. Python backtest code generator (reproduces fitness metrics)
2. JSON strategy export (REPLACES pickle for security)
3. Result visualization (equity curves, GA convergence plots)
4. CLI polish (progress bars, colored output, help text)
5. Comprehensive documentation (user guide, API reference, Sphinx)
6. Hyperparameter tuning protocol (population/crossover/mutation sensitivity)

**New Files:**
```
Src/export/
├── python_code_gen.py      # Generate standalone backtest script
├── json_exporter.py        # SECURITY FIX: JSON strategy export (replaces pickle)
└── visualization.py        # Equity curves, GA convergence
Src/cli/
├── main.py                 # CLI entry point (Click/Typer)
└── progress.py             # tqdm progress bars
docs/
├── user_guide.md
├── api_reference.md
└── methodology.md
```

**SECURITY FIX - JSON Export (replaces pickle):**
```python
# Src/export/json_exporter.py
import json
from dataclasses import dataclass, asdict
from typing import Any
from pathlib import Path

@dataclass
class StrategyExport:
    """
    Safe, serializable strategy representation.

    SECURITY: Replaces pickle (RCE vulnerability) with JSON.
    """
    chromosome: list[float]  # GA chromosome values
    fitness_metrics: dict[str, float]  # Sharpe, PF, trades, etc.
    validation_results: dict[str, Any]  # Pearson, OOS, noise, family
    metadata: dict[str, Any]  # Ticker, dates, random seed, GA config

    def to_json_file(self, path: Path) -> None:
        """Export strategy to JSON file (safe, no code execution)."""
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def from_json_file(cls, path: Path) -> 'StrategyExport':
        """Load strategy from JSON file with validation."""
        with open(path, 'r') as f:
            data = json.load(f)

        # Validate required fields
        required = {'chromosome', 'fitness_metrics', 'validation_results', 'metadata'}
        if not required.issubset(data.keys()):
            raise ValueError(f"Invalid strategy file, missing keys: {required - set(data.keys())}")

        # Type validation
        if not isinstance(data['chromosome'], list):
            raise TypeError("Chromosome must be list")
        if not isinstance(data['fitness_metrics'], dict):
            raise TypeError("Fitness metrics must be dict")

        return cls(**data)
```

**Week-by-Week Breakdown:**
- **Week 29-30**: Python code generator (export best strategy as standalone script)
- **Week 31**: Visualization (train vs test equity, GA fitness over generations)
- **Week 32**: CLI polish (Click framework, progress bars, colored logging)
- **Week 33-34**: Documentation (Sphinx API docs, user guide, methodology)

**Success Criteria (Phase 4):**
- [ ] Generated Python code reproduces fitness metrics (±0.01% tolerance)
- [ ] Users can run full GA optimization from YAML config in <5 min setup
- [ ] Documentation enables new user to reproduce SPY optimization in <30 min
- [ ] Visualization shows train vs test equity alignment clearly
- [ ] Code coverage ≥80%

**EasyLanguage Deferred to Phase 5** (4 weeks estimated complexity):
- Requires TradeStation SDK research (2 weeks)
- Bar-by-bar translation non-trivial (2 weeks)
- TradeStation subscription for testing ($99/month)

---

### Phase 5: Advanced Features (8 weeks, optional)

**Deliverables:**
1. EasyLanguage code generator (TradeStation/MultiCharts)
2. Backtrader integration (complex entry/exit logic fallback)
3. Multi-objective fitness (Pareto frontier: return vs risk)
4. Adaptive mutation (anneal mutation rate by generation)
5. GPU acceleration (CUDA/JAX for parallel fitness evaluations)
6. Theta Data integration (1-min futures upgrade path)

**Success Criteria (Phase 5):**
- [ ] Generated EasyLanguage compiles in TradeStation
- [ ] EasyLanguage backtest reproduces Python fitness (±1% tolerance)
- [ ] Multi-objective GA produces Pareto frontier (10+ non-dominated solutions)
- [ ] GPU acceleration achieves ≥5x speedup (realistic, not 10x)
- [ ] Theta Data integration enables 1-min futures optimization

---

## Implementation Phases (Detailed Specifications)

### Chromosome Encoding (DEAP Implementation)

```python
from deap import creator, base, tools
import random

# Fitness: maximize NetProfit × AvgTrade
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# Individual: hybrid discrete-continuous chromosome
creator.create("Individual", list, fitness=creator.FitnessMax)

def init_individual() -> list[float | int]:
    """
    Initialize GA chromosome.

    Genes:
    [0] indicator_type: int [0, 14] - which of 15 standard indicators
    [1] period: int [5, 100] - indicator period
    [2] weight: float [-1.0, 2.0] - signal weighting (negative = contrarian)
    [3] threshold: float [0.0, 50.0] - entry threshold
    [4] stop_loss: float [200, 2000] - dollars
    [5] take_profit: float [200, 2000] - dollars
    [6] position_size_mult: float [0.5, 2.0] - position sizing multiplier
    """
    return [
        random.randint(0, 14),          # [0] indicator_type
        random.randint(5, 100),         # [1] period
        random.uniform(-1.0, 2.0),      # [2] weight
        random.uniform(0.0, 50.0),      # [3] threshold
        random.uniform(200, 2000),      # [4] stop_loss
        random.uniform(200, 2000),      # [5] take_profit
        random.uniform(0.5, 2.0),       # [6] position_size_mult
    ]

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
```

### Genetic Operators

```python
def crossover_hybrid(
    ind1: list[float | int],
    ind2: list[float | int]
) -> tuple[list[float | int], list[float | int]]:
    """
    Hybrid crossover: uniform for discrete genes, SBX for continuous.

    Discrete: [0, 1] (indicator_type, period)
    Continuous: [2, 3, 4, 5, 6] (weight, threshold, stops, position_size)
    """
    # Discrete: uniform crossover
    if random.random() < 0.5:
        ind1[0], ind2[0] = ind2[0], ind1[0]
    if random.random() < 0.5:
        ind1[1], ind2[1] = ind2[1], ind1[1]

    # Continuous: SBX (Simulated Binary Crossover)
    tools.cxSimulatedBinaryBounded(
        ind1[2:], ind2[2:],
        eta=20.0,  # Crowding degree
        low=[-1.0, 0.0, 200, 200, 0.5],
        up=[2.0, 50.0, 2000, 2000, 2.0]
    )

    return ind1, ind2

def mutate_hybrid(individual: list[float | int]) -> tuple[list[float | int]]:
    """
    Hybrid mutation: random flip for discrete, Gaussian for continuous.
    """
    # Discrete: random flip with 5% probability
    if random.random() < 0.05:
        individual[0] = random.randint(0, 14)
    if random.random() < 0.05:
        individual[1] = random.randint(5, 100)

    # Continuous: Gaussian mutation
    tools.mutGaussian(
        individual[2:],
        mu=0.0,
        sigma=0.1,  # 10% standard deviation
        indpb=0.05   # 5% probability per gene
    )

    # Enforce bounds
    individual[2] = np.clip(individual[2], -1.0, 2.0)
    individual[3] = np.clip(individual[3], 0.0, 50.0)
    individual[4] = np.clip(individual[4], 200, 2000)
    individual[5] = np.clip(individual[5], 200, 2000)
    individual[6] = np.clip(individual[6], 0.5, 2.0)

    return individual,

toolbox.register("mate", crossover_hybrid)
toolbox.register("mutate", mutate_hybrid)
toolbox.register("select", tools.selTournament, tournsize=3)
```

### Fitness Function (NetProfit × AvgTrade with Floors)

```python
def evaluate_individual(
    individual: list[float | int],
    data: pd.DataFrame
) -> tuple[float]:
    """
    Fitness evaluation with penalty function for failed validation.

    Returns:
        Tuple of (fitness_score,) for DEAP
    """
    # Generate signals from chromosome
    signals = generate_signals_weighted_sum(individual, data)

    # Split data (sequential for time-series)
    train, test = train_test_split_timeseries(data, train_frac=0.4)

    # Backtest on train
    train_sharpe, train_pf, train_trades = vectorized_backtest(
        signals[:len(train)],
        train['close'].values,
        stop_loss=individual[4],
        take_profit=individual[5],
        position_size=individual[6]
    )

    # Backtest on test
    test_sharpe, test_pf, test_trades = vectorized_backtest(
        signals[len(train):],
        test['close'].values,
        stop_loss=individual[4],
        take_profit=individual[5],
        position_size=individual[6]
    )

    # Equity curve correlation (Pearson filter)
    train_equity = generate_equity_curve(signals[:len(train)], train)
    test_equity = generate_equity_curve(signals[len(train):], test)
    pearson = calculate_pearson(train_equity, test_equity)

    # Base fitness: NetProfit × AvgTrade
    # Approximate as: Sharpe × sqrt(n_trades)
    net_profit_approx = test_sharpe * np.sqrt(max(test_trades, 1))
    avg_trade_approx = test_sharpe / np.sqrt(max(test_trades, 1))
    fitness = net_profit_approx * avg_trade_approx

    # Penalties (soft constraints)
    if pearson < 0.85:
        fitness -= (0.85 - pearson) * 10
    if train_pf < 1.2:
        fitness -= (1.2 - train_pf) * 5
    if test_pf < 1.2:
        fitness -= (1.2 - test_pf) * 5
    if test_trades < 30:
        fitness -= (30 - test_trades) * 0.1

    return max(0.0, fitness),  # Floor at 0

toolbox.register("evaluate", evaluate_individual)
```

### BacktestEngine Adapter (P0 FIX - Decoupling)

**CRITICAL FIX:** Decouple fitness function from VectorBT to enable testing, future engine swaps, and reduce tight coupling.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

@dataclass
class BacktestResult:
    """Standardized backtest output across all engines."""
    sharpe_ratio: float
    profit_factor: float
    n_trades: int
    equity_curve: np.ndarray
    returns: np.ndarray

class BacktestEngine(Protocol):
    """Protocol defining backtest engine interface (duck typing)."""

    def run(
        self,
        signals: np.ndarray,
        prices: np.ndarray,
        stop_loss: float,
        take_profit: float,
        position_size: float
    ) -> BacktestResult:
        """Execute backtest and return standardized results."""
        ...

class NumbaBacktestEngine:
    """Numba-optimized vectorized backtest (default MVP engine)."""

    def run(
        self,
        signals: np.ndarray,
        prices: np.ndarray,
        stop_loss: float,
        take_profit: float,
        position_size: float
    ) -> BacktestResult:
        """Delegate to Numba JIT implementation."""
        sharpe, pf, trades, equity, returns = vectorized_backtest_impl(
            signals, prices, stop_loss, take_profit, position_size
        )
        return BacktestResult(sharpe, pf, trades, equity, returns)

class VectorBTEngine:
    """VectorBT adapter (Phase 5 alternative if needed)."""

    def run(
        self,
        signals: np.ndarray,
        prices: np.ndarray,
        stop_loss: float,
        take_profit: float,
        position_size: float
    ) -> BacktestResult:
        """Use VectorBT Portfolio.from_signals()."""
        import vectorbt as vbt
        portfolio = vbt.Portfolio.from_signals(
            prices,
            entries=signals > 0,
            exits=signals < 0,
            sl_stop=stop_loss,
            tp_stop=take_profit,
            size=position_size
        )
        return BacktestResult(
            sharpe_ratio=portfolio.sharpe_ratio(),
            profit_factor=portfolio.stats()['Profit Factor'],
            n_trades=portfolio.stats()['Total Trades'],
            equity_curve=portfolio.value().values,
            returns=portfolio.returns().values
        )

# Global engine instance (injected for testing)
_backtest_engine: BacktestEngine = NumbaBacktestEngine()

def set_backtest_engine(engine: BacktestEngine) -> None:
    """Inject custom backtest engine (for testing or engine swap)."""
    global _backtest_engine
    _backtest_engine = engine

def get_backtest_engine() -> BacktestEngine:
    """Get current backtest engine."""
    return _backtest_engine
```

**Updated fitness function (uses adapter):**
```python
def evaluate_individual(
    individual: list[float | int],
    data: pd.DataFrame
) -> tuple[float]:
    """Fitness evaluation with BacktestEngine adapter (DECOUPLED)."""
    signals = generate_signals_weighted_sum(individual, data)
    train, test = train_test_split_timeseries(data, train_frac=0.4)

    # Use injected engine instead of hard-coded vectorized_backtest
    engine = get_backtest_engine()

    train_result = engine.run(
        signals[:len(train)],
        train['close'].values,
        stop_loss=individual[4],
        take_profit=individual[5],
        position_size=individual[6]
    )

    test_result = engine.run(
        signals[len(train):],
        test['close'].values,
        stop_loss=individual[4],
        take_profit=individual[5],
        position_size=individual[6]
    )

    # Validation and fitness calculation unchanged
    pearson = calculate_pearson(train_result.equity_curve, test_result.equity_curve)
    net_profit_approx = test_result.sharpe_ratio * np.sqrt(max(test_result.n_trades, 1))
    avg_trade_approx = test_result.sharpe_ratio / np.sqrt(max(test_result.n_trades, 1))
    fitness = net_profit_approx * avg_trade_approx

    # Penalties
    if pearson < 0.85:
        fitness -= (0.85 - pearson) * 10
    if train_result.profit_factor < 1.2:
        fitness -= (1.2 - train_result.profit_factor) * 5
    if test_result.profit_factor < 1.2:
        fitness -= (1.2 - test_result.profit_factor) * 5
    if test_result.n_trades < 30:
        fitness -= (30 - test_result.n_trades) * 0.1

    return max(0.0, fitness),
```

### Vectorized Backtest (Numba-Optimized)

```python
import numba
import numpy as np

@numba.jit(nopython=True, cache=True, fastmath=True)
def vectorized_backtest_impl(
    signals: np.ndarray,
    prices: np.ndarray,
    stop_loss: float,
    take_profit: float,
    position_size_mult: float
) -> tuple[float, float, int, np.ndarray, np.ndarray]:
    """
    Ultra-fast backtest targeting <50ms for daily data, <300ms for 1-min data.

    RENAMED from vectorized_backtest() to _impl() for BacktestEngine adapter pattern.

    Args:
        signals: np.array of entry signals (-1, 0, 1)
        prices: np.array of close prices
        stop_loss: Dollar stop loss
        take_profit: Dollar take profit
        position_size_mult: Position size multiplier

    Returns:
        (sharpe_ratio, profit_factor, n_trades, equity_curve, returns)
    """
    n = len(prices)
    capital = 100000.0  # Starting capital
    equity = capital
    equity_curve = np.zeros(n)
    equity_curve[0] = capital
    position = 0.0
    entry_price = 0.0
    entry_idx = 0
    trades = []

    for i in range(1, n):
        # Exit logic (if in position)
        if position != 0:
            pnl_dollars = (prices[i] - entry_price) * position

            # Check stop-loss and take-profit
            exit_signal = (pnl_dollars <= -stop_loss) or (pnl_dollars >= take_profit)

            if exit_signal or signals[i] == -position:
                # Close position
                equity += pnl_dollars
                trades.append(pnl_dollars)
                position = 0.0

        # Entry logic (if flat)
        if position == 0 and signals[i] != 0:
            # Calculate position size (fixed fractional risk)
            contracts = int(equity * 0.02 / stop_loss * position_size_mult)
            contracts = max(1, min(contracts, int(equity / prices[i])))

            position = signals[i] * contracts
            entry_price = prices[i]
            entry_idx = i

        # Update equity curve
        if position != 0:
            equity_curve[i] = equity + (prices[i] - entry_price) * position
        else:
            equity_curve[i] = equity

    # Close any remaining position at end
    if position != 0:
        pnl_dollars = (prices[-1] - entry_price) * position
        equity += pnl_dollars
        equity_curve[-1] = equity
        trades.append(pnl_dollars)

    # Calculate metrics
    if len(trades) == 0:
        returns_arr = np.zeros(1)
        return 0.0, 1.0, 0, equity_curve, returns_arr

    trades_arr = np.array(trades)
    returns_arr = trades_arr / capital

    sharpe = np.mean(returns_arr) / (np.std(returns_arr) + 1e-10) * np.sqrt(252)

    winners = trades_arr[trades_arr > 0]
    losers = trades_arr[trades_arr < 0]

    if len(losers) == 0:
        profit_factor = 999.0
    else:
        profit_factor = np.sum(winners) / abs(np.sum(losers))

    return sharpe, profit_factor, len(trades), equity_curve, returns_arr
```

---

## Alternative Approaches Considered

### 1. Backtrader vs VectorBT

**Rejected: Backtrader** (event-driven backtesting)

**Pros:**
- High flexibility for complex entry/exit logic
- Mature ecosystem (8+ years)
- Good for manual strategy prototyping

**Cons:**
- **100x slower** than VectorBT (event-driven Python loops vs vectorized NumPy)
- For 2M GA evaluations: 2M × 300ms = 23 days vs 16 hours with VectorBT
- Not suitable for GA optimization loops

**Decision:** VectorBT for MVP (Phases 1-4), optional Backtrader for Phase 5 EasyLanguage validation

---

### 2. DEAP vs Custom GA Implementation

**Rejected: Custom GA** (from scratch)

**Pros:**
- Full control over operators
- No dependency on DEAP API changes

**Cons:**
- Reinventing the wheel (DEAP is battle-tested, 10+ years mature)
- Months of development time for crossover/mutation/selection operators
- No parallelization out-of-box (would need to implement multiprocessing)

**Decision:** DEAP (standard in academic/industry GA research)

---

### 3. Strict Validation (GSBsys Thresholds) vs Tiered Validation (MVP/Production)

**Rejected: Strict GSBsys Thresholds** (Pearson ≥0.95, PF ≥1.8, 5/5 OOS)

**Pros:**
- Matches commercial system exactly
- Maximum overfitting prevention

**Cons:**
- **99.9% rejection rate** when compounded (Pearson 10% × PF 5% × OOS 20% × Noise 40% = 0.004%)
- May produce zero systems after 2M evaluations
- Too strict for public data (yfinance vs professional feeds)

**Decision:** Tiered validation (MVP relaxed thresholds, Production closer to GSBsys)

---

## Acceptance Criteria

### Functional Requirements

#### Phase 1 (Core GA)
- [ ] Load SPY/QQQ/IWM daily data 2010-2025 via yfinance
- [ ] Calculate all 15 standard indicators correctly (validated against TA-Lib reference)
- [ ] GA converges within 1,000 generations (fitness improvement >10%)
- [ ] 10 restarts produce diverse solutions (population diversity >15%)
- [ ] Single fitness evaluation <50ms (daily bars, ~4000 bars)
- [ ] Generate system with PF ≥1.2 on test set (40/60 split)

#### Phase 2 (Validation Framework)
- [ ] Systems pass MVP tier: Pearson ≥0.85, PF ≥1.2, 3/5 OOS periods
- [ ] Systems pass Production tier: Pearson ≥0.90, PF ≥1.5, 4/5 OOS periods
- [ ] Family grouping identifies stable systems (CoV ≤60% MVP, ≤50% Production)
- [ ] All runs reproducible via logged random seeds
- [ ] Indicator pre-filtering reduces search space (15 → 10 indicators)

#### Phase 3 (Robustness)
- [ ] MVP: Systems profitable on ≥5/8 noise variants (62.5%)
- [ ] Production: Systems profitable on ≥6/8 noise variants (75%)
- [ ] WF-GA improves OOS Sharpe by ≥10% vs baseline
- [ ] WF-GA runtime <24 hours (reduced-fidelity: 100 pop × 200 gen)
- [ ] Parameter sensitivity correlates with family grouping

#### Phase 4 (Export/Integration)
- [ ] Generated Python code reproduces fitness metrics (±0.01% tolerance)
- [ ] Users can run full GA optimization from YAML config in <5 min setup
- [ ] Documentation enables new user to reproduce SPY optimization in <30 min
- [ ] Visualization shows train vs test equity alignment clearly

### Non-Functional Requirements

#### Performance
- [ ] Single fitness eval <50ms (daily bars), <300ms (1-min bars)
- [ ] Full 10-restart GA cycle <2 hours wall-time (daily data, 8-core parallel)
- [ ] Memory usage <16GB RAM throughout execution

#### Quality
- [ ] Code coverage ≥70% (Phase 1-2), ≥80% (Phase 3-4)
- [ ] All GA runs reproducible via logged random seeds
- [ ] Configuration validated via Pydantic schemas

#### Documentation
- [ ] Sphinx API documentation with docstrings
- [ ] User guide with getting started, examples, troubleshooting
- [ ] Methodology documentation (GA parameters, validation, rationale)

### Comparison to Baselines

#### vs MaxAI (Best Academic GA+RL)
- [ ] Achieve PF ≥ MaxAI's 1.07 ✓ (our MVP: 1.2, Production: 1.5)
- [ ] Pass Pearson equity filter ✓ (MaxAI doesn't use, we require ≥0.85-0.90)
- [ ] Validate across ≥5 OOS periods ✓ (MaxAI single 4-year backtest)
- [ ] Complete faster ✓ (MVP: ~2 hours, MaxAI: days-weeks with RL training)

#### vs GSBsys (Commercial Baseline)
- [ ] Match GA parameters ✓ (Pop=200, Gen=1000, Restarts=10, CR=95%, MR=5%)
- [ ] Match validation methodology ✓ (Pearson, multi-period OOS, noise, family grouping)
- [ ] Fitness function ✓ (Net Profit × Avg Trade)
- [ ] Relaxed thresholds (Pearson 0.90 vs 0.95, PF 1.5 vs 1.8) - documented gap
- [ ] **Missing proprietary indicators** (15 standard vs 37 total) - documented gap

#### vs Red Queen (Failed GA+RL)
- [ ] Pearson filter prevents train/live divergence ✓ (Red Queen catastrophic failure)
- [ ] Noise testing catches data-specific overfitting ✓ (Red Queen lacked)
- [ ] Multi-period OOS prevents regime-specific optimization ✓ (Red Queen lacked)

---

## Dependencies & Prerequisites

### Software Dependencies

```txt
# requirements.txt

# Core
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0

# GA Framework
deap>=1.4.0

# Backtesting
vectorbt>=0.26.0

# Technical Indicators
TA-Lib>=0.4.28  # Requires C library: https://github.com/ta-lib/ta-lib-python

# Data
yfinance>=0.2.30
pyarrow>=14.0.0  # For Parquet

# JIT Compilation
numba>=0.58.0

# Configuration
pyyaml>=6.0.0
pydantic>=2.0.0

# Visualization
matplotlib>=3.7.0
plotly>=5.14.0

# CLI
click>=8.1.0
tqdm>=4.65.0

# Testing
pytest>=7.3.0
pytest-cov>=4.1.0

# Documentation
sphinx>=6.2.0
sphinx-rtd-theme>=1.2.0
```

**Critical Installation Steps:**

1. **TA-Lib C Library** (platform-specific):
   ```bash
   # macOS
   brew install ta-lib

   # Ubuntu/Debian
   sudo apt-get install ta-lib

   # Windows
   # Download precompiled from: https://github.com/cgohlke/talib-build/releases
   pip install TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl
   ```

2. **VectorBT** (optional C++ dependencies for speed):
   ```bash
   pip install vectorbt[full]  # Includes numba, TA-Lib bindings
   ```

### Hardware Prerequisites

**Minimum Spec (MVP - Daily Data):**
- CPU: 8 cores (Intel i7/i9, AMD Ryzen 7/9)
- RAM: 16 GB
- Storage: 100 GB SSD
- OS: Windows 10+, macOS 11+, Ubuntu 20.04+

**Recommended Spec (Production - 1-min Data):**
- CPU: 12-16 cores (Ryzen 9, Threadripper, Xeon)
- RAM: 32 GB
- Storage: 500 GB NVMe SSD
- GPU: NVIDIA RTX 3060+ 12GB VRAM (Phase 5 GPU acceleration)

### Data Prerequisites

**MVP (Phases 1-4):**
- yfinance API access (free, no API key required)
- Stable internet connection for initial download
- ~50 MB disk space per ticker (SPY/QQQ/IWM daily 2010-2025)

**Production (Phase 5):**
- Theta Data subscription ($150/month)
- ~5 GB disk space per ticker (NQ/ES 1-min 2015-2025)
- Theta Data API key

---

## Risk Analysis & Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| **GA doesn't converge in 1000 generations** | High | Medium | Tune crossover/mutation rates (sweep 85-98%, 3-10%), add adaptive operators | Increase to 2000 generations, reduce population to 150 |
| **Fitness evaluation >300ms (1-min data)** | High | Low | Profile with line_profiler, optimize hot paths, use Numba JIT | Reduce data size (skip 1-min, use 5-min bars), reduce GA population |
| **VectorBT can't handle indicator combination** | Medium | Low | Test weighted-sum signals early (Phase 1), verify VectorBT API compatibility | Fallback: Backtrader (slower but more flexible) |
| **TA-Lib installation fails** | Medium | Medium | Platform-specific install guides, test on CI/CD early | Fallback: pandas-ta (pure Python, 10x slower) |
| **Multiprocessing overhead negates speedup** | Medium | Low | Benchmark serial vs parallel (Week 7), ensure fitness function >100ms | Use serial execution, reduce restarts to 5 |
| **Memory overflow with 200 population** | Low | Low | Profile memory usage (Week 10), use float32 dtypes, periodic GC | Reduce population to 100, use generators |

### Reproducibility Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| **Random seed mismanagement breaks reproducibility** | Medium | Medium | Centralize RNG seeding in `utils/random_state.py`, log all seeds | Add reproducibility integration tests to CI/CD |
| **Floating-point precision differences across platforms** | Low | Medium | Use fixed precision (np.float64), add tolerance to assertions (±0.01%) | Document platform-specific results in ASSUMPTIONS.md |
| **yfinance data changes retroactively** | Low | Low | Hash downloaded data (SHA-256), cache to Parquet, version data | Store dated snapshots (e.g., `SPY_2010-2025_downloaded_2026-02-21.parquet`) |

### Validation Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| **All systems fail validation (0 passing)** | High | Medium | Use penalty function (Phase 1), adaptive threshold relaxation | Lower MVP thresholds (Pearson ≥0.80, PF ≥1.1), increase restarts to 20 |
| **Overfitting despite multi-stage validation** | High | Low | Add additional robustness tests (Monte Carlo resampling), require longer OOS (3+ years) | Paper trading before live deployment (out of scope for MVP) |
| **Market regime shift invalidates all systems** | High | Low | Regular retraining via WF-GA (Phase 3), maintain diverse system portfolio | Monitor performance degradation, retrain quarterly |

### Project Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| **Scope creep (too many features)** | Medium | High | Strict phase gating, MVP focuses Phases 1-2 only, defer Phase 5 | Cut Phase 4 documentation, deliver code-only MVP |
| **Solo developer burnout** | Medium | Medium | 32 weeks manageable if paced (20-30 hrs/week side project), take breaks between phases | Reduce scope (skip Phase 5), extend timeline to 40 weeks |
| **Insufficient testing coverage** | Medium | Medium | TDD approach (write tests first), target 70% Phase 1-2, 80% Phase 3-4 | Automated coverage reports, block merges <70% |
| **Documentation lags behind code** | Low | High | Generate API docs from docstrings (Sphinx), update user guide each phase | Defer docs to Phase 4, prioritize code delivery |

---

## Success Metrics

### Quantitative Metrics

| Metric | MVP Target | Production Target | Measurement Method |
|--------|------------|-------------------|-------------------|
| **Reproduction Fidelity** | ≥85% | ≥93% | Component-by-component comparison to GSBsys |
| **Validation Profit Factor** | ≥1.2 | ≥1.5 | Out-of-sample backtest on test set |
| **Equity Curve Pearson** | ≥0.85 | ≥0.90 | Correlation between train/test equity curves |
| **Multi-Period OOS Pass Rate** | 60% (3/5) | 80% (4/5) | Profitable in distinct regime windows |
| **Noise Test Pass Rate** | 62.5% (5/8) | 75% (6/8) | Profitable on perturbed datasets |
| **Parameter Stability (CoV)** | ≤60% | ≤50% | Coefficient of variation across family variants |
| **Single Fitness Eval Time** | <50ms (daily) | <300ms (1-min) | Benchmark with timeit module |
| **Full GA Runtime** | <2 hours (daily, 8-core) | <25 hours (1-min, 8-core) | Wall-clock time for 10 restarts |
| **Code Coverage** | ≥70% | ≥80% | pytest-cov report |

### Qualitative Metrics

- [ ] **Usability**: New user can reproduce SPY optimization in <30 minutes (timed user testing)
- [ ] **Documentation Quality**: All public APIs have docstrings, user guide covers getting started/examples/troubleshooting
- [ ] **Reproducibility**: 100% of GA runs reproducible via logged seeds (integration test)
- [ ] **Maintainability**: Modular architecture with clear separation (data, indicators, GA, validation, export)

---

## Future Considerations

### Post-MVP Enhancements (Phase 6+)

**Advanced Validation:**
- Adversarial stress testing (worst-case scenarios: flash crashes, circuit breakers)
- Ensemble systems (combine multiple GA-evolved strategies, vote/average signals)
- Regime detection (auto-switch systems based on detected market state: bull/bear/vol)

**Performance Optimization:**
- GPU acceleration (CUDA/JAX for parallel fitness evaluations, target 10x speedup)
- Distributed GA (SCOOP framework, multi-machine clusters)
- Incremental backtesting (cache indicator values across generations)

**Feature Extensions:**
- Custom indicator plugin system (user-defined indicators via Python scripts)
- Multi-objective optimization (Pareto frontier: return vs risk, drawdown vs Sharpe)
- Reinforcement learning hybrid (GA for strategy structure, RL for parameter fine-tuning)
- Live trading connector (Interactive Brokers, Alpaca integration)
- Performance monitoring dashboard (track live vs backtest divergence, Grafana/Plotly Dash)

### Research Questions

1. **Pure GA vs GA+RL**: Can pure GA with rigorous validation match GA+RL performance?
   - **Hypothesis**: Yes, based on GSBsys commercial success vs academic GA+RL failures (Red Queen)
   - **Test**: Compare GA-Trading-Sys to MaxAI (best academic GA+RL) on same NQ dataset

2. **Optimal Train/Test Split**: Is 40/60 always better than 60/40?
   - **Hypothesis**: Depends on data availability and market stability
   - **Test**: Sweep train/test ratios (30/70, 40/60, 50/50, 60/40), measure OOS degradation

3. **Indicator Pre-Filtering**: Does greedy single-indicator ranking miss synergistic combinations?
   - **Hypothesis**: Possibly, but empirical success of GSBsys suggests acceptable
   - **Test**: Compare pre-filtered GA vs full search on small indicator set (10 vs 15 total)

4. **Restart vs Diversity Preservation**: Are 10 restarts better than single run with niching?
   - **Hypothesis**: Restarts simpler and equally effective
   - **Test**: Compare 10×1000-gen restarts vs 1×10000-gen with diversity operators

---

## Documentation Plan

### User-Facing Documentation

1. **README.md** (Quick Start):
   - Installation instructions (TA-Lib, requirements.txt)
   - 5-minute getting started (run SPY optimization example)
   - Project structure overview
   - Links to detailed docs

2. **docs/user_guide.md** (Comprehensive Guide):
   - **Installation**: Step-by-step for Windows/macOS/Linux
   - **Configuration**: YAML schema explanation, parameter tuning
   - **Running Optimizations**: CLI usage, YAML config examples
   - **Interpreting Results**: Validation reports, equity curves, metrics
   - **Troubleshooting**: Common errors, debugging, performance tips

3. **docs/methodology.md** (Technical Deep Dive):
   - GA algorithm explanation (crossover, mutation, selection)
   - Validation framework rationale (Pearson, multi-period OOS, noise, family grouping)
   - Fitness function design (NetProfit × AvgTrade, penalty functions)
   - Comparison to GSBsys and academic baselines

4. **docs/api_reference.md** (Sphinx-Generated):
   - Module documentation (data, indicators, ga, backtesting, validation)
   - Function signatures, parameters, return types
   - Code examples for each public API

### Developer-Facing Documentation

1. **CONTRIBUTING.md**:
   - Code style guide (Black formatter, type hints, docstrings)
   - Testing requirements (pytest, 70% coverage minimum)
   - PR submission process (feature branches, CI/CD checks)

2. **ARCHITECTURE.md**:
   - System design overview (data flow, component interactions)
   - Class diagrams (UML for GA engine, validation framework)
   - Design decisions (why VectorBT, why DEAP, why weighted-sum signals)

3. **ASSUMPTIONS.md** (Critical):
   - Document all ambiguous PRD specs and chosen defaults
   - Normalization window size (252-day)
   - Infeasible population handling (penalty function)
   - Multi-market partial failure interpretation (2/3 MVP, 3/3 Production)
   - Train/test split method (sequential only)

---

## References & Research

### Internal References

**From Repository Research:**
- [Volatility-Trader walk-forward pattern](C:\Users\kiaur\Documents\AI-ML\AI-Product-Development\2026-Bootcamp\Volatility-Trader\docs\Methodology-Best-Practices-Framework.md) - 19 folds, expanding window, 5yr min training
- [Risk metrics implementation](C:\Users\kiaur\Documents\AI-ML\AI-Product-Development\2026-Bootcamp\Volatility-Trader\Src\utils\risk_metrics.py) - Sortino, Omega calculations
- [Backtesting pattern](C:\Users\kiaur\Documents\AI-ML\AI-Product-Development\2026-Bootcamp\Volatility-Trader\Src\backtesting\variance_swap.py) - Timing conventions, P&L formulas
- [Configuration pattern](C:\Users\kiaur\Documents\AI-ML\AI-Product-Development\Bootcamp25\AI-Strategy-Builder\src\forecaster\config\settings.py) - Frozen dataclasses, single source of truth

**From PRD:**
- [GA-Trading-Sys PRD v1.1](Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Design/GA-Trading-Sys-PRD.md) - Full requirements, 970 lines
- [GSBsys Technical Specifications](Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Technical-Specifications.md) - GA parameters, validation methodology
- [GSBsys Comparison to Research](Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Comparison-to-Research.md) - MaxAI, Red Queen, DERL analysis

### External References (From Research)

**DEAP Framework:**
- [DEAP Official Documentation](https://deap.readthedocs.io/)
- [DEAP GitHub Repository](https://github.com/DEAP/deap)
- [DEAP Multiprocessing Tutorial](https://tk42.medium.com/python-deap-with-multiprocessing-example-9c4fa8a8a424)

**VectorBT:**
- [VectorBT Documentation](https://vectorbt.dev/)
- [Vectorized Backtesting Tutorial](https://onepagecode.substack.com/p/mastering-vectorized-backtesting-3d6)
- [VectorBT GitHub Examples](https://github.com/hudson-and-thames/backtest_tutorial)

**Validation Best Practices:**
- [Walk-Forward Optimization (Wikipedia)](https://en.wikipedia.org/wiki/Walk_forward_optimization)
- [Robustness Testing Guide (BuildAlpha)](https://www.buildalpha.com/robustness-testing-guide/)
- [Monte Carlo Robustness (StrategyQuant)](https://strategyquant.com/blog/new-robustness-tests-on-the-strategyquant-codebase-5-monte-carlo-methods-to-bulletproof-your-trading-strategies/)

**Performance Optimization:**
- [Numba 5-Minute Guide](https://numba.pydata.org/numba-doc/dev/user/5minguide.html)
- [Numba Performance Tips](https://numba.pydata.org/numba-doc/dev/user/performance-tips.html)
- [Python Performance Guide 2025](https://www.fyld.pt/blog/python-performance-guide-writing-code-25/)

---

## Appendix A: Configuration Example

```yaml
# config/ga_trading_sys_spy_mvp.yaml

project:
  name: "SPY-Daily-MVP"
  description: "MVP optimization on SPY daily data"
  data_source: "yfinance"
  ticker: "SPY"
  output_dir: "results/spy_mvp"
  random_seed: 42

data:
  source: "yfinance"  # or "theta" for Phase 5
  ticker: "SPY"
  start_date: "2010-01-01"
  end_date: "2025-12-31"
  train_test_split: [0.4, 0.6]  # Sequential split
  normalize_window: 252  # Days (1 year)
  cache_dir: "data/cache"

indicators:
  standard:
    - {name: "RSI", param_range: [5, 50]}
    - {name: "CCI", param_range: [10, 100]}
    - {name: "Stochastic", param_range: [5, 50]}
    - {name: "ADX", param_range: [10, 30]}
    - {name: "ATR", param_range: [10, 50]}
    - {name: "MACD", fast_range: [8, 15], slow_range: [20, 30]}
    - {name: "Bollinger", param_range: [10, 30], std_range: [1.5, 2.5]}
    - {name: "ROC", param_range: [5, 50]}
    - {name: "Williams_R", param_range: [10, 30]}
    - {name: "Momentum", param_range: [5, 50]}
    - {name: "EMA", param_range: [10, 100]}
    - {name: "SMA", param_range: [10, 100]}
    - {name: "Volume"}
    - {name: "OBV"}
    - {name: "DMI", param_range: [10, 30]}

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
    enabled: false  # Phase 3
    population_size: 100  # Reduced fidelity
    generations: 200      # Reduced fidelity

  chromosome:
    indicator_type: [0, 14]  # Which of 15 standard indicators
    period: [5, 100]
    weight: [-1.0, 2.0]
    threshold: [0.0, 50.0]
    stop_loss: [200, 2000]  # Dollars
    take_profit: [200, 2000]
    position_size_mult: [0.5, 2.0]

fitness:
  primary: "net_profit * avg_trade"
  signal_method: "weighted_sum"  # or "multiplicative" (Phase 3)

  # Penalty function (soft constraints)
  penalties:
    pearson_below_threshold: 10
    pf_below_threshold: 5
    min_trades: 30
    min_trades_penalty: 0.1

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
    noise_level: 0.005  # ±0.5% price perturbation
    mvp_pass_threshold: 0.625  # 5/8 variants
    production_pass_threshold: 0.75  # 6/8 variants
    random_seeds: [42, 123, 456, 789, 101112, 131415, 161718, 192021]

  family_grouping:
    enabled: true
    variants: 10
    perturbation: 0.05  # ±5% parameter perturbation
    mvp_cov_threshold: 0.60
    production_cov_threshold: 0.50

backtesting:
  position_sizing:
    method: "fixed_fractional"
    risk_per_trade: 0.02  # 2% of capital
    starting_capital: 100000

  costs:
    stocks:  # For yfinance MVP
      commission: 0.0
      slippage_bps: 5  # 0.05%
    futures:  # For Phase 5 Theta Data
      commission_per_rt: 2.50
      slippage_ticks:
        ES: 3
        NQ: 3
        YM: 3

performance:
  parallel_restarts: true
  max_workers: 8  # CPU cores for multiprocessing
  vectorized_backtest: true
  cache_indicator_calcs: true
  jit_compile: true  # Numba

output:
  export_formats: ["python"]  # "easylanguage" in Phase 5
  generate_reports: true
  plot_equity_curves: true
  save_population_history: true
  log_level: "INFO"

  files:
    best_strategy: "best_strategy.json"  # SECURITY FIX: JSON instead of pickle
    validation_report: "validation_report.json"
    equity_plot: "equity_curve.png"
    convergence_plot: "ga_convergence.png"
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **AIC** | Any Indicators Cross - entry mode that triggers when any weighted indicator crosses threshold (OR logic) |
| **ATR** | Average True Range - volatility indicator measuring average price range |
| **Chromosome** | Individual solution encoding in GA (e.g., [indicator_type, period, weight, threshold, stops]) |
| **CoV** | Coefficient of Variation - stddev / mean (measures relative parameter sensitivity) |
| **Equity Curve** | Cumulative profit/loss over time plotted as line chart |
| **Fitness** | Objective function score (higher = better individual). Our fitness: Net Profit × Avg Trade |
| **GA** | Genetic Algorithm - evolutionary optimization technique mimicking natural selection |
| **Generation** | Iteration of GA (selection → crossover → mutation → fitness evaluation) |
| **HighestLowest** | Normalization method: maps indicator to [-100, +100] range using rolling highest/lowest values |
| **NCC** | No Conflict Cross - entry mode that triggers only when no opposing signals exist (AND logic) |
| **OOS** | Out-of-Sample - data not used during training (test/validation set) to measure generalization |
| **Pearson** | Pearson correlation coefficient (measures linear relationship strength, -1 to +1). Used to compare equity curve shapes. |
| **PF** | Profit Factor - gross profit / gross loss (PF > 1.0 = profitable, PF < 1.0 = losing) |
| **Population** | Set of candidate solutions in GA (e.g., 200 trading systems) |
| **Regime** | Market condition characterized by trend and volatility (bull/bear/sideways, high-vol/low-vol) |
| **Restart** | Independent GA run with new random seed (diversity mechanism) |
| **SBX** | Simulated Binary Crossover - GA crossover operator for continuous variables (indicator params, weights) |
| **Walk-Forward** | Rolling retraining methodology: optimize on past data, test on future data, advance window, repeat |

---

**END OF IMPLEMENTATION PLAN**

---

**Next Steps:**
1. Review this plan with stakeholders
2. Resolve 5 spec-flow blocking questions (normalization window, infeasible handling, WF-GA cost, multi-market criteria, train/test split)
3. Set up development environment (Python 3.10+, TA-Lib, DEAP, VectorBT)
4. Begin Phase 1: Core GA Engine (Week 1: Data pipeline)

**Contact:**
- PRD: [GA-Trading-Sys-PRD.md v1.1](Bootcamp25/AI-Strategy-Builder/docs/GSBSys/Design/GA-Trading-Sys-PRD.md)
- Research: [Framework Documentation](Bootcamp25/ai_agent_framework/research/Research-Results/FinanceRL-Q126/GA-Trading-Sys-Framework-Documentation.md)
- Questions: Resolve via triage session before Phase 1 coding
