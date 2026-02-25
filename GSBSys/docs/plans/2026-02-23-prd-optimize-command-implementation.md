# **PRD Addendum: `optimize` Command Implementation**

**Version:** 1.1
**Date:** 2026-02-23
**Status:** Ready for Implementation
**Author:** Product Specification (revised against codebase audit)

---

## **Revision Notes (v1.0 → v1.1)**

- Section 4: Replaced assumed `run_ga_with_restarts()` with actual API (`run_restarts_parallel` / `run_restarts_sequential` in `src/utils/parallel.py`)
- Section 4: Added fitness_fn construction — pickling constraint, `functools.partial` requirement
- Section 4: Added seed derivation via `make_restart_seeds()` (`src/utils/seed.py`)
- Section 4: Added `run_id` and `n_workers` parameters
- Section 3: Fixed gene names in `best_individual.yaml` example (`ind1_type` not `ind0_type`)
- Section 3: Aligned convergence CSV columns with what `run_single_restart()` actually writes
- Section 5: Removed infeasible per-generation progress bar; committed to per-restart updates
- Section 6: Clarified interrupt behaviour for parallel mode
- Section 11: Closed Q1 and Q2 (answered by code)

---

## **1. Executive Summary**

The `optimize` command runs the complete GA optimization pipeline and saves results to a structured output directory. It orchestrates Phase 1 (GA Engine) to search the 13-gene chromosome space and produces a validated, backtest-ready strategy.

**User workflow:**
```bash
# Step 1: Initialize config
ga-trading-sys init --output config.yaml

# Step 2: Edit config.yaml (set ticker, date range, GA parameters)

# Step 3: Run optimization
ga-trading-sys optimize --config config.yaml --output results/

# Step 4: Validate results (separate command)
ga-trading-sys validate --results results/

# Step 5: Backtest saved strategy
ga-trading-sys backtest --individual results/best_individual.yaml
```

---

## **2. Pipeline Scope**

### **What `optimize` Does**

✅ **Phase 1: GA Optimization**
- Load config and market data
- Run `n_restarts` independent GA runs (default: 10)
- Each restart: up to `n_generations` of evolution (default: 1000, with early-stop)
- Select best individual across all restarts (highest fitness)
- Save best individual + convergence data

❌ **Phase 2: Validation** (Separate Command)
- Pearson filter, OOS testing, noise injection, family grouping
- Run via: `ga-trading-sys validate --results results/`

❌ **Phase 3: Robustness Testing** (Separate Command)
- Walk-forward, sensitivity analysis, regime testing
- Future work (not in v1.0 scope)

### **Rationale**

**Separation of concerns:**
- `optimize` is long-running (1-2 hours) — user may want to run validation later
- Validation can be re-run with different thresholds without re-optimizing
- Faster iteration during development (validate multiple individuals without GA re-run)

---

## **3. Output Structure**

### **Results Directory Layout**

```
results/
├── best_individual.yaml           # Winner across all restarts (human-readable)
├── strategy.py                    # Self-contained backtest script
├── config.yaml                    # Copy of input config (reproducibility)
├── optimization_summary.txt       # Human-readable summary
├── SPY_20260223_143052/           # run_id subdirectory (created by run_single_restart)
│   ├── convergence_0.csv          # Convergence data per restart (engine naming)
│   ├── convergence_1.csv
│   ...
│   └── convergence_9.csv
└── logs/
    └── optimize_20260223_143052.log   # Timestamped log file
```

**Note on convergence subdirectory:** `run_single_restart()` writes convergence CSVs to
`{results_dir}/{run_id}/convergence_{restart_id}.csv`. The CLI sets `run_id` to
`f"{ticker}_{timestamp}"` (e.g. `SPY_20260223_143052`) so runs are distinguishable.

### **File Specifications**

#### **3.1. best_individual.yaml**

YAML dict keyed by gene name (produced by `export_strategy_yaml`). Gene names come
from `src/ga/chromosome.py::GENE_NAMES` — **1-indexed** (`ind1_type`, not `ind0_type`):

