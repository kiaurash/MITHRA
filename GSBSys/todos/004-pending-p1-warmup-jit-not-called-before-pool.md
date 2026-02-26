---
status: complete
priority: p1
issue_id: "004"
tags: [code-review, performance, numba, multiprocessing]
dependencies: []
---

# `warmup_jit()` not called in main process before Pool — JIT penalty per worker

## Problem Statement

`warmup_jit()` exists in `numba_engine.py` to pre-compile the Numba JIT kernel before spawning worker processes. It is correctly called in the CLI `optimize` command (step 5). However, the multiprocessing Pool is created inside `run_restarts_parallel()` in `src/utils/parallel.py`. Because each worker is spawned AFTER the main process has already called `warmup_jit()`, the workers do NOT inherit the JIT-compiled kernel — they must each recompile it on first use. With `n_workers=8` (default), that is 8 simultaneous JIT compilations (2–10 seconds each) happening in the workers before any GA evaluation occurs.

## Findings

- **File:** `src/utils/parallel.py:63-78` — Pool created; `warmup_jit()` NOT called here
- **File:** `src/cli/commands.py:127-130` — `warmup_jit()` called in main process (correct), but this doesn't help workers on Windows spawn context
- **Platform impact:** Windows uses `spawn` (hard-coded in `parallel.py:67`), which means each worker is a fresh Python interpreter that must import and recompile everything from scratch. The Numba cache (`cache=True` in `numba_engine.py:44`) should persist to disk after the first worker compiles, but on Windows, concurrent workers may all miss the cache and compile simultaneously.
- **Estimated impact:** 8 workers × 2-10 seconds JIT = 16–80 seconds wasted at startup per optimization run.

## Proposed Solutions

### Option A — Call `warmup_jit()` in `parallel.py` before Pool creation (Recommended)
In `src/utils/parallel.py`, before line 76 (`with ctx.Pool(...)`):
```python
from src.backtesting.numba_engine import warmup_jit
warmup_jit()  # Pre-warm JIT in main process so Numba cache is on disk
```
This ensures the disk cache is written before workers start, so workers can read the cached binary rather than recompiling.

- **Effort:** Small (2 lines)
- **Risk:** Low — warmup_jit is idempotent (Numba skips recompilation if cached)

### Option B — Pre-warm inside each worker initializer
Pass a `pool_initializer=warmup_jit` to `ctx.Pool(...)`. Workers run warmup on startup.

- **Effort:** Small
- **Risk:** Low — adds N seconds of startup, but they run in parallel

### Option C — Remove warmup_jit call from CLI (document Numba handles cache)
Accept that workers compile on first call and rely on Numba's disk cache.

- **Effort:** None
- **Risk:** First run on any machine will be slow; acceptable for a developer tool

## Recommended Action

Option A — minimal change, maximal benefit on repeated runs.

## Acceptance Criteria

- [ ] `warmup_jit()` called in `run_restarts_parallel()` before `Pool` creation
- [ ] Same applied to `run_restarts_sequential()` for consistency
- [ ] Test: mock `warmup_jit` and confirm it is called inside `run_restarts_parallel`
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by performance review agent
