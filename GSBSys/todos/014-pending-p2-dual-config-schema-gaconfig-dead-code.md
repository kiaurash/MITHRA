---
status: pending
priority: p2
issue_id: "014"
tags: [code-review, architecture, quality, maintainability]
dependencies: []
---

# Two config schemas (`GAConfig` + `OptimizationConfig`) — one is dead code with key mismatches

## Problem Statement

The codebase has two overlapping config schemas: `GAConfig` (the "old" schema with `from_yaml()` classmethod) and `OptimizationConfig` (the "new" nested schema that the CLI actually uses). `GAConfig` has fields like `train_ratio` and `use_lhs` that don't exist in `OptimizationConfig`. The YAML template uses `seed` but `GAConfig` reads `random_seed`. `GAConfig.from_yaml()` is never called in production code — it's dead code that diverged from the live config schema. Users who read `GAConfig` source code will be confused about which config is canonical. Developers maintaining the codebase have two schema definitions to keep in sync.

## Findings

- **`src/config.py`** — both `GAConfig` and `OptimizationConfig` defined
- **`src/config.py:GAConfig.from_yaml()`** — classmethod that reads YAML into `GAConfig`; never called in CLI or GA runner
- **`src/cli/commands.py`** — uses `OptimizationConfig.from_yaml()` exclusively
- **`src/config.py:GAConfig.train_ratio`** — field with no equivalent in `OptimizationConfig`; silent dead config
- **YAML template:** uses key `seed`; `GAConfig` reads `random_seed` — key mismatch
- **Code quality/simplicity reviewer finding:** "Dual config schema — one is dead; YAML key `seed` vs `random_seed` mismatch"

## Proposed Solutions

### Option A — Delete `GAConfig`, consolidate into `OptimizationConfig` (Recommended)
1. Remove `GAConfig` class entirely (or keep as a deprecated alias)
2. Move `GAConfig.from_yaml()` into `OptimizationConfig` if not already present
3. Fix all YAML key mismatches (`seed` → `random_seed` or vice versa, whichever is correct)
4. Remove dead fields (`train_ratio`, `use_lhs`)

- **Effort:** Small — config.py cleanup + YAML template update
- **Risk:** Low — `GAConfig` callers are limited to tests (update them)

### Option B — Remove `GAConfig.from_yaml()` only; keep class for type hints
Keep `GAConfig` as a dataclass for documentation, but mark `from_yaml()` deprecated.

- **Effort:** Tiny
- **Risk:** None — doesn't clean up the confusion

### Option C — Keep both; add comment explaining the relationship
Document that `GAConfig` is legacy and `OptimizationConfig` is current.

- **Effort:** Tiny
- **Risk:** None — but perpetuates the confusion

## Recommended Action

Option A — single canonical config schema prevents future drift. YAML key mismatch (`seed` vs `random_seed`) must be fixed regardless.

## Acceptance Criteria

- [ ] Single canonical config class for GA configuration
- [ ] YAML template key names match config field names exactly
- [ ] `train_ratio` dead field removed or documented as unused
- [ ] `GAConfig.from_yaml()` either removed or points to `OptimizationConfig.from_yaml()`
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by code-quality and architecture review agents