```yaml
ind1_type: 0.0
ind1_period: 14.0
ind1_weight: 1.2
ind2_type: 5.0
ind2_period: 9.0
ind2_weight: 0.8
ind3_type: 13.0
ind3_period: 20.0
ind3_weight: 1.0
entry_threshold: 0.3
stop_loss_pct: 0.04
take_profit_pct: 0.08
position_size_mult: 1.0
```

#### **3.2. strategy.py**

Generated via `generate_backtest_code(best_individual)` — self-contained Python script.

#### **3.3. optimization_summary.txt**

Human-readable summary:

```
GA-Trading-Sys Optimization Summary
====================================
Date:       2026-02-23 14:30:52
Config:     config.yaml
Ticker:     SPY (2010-01-01 to 2024-12-31)
Data bars:  3523 (warmup: 252)

GA Parameters:
  Population:  200
  Generations: 1000
  Restarts:    10
  Workers:     8
  Crossover:   0.95
  Mutation:    0.05
  Master seed: 42

Results:
  Best restart:       7
  Best fitness:       142.58
  Generations run:    847 (converged early)

Elapsed time: 1h 23m 14s
```

#### **3.4. {run_id}/convergence_{i}.csv**

Written directly by `run_single_restart()` during the run — one file per restart.
Columns match what the engine actually writes:

```csv
gen,best_fitness,avg_fitness,std_fitness
0,45.2,12.3,8.7
1,52.1,15.8,9.2
2,58.3,18.4,10.1
...
847,142.5,98.2,25.4
```

**Note:** `n_trades_test` is NOT a column — it is not tracked per-generation by the engine.

#### **3.5. config.yaml**

Copy of input config for reproducibility.

#### **3.6. logs/optimize_{timestamp}.log**

Python logging output (DEBUG level if `--verbose`):

```
2026-02-23 14:30:52 INFO  Loading config: config.yaml
2026-02-23 14:30:53 INFO  Downloading SPY data (2010-01-01 to 2024-12-31)
2026-02-23 14:30:58 INFO  Loaded 3523 bars
2026-02-23 14:31:02 INFO  Warming up Numba JIT...
2026-02-23 14:31:05 INFO  Starting GA optimization (10 restarts × 1000 generations)
2026-02-23 14:31:05 INFO  run_id: SPY_20260223_143052  master_seed: 42
2026-02-23 14:31:05 INFO  Restart seeds: [639426071, 1841268066, ...]
2026-02-23 14:32:18 INFO  Restart 0/10 complete | fitness: 128.4 | gens: 1000 | elapsed: 73s
...
2026-02-23 15:53:19 INFO  All restarts complete | Best: restart 7 (fitness 142.5)
2026-02-23 15:53:20 INFO  Saved: results/best_individual.yaml
2026-02-23 15:53:20 INFO  Saved: results/strategy.py
2026-02-23 15:53:20 INFO  Optimization complete. Elapsed: 1h 23m 14s
```

---

## **4. API Contracts**

### **4.1. Actual Entry Points**

There is **no** `run_ga_with_restarts()` function. The real entry points are in
`src/utils/parallel.py`:

```python
# Parallel (production) — uses multiprocessing spawn pool
def run_restarts_parallel(
    seeds: List[int],
    fitness_fn: Callable[[list], Tuple[float, ...]],
    config: GAConfig,
    run_id: str = "default",
    results_dir: str = "results",
    n_workers: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Returns list of result dicts sorted by best_fitness descending."""

# Sequential (fallback for single-core / testing)
def run_restarts_sequential(
    seeds: List[int],
    fitness_fn: Callable[[list], Tuple[float, ...]],
    config: GAConfig,
    run_id: str = "default",
    results_dir: str = "results",
) -> List[Dict[str, Any]]:
```

**Return value** — each dict in the list contains:

