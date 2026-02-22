"""Pydantic v2 configuration schema for GA-Trading-Sys.

Load from YAML::

    config = GAConfig.from_yaml("config/spy_mvp.yaml")

All models are frozen — mutation after construction raises ``ValidationError``.
"""

from __future__ import annotations

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
