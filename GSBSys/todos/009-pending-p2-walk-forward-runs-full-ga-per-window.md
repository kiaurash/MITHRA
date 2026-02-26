---
status: pending
priority: p2
issue_id: "009"
tags: [code-review, performance, architecture]
dependencies: []
---

# Walk-forward validation runs a full GA optimization per window — O(n_windows × GA_cost) runtime

## Problem Statement

`src/robustness/walk_forward.py` calls `run_restarts_parallel()` (a full GA optimization) inside each walk-forward window to find the best individual for that window. With default config (`n_windows=5`, `n_restarts=3`, `n_generations=200`, `population_size=100`), this means 5 × 3 × 200 × 100 = **300,000 individual evaluations** just for walk-forward validation — the same cost as the primary optimization run. A single `optimize` command invocation therefore costs 2× what the user expects, and the walk-forward results are questionable because re-optimizing per window introduces look-ahead bias by design.

## Findings

- **`src/robustness/walk_forward.py:173-206`** — `run_restarts_parallel()` called inside window loop
- **Performance reviewer finding:** "Walk-forward is O(n_windows × GA_cost) — a multiplier on the total runtime"
- **Typical impact:** with `n_windows=5`, total runtime is 6× the optimization cost alone
- **Conceptual concern:** Re-optimizing on each window IS the correct walk-forward methodology (train on window, test out-of-sample), but the GA population and restart count should be reduced for validation windows to control cost

## Proposed Solutions

### Option A — Add a `validation_restarts` / `validation_generations` config (Recommended)
Add to `OptimizationConfig` (or `GAConfig`):
```python
validation_restarts: int = 1      # vs. n_restarts=3 in full optimization
validation_generations: int = 50  # vs. n_generations=200
```
Walk-forward windows use these reduced params. Reduces walk-forward cost by ~85%.

- **Effort:** Small — thread reduced config into `run_walk_forward()`
- **Risk:** Low — separate config for validation phase is a standard WFO pattern

### Option B — Walk-forward evaluates fixed individual, no re-optimization
Pass the best individual found in the primary optimization; walk-forward only back-tests it per window (no GA). True OOS test with zero additional GA cost.

- **Effort:** Small
- **Risk:** Low — but changes the semantics of walk-forward (no per-window adaptation)

### Option C — Keep current behavior; add progress reporting
Show estimated total time and per-window progress so users understand cost.

- **Effort:** Tiny
- **Risk:** None — doesn't reduce cost

## Recommended Action

Option B for the MVP — walk-forward should validate the already-optimized individual OOS per window, not re-optimize. This is the correct interpretation for most trading strategy validation. Option A is appropriate if per-window adaptation is an explicit product requirement.

## Acceptance Criteria

- [ ] Walk-forward validation mode documented (re-optimize vs. fixed individual)
- [ ] If Option B: `run_walk_forward(individual, ...)` evaluates the fixed individual per window
- [ ] If Option A: `validation_restarts` and `validation_generations` added to config
- [ ] Total optimize runtime reduced by at least 50% vs. current
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by performance review agent