```python
{
    "best_individual":   list[float],  # 13-gene chromosome
    "best_fitness":      float,
    "restart_id":        int,
    "seed":              int,
    "n_generations_run": int,          # may be < n_generations on early stop
    "converged_early":   bool,
}
```

Results are sorted best-first. `results[0]` is always the winner.

### **4.2. Seed Derivation**

Use `src/utils/seed.py::make_restart_seeds()` — do NOT use `range(n_restarts)` arithmetic:

```python
from src.utils.seed import make_restart_seeds

seeds = make_restart_seeds(config.random_seed, n=config.n_restarts)
# Deterministic, non-overlapping, stable across Python versions
```

Log the seeds at INFO level for FR-8.4 reproducibility.

### **4.3. Fitness Function Construction (Critical — Windows Spawn)**

`run_restarts_parallel` uses the `spawn` multiprocessing context (hard-coded). This
means `fitness_fn` **must be a picklable top-level function** — no lambdas, no closures.

The only supported pattern is `functools.partial` applied to the top-level
`evaluate_individual` from `src/ga/fitness.py`:

```python
from functools import partial
from src.ga.fitness import evaluate_individual
from src.indicators.calculator import build_indicator_cache

# Build data and cache in the main process
cache = build_indicator_cache(df, normalization_window=cfg.backtest.normalization_window)
sliced_cache = {k: v[cfg.backtest.warmup_bars:] for k, v in cache.items()}
prices = df["close"].values[cfg.backtest.warmup_bars:].astype(np.float32)
n_train = int(len(prices) * cfg.backtest.train_fraction)
train_prices = prices[:n_train]
test_prices  = prices[n_train:]
train_cache  = {k: v[:n_train] for k, v in sliced_cache.items()}
test_cache   = {k: v[n_train:] for k, v in sliced_cache.items()}

# Merge caches for the full signal (fitness.py generates signals on full cache)
full_cache = {k: v for k, v in sliced_cache.items()}

fitness_fn = partial(
    evaluate_individual,
    train_prices=train_prices,
    test_prices=test_prices,
    n_train=n_train,
    cache=full_cache,
    engine=engine,
)
```

The cache dict contains only NumPy arrays (pickle-safe). The `NumbaBacktestEngine`
instance must also be picklable — verify this holds (it has no file handles or
unpicklable state in the current implementation).

### **4.4. BacktestResult Signature**

Confirmed from `src/backtesting/engine.py`:

```python
@dataclass(frozen=True)
class BacktestResult:
    sharpe_ratio: float
    profit_factor: float
    n_trades: int
    total_pnl: float
    avg_trade_pnl: float
    equity_curve: np.ndarray
    returns: np.ndarray
```

The `optimization_summary.txt` does not include a per-individual backtest result —
that comes from `validate`. The summary only reports the GA fitness score and
`n_generations_run` from the restart result dict.

---

## **5. Progress Display**

### **5.1. Feasible Approach: Per-Restart Updates**

`run_restarts_parallel` blocks on `pool.starmap()` until all workers finish — there
is no callback mechanism for per-generation updates. Per-restart updates are the
only feasible approach without modifying `run_single_restart()`.

**UX output:**

```bash
$ ga-trading-sys optimize --config config.yaml

Config  : config.yaml
Ticker  : SPY (2010-01-01 to 2024-12-31)
Data    : 3523 bars
Restarts: 10 × 1000 generations
Workers : 8
Results : results/

Downloading SPY data...  ✓ (3523 bars)
Warming up Numba...      ✓

Running GA optimization (10 restarts × 1000 generations)...
[Restarts run in parallel — results appear as each worker finishes]

Restart  3/10 complete | fitness:  128.4 | gens: 1000 | elapsed: 22m 54s
Restart  1/10 complete | fitness:   89.2 | gens:  847 | elapsed: 22m 59s  (converged early)
Restart  7/10 complete | fitness:  142.5 | gens: 1000 | elapsed: 23m 12s  ← BEST
...

Optimization complete! (1h 16m 19s)

Saved: results/best_individual.yaml
Saved: results/strategy.py
Saved: results/optimization_summary.txt
Saved: results/SPY_20260223_143052/convergence_0.csv ... convergence_9.csv

Next steps:
  1. Validate:  ga-trading-sys validate --results results/
  2. Backtest:  ga-trading-sys backtest --individual results/best_individual.yaml
```

