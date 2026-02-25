---
status: pending
priority: p2
issue_id: "013"
tags: [code-review, quality, data-integrity, bug]
dependencies: []
---

# `warmup_bars=0` accepted silently — indicator warmup disabled with no error or warning

## Problem Statement

`OptimizationConfig.warmup_bars` can be set to `0` (or any non-positive integer) in the config YAML without any validation error. With `warmup_bars=0`, indicator calculations begin from the first bar, where indicators like RSI(14) and MACD(26,12) have no historical data and produce `NaN` or garbage values. These NaN values propagate into the fitness function, producing `NaN` fitness scores that DEAP cannot rank, causing the GA to behave erratically. The Numba engine may receive NaN signal arrays and produce unpredictable results. There is no guard against this at the config parsing or data-split level.

## Findings

- **`src/config.py`** — `warmup_bars: int` field with no minimum validator
- **`src/cli/commands.py`** — no post-load validation of `warmup_bars > 0`
- **`src/backtesting/`** — warmup bars are sliced away before backtesting; with `warmup_bars=0` all bars are used including NaN indicator prefix
- **Data integrity reviewer finding:** "`warmup_bars=0` allowed — NaN fitness scores possible"
- **Minimum useful value:** longest indicator period is typically 26 (MACD slow); `warmup_bars` should be ≥ `max_period + buffer`

## Proposed Solutions

### Option A — Add Pydantic field validator (Recommended)
```python
from pydantic import field_validator

class GAConfig(BaseModel):
    warmup_bars: int = 252

    @field_validator("warmup_bars")
    @classmethod
    def warmup_bars_positive(cls, v):
        if v < 50:
            raise ValueError(f"warmup_bars must be >= 50 (got {v}); minimum for indicator convergence")
        return v
```

- **Effort:** Tiny — one validator
- **Risk:** None — Config already uses Pydantic v2

### Option B — Validate in CLI commands
After loading config, check `config.warmup_bars >= 50` and `sys.exit(1)` with a message.

- **Effort:** Tiny
- **Risk:** None — but only protects CLI path, not library callers

### Option C — Document minimum but don't enforce
Add a comment in the YAML template: `warmup_bars: 252  # minimum 50 recommended`.

- **Effort:** Trivial
- **Risk:** None — doesn't prevent the problem

## Recommended Action

Option A — Pydantic validator is the canonical approach for this codebase. Prevents NaN fitness issues from config errors.

## Acceptance Criteria

- [ ] `warmup_bars < 50` raises `ValueError` with helpful message during config load
- [ ] YAML template comment updated to document minimum
- [ ] Test: config with `warmup_bars=0` raises on instantiation
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by data-integrity review agent
