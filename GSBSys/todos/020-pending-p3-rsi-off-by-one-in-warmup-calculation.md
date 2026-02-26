---
status: pending
priority: p3
issue_id: "020"
tags: [code-review, bug, data-integrity, quality]
dependencies: []
---

# RSI calculation may have off-by-one error in warmup period — first valid value may be NaN

## Problem Statement

The RSI(n) indicator requires `n` bars of price data before producing a valid value. Some RSI implementations use `n` bars (correct) while others use `n+1` bars (also common, due to Wilder's smoothing needing one extra bar for the first average). If the warmup period in the backtest data split does not account for this off-by-one, the first bar of in-sample data may have `NaN` RSI, which propagates as a `NaN` signal into the backtest engine. With `warmup_bars=252` this is unlikely to cause observable issues (252 >> 14), but for users who reduce `warmup_bars` aggressively, one NaN bar at the start can cause a NaN fitness score.

## Findings

- **`src/indicators/`** — RSI implementation; check whether it uses `n` or `n+1` bars before first valid value
- **Data integrity reviewer finding:** "RSI may have off-by-one in warmup calculation"
- **Risk context:** low severity given default `warmup_bars=252` >> max RSI period (typically 14-21); becomes relevant only with aggressive warmup reduction

## Proposed Solutions

### Option A — Add NaN check and forward-fill first bar in signal array (Recommended)
```python
signals = generate_signals_weighted_sum(individual, cache)
if np.isnan(signals[0]):
    signals[0] = 0.0  # No signal on first bar if indicator not converged
```
Defensive NaN handling prevents propagation.

- **Effort:** Tiny
- **Risk:** None

### Option B — Verify RSI implementation uses Wilder's +1 bar rule; document
Audit the RSI code and confirm/correct the off-by-one. Add a comment.

- **Effort:** Small — code audit
- **Risk:** None

### Option C — Add assertion in tests
`assert not np.any(np.isnan(signals))` in indicator test suite.

- **Effort:** Tiny
- **Risk:** None — test-only change

## Recommended Action

Option B first (audit), then Option A if off-by-one is confirmed. Option C is a good addition regardless.

## Acceptance Criteria

- [ ] RSI warmup requirement documented (n or n+1 bars)
- [ ] Signal array NaN check added or confirmed unnecessary
- [ ] Test: `generate_signals_weighted_sum` with `warmup_bars >= period+1` produces no NaN values
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by data-integrity review agent