**Note on ordering:** With parallel execution, restarts complete out of order. Print
each result as it arrives if using a callback, or print all results after
`pool.starmap()` returns. Per-restart progress during parallel execution requires
adding a callback mechanism — defer to v1.1.

**v1.0 simplification:** Print a "starting..." message before pool.starmap(), then
print all restart results together after the pool returns (sorted by restart_id).

### **5.2. Implementation**

```python
click.echo(f"Running GA optimization ({cfg.ga.n_restarts} restarts × "
           f"{cfg.ga.n_generations} generations)...")
click.echo(f"[Running {n_workers} restarts in parallel]")
click.echo()

results = run_restarts_parallel(seeds, fitness_fn, cfg.ga,
                                run_id=run_id, results_dir=results_dir,
                                n_workers=cfg.ga.n_workers)

for r in sorted(results, key=lambda x: x["restart_id"]):
    marker = "  ← BEST" if r["restart_id"] == results[0]["restart_id"] else ""
    early  = " (converged early)" if r["converged_early"] else ""
    click.echo(
        f"Restart {r['restart_id']+1:2d}/{cfg.ga.n_restarts} complete | "
        f"fitness: {r['best_fitness']:7.1f} | "
        f"gens: {r['n_generations_run']:4d}{early}{marker}"
    )
```

---

## **6. Error Handling**

### **6.1. Interrupt (Ctrl+C)**

**Parallel mode behaviour:**

`KeyboardInterrupt` in the main process terminates the multiprocessing pool workers
abruptly. Convergence CSVs written to disk by completed workers are preserved (they
flush per-generation). However, the `pool.starmap()` return value is lost — only
restarts that wrote their full results dict before the interrupt contribute to
`best_individual.yaml`.

**Feasible v1.0 behaviour:**

```python
try:
    results = run_restarts_parallel(seeds, fitness_fn, cfg.ga,
                                    run_id=run_id, results_dir=results_dir,
                                    n_workers=cfg.ga.n_workers)
except KeyboardInterrupt:
    click.echo("\n\nInterrupt received. Convergence CSVs written so far are preserved.")
    click.echo(f"See: {results_dir}/{run_id}/convergence_*.csv")
    click.echo("Re-run to restart optimization (resume not implemented in v1.0).")
    sys.exit(130)
```

**What IS saved on interrupt:** Convergence CSVs for any restart that completed
at least one generation before the interrupt (written incrementally to disk).

**What is NOT saved on interrupt:** `best_individual.yaml`, `strategy.py`,
`optimization_summary.txt` (these require the `pool.starmap()` return value).

**Exit code:** 130 (standard SIGINT convention).

### **6.2. Data Download Failure**

```python
try:
    df = load_market_data(ticker, start, end)
    if df is None or len(df) == 0:
        raise ValueError("Empty DataFrame returned")
except Exception as e:
    click.echo(f"Error downloading {ticker} data: {e}", err=True)
    click.echo("Check ticker symbol and date range in config.", err=True)
    sys.exit(1)
```

### **6.3. Insufficient Data**

```python
min_bars = cfg.backtest.warmup_bars + 200  # warmup + minimal train+test
if len(df) < min_bars:
    click.echo(
        f"Insufficient data: {len(df)} bars "
        f"(need at least {min_bars}: {cfg.backtest.warmup_bars} warmup + 200 train/test)",
        err=True,
    )
    sys.exit(1)
```

### **6.4. No Profitable Restarts**

```python
best = results[0]  # sorted best-first
if best["best_fitness"] <= 0:
    click.echo("Warning: No profitable strategy found across all restarts.", err=True)
    click.echo("Try: more generations, larger population, different date range.")
    # Still save results — useful for debugging
```

