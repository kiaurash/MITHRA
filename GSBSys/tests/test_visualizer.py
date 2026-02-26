"""Tests for src/export/visualizer.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.export.visualizer import plot_equity_curves, plot_regime_performance


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _equity(n: int = 100, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return (10_000 + np.cumsum(rng.normal(0, 50, n))).astype(np.float32)


def _make_regime_result() -> MagicMock:
    """Build a mock RegimeTestResult with required attributes."""
    from src.robustness.regime_classifier import RegimeLabel, RegimePerformance

    bull_perf = RegimePerformance(
        label=RegimeLabel.BULL, n_bars=50, profit_factor=1.8,
        total_return_pct=5.0, profitable=True,
    )
    bear_perf = RegimePerformance(
        label=RegimeLabel.BEAR, n_bars=30, profit_factor=0.7,
        total_return_pct=-3.0, profitable=False,
    )
    side_perf = RegimePerformance(
        label=RegimeLabel.SIDEWAYS, n_bars=70, profit_factor=1.1,
        total_return_pct=1.0, profitable=True,
    )
    result = MagicMock()
    result.bull     = bull_perf
    result.bear     = bear_perf
    result.sideways = side_perf
    return result


# ---------------------------------------------------------------------------
# plot_equity_curves
# ---------------------------------------------------------------------------

class TestPlotEquityCurves:
    def test_runs_without_error(self):
        plot_equity_curves(_equity(), _equity(seed=1))

    def test_saves_png_to_file(self, tmp_path):
        path = tmp_path / "equity.png"
        plot_equity_curves(_equity(), _equity(seed=1), save_path=str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "equity.png"
        plot_equity_curves(_equity(), _equity(seed=1), save_path=str(path))
        assert path.exists()

    def test_custom_title_accepted(self):
        plot_equity_curves(_equity(), _equity(seed=1), title="My Strategy")

    def test_single_bar_equity(self):
        """Edge case: 1-element array should not crash."""
        plot_equity_curves(
            np.array([10_000.0], dtype=np.float32),
            np.array([10_000.0], dtype=np.float32),
        )

    def test_large_equity(self, tmp_path):
        path = tmp_path / "large.png"
        plot_equity_curves(_equity(500), _equity(500, seed=5), save_path=str(path))
        assert path.exists()


# ---------------------------------------------------------------------------
# plot_regime_performance
# ---------------------------------------------------------------------------

class TestPlotRegimePerformance:
    def test_runs_without_error(self):
        result = _make_regime_result()
        plot_regime_performance(result)

    def test_saves_png_to_file(self, tmp_path):
        path = tmp_path / "regime.png"
        result = _make_regime_result()
        plot_regime_performance(result, save_path=str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "sub" / "regime.png"
        result = _make_regime_result()
        plot_regime_performance(result, save_path=str(path))
        assert path.exists()

    def test_infinite_pf_does_not_crash(self):
        """Bull with infinite PF should be capped gracefully."""
        from src.robustness.regime_classifier import RegimeLabel, RegimePerformance

        bull_perf = RegimePerformance(
            label=RegimeLabel.BULL, n_bars=50, profit_factor=float("inf"),
            total_return_pct=10.0, profitable=True,
        )
        bear_perf = RegimePerformance(
            label=RegimeLabel.BEAR, n_bars=30, profit_factor=0.5,
            total_return_pct=-2.0, profitable=False,
        )
        side_perf = RegimePerformance(
            label=RegimeLabel.SIDEWAYS, n_bars=70, profit_factor=1.0,
            total_return_pct=0.0, profitable=True,
        )
        result = MagicMock()
        result.bull = bull_perf
        result.bear = bear_perf
        result.sideways = side_perf
        plot_regime_performance(result)
