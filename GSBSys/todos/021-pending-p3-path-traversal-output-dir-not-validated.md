---
status: pending
priority: p3
issue_id: "021"
tags: [code-review, security, quality]
dependencies: []
---

# `--output` CLI flag accepts arbitrary paths — no validation against path traversal

## Problem Statement

The `optimize` and `backtest` CLI commands accept an `--output` / `--output-dir` flag specifying where results are written. The path is used directly without validation: (1) no check that it stays within the project directory or a user-approved base path, (2) no check that the path doesn't contain `..` components for path traversal, (3) no check that the path is writable before the optimization run starts (the user discovers unwritable paths only after a 20-minute optimization completes). For a developer tool, the security risk is low, but the UX issue (late failure discovery) is real.

## Findings

- **`src/cli/commands.py`** — `--output` flag passed to `Path(output_dir).mkdir(parents=True, exist_ok=True)`
- **Security reviewer finding:** "No output path validation — path traversal possible"
- **UX issue:** Path writability not checked before optimization starts
- **Risk level:** Low for a local CLI tool (user runs their own commands); medium for any future web/API exposure

## Proposed Solutions

### Option A — Validate output path is absolute or resolvable; check writable before run (Recommended)
```python
output = Path(output_dir).resolve()
try:
    output.mkdir(parents=True, exist_ok=True)
    # Touch a test file to verify write access
    test_file = output / ".write_test"
    test_file.touch()
    test_file.unlink()
except PermissionError as e:
    raise click.BadParameter(f"Output directory not writable: {e}", param_hint="--output")
```

- **Effort:** Small — 5-10 lines
- **Risk:** None — stricter input validation

### Option B — Use `click.Path(writable=True, file_okay=False, dir_okay=True)` parameter type
Click has built-in path validation types.

- **Effort:** Tiny — change Click option type
- **Risk:** None

### Option C — Accept current behavior for a developer-only CLI tool
Path traversal is a non-issue when the user runs their own commands.

- **Effort:** None
- **Risk:** None in current context

## Recommended Action

Option B — `click.Path(writable=True, ...)` is one-line and provides correct early failure with good UX.

## Acceptance Criteria

- [ ] `--output` validates path is a writable directory before starting optimization
- [ ] Clear error message shown before optimization begins if path is invalid
- [ ] Test: `--output /nonexistent/readonly` exits non-zero before starting GA
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by security review agent