---

## **7. Command Signature**

```bash
ga-trading-sys optimize --config CONFIG [--output DIR] [--sequential] [--verbose]
```

### **Arguments**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--config`, `-c` | ✅ Yes | — | Path to YAML config file |
| `--output`, `-o` | ❌ No | From `config.output.dir` | Override output directory |
| `--sequential` | ❌ No | False | Disable parallel execution (for debugging) |
| `--verbose`, `-v` | ❌ No | False | Enable DEBUG logging |

### **Examples**

```bash
# Basic usage
ga-trading-sys optimize --config config.yaml

# Custom output directory
ga-trading-sys optimize --config config.yaml --output results_spy/

# Debug: single-process, verbose
ga-trading-sys optimize --config config.yaml --sequential --verbose
```

---

## **8. Performance Requirements**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Wall time** | <2 hours | 10 restarts × 1000 gen on 8-core CPU |
| **Memory** | <4 GB | Peak RSS during GA run |
| **Disk I/O** | <100 MB | Total results/ directory size |

---

## **9. Config Respect**

| Config Path | Behavior |
|-------------|----------|
| `ga.n_workers` | Passed to `run_restarts_parallel` as `n_workers` |
| `ga.random_seed` | Passed to `make_restart_seeds()` as `base_seed` |
| `output.save_code` | If `true`, save `strategy.py` + `best_individual.yaml` |
| `output.save_reports` | If `true`, save `optimization_summary.txt` |
| `output.save_plots` | Ignored during `optimize` — plots deferred to `validate` |

**Note:** Convergence CSVs are **always** saved (written by the engine regardless of config flags).

---

## **10. Success Criteria**

### **Implementation Complete When:**

✅ **1. Command runs end-to-end**
- `ga-trading-sys optimize --config config.yaml` completes without errors
- Results directory created with correct structure

✅ **2. Output validation**
- `best_individual.yaml` loads correctly via `load_strategy_yaml()`
- `strategy.py` executes without errors (`python results/strategy.py`)
- Convergence CSVs have correct columns (`gen,best_fitness,avg_fitness,std_fitness`)

✅ **3. Interrupt handling**
- Ctrl+C exits with code 130
- Convergence CSVs written so far are preserved on disk

✅ **4. Error messages**
- Clear error on missing config file
- Clear error on invalid/unavailable ticker
- Clear error on insufficient data

✅ **5. Performance**
- 10 restarts complete in <2 hours on 8-core machine
- Memory usage <4 GB

✅ **6. Integration test**
- Full workflow: `init` → edit config → `optimize` → `validate` → `backtest`
- All commands execute successfully with generated files

---

## **11. Open Questions for Developer**

**Q1** ~~Does `src/ga/evolution.py` have a `run_ga_with_restarts` function?~~
**Answered:** No. Use `run_restarts_parallel` / `run_restarts_sequential` from
`src/utils/parallel.py`.

**Q2** ~~Does DEAP's evolution loop provide convergence data?~~
**Answered:** Yes. `run_single_restart()` writes `gen,best_fitness,avg_fitness,std_fitness`
to `{results_dir}/{run_id}/convergence_{restart_id}.csv` each generation.

**Q3: Should we implement resume capability in v1.0?**
- **Decision:** NO — defer to v1.1
- **Rationale:** Requires checkpoint serialisation and DEAP state management

**Q4: Is `NumbaBacktestEngine` picklable for the spawn pool?**
- **Verify before implementation.** It has no file handles or thread locks in the
  current code, so it should be picklable. If not, the engine must be instantiated
  inside `evaluate_individual` rather than passed via `partial`.

---

## **12. Implementation Checklist**

