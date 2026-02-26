---
status: pending
priority: p2
issue_id: "007"
tags: [code-review, quality, data-integrity, security]
dependencies: []
---

# `validate_ohlcv()` exists but is never called in optimize pipeline — bad data silently accepted

## Problem Statement

`src/data/validator.py` exports `validate_ohlcv(df)` which checks for nulls, negative prices, zero volumes, and shape correctness. The `optimize` and `backtest` CLI commands call `load_market_data()` but never call `validate_ohlcv()` on the result. Corrupt or incomplete market data (missing bars, NaN prices, negative volumes from data provider errors) flows directly into indicator calculation and the Numba backtest engine with no guard. The engine may silently produce nonsensical fitness values or panic inside Numba's JIT-compiled kernel.

## Findings

- **`src/data/validator.py`** — `validate_ohlcv(df)` is fully implemented and tested
- **`src/cli/commands.py:353-360`** — `backtest` command calls `load_market_data()`; no validation call follows
- **`src/cli/commands.py:~200`** — `optimize` command likewise skips validation
- **`src/data/loader.py`** — `load_market_data()` does NOT call validator internally
- **Security reviewer finding F-3:** "validate_ohlcv() exists and is dead code in the pipeline"
- **Architecture reviewer finding:** DataCache and validator both implemented but not wired

## Proposed Solutions

### Option A — Call `validate_ohlcv()` in both CLI commands after `load_market_data()` (Recommended)
```python
df = load_market_data(ticker, start, end)
from src.data.validator import validate_ohlcv
validate_ohlcv(df)  # Raises ValueError if data is corrupt
```
One line per command. Errors surface early with a clear message.

- **Effort:** Tiny (2 lines in 2 places)
- **Risk:** None — validator raises ValueError which Click will display cleanly

### Option B — Call `validate_ohlcv()` inside `load_market_data()`
Integrate validation into the loader so callers can't forget.

- **Effort:** Small — modify loader
- **Risk:** Low — but couples validation to loader (some callers may want raw data)

### Option C — Keep as dead code with a warning comment
Add `# TODO: call validate_ohlcv()` comments.

- **Effort:** Trivial
- **Risk:** Doesn't protect from bad data

## Recommended Action

Option A — two-line fix in both CLI commands. Fast, safe, immediately protects both pipelines.

## Acceptance Criteria

- [ ] `validate_ohlcv(df)` called in `optimize` command after data load
- [ ] `validate_ohlcv(df)` called in `backtest` command after data load
- [ ] ValueError from validator printed as user-friendly Click error (not stack trace)
- [ ] Test added: `optimize` with dataframe containing NaN prices exits non-zero
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by security and architecture review agents
