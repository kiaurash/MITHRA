"""Tests for src/cli/commands.py — Click CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import yaml
from click.testing import CliRunner

from src.cli.commands import cli


# ---------------------------------------------------------------------------
# Helpers — shared
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


def _write_config_yaml(tmp_path: Path, output_dir: str | None = None) -> str:
    path = tmp_path / "config.yaml"
    content = {
        "data": {"ticker": "SPY", "start_date": "2010-01-01", "end_date": "2024-12-31"},
        "ga": {"population_size": 50},
        "backtest": {"train_fraction": 0.40},
        "output": {"dir": output_dir or str(tmp_path / "results")},
    }
    with open(path, "w") as f:
        yaml.dump(content, f)
    return str(path)


# ---------------------------------------------------------------------------
# Helpers — optimize mocks
# ---------------------------------------------------------------------------

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


def _make_mock_df(n_bars: int = 600) -> pd.DataFrame:
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars),
        "open":   np.ones(n_bars) * 100.0,
        "high":   np.ones(n_bars) * 101.0,
        "low":    np.ones(n_bars) * 99.0,
        "close":  np.ones(n_bars, dtype=np.float32) * 100.0,
        "volume": np.ones(n_bars) * 1_000_000.0,
    })


def _make_mock_cache(n_bars: int = 600) -> dict:
    return {"mock_0_10": np.zeros(n_bars, dtype=np.float32)}


def _run_optimize(
    cli_args: list,
    *,
    n_restarts: int = 1,
    n_bars: int = 600,
    results: list | None = None,
) -> "CliRunner":
    """Invoke optimize CLI command with all heavy dependencies mocked."""
    mock_df = _make_mock_df(n_bars)
    mock_cache = _make_mock_cache(n_bars)
    mock_results = results if results is not None else _make_restart_results(n_restarts)
    with (
        patch("src.data.loader.load_market_data", return_value=mock_df),
        patch("src.backtesting.numba_engine.warmup_jit"),
        patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=MagicMock()),
        patch("src.indicators.calculator.build_indicator_cache", return_value=mock_cache),
        patch("src.utils.parallel.run_restarts_parallel", return_value=mock_results),
        patch("src.utils.parallel.run_restarts_sequential", return_value=mock_results),
        patch("src.utils.seed.make_restart_seeds", return_value=list(range(n_restarts))),
    ):
        return _runner().invoke(cli, cli_args)


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

    def test_missing_config_file_raises(self):
        result = _runner().invoke(cli, ["optimize", "--config", "nonexistent.yaml"])
        assert result.exit_code != 0

    def test_runs_with_valid_config(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _run_optimize(["optimize", "--config", cfg_path])
        assert result.exit_code == 0

    def test_shows_ticker(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _run_optimize(["optimize", "--config", cfg_path])
        assert "SPY" in result.output

    def test_shows_results_dir(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        result = _run_optimize(["optimize", "--config", cfg_path])
        assert "results" in result.output

    def test_output_override(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        out_dir = str(tmp_path / "my_out")
        result = _run_optimize(["optimize", "--config", cfg_path, "--output", out_dir])
        assert "my_out" in result.output

    # --- New behaviour tests ---

    def test_saves_best_individual_yaml(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        out_dir = str(tmp_path / "results")
        _run_optimize(["optimize", "--config", cfg_path, "--output", out_dir])
        assert (tmp_path / "results" / "best_individual.yaml").exists()

    def test_saves_strategy_py(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        out_dir = str(tmp_path / "results")
        _run_optimize(["optimize", "--config", cfg_path, "--output", out_dir])
        assert (tmp_path / "results" / "strategy.py").exists()

    def test_saves_optimization_summary(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        out_dir = str(tmp_path / "results")
        _run_optimize(["optimize", "--config", cfg_path, "--output", out_dir])
        assert (tmp_path / "results" / "optimization_summary.txt").exists()

    def test_saves_config_copy(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        out_dir = str(tmp_path / "results")
        _run_optimize(["optimize", "--config", cfg_path, "--output", out_dir])
        assert (tmp_path / "results" / "config.yaml").exists()

    def test_shows_best_marker(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        results = _make_restart_results(3)
        result = _run_optimize(
            ["optimize", "--config", cfg_path], n_restarts=3, results=results
        )
        assert "<- BEST" in result.output

    def test_sequential_flag_uses_sequential_runner(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        mock_df = _make_mock_df()
        mock_cache = _make_mock_cache()
        mock_results = _make_restart_results(1)
        with (
            patch("src.data.loader.load_market_data", return_value=mock_df),
            patch("src.backtesting.numba_engine.warmup_jit"),
            patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=MagicMock()),
            patch("src.indicators.calculator.build_indicator_cache", return_value=mock_cache),
            patch("src.utils.parallel.run_restarts_parallel", return_value=mock_results) as mock_par,
            patch("src.utils.parallel.run_restarts_sequential", return_value=mock_results) as mock_seq,
            patch("src.utils.seed.make_restart_seeds", return_value=[42]),
        ):
            result = _runner().invoke(cli, ["optimize", "--config", cfg_path, "--sequential"])
            assert result.exit_code == 0
            mock_seq.assert_called_once()
            mock_par.assert_not_called()

    def test_interrupt_exits_130(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        mock_df = _make_mock_df()
        mock_cache = _make_mock_cache()
        with (
            patch("src.data.loader.load_market_data", return_value=mock_df),
            patch("src.backtesting.numba_engine.warmup_jit"),
            patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=MagicMock()),
            patch("src.indicators.calculator.build_indicator_cache", return_value=mock_cache),
            patch("src.utils.parallel.run_restarts_parallel", side_effect=KeyboardInterrupt),
            patch("src.utils.seed.make_restart_seeds", return_value=[42]),
        ):
            result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
            assert result.exit_code == 130

    def test_no_profitable_warning(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        bad_results = _make_restart_results(1)
        bad_results[0]["best_fitness"] = -1.0
        result = _run_optimize(["optimize", "--config", cfg_path], results=bad_results)
        # CliRunner mixes stderr into output by default
        assert "Warning" in result.output

    def test_insufficient_data_exits(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        # 10 bars — well below warmup_bars (252) + 200 = 452
        tiny_df = _make_mock_df(10)
        with (
            patch("src.data.loader.load_market_data", return_value=tiny_df),
            patch("src.backtesting.numba_engine.warmup_jit"),
            patch("src.backtesting.numba_engine.NumbaBacktestEngine", return_value=MagicMock()),
        ):
            result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
            assert result.exit_code == 1

    def test_download_failure_exits(self, tmp_path):
        cfg_path = _write_config_yaml(tmp_path)
        with patch("src.data.loader.load_market_data", side_effect=RuntimeError("network down")):
            result = _runner().invoke(cli, ["optimize", "--config", cfg_path])
            assert result.exit_code == 1


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
