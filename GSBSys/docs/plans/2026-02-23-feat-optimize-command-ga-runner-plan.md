---
title: "feat: Wire optimize command to GA runner"
type: feat
date: 2026-02-23
prd: docs/plans/2026-02-23-prd-optimize-command-implementation.md
prd_version: "1.1"
---

# feat: Wire `optimize` Command to GA Runner

## Overview

Replace the `optimize` command stub in `src/cli/commands.py` with a real implementation that runs the full GA optimization pipeline: downloads data, builds the fitness function, calls `run_restarts_parallel`, saves results, and reports progress. Also adds the missing CLI entry point to `pyproject.toml`.

---

## Problem Statement

`ga-trading-sys optimize` currently only validates the config and prints parameters. No GA execution occurs. The full pipeline (data download → indicator cache → fitness fn → restarts → save results) needs to be wired.

Additionally, the `ga-trading-sys` CLI is not registered as a console script entry point in `pyproject.toml`, so it cannot be invoked as a command after `pip install -e .`.

---

## Proposed Solution

1. **Replace the optimize stub** with the full pipeline per PRD v1.1
2. **Add `--sequential` and `--verbose` flags** to the command signature
3. **Update tests** — existing `TestOptimizeCommand` stub tests need mocking; add new behaviour tests
4. **Fix `pyproject.toml`** — add `[project.scripts]` entry point

---

## Technical Considerations

### Fitness function pickling (critical on Windows)

`run_restarts_parallel` uses `multiprocessing.get_context("spawn")`. The `fitness_fn` must be a picklable top-level function — **no lambdas or closures**. Use `functools.partial`:

```python
# src/cli/commands.py
from functools import partial
from src.ga.fitness import evaluate_individual

fitness_fn = partial(
    evaluate_individual,
    train_prices=train_prices,
    test_prices=test_prices,
    n_train=n_train,
    cache=full_cache,
    engine=engine,
)
```

`NumbaBacktestEngine` contains only scalar fields — it is picklable. The indicator cache contains only NumPy arrays — also picklable.

### Train/test split — which config field to use

`GAConfig` has `train_ratio` (field under `cfg.ga`) and `BacktestConfig` has `train_fraction` (field under `cfg.backtest`). Both default to 0.40. The `optimize` command should use **`cfg.backtest.train_fraction`** — it is the explicit user-facing backtest setting and the one exposed in the YAML template.

### run_id and output directory interaction

`run_single_restart` writes convergence CSVs to `{results_dir}/{run_id}/convergence_{restart_id}.csv`. Set:
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_id = f"{cfg.data.ticker}_{timestamp}"
results_dir = output or cfg.output.dir
```

This means convergence CSVs land in `results/SPY_20260223_143052/convergence_0.csv` — consistent with PRD v1.1 Section 3.

### Progress display

Per PRD v1.1 Section 5: print a "starting" banner before `pool.starmap()`, then print all restart results together after it returns (sorted by `restart_id`). Per-generation updates are not feasible without modifying `run_single_restart()` — defer to v1.1.

### KeyboardInterrupt in parallel mode

`pool.starmap()` raises `KeyboardInterrupt` in the main process when Ctrl+C is pressed. Convergence CSVs written by completed workers survive on disk. The `List[Dict]` return value is lost. Only print a message pointing to the CSVs; do not attempt to save `best_individual.yaml` on interrupt.

---

## Acceptance Criteria

- [ ] `ga-trading-sys optimize --config config.yaml` runs end-to-end with real GA execution
- [ ] `results/best_individual.yaml` is saved and loads via `load_strategy_yaml()`
- [ ] `results/strategy.py` is saved when `output.save_code = true`
- [ ] `results/optimization_summary.txt` is saved when `output.save_reports = true`
- [ ] Config copy saved to `results/config.yaml`
- [ ] Convergence CSVs at `results/{run_id}/convergence_{i}.csv`
- [ ] Log file at `results/logs/optimize_{timestamp}.log`
- [ ] `--sequential` flag uses `run_restarts_sequential` instead of `run_restarts_parallel`
- [ ] `--verbose` flag enables DEBUG logging
- [ ] Ctrl+C exits with code 130 and prints CSV preservation message
- [ ] Clear error on missing config, download failure, insufficient data
- [ ] Warning (not error) when best fitness ≤ 0
- [ ] `ga-trading-sys` is invokable as console script after `pip install -e .`
- [ ] All existing tests pass; new `TestOptimizeCommand` tests cover mocked GA execution

---

## Implementation Plan

### File 1: `src/cli/commands.py`

Replace the `optimize` stub. Keep the same `@cli.command()` decorator, add two new flags.

**New command signature:**
```python
@cli.command()
@click.option("--config", "-c", required=True, help="Path to YAML config file.")
@click.option("--output", "-o", default=None, help="Override output directory.")
@click.option("--sequential", is_flag=True, default=False,
              help="Disable parallel execution (single process, for debugging).")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Enable DEBUG logging.")
