---
status: pending
priority: p3
issue_id: "019"
tags: [code-review, architecture, maintainability, quality]
dependencies: []
---

# Indicator period bounds (`5–200`) defined in three separate places — DRY violation

## Problem Statement

The valid range for indicator period genes (min=5, max=200) is defined independently in: (1) `src/ga/chromosome.py` `GENE_BOUNDS`, (2) `src/indicators/signal_generator.py` `_IDX_*` private constants or validation, and (3) possibly `src/config.py` default ranges. When the valid period range changes (e.g., allowing periods up to 500 for weekly data), all three locations must be updated synchronously with no compiler-enforced safety net. This is a DRY violation with the same failure mode as the hardcoded gene indices (issue 006).

## Findings

- **`src/ga/chromosome.py`** — `GENE_BOUNDS` contains period min/max for indicator genes
- **`src/indicators/signal_generator.py`** — private period validation or clipping using the same values
- **Code quality reviewer finding:** "Indicator period bounds defined in multiple places"
- **Architecture reviewer finding:** "Three copies of indicator period constraints — single source of truth needed"

## Proposed Solutions

### Option A — Define bounds in `chromosome.py` only; import in other files (Recommended)
```python
# chromosome.py
INDICATOR_PERIOD_MIN = 5
INDICATOR_PERIOD_MAX = 200
```
All other files import from `chromosome.py`.

- **Effort:** Small — search and replace
- **Risk:** None — pure refactor

### Option B — Define in a shared `src/ga/constants.py`
Move all GA-related constants to a dedicated constants module.

- **Effort:** Small — new file + update imports
- **Risk:** None

### Option C — Accept current state
The values rarely change; duplication is manageable.

- **Effort:** None
- **Risk:** Low — but increases maintenance burden if chromosome is extended (issue 012)

## Recommended Action

Option A — add exported constants to `chromosome.py` (already the home of `GENE_NAMES`, `GENE_BOUNDS`).

## Acceptance Criteria

- [ ] `INDICATOR_PERIOD_MIN` and `INDICATOR_PERIOD_MAX` defined in exactly one place
- [ ] All other references import from that single location
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by architecture and code-quality review agents
