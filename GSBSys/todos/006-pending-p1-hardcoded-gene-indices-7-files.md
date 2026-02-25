---
status: complete
priority: p1
issue_id: "006"
tags: [code-review, architecture, quality, maintainability]
dependencies: []
---

# Risk parameter gene indices (10/11/12) hardcoded in 7 files — brittle chromosome extension

## Problem Statement

The chromosome's three risk parameters are accessed by raw integer index in 7 source files: `fitness.py`, `regime_classifier.py`, `sensitivity.py`, `walk_forward.py`, `multi_period_oos.py`, `noise_injection.py`, and `cli/commands.py`. `chromosome.py` already exports `GENE_NAMES` and could export named constants, but doesn't. Extending the chromosome to 4 indicator slots (planned in config as `n_indicators: up to 5`) shifts these indices and requires synchronized changes across all 7 files with no compiler-enforced safety net.

## Findings

- **`src/ga/fitness.py:70-72`** — `individual[10]`, `individual[11]`, `individual[12]`
- **`src/robustness/regime_classifier.py:189-191`** — same
- **`src/robustness/sensitivity.py:140-142`** — same
- **`src/robustness/walk_forward.py:180-182`** — same
- **`src/validation/multi_period_oos.py:129-131`** — same
- **`src/validation/noise_injection.py:167-169`** — same
- **`src/cli/commands.py:365`** — `ind[10]`, `ind[11]`, `ind[12]` in `backtest` command
- `signal_generator.py` defines private `_IDX_STOP_LOSS_PCT = 10` etc. but marks them private and doesn't share them.

## Proposed Solutions

### Option A — Export named constants from chromosome.py (Recommended)
Add to `src/ga/chromosome.py` after `GENE_NAMES`:
```python
IDX_STOP_LOSS_PCT      = 10
IDX_TAKE_PROFIT_PCT    = 11
IDX_POSITION_SIZE_MULT = 12
```
Then replace all 7 files' `individual[10]` → `individual[IDX_STOP_LOSS_PCT]` etc.

- **Effort:** Small (search + replace across 7 files)
- **Risk:** Zero functional change; purely mechanical refactor

### Option B — Named tuple or dataclass chromosome
Convert chromosome from `list[float]` to a named dataclass `Chromosome`.

- **Effort:** Large — touches DEAP integration, pickle, all existing tests
- **Risk:** High — DEAP expects list-like individuals

### Option C — Accept status quo with a comment
Document that these are indices 10/11/12 in a shared location.

- **Effort:** Tiny
- **Risk:** None — but doesn't prevent future breakage

## Recommended Action

Option A — pure refactor, zero behavior change, high maintainability value.

## Acceptance Criteria

- [ ] `IDX_STOP_LOSS_PCT = 10`, `IDX_TAKE_PROFIT_PCT = 11`, `IDX_POSITION_SIZE_MULT = 12` exported from `chromosome.py`
- [ ] All 7 files updated to import and use these constants
- [ ] `signal_generator.py` private constants deleted in favor of chromosome.py public ones
- [ ] All 460 existing tests pass (zero functional change)

## Work Log

- 2026-02-24: Identified by architecture and code-quality review agents