```markdown
## src/cli/commands.py:optimize Implementation

- [ ] Parse config; resolve results_dir (--output or config.output.dir)
- [ ] Set up file logger → results/logs/optimize_{timestamp}.log
- [ ] Download market data with error handling
- [ ] Validate data length (>= warmup + 200)
- [ ] Initialize NumbaBacktestEngine + warmup_jit()
- [ ] Build indicator cache + sliced train/test arrays
- [ ] Build fitness_fn via functools.partial(evaluate_individual, ...)
- [ ] Derive seeds via make_restart_seeds(config.random_seed, config.n_restarts)
- [ ] Generate run_id = f"{ticker}_{timestamp}"
- [ ] Call run_restarts_parallel (or run_restarts_sequential if --sequential)
- [ ] Handle KeyboardInterrupt (exit 130, print CSV preservation message)
- [ ] Print per-restart summary table
- [ ] Save best_individual.yaml (if output.save_code)
- [ ] Save strategy.py (if output.save_code)
- [ ] Save optimization_summary.txt (if output.save_reports)
- [ ] Copy config.yaml to results/
- [ ] Print completion message + next steps
- [ ] Handle no-profitable-restarts warning
```

---

## **13. Reference Architecture**

```
CLI Layer (commands.py:optimize)
    ↓ load_config()
Config Layer (config.py)
    ↓ load_market_data()
Data Layer (data/loader.py)
    ↓ build_indicator_cache()
Indicators Layer (indicators/calculator.py)
    ↓ functools.partial(evaluate_individual, ...)
Fitness Layer (ga/fitness.py)
    ↓ make_restart_seeds(base_seed, n_restarts)
Seed Layer (utils/seed.py)
    ↓ run_restarts_parallel(seeds, fitness_fn, config, run_id, results_dir, n_workers)
Parallel Layer (utils/parallel.py)
    ↓ run_single_restart() × n_restarts [in spawn pool]
Evolution Layer (ga/evolution.py)
    ↓ engine.run()
Backtest Layer (backtesting/numba_engine.py)
    ↓ writes convergence_{i}.csv per restart
    ↓ returns List[Dict] sorted best-first
Parallel Layer → CLI Layer
    ↓ export_strategy_yaml(), generate_backtest_code()
Export Layer (export/codegen.py)
    ↓ save results, print summary
CLI Layer
```

---

## **Appendix A: Example Full Run**

```bash
$ ga-trading-sys optimize --config config.yaml

Config  : config.yaml
Ticker  : SPY (2010-01-01 to 2024-12-31)
Data    : 3523 bars
Restarts: 10 × 1000 generations
Workers : 8
Results : results/

Downloading SPY data...  ✓ (3523 bars)
Warming up Numba...      ✓

Running GA optimization (10 restarts × 1000 generations)...
[Running 8 restarts in parallel — results printed when all complete]

Restart  1/10 complete | fitness:   89.2 | gens: 1000
Restart  2/10 complete | fitness:  105.8 | gens: 1000
Restart  3/10 complete | fitness:  128.4 | gens: 1000
Restart  4/10 complete | fitness:   95.1 | gens:  847 (converged early)
Restart  5/10 complete | fitness:  112.6 | gens: 1000
Restart  6/10 complete | fitness:   88.9 | gens: 1000
Restart  7/10 complete | fitness:  142.5 | gens: 1000  ← BEST
Restart  8/10 complete | fitness:  101.3 | gens: 1000
Restart  9/10 complete | fitness:   93.4 | gens: 1000
Restart 10/10 complete | fitness:  118.7 | gens: 1000

Optimization complete! (1h 16m 19s)

Saved: results/best_individual.yaml
Saved: results/strategy.py
Saved: results/optimization_summary.txt
Saved: results/SPY_20260223_143052/convergence_0.csv ... convergence_9.csv

Next steps:
  1. Validate:  ga-trading-sys validate --results results/
  2. Backtest:  ga-trading-sys backtest --individual results/best_individual.yaml
```

---

## **End of PRD Addendum**

**Status**: Ready for implementation
**Estimated development time**: 4-6 hours
**Estimated testing time**: 2-3 hours
**Total**: 1 developer-day
