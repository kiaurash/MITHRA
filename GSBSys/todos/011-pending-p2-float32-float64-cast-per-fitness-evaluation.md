---
status: pending
priority: p2
issue_id: "011"
tags: [code-review, performance, quality]
dependencies: []
---

# Float32→Float64 cast performed inside fitness function — allocates new array per evaluation

## Problem Statement

The Numba backtest engine stores its output arrays as `float32` (for memory efficiency and cache locality). The fitness function (`src/ga/fitness.py`) receives the `BacktestResult` and immediately casts arrays to `float64` to perform metric calculations. This cast allocates a new `float64` array on every single individual evaluation — 100 population × 200 generations × 3 restarts = **60,000 array allocations** per optimize run. For equity curves of length 3750, each allocation is 3750 × 8 bytes = 30 KB. Total: ~1.8 GB of GC pressure per run just from this one pattern.

## Findings

- **`src/ga/fitness.py`** — `float(result.equity_curve[-1])` and similar casts used in metric computation
- **Performance reviewer finding:** "float32→float64 cast per fitness evaluation adds GC pressure"
- **Numba engine:** uses `np.float32` arrays intentionally for speed
- **Metric calculations:** Sharpe ratio, max drawdown etc. only need ~5-10 scalar values extracted from the equity curve, not the full float64 array

## Proposed Solutions

### Option A — Extract scalars from float32 array without full-array cast (Recommended)
```python
# Instead of:
equity_f64 = result.equity_curve.astype(np.float64)
final_equity = equity_f64[-1]

# Do:
final_equity = float(result.equity_curve[-1])  # scalar cast, no array allocation

# For diff-based metrics:
bar_returns = np.diff(result.equity_curve.astype(np.float64))  # only if needed
# Better: compute from float32 then cast scalar result:
# equity diff is fine in float32 for drawdown/sharpe purposes
```
Review each metric computation and eliminate full-array casts where only scalars or short arrays are needed.

- **Effort:** Small — audit and fix each cast in fitness.py
- **Risk:** Very low — metric accuracy difference between float32 and float64 is negligible for trading metrics

### Option B — Change Numba engine output to float64
Remove float32 usage from `NumbaBacktestEngine`.

- **Effort:** Small
- **Risk:** Low — slightly higher memory usage in engine, but eliminates casts everywhere

### Option C — Accept current behavior
GC in CPython is generational; short-lived arrays rarely cause issues in practice.

- **Effort:** None
- **Risk:** None — may be premature optimization

## Recommended Action

Option A — eliminate unnecessary full-array casts. Only cast to float64 when the full array is needed for computation; extract scalars directly from float32 otherwise.

## Acceptance Criteria

- [ ] No full-array `astype(np.float64)` calls inside fitness function hot path unless strictly necessary
- [ ] All fitness metric values remain numerically identical (within tolerance) after change
- [ ] Memory profiling shows reduced peak allocation per optimize run
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by performance review agent