def optimize(config: str, output: str | None, sequential: bool, verbose: bool) -> None:
    """Run GA optimisation from a config file."""
```

**Implementation outline (all imports lazy, inside function body):**

```python
def optimize(config: str, output: str | None, sequential: bool, verbose: bool) -> None:
    import logging
    import os
    from datetime import datetime
    from functools import partial
    from pathlib import Path
    import numpy as np
    import shutil

    from src.config import load_config
    from src.data.loader import load_market_data
    from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
    from src.indicators.calculator import build_indicator_cache
    from src.ga.fitness import evaluate_individual
    from src.utils.seed import make_restart_seeds
    from src.utils.parallel import run_restarts_parallel, run_restarts_sequential
    from src.export.codegen import export_strategy_yaml, generate_backtest_code
    from src.export.reporter import build_report, format_text   # (unused in optimize, but available)

    # 1. Load config
    cfg = load_config(config)
    results_dir = output or cfg.output.dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{cfg.data.ticker}_{timestamp}"

    # 2. Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_dir = Path(results_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"optimize_{timestamp}.log"
    # ... configure file + console handlers ...

    # 3. Print banner
    click.echo(f"Config  : {config}")
    click.echo(f"Ticker  : {cfg.data.ticker} ({cfg.data.start_date} → {cfg.data.end_date})")
    click.echo(f"Restarts: {cfg.ga.n_restarts} × {cfg.ga.n_generations} generations")
    click.echo(f"Workers : {cfg.ga.n_workers if not sequential else 1}")
    click.echo(f"Results : {results_dir}")
    click.echo()

    # 4. Download data
    click.echo("Downloading data...  ", nl=False)
    try:
        df = load_market_data(cfg.data.ticker, cfg.data.start_date, cfg.data.end_date)
    except Exception as exc:
        click.echo(f"\nError: {exc}", err=True)
        sys.exit(1)
    if df is None or len(df) == 0:
        click.echo("Error: empty dataset returned", err=True)
        sys.exit(1)
    min_bars = cfg.backtest.warmup_bars + 200
    if len(df) < min_bars:
        click.echo(
            f"Error: {len(df)} bars insufficient (need ≥{min_bars})", err=True)
        sys.exit(1)
    click.echo(f"✓ ({len(df)} bars)")

    # 5. Numba warm-up
    click.echo("Warming up Numba...  ", nl=False)
    warmup_jit()
    engine = NumbaBacktestEngine()
    click.echo("✓")
    click.echo()

    # 6. Build indicator cache + train/test split
    warmup = cfg.backtest.warmup_bars
    norm_win = cfg.backtest.normalization_window
    cache = build_indicator_cache(df, normalization_window=norm_win)
    sliced_cache = {k: v[warmup:] for k, v in cache.items()}
    prices = df["close"].values[warmup:].astype(np.float32)
    n_train = int(len(prices) * cfg.backtest.train_fraction)
    train_prices = prices[:n_train]
    test_prices  = prices[n_train:]
    train_cache  = {k: v[:n_train] for k, v in sliced_cache.items()}
    test_cache   = {k: v[n_train:] for k, v in sliced_cache.items()}

    # 7. Build picklable fitness function
    fitness_fn = partial(
        evaluate_individual,
        train_prices=train_prices,
        test_prices=test_prices,
        n_train=n_train,
        cache=sliced_cache,
        engine=engine,
    )

    # 8. Seeds
    seeds = make_restart_seeds(cfg.ga.random_seed, n=cfg.ga.n_restarts)

    # 9. Run
    click.echo(
        f"Running GA optimization ({cfg.ga.n_restarts} restarts × "
        f"{cfg.ga.n_generations} generations)..."
    )
    if not sequential:
        click.echo(f"[Running {cfg.ga.n_workers} restarts in parallel]")
    click.echo()

    start_time = datetime.now()
    try:
        if sequential:
            results = run_restarts_sequential(
                seeds, fitness_fn, cfg.ga,
                run_id=run_id, results_dir=results_dir,
            )
        else:
            results = run_restarts_parallel(
                seeds, fitness_fn, cfg.ga,
                run_id=run_id, results_dir=results_dir,
                n_workers=cfg.ga.n_workers,
            )
    except KeyboardInterrupt:
        elapsed = datetime.now() - start_time
        click.echo(f"\n\nInterrupt received after {elapsed}.")
        click.echo(f"Convergence CSVs preserved at: {results_dir}/{run_id}/")
        click.echo("Re-run to restart (resume not implemented in v1.0).")
        sys.exit(130)

    elapsed = datetime.now() - start_time

    # 10. Print per-restart summary
    best_restart_id = results[0]["restart_id"]
    for r in sorted(results, key=lambda x: x["restart_id"]):
        marker = "  ← BEST" if r["restart_id"] == best_restart_id else ""
        early  = " (converged early)" if r["converged_early"] else ""
        click.echo(
            f"Restart {r['restart_id']+1:2d}/{cfg.ga.n_restarts} | "
            f"fitness: {r['best_fitness']:8.2f} | "
            f"gens: {r['n_generations_run']:4d}{early}{marker}"
        )

    best = results[0]
    if best["best_fitness"] <= 0:
        click.echo("\nWarning: no profitable strategy found. "
                   "Try more generations or a different date range.", err=True)

    # 11. Save results
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    # best_individual.yaml + strategy.py
    if cfg.output.save_code:
        ind_path = str(Path(results_dir) / "best_individual.yaml")
        export_strategy_yaml(best["best_individual"], ind_path)
        code_path = Path(results_dir) / "strategy.py"
        code_path.write_text(
            generate_backtest_code(best["best_individual"]), encoding="utf-8"
        )

    # config copy
    shutil.copy2(config, str(Path(results_dir) / "config.yaml"))

    # optimization_summary.txt
    if cfg.output.save_reports:
        h_elapsed = str(elapsed).split(".")[0]  # strip microseconds
        summary_path = Path(results_dir) / "optimization_summary.txt"
        # ... write summary text ...

    # 12. Completion message
    h_elapsed = str(elapsed).split(".")[0]
    click.echo(f"\nOptimization complete! ({h_elapsed})")
    click.echo()
    click.echo(f"Saved: {results_dir}/best_individual.yaml")
    click.echo(f"Saved: {results_dir}/strategy.py")
    click.echo(f"Saved: {results_dir}/optimization_summary.txt")
    click.echo(f"Saved: {results_dir}/{run_id}/convergence_*.csv")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Validate:  ga-trading-sys validate --results {results_dir}/")
    click.echo(f"  2. Backtest:  ga-trading-sys backtest "
               f"--individual {results_dir}/best_individual.yaml")
