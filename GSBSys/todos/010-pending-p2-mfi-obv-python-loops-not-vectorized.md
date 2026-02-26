---
status: pending
priority: p2
issue_id: "010"
tags: [code-review, performance, quality]
dependencies: []
---

# MFI and OBV indicator calculations use Python loops — 100× slower than vectorized alternatives

## Problem Statement

The MFI (Money Flow Index) and OBV (On-Balance Volume) indicators in `src/indicators/` are computed with Python `for` loops over bar arrays. With 10 years of daily data (≈3750 bars) and 3 indicator slots per chromosome, indicator calculation is called inside the fitness function for every individual evaluation. Python loops at this scale are ~100× slower than equivalent NumPy vectorized operations. The bottleneck compounds with population size (100) and generations (200), making indicator calculation a dominant fraction of total runtime.

## Findings

- **`src/indicators/`** — MFI and OBV implementations use explicit Python loops
- **Performance reviewer finding:** "Python loops in indicator calculation — vectorize with NumPy"
- **Impact estimate:** Indicator calc is ~10-30% of per-individual fitness time; 100× speedup → 10-30% total optimization speedup
- **Existing pattern:** RSI is already vectorized using NumPy; MACD uses `np.convolve` — the project already knows how to vectorize

## Proposed Solutions

### Option A — Vectorize MFI and OBV using NumPy (Recommended)
**OBV vectorized:**
```python
def calc_obv(close, volume):
    direction = np.sign(np.diff(close, prepend=close[0]))
    return np.cumsum(direction * volume)
```

**MFI vectorized:**
```python
def calc_mfi(high, low, close, volume, period=14):
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume
    price_diff = np.diff(typical_price, prepend=typical_price[0])
    positive_flow = np.where(price_diff > 0, raw_money_flow, 0)
    negative_flow = np.where(price_diff <= 0, raw_money_flow, 0)
    # Rolling sums via np.convolve or cumsum with sliding window
    ...
```

- **Effort:** Small — 20-40 lines replacing loop-based implementations
- **Risk:** Low — validate against existing loop results with unit tests

### Option B — Use `pandas_ta` or `ta-lib` for indicator calculation
External library handles all indicators with C-level speed.

- **Effort:** Medium — adds dependency, refactors indicator interface
- **Risk:** Medium — adds external dependency, changes how indicators are called

### Option C — Accept current performance
Document that MFI/OBV are slower; only matters for large populations.

- **Effort:** None
- **Risk:** None

## Recommended Action

Option A — self-contained fix, maintains zero new dependencies, consistent with existing RSI vectorization pattern.

## Acceptance Criteria

- [ ] MFI calculation uses NumPy vectorized operations (no Python `for` loops)
- [ ] OBV calculation uses NumPy vectorized operations (no Python `for` loops)
- [ ] Unit tests confirm vectorized output matches previous loop-based output (within float tolerance)
- [ ] Benchmark shows ≥50× speedup for vectorized vs. loop implementation
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by performance review agent
