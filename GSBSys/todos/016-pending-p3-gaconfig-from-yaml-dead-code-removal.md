---
status: pending
priority: p3
issue_id: "016"
tags: [code-review, quality, maintainability]
dependencies: ["014"]
---

# `GAConfig.from_yaml()` is dead code — never called in production or tests

## Problem Statement

`GAConfig.from_yaml()` classmethod in `src/config.py` loads a YAML file into a `GAConfig` instance. It is never invoked by any CLI command, GA runner, or test. Its existence alongside the live `OptimizationConfig.from_yaml()` path creates confusion about which loader is canonical. Dead classmethods also receive future maintenance work (e.g., if YAML structure changes, maintainers may update `GAConfig.from_yaml()` instead of the live path).

## Findings

- **`src/config.py`** — `GAConfig.from_yaml()` defined
- **Grep result:** zero references to `GAConfig.from_yaml` in `src/` or `tests/` (excluding the definition itself)
- **Code quality reviewer finding:** "GAConfig.from_yaml() is unreferenced dead code"
- **Dependency on 014:** If `GAConfig` is removed entirely (issue 014), this is resolved automatically

## Proposed Solutions

### Option A — Delete `GAConfig.from_yaml()` if not needed for tests
Remove the dead classmethod.

- **Effort:** Trivial
- **Risk:** None if no callers exist

### Option B — Mark `@deprecated` with a warning
```python
import warnings
@classmethod
def from_yaml(cls, path):
    warnings.warn("GAConfig.from_yaml is deprecated; use OptimizationConfig.from_yaml", DeprecationWarning)
    ...
```

- **Effort:** Trivial
- **Risk:** None

## Recommended Action

Delete it. If 014 is resolved first (GAConfig removal), this is automatically done.

## Acceptance Criteria

- [ ] `GAConfig.from_yaml()` removed or marked deprecated
- [ ] No references to it in codebase
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by code-quality review agent
