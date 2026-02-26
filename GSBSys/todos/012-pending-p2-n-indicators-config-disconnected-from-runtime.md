---
status: pending
priority: p2
issue_id: "012"
tags: [code-review, architecture, quality, data-integrity]
dependencies: []
---

# `n_indicators` config field present but chromosome always uses exactly 3 — config has no effect

## Problem Statement

`OptimizationConfig` (or `GAConfig`) exposes an `n_indicators` field with a comment suggesting support for "up to 5" indicator slots. The chromosome is hardcoded to exactly 3 indicator slots (genes 0-8: type/period/weight × 3) in `src/ga/chromosome.py`. `n_indicators` is read from YAML config but is never passed to `build_chromosome()`, `GENE_NAMES`, or `GENE_BOUNDS`. A user who sets `n_indicators: 5` in their config YAML will see no change in behaviour — the GA always evolves a 13-gene chromosome with 3 indicators. This is a silent misconfiguration with zero feedback to the user.

## Findings

- **`src/ga/chromosome.py`** — `GENE_NAMES` has exactly 9 indicator genes (3 indicators × 3 genes each), hardcoded
- **`src/config.py`** — `n_indicators` field defined in config schema
- **`src/ga/fitness.py`** — uses `chromosome.GENE_NAMES`; doesn't reference config's `n_indicators`
- **`src/indicators/signal_generator.py`** — `_N_INDICATORS = 3` hardcoded private constant
- **Architecture reviewer finding:** "`n_indicators` config is disconnected from chromosome construction"
- **Impact:** User-facing config that has zero effect is a UX bug and a source of confusion

## Proposed Solutions

### Option A — Make chromosome construction dynamic based on `n_indicators` (Recommended for future)
Pass `n_indicators` to a `build_chromosome_spec(n_indicators)` function that returns `GENE_NAMES`, `GENE_BOUNDS`, `GENE_RANGES` dynamically. `signal_generator.py` accepts `n_indicators` parameter.

- **Effort:** Large — touches chromosome, fitness, signal_generator, CLI, codegen, all tests
- **Risk:** Medium — chromosome length changes break serialized YAML results

### Option B — Remove `n_indicators` from config (Recommended for now)
Delete the field from the config schema, or rename it to `_n_indicators_future` with a comment: "planned for Phase 2; currently always 3". Prevents user confusion.

- **Effort:** Tiny — remove field from config dataclass and YAML template
- **Risk:** None for existing functionality; breaks any YAML that explicitly sets it (unlikely in practice)

### Option C — Add a validation error if `n_indicators != 3`
```python
if config.n_indicators != 3:
    raise ValueError("n_indicators: only 3 is currently supported")
```

- **Effort:** Tiny
- **Risk:** None — surfaces misconfiguration immediately

## Recommended Action

Option C now (add validation) + Option A as a Phase 2 feature. Option B is acceptable if the field name is too confusing to keep around.

## Acceptance Criteria

- [ ] If `n_indicators` is set to anything other than 3, user sees a clear error message (not silent ignore)
- [ ] OR: field removed from config schema with a `# Phase 2: n_indicators` comment
- [ ] OR: full dynamic chromosome support implemented (Option A)
- [ ] Config YAML template updated to reflect current limitation
- [ ] All 460 existing tests pass

## Work Log

- 2026-02-24: Identified by architecture review agent
