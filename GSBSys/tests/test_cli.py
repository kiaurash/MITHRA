"""Tests for src/cli/commands.py — Click CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import yaml
from click.testing import CliRunner

from src.cli.commands import cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _runner() -> CliRunner:
    return CliRunner()


def _make_individual() -> list:
    return [0, 14, 1.2, 5, 9, 0.8, 13, 20, 1.0, 0.3, 0.04, 0.08, 1.0]


def _write_individual_yaml(tmp_path: Path) -> str:
    from src.export.codegen import export_strategy_yaml
    path = str(tmp_path / "individual.yaml")
    export_strategy_yaml(_make_individual(), path)
    return path


def _write_config_yaml(tmp_path: Path) -> str:
    path = tmp_path / "config.yaml"
    content = {
        "data": {"ticker": "SPY", "start_date": "2010-01-01", "end_date": "2024-12-31"},
        "ga": {"population_size": 50},
        "backtest": {"train_fraction": 0.40},
        "output": {"dir": "results"},
    }
    with open(path, "w") as f:
        yaml.dump(content, f)
    return str(path)


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

class TestCliRoot:
    def test_help_exits_zero(self):
        r = _runner()
        result = r.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "GA Trading System" in result.output

    def test_no_args_shows_usage(self):
        r = _runner()
        result = r.invoke(cli, [])
        # Click groups show usage text (exit 0 or 2 depending on version)
        assert result.exit_code in (0, 2)


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

class TestInitCommand:
    def test_creates_config_file(self, tmp_path):
        path = str(tmp_path / "cfg.yaml")
        result = _runner().invoke(cli, ["init", "--output", path])
        assert result.exit_code == 0
        assert Path(path).exists()

    def test_output_contains_path(self, tmp_path):
        path = str(tmp_path / "cfg.yaml")
        result = _runner().invoke(cli, ["init", "--output", path])
        assert "cfg.yaml" in result.output

    def test_created_file_is_valid_yaml(self, tmp_path):
        path = str(tmp_path / "cfg.yaml")
        _runner().invoke(cli, ["init", "--output", path])
        with open(path) as f:
            parsed = yaml.safe_load(f)
        assert isinstance(parsed, dict)
        assert "data" in parsed
        assert "ga" in parsed

    def test_existing_file_exits_nonzero(self, tmp_path):
        path = str(tmp_path / "cfg.yaml")
        Path(path).write_text("existing: content")
        result = _runner().invoke(cli, ["init", "--output", path])
        assert result.exit_code != 0

    def test_default_output_name(self, tmp_path):
        # Run in a temp dir so we don't pollute CWD
        with _runner().isolated_filesystem(temp_dir=tmp_path):
            result = _runner().invoke(cli, ["init"])
            assert result.exit_code == 0
            assert Path("config.yaml").exists()

    def test_creates_parent_dirs(self, tmp_path):
        path = str(tmp_path / "sub" / "dir" / "cfg.yaml")
        result = _runner().invoke(cli, ["init", "--output", path])
        assert result.exit_code == 0
        assert Path(path).exists()


# ---------------------------------------------------------------------------
# optimize
# ---------------------------------------------------------------------------

class TestOptimizeCommand:
    def test_requires_config(self):
        result = _runner().invoke(cli, ["optimize"])
        assert result.exit_code != 0

    def test_runs_with_valid_config(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
        assert result.exit_code == 0

    def test_shows_ticker(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
        assert "SPY" in result.output

    def test_shows_results_dir(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
        assert "results" in result.output

    def test_output_override(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _runner().invoke(cli, ["optimize", "--config", cfg_path, "--output", "my_out"])
        assert "my_out" in result.output

    def test_missing_config_file_raises(self, tmp_path):
        result = _runner().invoke(cli, ["optimize", "--config", "nonexistent.yaml"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidateCommand:
    def test_requires_results(self):
        result = _runner().invoke(cli, ["validate"])
        assert result.exit_code != 0

    def test_missing_results_dir_exits_nonzero(self, tmp_path):
        result = _runner().invoke(cli, ["validate", "--results", str(tmp_path / "nope")])
        assert result.exit_code != 0

    def test_empty_results_dir_exits_zero(self, tmp_path):
        result = _runner().invoke(cli, ["validate", "--results", str(tmp_path)])
        assert result.exit_code == 0

    def test_shows_results_path(self, tmp_path):
        result = _runner().invoke(cli, ["validate", "--results", str(tmp_path)])
        assert result.exit_code == 0
        assert str(tmp_path.name) in result.output

    def test_lists_csv_reports(self, tmp_path):
        (tmp_path / "report.csv").write_text("profit_factor\n1.5\n")
        result = _runner().invoke(cli, ["validate", "--results", str(tmp_path)])
        assert "report.csv" in result.output

    def test_individual_yaml_flag(self, tmp_path):
        ind_path = _write_individual_yaml(tmp_path)
        result = _runner().invoke(
            cli, ["validate", "--results", str(tmp_path), "--individual", ind_path]
        )
        assert result.exit_code == 0
        assert "individual.yaml" in result.output

    def test_missing_individual_exits_nonzero(self, tmp_path):
        result = _runner().invoke(
            cli, ["validate", "--results", str(tmp_path), "--individual", "nope.yaml"]
        )
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# backtest
# ---------------------------------------------------------------------------

class TestBacktestCommand:
    def test_requires_individual(self):
        result = _runner().invoke(cli, ["backtest"])
        assert result.exit_code != 0

    def test_missing_individual_file_exits_nonzero(self, tmp_path):
        result = _runner().invoke(cli, ["backtest", "--individual", "nope.yaml"])
        assert result.exit_code != 0

    def test_loads_individual_and_shows_gene_count(self, tmp_path):
        """backtest shows gene count before trying network calls."""
        ind_path = _write_individual_yaml(tmp_path)
        # Patch load_market_data to avoid network access
        equity = np.linspace(10_000, 10_500, 101).astype(np.float32)
        returns = np.diff(equity) / equity[:-1]
        mock_result = MagicMock()
        mock_result.sharpe_ratio = 1.0
        mock_result.profit_factor = 1.5
        mock_result.n_trades = 20
        mock_result.total_pnl = 500.0
        mock_result.avg_trade_pnl = 25.0
        mock_result.equity_curve = equity
        mock_result.returns = returns

        mock_engine = MagicMock()
        mock_engine.run.return_value = mock_result

        with (
            patch("src.data.loader.load_market_data") as mock_load,
            patch("src.backtesting.numba_engine.warmup_jit"),
            patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=mock_engine),
        ):
            import pandas as pd
            n_bars = 500
            mock_df = pd.DataFrame({
                "date":   pd.date_range("2010-01-01", periods=n_bars),
                "open":   np.ones(n_bars) * 100.0,
                "high":   np.ones(n_bars) * 101.0,
                "low":    np.ones(n_bars) * 99.0,
                "close":  np.ones(n_bars, dtype=np.float32) * 100.0,
                "volume": np.ones(n_bars) * 1_000_000.0,
            })
            mock_load.return_value = mock_df

            result = _runner().invoke(cli, ["backtest", "--individual", ind_path])

        assert "13 genes" in result.output

    def test_backtest_with_config(self, tmp_path):
        """backtest accepts --config flag."""
        ind_path = _write_individual_yaml(tmp_path)
        cfg_path = _write_config_yaml(tmp_path)

        equity = np.linspace(10_000, 11_000, 101).astype(np.float32)
        returns = np.diff(equity) / equity[:-1]
        mock_result = MagicMock()
        mock_result.sharpe_ratio = 1.5
        mock_result.profit_factor = 1.8
        mock_result.n_trades = 30
        mock_result.total_pnl = 1000.0
        mock_result.avg_trade_pnl = 33.3
        mock_result.equity_curve = equity
        mock_result.returns = returns

        mock_engine = MagicMock()
        mock_engine.run.return_value = mock_result

        with (
            patch("src.data.loader.load_market_data") as mock_load,
            patch("src.backtesting.numba_engine.warmup_jit"),
            patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=mock_engine),
        ):
            import pandas as pd
            n_bars = 500
            mock_df = pd.DataFrame({
                "date":   pd.date_range("2010-01-01", periods=n_bars),
                "open":   np.ones(n_bars) * 100.0,
                "high":   np.ones(n_bars) * 101.0,
                "low":    np.ones(n_bars) * 99.0,
                "close":  np.ones(n_bars, dtype=np.float32) * 100.0,
                "volume": np.ones(n_bars) * 1_000_000.0,
            })
            mock_load.return_value = mock_df

            result = _runner().invoke(
                cli, ["backtest", "--individual", ind_path, "--config", cfg_path]
            )

        assert result.exit_code == 0
        assert "SPY" in result.output
