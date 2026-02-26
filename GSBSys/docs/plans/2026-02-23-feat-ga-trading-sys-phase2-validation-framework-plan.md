---
title: "GA-Trading-Sys Phase 2: Validation Framework"
type: feat
date: 2026-02-23
prd: Design/GA-Trading-Sys-MVP-PRD.md
prd_version: "2.0"
prior_plan: docs/plans/2026-02-22-feat-ga-trading-sys-phase1-core-engine-plan.md
phase: 2
timeline: "8 weeks (Weeks 13–20)"
---

# feat: GA-Trading-Sys Phase 2 — Validation Framework

## Overview

Phase 2 transitions from single-run optimization (Phase 1) to **multi-stage
validation** that prevents overfitting and confirms live-trading readiness.
Systems that pass all 4 validation layers are significantly more likely to
survive live trading.

**Phase 1 status:** Complete — 184 tests passing, full GA stack operational.

**What's already done from Phase 1:**
- Pearson *penalty* in fitness.py (inline, not standalone pass/fail)
- 10-restart runner in parallel.py (runs exist, CoV analysis not yet computed)

**What Phase 2 adds:**
1. Standalone **Pearson pass/fail gate** (MVP ≥0.85, Production ≥0.90)
2. **Multi-period OOS** — 5 market regime windows (15 years)
3. **Noise injection** — 8 data perturbation variants
4. **Family grouping** — CoV analysis across 10 restart results
5. **Validation report** — unified pass/fail summary with tiered thresholds

---

## Validation Layers

### Layer 1: Pearson Equity Filter (`src/validation/pearson_filter.py`)

Already used as a **penalty** in fitness.py.  Phase 2 adds a **hard gate**
post-run: if train/test equity curve Pearson < threshold, the system is
rejected (not just penalised).

```python
@dataclass(frozen=True)
class PearsonResult:
    pearson_r: float
    passed_mvp: bool        # r >= 0.85
    passed_production: bool # r >= 0.90

def run_pearson_filter(train_equity: np.ndarray,
                       test_equity:  np.ndarray) -> PearsonResult
```

Thresholds:
- MVP: ≥0.85
- Production: ≥0.90

### Layer 2: Multi-Period OOS (`src/validation/multi_period_oos.py`)

Run the best chromosome from Phase 1 on 5 fixed 3-year regime windows.
Each window is an independent backtest on that period's price data.
Pass criteria: ≥3/5 profitable (MVP) or ≥4/5 (Production).

```python
REGIMES = [
    ("2010-01-01", "2012-12-31", "post-crisis-recovery"),
    ("2013-01-01", "2015-12-31", "stable-growth"),
    ("2016-01-01", "2018-12-31", "pre-covid-bull"),
    ("2019-01-01", "2021-12-31", "covid-crash-recovery"),
    ("2022-01-01", "2024-12-31", "rate-hikes-sideways"),
]

@dataclass(frozen=True)
class OOSResult:
    regime_results: list[RegimeResult]  # one per window
    n_profitable: int
    passed_mvp: bool        # n_profitable >= 3
    passed_production: bool # n_profitable >= 4

def run_multi_period_oos(individual, engine, data_loader, config) -> OOSResult
```

### Layer 3: Noise Injection (`src/validation/noise_injection.py`)

Re-run backtest 8 times with perturbed input data.  Tests whether the
strategy is robust to realistic data imperfections.

```python
NOISE_VARIANTS = [
    ("price_plus_1pct",   {"price_noise": +0.01}),
    ("price_minus_1pct",  {"price_noise": -0.01}),
    ("price_plus_2pct",   {"price_noise": +0.02}),
    ("price_minus_2pct",  {"price_noise": -0.02}),
    ("volume_plus_10pct", {"volume_noise": +0.10}),
    ("volume_minus_10pct",{"volume_noise": -0.10}),
    ("entry_shift_plus1", {"entry_shift": +1}),
    ("entry_shift_minus1",{"entry_shift": -1}),
]

@dataclass(frozen=True)
class NoiseResult:
    variant_results: list[VariantResult]
    n_profitable: int
    passed_mvp: bool        # n_profitable >= 5  (62.5%)
    passed_production: bool # n_profitable >= 6  (75.0%)

def run_noise_injection(individual, prices, cache, engine, config) -> NoiseResult
```

