---
status: pending
priority: p3
issue_id: "017"
tags: [code-review, quality, maintainability]
dependencies: []
---

# `--save-plots` CLI flag present but no plotting code exists — silent no-op

## Problem Statement

The `optimize` (or `backtest`) CLI command exposes a `--save-plots` flag. No plotting implementation exists anywhere in the codebase. The flag is accepted and silently ignored. Users who pass `--save-plots` will not see any plots or any error message explaining that plotting is not yet implemented. This creates a misleading UX.

## Findings

- **`src/cli/commands.py`** — `--save-plots` flag defined as a Click option
- **`src/`** — no `plot`, `chart`, or `matplotlib` references in any source file
- **Code quality reviewer finding:** "`--save-plots` flag is a no-op — no plotting code exists"

## Proposed Solutions

### Option A — Remove the `--save-plots` flag (Recommended)
Delete the Click option entirely. If plotting is a future feature, add it when implemented.

- **Effort:** Trivial
- **Risk:** None — breaking change to CLI interface, but the flag never did anything

### Option B — Print a "not implemented" warning when flag is used
```python
if save_plots:
    click.echo("Warning: --save-plots is not yet implemented", err=True)
```

- **Effort:** Trivial
- **Risk:** None — preserves CLI interface while being honest

### Option C — Keep as silent no-op
Accept that advanced users can infer it's planned.

- **Effort:** None
- **Risk:** Misleading UX persists

## Recommended Action

Option A — YAGNI. Remove the flag. Add plotting with `--save-plots` when the feature is actually implemented.

## Acceptance Criteria

- [ ] `--save-plots` flag removed from CLI or replaced with "not implemented" warning
- [ ] Help text (`--help`) no longer shows the flag (if removed)
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by code-quality review agent
