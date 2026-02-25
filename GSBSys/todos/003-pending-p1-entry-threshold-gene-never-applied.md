---
status: complete
priority: p1
issue_id: "003"
tags: [code-review, quality, data-integrity, ga]
dependencies: []
---

# `entry_threshold` gene (index 9) evolved but never applied — wasted search space

## Problem Statement

The chromosome has 13 genes, of which gene index 9 is `entry_threshold` (range 0–50). The GA evolves this gene every generation, but `evaluate_individual()` in `fitness.py` never calls `get_entry_signals()` to apply it. The engine receives raw composite signals with an implicit threshold of `> 0.0`. Gene 9 is genomic junk — it costs 1/13th (~7.7%) of the chromosome search budget and produces no effect on fitness. Every evolved strategy reports an `entry_threshold` value that was never used.

## Findings

- **File:** `src/ga/fitness.py:76-79` — `generate_signals_weighted_sum` called; `get_entry_signals()` NOT called
- **File:** `src/indicators/signal_generator.py` — `get_entry_signals(composite, threshold)` exists and is designed for this purpose
- **File:** `src/ga/chromosome.py:41` — gene 9 is `entry_threshold`, range `[0.0, 50.0]`
- **File:** `results/phase4_demo/strategy.py:84-88` — generated replay also skips `get_entry_signals()`
- **Consequence:** The GA wastes evolution budget. Any benefit attributed to gene 9 in the chromosome is noise. All exported `entry_threshold` values in YAML files are meaningless.

## Proposed Solutions

### Option A — Wire `get_entry_signals()` into fitness path (Recommended)
In `src/ga/fitness.py`, after computing signals:
```python
from src.indicators.signal_generator import generate_signals_weighted_sum, get_entry_signals

signals = generate_signals_weighted_sum(individual, cache)
entry_threshold = float(individual[9])
signals = get_entry_signals(signals, entry_threshold)  # Apply threshold
```
Also update `generate_backtest_code()` in `codegen.py` to emit the same call in the generated script.

- **Effort:** Small
- **Risk:** Low — this is the designed API. May change GA fitness landscape; existing tests may need updated thresholds.

### Option B — Remove gene 9 from chromosome
Remove `entry_threshold` from `GENE_NAMES`, `GENE_BOUNDS`, and `GENE_RANGES`. Shift to 12-gene chromosome with implicit `> 0.0` threshold.

- **Effort:** Medium (touches 7 files)
- **Risk:** Medium — breaks existing YAML files and serialized results

### Option C — Document the dead gene
Add a comment to `fitness.py` explaining that gene 9 is intentionally not used (Phase 1 simplification).

- **Effort:** Tiny
- **Risk:** None — preserves existing behavior but makes the intent explicit; gene remains wasted but documented

## Recommended Action

Option A — wire the gene. If the fitness landscape change breaks tests significantly, fall back to Option C with a documented Phase 2 ticket.

## Acceptance Criteria

- [ ] `get_entry_signals(signals, float(individual[9]))` called in `evaluate_individual()` before signal split
- [ ] Generated `strategy.py` emits the same `get_entry_signals()` call
- [ ] Tests in `test_fitness.py` updated to confirm entry_threshold has measurable effect
- [ ] All other 460 tests pass

## Work Log

- 2026-02-24: Identified by data-integrity review agent
