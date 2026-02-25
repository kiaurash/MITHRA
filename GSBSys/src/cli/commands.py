"""Click CLI for ga-trading-sys.

Commands::

    ga-trading-sys init     --output config.yaml
    ga-trading-sys optimize --config config.yaml [--output results/]
    ga-trading-sys validate --results results/ [--individual individual.yaml]
    ga-trading-sys backtest --individual results/individual.yaml

``init``      — write a default config YAML template.
``optimize``  — run GA optimisation (loads config, downloads data, runs GA).
``validate``  — summarise performance from a results directory.
``backtest``  — replay a saved individual and print a performance report.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(package_name="ga-trading-sys")
def cli() -> None:
    """GA Trading System — genetic algorithm strategy optimiser."""


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

@cli.command()
@click.option(
    "--output", "-o",
    default="config.yaml",
    show_default=True,
    help="Destination path for the config template.",
)
def init(output: str) -> None:
    """Write a default configuration YAML template."""
    from src.config import default_config_yaml

    path = Path(output)
    if path.exists():
        click.echo(f"File already exists: {path}  (use a different --output path)", err=True)
        sys.exit(1)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_config_yaml(), encoding="utf-8")
    click.echo(f"Config template written to: {path}")
    click.echo("Edit the file, then run:  ga-trading-sys optimize --config " + str(path))


# ---------------------------------------------------------------------------
# optimize
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--config", "-c", required=True, help="Path to YAML config file.")
@click.option("--output", "-o", default=None, help="Override output directory.")
@click.option(
    "--sequential", is_flag=True, default=False,
    help="Disable parallel execution (single process, for debugging).",
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False,
    help="Enable DEBUG logging.",
)
def optimize(config: str, output: str | None, sequential: bool, verbose: bool) -> None:
    """Run GA optimisation from a config file."""
    import logging
    import shutil
    from datetime import datetime
    from functools import partial
    from pathlib import Path as _Path

    import numpy as np

    from src.config import load_config
    from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
    from src.data.loader import load_market_data
    from src.export.codegen import export_strategy_yaml, generate_backtest_code
    from src.ga.fitness import evaluate_individual
    from src.indicators.calculator import build_indicator_cache
    from src.utils.parallel import run_restarts_parallel, run_restarts_sequential
    from src.utils.seed import make_restart_seeds

    # 1. Load config
    cfg = load_config(config)
    results_dir = output or cfg.output.dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{cfg.data.ticker}_{timestamp}"

    # 2. Set up file logger (non-intrusive: does not touch root logger)
    log_dir = _Path(results_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"optimize_{timestamp}.log"
    log = logging.getLogger(f"ga_optimize_{timestamp}")
    log.setLevel(logging.DEBUG if verbose else logging.INFO)
    log.propagate = False
    _fh = logging.FileHandler(str(log_path), encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s  %(message)s"))
    log.addHandler(_fh)

    # 3. Print startup banner
    n_workers_display = 1 if sequential else cfg.ga.n_workers
    click.echo(f"Config  : {config}")
    click.echo(f"Ticker  : {cfg.data.ticker} ({cfg.data.start_date} -> {cfg.data.end_date})")
    click.echo(f"Restarts: {cfg.ga.n_restarts} x {cfg.ga.n_generations} generations")
    click.echo(f"Workers : {n_workers_display}")
    click.echo(f"Results : {results_dir}")
    click.echo()

    # 4. Download data
    click.echo("Downloading data...  ", nl=False)
    try:
        df = load_market_data(cfg.data.ticker, cfg.data.start_date, cfg.data.end_date)
    except Exception as exc:
        click.echo(f"\nError downloading data: {exc}", err=True)
        sys.exit(1)

    if df is None or len(df) == 0:
        click.echo("Error: empty dataset returned", err=True)
        sys.exit(1)

    min_bars = cfg.backtest.warmup_bars + 200
    if len(df) < min_bars:
        click.echo(
            f"\nError: {len(df)} bars insufficient (need >= {min_bars})",
            err=True,
        )
        sys.exit(1)
    click.echo(f"OK ({len(df)} bars)")

    # 5. Numba warm-up
    click.echo("Warming up Numba...  ", nl=False)
    warmup_jit()
    engine = NumbaBacktestEngine()
    click.echo("OK")
    click.echo()

    # 6. Build indicator cache + train/test split
    warmup = cfg.backtest.warmup_bars
    norm_win = cfg.backtest.normalization_window
    full_cache = build_indicator_cache(df, normalization_window=norm_win)
    sliced_cache = {k: v[warmup:] for k, v in full_cache.items()}
    prices = df["close"].values[warmup:].astype(np.float32)
    n_train = int(len(prices) * cfg.backtest.train_fraction)
    train_prices = prices[:n_train]
    test_prices = prices[n_train:]

    # 7. Build picklable fitness function (functools.partial required for spawn pool)
    fitness_fn = partial(
        evaluate_individual,
        train_prices=train_prices,
        test_prices=test_prices,
        n_train=n_train,
        cache=sliced_cache,
        engine=engine,
    )

    # 8. Derive restart seeds deterministically from master seed
    seeds = make_restart_seeds(cfg.ga.random_seed, n=cfg.ga.n_restarts)

    # 9. Run GA restarts
    click.echo(
        f"Running GA optimization ({cfg.ga.n_restarts} restarts x "
        f"{cfg.ga.n_generations} generations)..."
    )
    if not sequential:
        click.echo(f"[Parallel: {cfg.ga.n_workers} workers — no per-restart progress]")
    click.echo()

    start_time = datetime.now()
    try:
        if sequential:
            results = run_restarts_sequential(
                seeds, fitness_fn, cfg.ga,
                run_id=run_id,
                results_dir=results_dir,
            )
        else:
            results = run_restarts_parallel(
                seeds, fitness_fn, cfg.ga,
                run_id=run_id,
                results_dir=results_dir,
                n_workers=cfg.ga.n_workers,
            )
    except KeyboardInterrupt:
        elapsed = datetime.now() - start_time
        click.echo(f"\n\nInterrupt received after {elapsed}.")
        click.echo(f"Convergence CSVs preserved at: {results_dir}/{run_id}/")
        click.echo("Re-run to restart (resume not supported in v1.0).")
        sys.exit(130)

    elapsed = datetime.now() - start_time

    # 10. Print per-restart summary table (sorted by restart_id for readability)
    best_restart_id = results[0]["restart_id"]
    for r in sorted(results, key=lambda x: x["restart_id"]):
        marker = "  <- BEST" if r["restart_id"] == best_restart_id else ""
        early = " (early stop)" if r["converged_early"] else ""
        click.echo(
            f"Restart {r['restart_id'] + 1:2d}/{cfg.ga.n_restarts} | "
            f"fitness: {r['best_fitness']:10.2f} | "
            f"gens: {r['n_generations_run']:4d}{early}{marker}"
        )
    click.echo()

    best = results[0]
    if best["best_fitness"] <= 0:
        click.echo(
            "Warning: no profitable strategy found. "
            "Try more generations or a different date range.",
            err=True,
        )

    # 11. Save results
    _Path(results_dir).mkdir(parents=True, exist_ok=True)

    if cfg.output.save_code:
        ind_path = str(_Path(results_dir) / "best_individual.yaml")
        export_strategy_yaml(best["best_individual"], ind_path)
        code_path = _Path(results_dir) / "strategy.py"
        code_path.write_text(
            generate_backtest_code(
                best["best_individual"],
                warmup_bars=cfg.backtest.warmup_bars,
                train_fraction=cfg.backtest.train_fraction,
            ),
            encoding="utf-8",
        )

    shutil.copy2(config, str(_Path(results_dir) / "config.yaml"))

    if cfg.output.save_reports:
        h_elapsed_save = str(elapsed).split(".")[0]
        summary_lines = [
            "GA Optimization Summary",
            "=" * 40,
            f"Ticker     : {cfg.data.ticker}",
            f"Date range : {cfg.data.start_date} -> {cfg.data.end_date}",
            f"Restarts   : {cfg.ga.n_restarts}",
            f"Generations: {cfg.ga.n_generations}",
            f"Elapsed    : {h_elapsed_save}",
            f"Best fitness: {best['best_fitness']:.4f}",
            f"Run ID     : {run_id}",
        ]
        summary_path = _Path(results_dir) / "optimization_summary.txt"
        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    # 12. Completion message
    h_elapsed = str(elapsed).split(".")[0]
    click.echo(f"Optimization complete! ({h_elapsed})")
    click.echo()
    click.echo(f"Saved: {results_dir}/best_individual.yaml")
    click.echo(f"Saved: {results_dir}/strategy.py")
    click.echo(f"Saved: {results_dir}/optimization_summary.txt")
    click.echo(f"Saved: {results_dir}/{run_id}/convergence_*.csv")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Validate:  ga-trading-sys validate --results {results_dir}/")
    click.echo(
        f"  2. Backtest:  ga-trading-sys backtest "
        f"--individual {results_dir}/best_individual.yaml"
    )


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--results", "-r", required=True, help="Path to results directory.")
@click.option(
    "--individual", "-i", default=None,
    help="Optional path to an individual YAML (overrides best in results dir).",
)
def validate(results: str, individual: str | None) -> None:
    """Validate and summarise performance from a results directory."""
    results_path = Path(results)
    if not results_path.exists():
        click.echo(f"Results directory not found: {results}", err=True)
        sys.exit(1)

    ind_path: Path | None = None
    if individual:
        ind_path = Path(individual)
        if not ind_path.exists():
            click.echo(f"Individual YAML not found: {individual}", err=True)
            sys.exit(1)

    click.echo(f"Results directory : {results_path.resolve()}")
    if ind_path:
        click.echo(f"Individual file   : {ind_path.resolve()}")

    # List CSV reports
    csvs = list(results_path.glob("*.csv"))
    if csvs:
        click.echo(f"\nFound {len(csvs)} report(s):")
        for csv_path in csvs:
            click.echo(f"  {csv_path.name}")
    else:
        click.echo("\nNo CSV reports found in results directory.")


# ---------------------------------------------------------------------------
# backtest
# ---------------------------------------------------------------------------

@cli.command()
@click.option(
    "--individual", "-i", required=True,
    help="Path to individual YAML produced by export_strategy_yaml.",
)
@click.option("--config", "-c", default=None, help="Optional config YAML to get data settings.")
def backtest(individual: str, config: str | None) -> None:
    """Replay a saved individual and print a performance report."""
    from src.export.codegen import load_strategy_yaml
    from src.export.reporter import build_report, format_text

    ind_path = Path(individual)
    if not ind_path.exists():
        click.echo(f"Individual YAML not found: {individual}", err=True)
        sys.exit(1)

    ind = load_strategy_yaml(ind_path)
    click.echo(f"Loaded individual: {ind_path.name}  ({len(ind)} genes)")

    if config:
        from src.config import load_config
        cfg = load_config(config)
        ticker     = cfg.data.ticker
        start_date = cfg.data.start_date
        end_date   = cfg.data.end_date
        warmup     = cfg.backtest.warmup_bars
        norm_win   = cfg.backtest.normalization_window
    else:
        ticker     = "SPY"
        start_date = "2010-01-01"
        end_date   = "2024-12-31"
        warmup     = 252
        norm_win   = 252

    click.echo(f"Data: {ticker}  {start_date} → {end_date}")
    click.echo("Downloading data and running backtest …")

    try:
        import numpy as np
        from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
        from src.data.loader import load_market_data
        from src.ga.chromosome import IDX_STOP_LOSS_PCT, IDX_TAKE_PROFIT_PCT, IDX_POSITION_SIZE_MULT
        from src.indicators.calculator import build_indicator_cache
        from src.indicators.signal_generator import generate_signals_weighted_sum

        df = load_market_data(ticker, start_date, end_date)
        warmup_jit()
        engine = NumbaBacktestEngine()

        cache = build_indicator_cache(df, normalization_window=norm_win)
        sliced = {k: v[warmup:] for k, v in cache.items()}
        prices = df["close"].values[warmup:].astype(np.float32)

        signals = generate_signals_weighted_sum(ind, sliced)
        result = engine.run(signals, prices, float(ind[IDX_STOP_LOSS_PCT]), float(ind[IDX_TAKE_PROFIT_PCT]), float(ind[IDX_POSITION_SIZE_MULT]))
        report = build_report(result)
        click.echo()
        click.echo(format_text(report))

    except Exception as exc:
        click.echo(f"\nBacktest failed: {exc}", err=True)
        sys.exit(1)
