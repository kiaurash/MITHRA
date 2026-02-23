---
title: "GA-Trading-Sys Phase 3: Robustness Testing"
type: feat
date: 2026-02-23
prd: Design/GA-Trading-Sys-MVP-PRD.md
prd_version: "2.0"
prior_plan: docs/plans/2026-02-23-feat-ga-trading-sys-phase2-validation-framework-plan.md
phase: 3
timeline: "6 weeks (Weeks 21–26)"
---

# feat: GA-Trading-Sys Phase 3 — Robustness Testing

## Overview

Phase 3 adds three robustness tests that go beyond Phase 2's static validation
to probe the strategy's durability under realistic deployment conditions:
adaptive re-optimisation, parameter sensitivity, and regime-specific performance.

**Phase 2 status:** Complete — 226 tests passing, 4-layer validation operational.

**What Phase 3 adds:**
1. **Walk-Forward GA** — rolling re-optimisation with 100 pop × 200 gen;
   compare OOS performance to baseline (no retraining)
2. **Sensitivity Analysis** — perturb each gene ±10%; measure PF impact;
   correlate with family-grouping CoV
3. **Regime Testing** — classify bars as BULL/BEAR/SIDEWAYS; aggregate
   per-regime backtest metrics

---

## Robustness Modules

### Module 1: Walk-Forward GA (`src/robustness/walk_forward.py`)

Splits data into rolling windows (train=2yr, test=6mo, step=6mo).
For each window, runs a reduced-fidelity GA and reports test PF.

```python
@dataclass(frozen=True)
class WalkForwardWindow:
    window_idx: int
    train_start_bar: int
    train_end_bar: int
    test_start_bar: int
    test_end_bar: int
    best_individual: list
    test_profit_factor: float
    test_total_pnl: float
    n_test_trades: int
    profitable: bool          # test PF >= 1.0

@dataclass(frozen=True)
class WalkForwardResult:
    windows: List[WalkForwardWindow]
    n_profitable_windows: int
    n_total_windows: int
    avg_test_pf: float
    passed_mvp: bool        # n_profitable >= 60% of windows
    passed_production: bool # n_profitable >= 70% of windows

def run_walk_forward_ga(
    df: pd.DataFrame,
    ga_runner: Callable[[pd.DataFrame, int, int, int], list],
    engine: BacktestEngine,
    train_bars: int = 504,     # ~2 years daily
    test_bars: int = 126,      # ~6 months daily
    step_bars: int = 126,
    normalization_window: int = 252,
    warmup_bars: int = 252,
) -> WalkForwardResult
```

Pass criteria:
- MVP: ≥60% of windows profitable
- Production: ≥70% of windows profitable

### Module 2: Sensitivity Analysis (`src/robustness/sensitivity.py`)

Perturbs each of the 13 genes by ±10% and measures the resulting change
in test profit factor.  High sensitivity + high CoV = fragile strategy.

```python
@dataclass(frozen=True)
class GeneSensitivity:
    gene_name: str
    gene_idx: int
    base_value: float
    plus_pf: float     # PF with gene * 1.10
    minus_pf: float    # PF with gene * 0.90
    sensitivity: float # abs(plus_pf - minus_pf) / max(base_pf, 0.001)

@dataclass(frozen=True)
class SensitivityResult:
    gene_sensitivities: List[GeneSensitivity]
    base_pf: float
    mean_sensitivity: float
    most_sensitive_gene: str
    cov_correlation: Optional[float]   # Pearson r(sensitivity, CoV) if family provided

def run_sensitivity_analysis(
    individual: list,
    df: pd.DataFrame,
    engine: BacktestEngine,
    normalization_window: int = 252,
    warmup_bars: int = 252,
    perturbation: float = 0.10,
    family_result: Optional[FamilyResult] = None,
) -> SensitivityResult
```

### Module 3: Regime Testing (`src/robustness/regime_classifier.py`)

Classifies each bar using a rolling momentum window, then aggregates
backtest returns by regime type.

```python
class RegimeLabel(str, Enum):
    BULL     = "bull"
    BEAR     = "bear"
    SIDEWAYS = "sideways"

def classify_regimes(
    prices: np.ndarray,
    window: int = 63,
    bull_threshold: float = 0.10,
    bear_threshold: float = -0.10,
) -> np.ndarray   # dtype str/RegimeLabel, len == len(prices)

@dataclass(frozen=True)
class RegimePerformance:
    label: RegimeLabel
    n_bars: int
    profit_factor: float
    total_return_pct: float
    profitable: bool

@dataclass(frozen=True)
class RegimeTestResult:
    bull:     RegimePerformance
    bear:     RegimePerformance
    sideways: RegimePerformance
    dominant_regime: RegimeLabel  # most bars
    best_regime: RegimeLabel      # highest PF
    worst_regime: RegimeLabel     # lowest PF

def run_regime_testing(
    individual: list,
    df: pd.DataFrame,
    engine: BacktestEngine,
    normalization_window: int = 252,
    warmup_bars: int = 252,
    regime_window: int = 63,
    bull_threshold: float = 0.10,
    bear_threshold: float = -0.10,
) -> RegimeTestResult
```

---

## File Structure

```
src/robustness/
├── __init__.py
├── walk_forward.py
├── sensitivity.py
└── regime_classifier.py

tests/
├── test_walk_forward.py
├── test_sensitivity.py
└── test_regime_classifier.py

experiments/
└── 04_phase3_robustness.py
```

---

## Implementation Checklist

### Phase 3a: Walk-Forward GA
- [ ] `src/robustness/__init__.py`
- [ ] `src/robustness/walk_forward.py` — `WalkForwardWindow`, `WalkForwardResult`, `run_walk_forward_ga()`
- [ ] `tests/test_walk_forward.py`

### Phase 3b: Sensitivity Analysis
- [ ] `src/robustness/sensitivity.py` — `GeneSensitivity`, `SensitivityResult`, `run_sensitivity_analysis()`
- [ ] `tests/test_sensitivity.py`

### Phase 3c: Regime Testing
- [ ] `src/robustness/regime_classifier.py` — `RegimeLabel`, `classify_regimes()`, `RegimePerformance`, `RegimeTestResult`, `run_regime_testing()`
- [ ] `tests/test_regime_classifier.py`

### Phase 3d: Integration + commit
- [ ] `experiments/04_phase3_robustness.py` — end-to-end demo
- [ ] Run full suite + commit

---

## Acceptance Criteria

### MVP Tier
- [ ] Walk-Forward: ≥60% of windows profitable
- [ ] Sensitivity: all 13 genes have computable sensitivity scores
- [ ] Regime: performance reported for BULL / BEAR / SIDEWAYS

### Production Tier
- [ ] Walk-Forward: ≥70% of windows profitable
- [ ] Sensitivity: CoV correlation computed when FamilyResult provided
- [ ] Regime: strategy profitable in ≥2/3 regime types

### Quality
- [ ] All new tests pass (full suite ≥ 226 + new)
- [ ] Walk-forward windows use no-lookahead slicing
- [ ] Fixed random seeds for reproducibility
