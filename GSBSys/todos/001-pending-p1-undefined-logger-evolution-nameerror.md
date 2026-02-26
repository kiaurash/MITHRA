---
status: complete
priority: p1
issue_id: "001"
tags: [code-review, quality, bug]
dependencies: []
---

# Undefined `logger` in evolution.py causes NameError on population collapse

## Problem Statement

`evolution.py` references `logger.warning(...)` at line 228 but never imports `logging` or defines `logger = logging.getLogger(__name__)`. This raises a `NameError: name 'logger' is not defined` at runtime when the all-zero fitness population branch is hit (after generation 50, when `best_fit == 0.0`). The very code path meant to diagnose a serious optimization problem instead crashes the restart silently.

## Findings

- **File:** `src/ga/evolution.py:228-233`
- **Trigger condition:** `best_fit == 0.0 and gen > 50` — occurs when all individuals have zero fitness after the 50th generation (over-penalised fitness or no profitable signals)
- **Consequence:** The restart crashes with `NameError`. The `finally: csv_file.close()` still runs, so the CSV is preserved. The restart returns with `best_fitness=0.0`, which sorts last in `run_restarts_parallel`. Effectively: this population collapse is silently swallowed with no diagnostic information.
- **Secondary issue:** The guard `restart_id if "restart_id" in dir() else -1` is always `True` since `restart_id` is a function parameter — confirming the author was uncertain about scope.
- All other modules correctly define `logger = logging.getLogger(__name__)` at module level: `fitness.py:31`, `numba_engine.py:36`, `parallel.py:26`.

## Proposed Solutions

### Option A — Add module-level logger (Recommended)
Add at module top of `evolution.py` after existing imports:
```python
import logging
logger = logging.getLogger(__name__)
```
Remove the `restart_id if "restart_id" in dir() else -1` guard; just use `restart_id` directly.

- **Effort:** Small (2 lines)
- **Risk:** None

### Option B — Replace with click.echo / print
Replace `logger.warning(...)` with `click.echo(...)` or `print(...)`.

- **Effort:** Small
- **Risk:** Low — but `click` is a CLI dependency, not appropriate in the `ga/` library layer

### Option C — Remove the warning entirely
Delete lines 228-233. Population collapse will still be detectable by `best_fitness=0.0` in restart results.

- **Effort:** Tiny
- **Risk:** Loses diagnostic signal

## Recommended Action

Option A — two-line fix, consistent with all other modules.

## Technical Details

- **Affected file:** `src/ga/evolution.py`
- **Lines affected:** 228-233 (add import + logger at top)

## Acceptance Criteria

- [ ] `import logging` and `logger = logging.getLogger(__name__)` added to `evolution.py`
- [ ] The `logger.warning(...)` call uses `restart_id` directly without the `dir()` guard
- [ ] Test added that exercises the all-zero fitness branch (mock fitness returning 0.0 for 51+ gens)
- [ ] All 460 existing tests still pass

## Work Log

- 2026-02-24: Identified by code-quality and data-integrity review agents