### Layer 4: Family Grouping (`src/validation/family_grouping.py`)

Analyse parameter stability across 10 restart results.  Systems where
parameters converge (low CoV) are more stable than those where each
restart finds a completely different solution.

```python
@dataclass(frozen=True)
class FamilyResult:
    cov_per_gene: dict[str, float]  # CoV for each of 13 genes
    mean_cov: float                  # average CoV across all genes
    passed_mvp: bool        # mean_cov <= 0.60
    passed_production: bool # mean_cov <= 0.50
    n_profitable_restarts: int

def run_family_grouping(restart_results: list[dict]) -> FamilyResult
```

CoV = std / |mean| per gene across all restarts.

### Layer 5: Validation Report (`src/validation/report.py`)

```python
@dataclass(frozen=True)
class ValidationReport:
    pearson:       PearsonResult
    oos:           OOSResult
    noise:         NoiseResult
    family:        FamilyResult
    passed_mvp:        bool  # ALL 4 layers pass MVP
    passed_production: bool  # ALL 4 layers pass Production
    summary: str             # human-readable

def build_report(pearson, oos, noise, family) -> ValidationReport
def save_report(report, path: str) -> None  # JSON
```

---

## File Structure

```
src/validation/
├── __init__.py
├── pearson_filter.py
├── multi_period_oos.py
├── noise_injection.py
├── family_grouping.py
└── report.py

tests/
├── test_pearson_filter.py
├── test_multi_period_oos.py
├── test_noise_injection.py
├── test_family_grouping.py
└── test_validation_report.py

experiments/
└── 03_phase2_validation.py   # Run all 4 layers on best Phase 1 result
```

---

## Implementation Checklist

### Phase 2a: Pearson Filter
- [ ] `src/validation/__init__.py`
- [ ] `src/validation/pearson_filter.py` — `PearsonResult`, `run_pearson_filter()`
- [ ] `tests/test_pearson_filter.py`

### Phase 2b: Multi-Period OOS
- [ ] `src/validation/multi_period_oos.py` — `REGIMES`, `RegimeResult`, `OOSResult`, `run_multi_period_oos()`
- [ ] `tests/test_multi_period_oos.py`

### Phase 2c: Noise Injection
- [ ] `src/validation/noise_injection.py` — `NOISE_VARIANTS`, `VariantResult`, `NoiseResult`, `run_noise_injection()`
- [ ] `tests/test_noise_injection.py`

### Phase 2d: Family Grouping
- [ ] `src/validation/family_grouping.py` — `FamilyResult`, `run_family_grouping()`
- [ ] `tests/test_family_grouping.py`

### Phase 2e: Validation Report + Integration
- [ ] `src/validation/report.py` — `ValidationReport`, `build_report()`, `save_report()`
- [ ] `tests/test_validation_report.py`
- [ ] `experiments/03_phase2_validation.py` — end-to-end demo
- [ ] Run full suite + commit

---

## Acceptance Criteria

### MVP Tier
- [ ] Pearson r ≥ 0.85 (train/test equity curve)
- [ ] Multi-period OOS: ≥3/5 regime windows profitable
- [ ] Noise robustness: ≥5/8 variants profitable
- [ ] Family CoV ≤ 60% (mean across genes)

### Production Tier
- [ ] Pearson r ≥ 0.90
- [ ] Multi-period OOS: ≥4/5 profitable
- [ ] Noise robustness: ≥6/8 profitable
- [ ] Family CoV ≤ 50%

### Quality
- [ ] All new tests pass (full suite ≥ 184 + new)
- [ ] No lookahead bias in OOS regime windows
- [ ] Noise variants use fixed seeds for reproducibility
- [ ] Validation report is serialisable to JSON