```

### File 2: `pyproject.toml`

Add the missing console script entry point:

```toml
[project.scripts]
ga-trading-sys = "src.cli.commands:cli"
```

### File 3: `tests/test_cli.py`

Update `TestOptimizeCommand`. The existing 6 stub tests pass today without mocking (the stub does no real work). Once real execution is wired, those tests will need the `patch` pattern from `TestBacktestCommand`.

**Mock return value for the GA runner:**
```python
def _make_restart_results(n: int = 1) -> list:
    return [
        {
            "best_individual":   [0, 14, 1.2, 5, 9, 0.8, 13, 20, 1.0, 0.3, 0.04, 0.08, 1.0],
            "best_fitness":      1234.5,
            "restart_id":        i,
            "seed":              42 + i,
            "n_generations_run": 100,
            "converged_early":   False,
        }
        for i in range(n)
    ]
```

**Patch targets for optimize:**
```python
with (
    patch("src.data.loader.load_market_data", return_value=mock_df) as mock_load,
    patch("src.backtesting.numba_engine.warmup_jit"),
    patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=MagicMock()),
    patch("src.utils.parallel.run_restarts_parallel",
          return_value=_make_restart_results(10)) as mock_parallel,
    patch("src.utils.seed.make_restart_seeds", return_value=list(range(10))),
):
    result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
