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
def optimize(config: str, output: str | None) -> None:
    """Run GA optimisation from a config file."""
    from src.config import load_config

    cfg = load_config(config)
    results_dir = output or cfg.output.dir

    click.echo(f"Config  : {config}")
    click.echo(f"Ticker  : {cfg.data.ticker}")
    click.echo(f"Dates   : {cfg.data.start_date} → {cfg.data.end_date}")
    click.echo(f"GA      : pop={cfg.ga.population_size}  gen={cfg.ga.n_generations}"
               f"  restarts={cfg.ga.n_restarts}")
    click.echo(f"Results : {results_dir}")
    click.echo()
    click.echo("Note: full GA optimisation requires the GA runner (Phase 1-2 engine).")
    click.echo("This command validates the config and shows run parameters.")


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
        from src.indicators.calculator import build_indicator_cache
        from src.indicators.signal_generator import generate_signals_weighted_sum

        df = load_market_data(ticker, start_date, end_date)
        warmup_jit()
        engine = NumbaBacktestEngine()

        cache = build_indicator_cache(df, normalization_window=norm_win)
        sliced = {k: v[warmup:] for k, v in cache.items()}
        prices = df["close"].values[warmup:].astype(np.float32)

        signals = generate_signals_weighted_sum(ind, sliced)
        result = engine.run(signals, prices, float(ind[10]), float(ind[11]), float(ind[12]))
        report = build_report(result)
        click.echo()
        click.echo(format_text(report))

    except Exception as exc:
        click.echo(f"\nBacktest failed: {exc}", err=True)
        sys.exit(1)
