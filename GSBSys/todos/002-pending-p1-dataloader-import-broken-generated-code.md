---
status: complete
priority: p1
issue_id: "002"
tags: [code-review, quality, bug, export]
dependencies: []
---

# Generated `strategy.py` imports non-existent `DataLoader` class — ImportError on run

## Problem Statement

`src/export/codegen.py` generates a standalone `strategy.py` file that begins with `from src.data.loader import DataLoader`. The class `DataLoader` does not exist — `src/data/loader.py` exports only the function `load_market_data()`. Every generated strategy file fails with `ImportError` on the first line, making the entire export/codegen feature non-functional for end users.

## Findings

- **File:** `src/export/codegen.py:105-110`
- **Generated code (broken):**
  ```python
  from src.data.loader import DataLoader
  loader = DataLoader()
  df = loader.load(TICKER, START_DATE, END_DATE)
  ```
- **Actual API:** `from src.data.loader import load_market_data` / `df = load_market_data(ticker, start, end)`
- **CLI `backtest` command** correctly uses `load_market_data()` at `commands.py:356` — so only the generated artifact is broken
- **Secondary issue:** The generated code hardcodes `WARMUP_BARS = 252` (`codegen.py:95`) and `TRAIN_FRACTION = 0.40` (`codegen.py:98`) regardless of the config used during optimization. If the user ran with `warmup_bars=100`, the generated replay script uses wrong split boundaries.
- **No test** currently exercises the generated `strategy.py` for import validity or execution

## Proposed Solutions

### Option A — Fix the template (Recommended)
In `src/export/codegen.py`, lines 105-110, replace:
```python
from src.data.loader import DataLoader
...
loader = DataLoader()
df = loader.load(TICKER, START_DATE, END_DATE)
```
With:
```python
from src.data.loader import load_market_data
...
df = load_market_data(TICKER, START_DATE, END_DATE)
```
Also thread the actual config values into `generate_backtest_code(individual, warmup_bars=252, train_fraction=0.40)` so the generated constants reflect the optimization run.

- **Effort:** Small
- **Risk:** Low — pure template fix

### Option B — Add a compile/exec test
Keep the template as-is but add a test that `compile(code, "<string>", "exec")` succeeds and that `load_market_data` is referenced, not `DataLoader`.

- **Effort:** Tiny
- **Risk:** Does not fix the actual broken code

### Option C — Drop generated strategy.py
Remove `generate_backtest_code` from the export pipeline; rely on YAML + `backtest` CLI.

- **Effort:** Medium
- **Risk:** Removes a user-facing feature

## Recommended Action

Option A, extended: fix the template AND add `warmup_bars`/`train_fraction` as parameters to `generate_backtest_code()`.

## Acceptance Criteria

- [ ] `DataLoader` removed from codegen template
- [ ] `load_market_data(TICKER, START_DATE, END_DATE)` used instead
- [ ] `generate_backtest_code` accepts `warmup_bars` and `train_fraction` parameters
- [ ] Generated WARMUP_BARS and TRAIN_FRACTION reflect actual optimization config, not hardcoded defaults
- [ ] Test added: `compile(generate_backtest_code(...), "<string>", "exec")` succeeds
- [ ] All 460 existing tests still pass

## Work Log

- 2026-02-24: Identified by architecture, code-quality, and data-integrity review agents
