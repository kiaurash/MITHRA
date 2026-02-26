---
status: complete
priority: p2
issue_id: "015"
tags: [code-review, quality, bug, export]
dependencies: ["002"]
---

# `generate_backtest_code()` hardcodes `WARMUP_BARS=252` and `TRAIN_FRACTION=0.40` regardless of config

## Problem Statement

`src/export/codegen.py` generates a standalone `strategy.py` replay script. Two critical constants in the generated code — `WARMUP_BARS` and `TRAIN_FRACTION` — are hardcoded to `252` and `0.40` respectively, regardless of what values were used during the optimization run. If the user optimized with `warmup_bars=100` and `train_fraction=0.60`, the generated script splits data differently, evaluates the strategy on a different in-sample/out-of-sample boundary, and produces different results than what the optimizer found. The replay script is not a faithful reproduction of the optimization environment.

## Findings

- **`src/export/codegen.py:95`** — `WARMUP_BARS = 252` hardcoded in template string
- **`src/export/codegen.py:98`** — `TRAIN_FRACTION = 0.40` hardcoded in template string
- **`generate_backtest_code(individual)`** — function signature has no `warmup_bars` or `train_fraction` parameters
- **`src/cli/commands.py`** — calls `generate_backtest_code(best)` without passing config values
- **Secondary to issue 002:** fixing this should be done together with the `DataLoader` → `load_market_data` fix
- **Code quality reviewer finding:** "Generated script hardcodes config constants — replay results may differ from optimization"

## Proposed Solutions

### Option A — Add parameters to `generate_backtest_code()` (Recommended)
```python
def generate_backtest_code(
    individual,
    warmup_bars: int = 252,
    train_fraction: float = 0.40,
    ticker: str = "SPY",
    start_date: str = "2015-01-01",
    end_date: str = "2024-12-31",
) -> str:
```
Caller (CLI `optimize` command) passes `config.warmup_bars` and `config.train_fraction`.

- **Effort:** Small — add params, thread from CLI
- **Risk:** None — pure template parametrization

### Option B — Write actual config YAML into generated script as a comment
Embed the full config YAML as a commented header in `strategy.py`.

- **Effort:** Small
- **Risk:** None — additional information, doesn't break execution

### Option C — Keep hardcoded defaults
Accept that replay script uses standard defaults; document the difference.

- **Effort:** None
- **Risk:** None — but misleading replay output

## Recommended Action

Option A — parametrize the template. Address together with issue 002 (DataLoader fix) since both touch `codegen.py`.

## Acceptance Criteria

- [ ] `generate_backtest_code()` accepts `warmup_bars` and `train_fraction` parameters
- [ ] CLI `optimize` command passes actual config values when calling `generate_backtest_code()`
- [ ] Generated `WARMUP_BARS` matches `config.warmup_bars`
- [ ] Generated `TRAIN_FRACTION` matches `config.train_fraction`
- [ ] Test: `generate_backtest_code(individual, warmup_bars=100)` produces code with `WARMUP_BARS = 100`
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by code-quality and data-integrity review agents
