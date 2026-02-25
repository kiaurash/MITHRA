---
status: pending
priority: p3
issue_id: "018"
tags: [code-review, quality, maintainability]
dependencies: []
---

# `PerformanceReport.expectancy` duplicates `avg_trade_pnl` — redundant field with no semantic difference

## Problem Statement

`PerformanceReport` (in `src/backtesting/` or `src/export/`) has both an `expectancy` field and an `avg_trade_pnl` field. In all code paths, `expectancy` is assigned the same value as `avg_trade_pnl` (average profit/loss per trade). In trading, "expectancy" is typically defined as `win_rate × avg_win - loss_rate × avg_loss`, which is a different, more informative metric than simple average P&L. The current duplication either: (a) wastes a field with no semantic distinction, or (b) has the wrong formula for a metric called "expectancy". Either way it should be resolved.

## Findings

- **`src/backtesting/`** or **`src/export/`** — `PerformanceReport` dataclass with both fields
- **Code simplicity reviewer finding:** "`expectancy` == `avg_trade_pnl` — duplicate field or wrong formula"
- **Impact:** Misleading metric name if formula is wrong; dead field if semantically identical

## Proposed Solutions

### Option A — Implement true expectancy formula (Recommended if metric is needed)
```python
# Expectancy = win_rate * avg_win + loss_rate * avg_loss
# where avg_loss is negative
expectancy = win_rate * avg_win_pnl + (1 - win_rate) * avg_loss_pnl
```
This is the standard Kelly-adjacent metric used in trading.

- **Effort:** Small — add calculation
- **Risk:** Low — changes metric value; update any tests that hardcode the old value

### Option B — Remove `expectancy` field, keep `avg_trade_pnl`
If the two fields are truly identical, keep the more accurately named one.

- **Effort:** Small — remove field, update callers
- **Risk:** Low

### Option C — Remove `avg_trade_pnl`, rename to `expectancy` with correct formula comment
Keep one field with the correct name and formula.

- **Effort:** Small
- **Risk:** Low

## Recommended Action

Option A — implement true expectancy. It's a more useful metric and justifies keeping the field name. Add a comment explaining the formula.

## Acceptance Criteria

- [ ] `expectancy` uses formula: `win_rate × avg_win + (1-win_rate) × avg_loss`
- [ ] `avg_trade_pnl` and `expectancy` are no longer identical values
- [ ] Unit test verifies expectancy formula with known inputs
- [ ] All 460 existing tests pass (update any hardcoded expectancy values)

## Work Log

- 2026-02-24: Identified by code-simplicity review agent
