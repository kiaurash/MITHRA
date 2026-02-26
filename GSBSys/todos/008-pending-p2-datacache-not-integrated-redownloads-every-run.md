---
status: pending
priority: p2
issue_id: "008"
tags: [code-review, performance, architecture, quality]
dependencies: []
---

# `DataCache` implemented but never wired — market data re-downloaded on every optimize run

## Problem Statement

`src/data/cache.py` implements a full disk-based cache (`DataCache`) for market data, including TTL expiry and cache-key hashing. The `optimize` and `backtest` CLI commands ignore it entirely, calling `load_market_data()` (which hits yfinance) on every invocation. A 10-year daily data request takes 2-8 seconds and consumes API rate limit. During development, users run `optimize` dozens of times per day — they wait for the same data download repeatedly. The cache class is dead infrastructure.

## Findings

- **`src/data/cache.py`** — `DataCache` fully implemented (load, save, TTL, hash-based key)
- **`src/cli/commands.py`** — neither `optimize` nor `backtest` import or use `DataCache`
- **`src/data/loader.py`** — `load_market_data()` calls yfinance directly, no caching
- **Architecture reviewer finding:** "DataCache not wired into the pipeline"
- **Impact:** Every `optimize` run downloads 2-8 seconds of market data unnecessarily

## Proposed Solutions

### Option A — Wire `DataCache` into `load_market_data()` transparently (Recommended)
```python
# In src/data/loader.py
from src.data.cache import DataCache

def load_market_data(ticker, start, end):
    cache = DataCache()
    cached = cache.load(ticker, start, end)
    if cached is not None:
        return cached
    df = _fetch_from_yfinance(ticker, start, end)
    cache.save(ticker, start, end, df)
    return df
```
All callers benefit automatically with zero CLI changes.

- **Effort:** Small
- **Risk:** Low — cache is read-through; failure falls back to live fetch

### Option B — Wire cache in CLI commands only
Pass `--no-cache` flag; default to cached.

- **Effort:** Small — but only helps CLI, not library callers
- **Risk:** Low

### Option C — Remove DataCache
Delete the unused class; accept re-downloads.

- **Effort:** Tiny
- **Risk:** None — but loses a complete, working feature

## Recommended Action

Option A — integrating at the loader level benefits all callers including tests. Add `--no-cache` CLI flag as a follow-up if needed.

## Acceptance Criteria

- [ ] `DataCache.load()` checked before yfinance fetch in `load_market_data()`
- [ ] `DataCache.save()` called after successful fetch
- [ ] Cache hit/miss logged at DEBUG level
- [ ] Test: second call with same args returns cached data without network call
- [ ] All 460 existing tests pass (mock yfinance fixture still works)

## Work Log

- 2026-02-24: Identified by architecture review agent
