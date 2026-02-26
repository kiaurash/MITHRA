---
status: complete
priority: p1
issue_id: "005"
tags: [code-review, bug, data-integrity, robustness]
dependencies: []
---

# Regime classifier uses trade-level returns as bar-level — all regime results are corrupt

## Problem Statement

`src/robustness/regime_classifier.py` assumes `BacktestResult.returns` is a bar-level array of shape `(n_bars - 1,)`. In reality, `NumbaBacktestEngine` builds `returns` as a trade-level array of shape `(n_trades,)`. The classifier then applies a boolean mask of length `(n_bars - 1,)` to an array of length `(n_trades,)`. This produces silent garbage: empty arrays, wrong values, or silently truncated results. All `RegimeTestResult` objects produced by the system are meaningless.

## Findings

- **File:** `src/robustness/regime_classifier.py:210-218`
  ```python
  returns = result.returns  # comment says "(n-1,)" — WRONG, it's (n_trades,)
  labels_aligned = regime_labels[1:]  # length = n_bars - 1
  bull_mask = np.array([l == RegimeLabel.BULL for l in labels_aligned])
  regime_returns = returns[bull_mask]  # mask len >> returns len → corrupt
  ```
- **File:** `src/backtesting/numba_engine.py:158-159` — `returns_arr = trades_arr / np.float32(starting_capital)` — confirms trade-level
- **File:** `src/backtesting/engine.py:42` — docstring: `"per-trade returns"` — confirms
- **Impact:** For a strategy trading 50 times over 3750 bars, `returns` has 50 elements, `labels_aligned` has 3749 elements. NumPy boolean indexing with mask longer than array returns only the first 50 elements that the mask indexes into `returns[:3749]` — which means first 50 elements regardless of regime label → completely wrong per-regime metrics.
- The `experiments/05_phase4_export.py` experiment wraps `run_regime_testing` in a try/except `IndexError` because of this bug.

## Proposed Solutions

### Option A — Use equity_curve to derive bar-level returns (Recommended)
`BacktestResult.equity_curve` IS bar-level (shape `(n_bars,)`). Compute bar-level returns from it:
```python
# In regime_classifier.py, replace:
returns = result.returns
labels_aligned = regime_labels[1:]

# With:
equity = result.equity_curve  # shape (n_bars,)
bar_returns = np.diff(equity) / np.maximum(equity[:-1], 1e-8)  # shape (n_bars-1,)
labels_aligned = regime_labels[1:]  # aligned to bar_returns
```
Then use `bar_returns[mask]` instead of `returns[mask]`.

- **Effort:** Small
- **Risk:** Low — uses existing data, fixes semantics

### Option B — Modify engine to also return bar-level equity returns
Add `equity_returns: np.ndarray` to `BacktestResult` (`(n_bars-1,)` shape).

- **Effort:** Medium (changes engine, BacktestResult, all callers)
- **Risk:** Medium — breaks engine interface

### Option C — Map trades to regime bars
For each trade, identify which bar it was entered on and label it by the bar's regime.

- **Effort:** Large — requires tracking entry bar index in engine
- **Risk:** Medium

## Recommended Action

Option A — the equity_curve is already available and has the right shape.

## Acceptance Criteria

- [ ] `bar_returns = np.diff(equity) / np.maximum(equity[:-1], 1e-8)` used in regime classifier
- [ ] Comment corrected: "bar-level returns from equity curve, shape (n_bars-1,)"
- [ ] `test_regime_classifier.py` tests verify that regime metrics are non-empty for realistic trade frequencies
- [ ] `experiments/05_phase4_export.py` try/except around `run_regime_testing` can be removed
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by performance, architecture, and data-integrity review agents (three independent confirmations)