```

**New tests to add:**
- `test_saves_best_individual_yaml` — assert file exists after run
- `test_saves_strategy_py` — assert file exists
- `test_saves_optimization_summary` — assert file exists
- `test_saves_config_copy` — assert config.yaml copied to results/
- `test_shows_best_marker` — assert "← BEST" in output
- `test_sequential_flag_uses_sequential_runner` — assert `run_restarts_sequential` called (not parallel)
- `test_interrupt_exits_130` — assert exit code 130 on `KeyboardInterrupt` from runner
- `test_no_profitable_warning` — assert warning shown when `best_fitness <= 0`
- `test_insufficient_data_exits` — assert exit 1 when df has too few bars
- `test_download_failure_exits` — assert exit 1 when `load_market_data` raises

---

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| `NumbaBacktestEngine` not picklable in spawn pool | Check `pickle.dumps(NumbaBacktestEngine())` in a test; if it fails, instantiate engine inside the fitness fn instead |
| `train_ratio` vs `train_fraction` field conflict in config | Use `cfg.backtest.train_fraction` in optimize; document that `cfg.ga.train_ratio` is legacy and unused by CLI |
| Windows spawn + large indicator cache pickle overhead | Cache dict is ~3750 bars × 15 indicators × float32 ≈ 1.5 MB — acceptable |
| Per-restart progress invisible to user during long parallel run | Expected limitation in v1.0; documented in PRD |

---

## References

### Internal
- `src/cli/commands.py` — current stub (`optimize` function, line ~60)
- `src/utils/parallel.py` — `run_restarts_parallel`, `run_restarts_sequential`
- `src/ga/evolution.py` — `run_single_restart` return dict schema
- `src/ga/fitness.py` — `evaluate_individual` signature
- `src/utils/seed.py` — `make_restart_seeds`
- `src/config.py` — `GAConfig.n_workers`, `GAConfig.random_seed`, `BacktestConfig.train_fraction`
- `tests/test_cli.py` — `TestBacktestCommand` mocking pattern (canonical template)
- `pyproject.toml` — missing `[project.scripts]`

### PRD
- `docs/plans/2026-02-23-prd-optimize-command-implementation.md` v1.1

---

## Implementation Checklist

### `src/cli/commands.py`
- [x] Add `--sequential` and `--verbose` flags to `optimize`
- [x] Lazy-import all heavy modules inside function body (match existing pattern)
- [x] Load config and resolve `results_dir` + `run_id` + `timestamp`
- [x] Set up file logger → `results/logs/optimize_{timestamp}.log`
- [x] Print startup banner (config, ticker, restarts, workers, results dir)
- [x] Download data with error handling (download failure, insufficient bars)
- [x] Numba warm-up + engine instantiation
- [x] Build indicator cache + sliced train/test arrays
- [x] Build `fitness_fn` via `functools.partial(evaluate_individual, ...)`
- [x] Derive seeds via `make_restart_seeds(cfg.ga.random_seed, cfg.ga.n_restarts)`
- [x] Call `run_restarts_parallel` or `run_restarts_sequential` based on `--sequential`
- [x] Handle `KeyboardInterrupt` → exit 130 + CSV preservation message
- [x] Print per-restart summary table sorted by `restart_id`
- [x] Warn if `best_fitness <= 0`
- [x] Save `best_individual.yaml` (if `output.save_code`)
- [x] Save `strategy.py` (if `output.save_code`)
- [x] Copy config to `results/config.yaml`
- [x] Write `optimization_summary.txt` (if `output.save_reports`)
- [x] Print completion banner + next-steps instructions

### `pyproject.toml`
- [x] Add `[project.scripts]` section with `ga-trading-sys = "src.cli.commands:cli"`

### `tests/test_cli.py`
- [x] Update existing 6 `TestOptimizeCommand` stub tests to use `patch` pattern
- [x] Add `_make_restart_results()` helper
- [x] Add `test_saves_best_individual_yaml`
- [x] Add `test_saves_strategy_py`
- [x] Add `test_saves_optimization_summary`
- [x] Add `test_saves_config_copy`
- [x] Add `test_shows_best_marker`
- [x] Add `test_sequential_flag_uses_sequential_runner`
- [x] Add `test_interrupt_exits_130`
- [x] Add `test_no_profitable_warning`
- [x] Add `test_insufficient_data_exits`
- [x] Add `test_download_failure_exits`
- [x] Verify all 450 pre-existing tests still pass (460 now pass)
