"""Pydantic v2 configuration schema for GA-Trading-Sys.

Load from YAML::

    config = GAConfig.from_yaml("config/spy_mvp.yaml")
    # or using the top-level OptimizationConfig:
    config = load_config("config/spy_mvp.yaml")

All models are frozen — mutation after construction raises ``ValidationError``.
"""

from __future__ import annotations

import os
import textwrap
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class DataConfig(BaseModel, frozen=True):
    """Market data acquisition and caching settings."""

    ticker: str = "SPY"
    start_date: str = "2010-01-01"
    end_date: str = "2025-12-31"
    cache_dir: str = "data/cache"


class GAConfig(BaseModel, frozen=True):
    """Top-level configuration for a GA optimization run.

    Attributes:
        data: Ticker, date range, and cache location.
        population_size: Individuals per generation (GSBsys default: 200).
        n_generations: Generations per restart (GSBsys default: 1000).
        n_restarts: Independent restarts with different seeds (default: 10).
        cxpb: Crossover probability (GSBsys target: 0.95).
        mutpb: Mutation probability (GSBsys target: 0.05).
        tournsize: Tournament selection size.
        n_indicators: Indicator slots per chromosome (3 for Phase 1).
        train_ratio: Fraction of bars used for training (sequential split).
        warmup_bars: Bars discarded for indicator warm-up (252 = 1 trading year).
        min_trades: Fast-exit threshold — individuals with fewer trades score 0.
        pearson_threshold: Minimum train/test equity curve correlation.
        n_workers: Parallel processes for restart pool.
        random_seed: Master seed; restart seeds derived deterministically.
        results_dir: Output directory for convergence CSVs and best individuals.
    """

    data: DataConfig = Field(default_factory=DataConfig)

    # GA parameters
    population_size: int = Field(default=200, ge=10, le=10_000)
    n_generations: int = Field(default=1000, ge=1, le=100_000)
    n_restarts: int = Field(default=10, ge=1, le=100)
    cxpb: float = Field(default=0.95, ge=0.0, le=1.0)
    mutpb: float = Field(default=0.05, ge=0.0, le=1.0)
    tournsize: int = Field(default=3, ge=2, le=20)

    # Chromosome
    n_indicators: int = Field(default=3, ge=1, le=5)

    # Fitness / train-test
    train_ratio: float = Field(default=0.4, ge=0.1, le=0.9)
    warmup_bars: int = Field(default=252, ge=0)
    min_trades: int = Field(default=5, ge=1)
    pearson_threshold: float = Field(default=0.85, ge=0.0, le=1.0)

    # Execution
    n_workers: int = Field(default=8, ge=1, le=64)
    random_seed: int = Field(default=42, ge=0)

    # Output
    results_dir: str = "results"

    @classmethod
    def from_yaml(cls, path: str | Path) -> "GAConfig":
        """Load and validate configuration from a YAML file.

        Args:
            path: Path to the YAML config file.

        Returns:
            Validated, frozen ``GAConfig`` instance.

        Raises:
            FileNotFoundError: If *path* does not exist.
            pydantic.ValidationError: If any field fails validation.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path) as f:
            raw = yaml.safe_load(f)
        return cls.model_validate(raw or {})


# ---------------------------------------------------------------------------
# Phase 4: Extended top-level config
# ---------------------------------------------------------------------------

class BacktestConfig(BaseModel, frozen=True):
    """Backtest and indicator override settings."""

    warmup_bars:          int            = Field(default=252, ge=0)
    normalization_window: int            = Field(default=252, ge=1)
    train_fraction:       float          = Field(default=0.40, ge=0.05, le=0.95)
    stop_loss_pct:        Optional[float] = Field(default=None, ge=0.001, le=0.50)
    take_profit_pct:      Optional[float] = Field(default=None, ge=0.001, le=1.00)
    position_size_mult:   Optional[float] = Field(default=None, ge=0.01, le=10.0)


class OutputConfig(BaseModel, frozen=True):
    """Output file settings."""

    dir:          str  = "results"
    save_code:    bool = True
    save_plots:   bool = True
    save_reports: bool = True


class OptimizationConfig(BaseModel, frozen=True):
    """Full optimization configuration (top-level YAML schema).

    Example YAML::

        data:
          ticker: SPY
          start_date: "2010-01-01"
          end_date: "2024-12-31"
        ga:
          population_size: 200
          n_generations: 1000
          n_restarts: 10
        backtest:
          train_fraction: 0.40
        output:
          dir: results
    """

    data:     DataConfig     = Field(default_factory=DataConfig)
    ga:       GAConfig       = Field(default_factory=GAConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    output:   OutputConfig   = Field(default_factory=OutputConfig)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def load_config(path: str) -> OptimizationConfig:
    """Load an OptimizationConfig from a YAML file.

    Args:
        path: Path to the YAML config file.

    Returns:
        Validated OptimizationConfig instance.

    Raises:
        FileNotFoundError: If *path* does not exist.
        pydantic.ValidationError: If the YAML content is invalid.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(p, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return OptimizationConfig.model_validate(raw)


def save_config(config: OptimizationConfig, path: str) -> None:
    """Serialise an OptimizationConfig to a YAML file.

    Args:
        config: Config instance to save.
        path:   Destination path (parent dirs created if needed).
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(config.model_dump(), fh, default_flow_style=False, sort_keys=False)


def default_config_yaml() -> str:
    """Return a commented YAML template string for `ga-trading-sys init`."""
    return textwrap.dedent("""\
        # GA-Trading-Sys configuration
        # Run: ga-trading-sys optimize --config this_file.yaml

        data:
          ticker: SPY               # yfinance ticker symbol
          start_date: "2010-01-01"
          end_date:   "2024-12-31"
          cache_dir:  data/cache

        ga:
          population_size: 200      # individuals per generation
          n_generations:   1000     # GA generations per restart
          n_restarts:      10       # independent restarts
          seed:            42       # master random seed
          use_lhs:         true

        backtest:
          warmup_bars:          252
          normalization_window: 252
          train_fraction:       0.40  # 40% train / 60% test
          stop_loss_pct:        null  # null = use GA-evolved value
          take_profit_pct:      null
          position_size_mult:   null

        output:
          dir:          results
          save_code:    true
          save_plots:   true
          save_reports: true
    """)
