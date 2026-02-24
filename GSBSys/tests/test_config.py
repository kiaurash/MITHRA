"""Tests for src/config.py — Pydantic v2 schema and helpers."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.config import (
    BacktestConfig,
    DataConfig,
    GAConfig,
    OptimizationConfig,
    OutputConfig,
    default_config_yaml,
    load_config,
    save_config,
)


# ---------------------------------------------------------------------------
# DataConfig
# ---------------------------------------------------------------------------

class TestDataConfig:
    def test_defaults(self):
        d = DataConfig()
        assert d.ticker == "SPY"
        assert d.start_date == "2010-01-01"
        assert d.end_date == "2025-12-31"
        assert d.cache_dir == "data/cache"

    def test_custom_values(self):
        d = DataConfig(ticker="QQQ", start_date="2015-01-01", end_date="2024-12-31")
        assert d.ticker == "QQQ"
        assert d.start_date == "2015-01-01"

    def test_frozen(self):
        d = DataConfig()
        with pytest.raises((ValidationError, TypeError)):
            d.ticker = "AAPL"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GAConfig
# ---------------------------------------------------------------------------

class TestGAConfig:
    def test_defaults(self):
        g = GAConfig()
        assert g.population_size == 200
        assert g.n_generations == 1000
        assert g.n_restarts == 10
        assert g.cxpb == 0.95
        assert g.mutpb == 0.05

    def test_population_size_bounds(self):
        with pytest.raises(ValidationError):
            GAConfig(population_size=9)   # below ge=10
        with pytest.raises(ValidationError):
            GAConfig(population_size=10_001)  # above le=10_000

    def test_cxpb_bounds(self):
        with pytest.raises(ValidationError):
            GAConfig(cxpb=1.1)
        with pytest.raises(ValidationError):
            GAConfig(cxpb=-0.1)

    def test_n_indicators_bounds(self):
        with pytest.raises(ValidationError):
            GAConfig(n_indicators=0)
        with pytest.raises(ValidationError):
            GAConfig(n_indicators=6)

    def test_frozen(self):
        g = GAConfig()
        with pytest.raises((ValidationError, TypeError)):
            g.population_size = 100  # type: ignore[misc]

    def test_from_yaml_classmethod(self, tmp_path):
        yaml_content = "population_size: 50\nn_generations: 500\n"
        p = tmp_path / "ga.yaml"
        p.write_text(yaml_content)
        g = GAConfig.from_yaml(p)
        assert g.population_size == 50
        assert g.n_generations == 500

    def test_from_yaml_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            GAConfig.from_yaml("nonexistent_file.yaml")


# ---------------------------------------------------------------------------
# BacktestConfig
# ---------------------------------------------------------------------------

class TestBacktestConfig:
    def test_defaults(self):
        b = BacktestConfig()
        assert b.warmup_bars == 252
        assert b.normalization_window == 252
        assert b.train_fraction == pytest.approx(0.40)
        assert b.stop_loss_pct is None
        assert b.take_profit_pct is None
        assert b.position_size_mult is None

    def test_train_fraction_bounds(self):
        with pytest.raises(ValidationError):
            BacktestConfig(train_fraction=0.04)   # below ge=0.05
        with pytest.raises(ValidationError):
            BacktestConfig(train_fraction=0.96)   # above le=0.95

    def test_stop_loss_bounds(self):
        with pytest.raises(ValidationError):
            BacktestConfig(stop_loss_pct=0.0)     # below ge=0.001
        with pytest.raises(ValidationError):
            BacktestConfig(stop_loss_pct=0.51)    # above le=0.50

    def test_optional_fields_set(self):
        b = BacktestConfig(stop_loss_pct=0.05, take_profit_pct=0.10, position_size_mult=2.0)
        assert b.stop_loss_pct == pytest.approx(0.05)
        assert b.take_profit_pct == pytest.approx(0.10)
        assert b.position_size_mult == pytest.approx(2.0)

    def test_frozen(self):
        b = BacktestConfig()
        with pytest.raises((ValidationError, TypeError)):
            b.warmup_bars = 100  # type: ignore[misc]


# ---------------------------------------------------------------------------
# OutputConfig
# ---------------------------------------------------------------------------

class TestOutputConfig:
    def test_defaults(self):
        o = OutputConfig()
        assert o.dir == "results"
        assert o.save_code is True
        assert o.save_plots is True
        assert o.save_reports is True

    def test_custom(self):
        o = OutputConfig(dir="out", save_plots=False)
        assert o.dir == "out"
        assert o.save_plots is False

    def test_frozen(self):
        o = OutputConfig()
        with pytest.raises((ValidationError, TypeError)):
            o.dir = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# OptimizationConfig
# ---------------------------------------------------------------------------

class TestOptimizationConfig:
    def test_defaults(self):
        c = OptimizationConfig()
        assert isinstance(c.data, DataConfig)
        assert isinstance(c.ga, GAConfig)
        assert isinstance(c.backtest, BacktestConfig)
        assert isinstance(c.output, OutputConfig)

    def test_nested_override(self):
        c = OptimizationConfig(data=DataConfig(ticker="TSLA"))
        assert c.data.ticker == "TSLA"

    def test_frozen(self):
        c = OptimizationConfig()
        with pytest.raises((ValidationError, TypeError)):
            c.data = DataConfig()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_config / save_config
# ---------------------------------------------------------------------------

class TestLoadSaveConfig:
    def _write_yaml(self, tmp_path, content: dict) -> str:
        p = tmp_path / "config.yaml"
        with open(p, "w") as f:
            yaml.dump(content, f)
        return str(p)

    def test_load_empty_yaml_uses_defaults(self, tmp_path):
        p = tmp_path / "empty.yaml"
        p.write_text("")
        c = load_config(str(p))
        assert c.data.ticker == "SPY"

    def test_load_partial_yaml(self, tmp_path):
        content = {"data": {"ticker": "QQQ"}}
        path = self._write_yaml(tmp_path, content)
        c = load_config(path)
        assert c.data.ticker == "QQQ"
        assert c.ga.population_size == 200  # default

    def test_load_full_yaml(self, tmp_path):
        content = {
            "data": {"ticker": "IWM", "start_date": "2015-01-01", "end_date": "2024-12-31"},
            "ga": {"population_size": 100, "n_generations": 500},
            "backtest": {"train_fraction": 0.50},
            "output": {"dir": "my_results"},
        }
        path = self._write_yaml(tmp_path, content)
        c = load_config(path)
        assert c.data.ticker == "IWM"
        assert c.ga.population_size == 100
        assert c.backtest.train_fraction == pytest.approx(0.50)
        assert c.output.dir == "my_results"

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("does_not_exist.yaml")

    def test_save_then_load_roundtrip(self, tmp_path):
        c = OptimizationConfig(
            data=DataConfig(ticker="GLD"),
            ga=GAConfig(population_size=50),
            backtest=BacktestConfig(train_fraction=0.60),
        )
        path = str(tmp_path / "roundtrip.yaml")
        save_config(c, path)
        loaded = load_config(path)
        assert loaded.data.ticker == "GLD"
        assert loaded.ga.population_size == 50
        assert loaded.backtest.train_fraction == pytest.approx(0.60)

    def test_save_creates_parent_dirs(self, tmp_path):
        c = OptimizationConfig()
        path = str(tmp_path / "nested" / "dir" / "config.yaml")
        save_config(c, path)
        assert Path(path).exists()

    def test_load_invalid_field_raises(self, tmp_path):
        content = {"ga": {"population_size": -1}}  # below ge=10
        path = self._write_yaml(tmp_path, content)
        with pytest.raises(ValidationError):
            load_config(path)


# ---------------------------------------------------------------------------
# default_config_yaml
# ---------------------------------------------------------------------------

class TestDefaultConfigYaml:
    def test_returns_string(self):
        result = default_config_yaml()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parseable_yaml(self):
        result = default_config_yaml()
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, dict)

    def test_contains_expected_sections(self):
        result = default_config_yaml()
        assert "data" in result
        assert "ga" in result
        assert "backtest" in result
        assert "output" in result

    def test_ticker_in_output(self):
        result = default_config_yaml()
        assert "SPY" in result
