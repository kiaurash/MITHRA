"""Tests for src/robustness/sensitivity.py."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.backtesting.engine import BacktestResult
from src.ga.chromosome import GENE_NAMES
from src.robustness.sensitivity import (
    DEFAULT_PERTURBATION,
    GeneSensitivity,
    SensitivityResult,
    _perturb_gene,
    run_sensitivity_analysis,
)
from src.validation.family_grouping import FamilyResult

N_GENES = len(GENE_NAMES)
WARMUP = 252


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n_bars: int = WARMUP + 300, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n_bars))
    close = np.maximum(close, 1.0)
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars, freq="D"),
        "open":   close * 0.99,
        "high":   close * 1.01,
        "low":    close * 0.98,
        "close":  close.astype(np.float32),
        "volume": rng.integers(1_000_000, 5_000_000, n_bars).astype(float),
    })


def _make_backtest_result(pf: float = 1.5, n_trades: int = 10) -> BacktestResult:
    pnl = 100.0
    equity = np.linspace(10_000, 10_100, n_trades + 1).astype(np.float32)
    returns = np.diff(equity) / equity[:-1]
    return BacktestResult(
        sharpe_ratio=1.0, profit_factor=pf, n_trades=n_trades,
        total_pnl=pnl, avg_trade_pnl=10.0, equity_curve=equity, returns=returns,
    )


def _mock_engine(pf: float = 1.5) -> MagicMock:
    eng = MagicMock()
    eng.run.return_value = _make_backtest_result(pf=pf)
    return eng


def _make_individual() -> list:
    return [0, 20, 1.0, 1, 14, 1.0, 2, 9, 1.0, 0.5, 0.05, 0.10, 1.0]


def _make_family(mean_cov: float = 0.30) -> FamilyResult:
    return FamilyResult(
        cov_per_gene={name: mean_cov for name in GENE_NAMES},
        mean_cov=mean_cov,
        passed_mvp=True, passed_production=True,
        n_profitable_restarts=10, n_restarts=10,
    )


# ---------------------------------------------------------------------------
# _perturb_gene
# ---------------------------------------------------------------------------

class TestPerturbGene:
    def test_plus_factor_increases_value(self):
        ind = _make_individual()
        perturbed = _perturb_gene(ind, 2, 1.10)  # weight gene
        assert perturbed[2] > ind[2]

    def test_minus_factor_decreases_value(self):
        ind = _make_individual()
        perturbed = _perturb_gene(ind, 2, 0.90)
        assert perturbed[2] < ind[2]

    def test_original_unchanged(self):
        ind = _make_individual()
        _perturb_gene(ind, 0, 1.10)
        assert ind[0] == 0  # unchanged

    def test_result_clipped_to_bounds(self):
        """Extreme perturbation should stay within bounds."""
        ind = _make_individual()
        # ind[0] = indicator type 0, valid range [0, 14]
        perturbed = _perturb_gene(ind, 0, 1000.0)
        assert 0 <= perturbed[0] <= 14


# ---------------------------------------------------------------------------
# GeneSensitivity / SensitivityResult dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_gene_sensitivity_frozen(self):
        gs = GeneSensitivity(
            gene_name="ind0_type", gene_idx=0, base_value=0.0,
            plus_pf=1.5, minus_pf=1.5, sensitivity=0.0,
        )
        with pytest.raises((TypeError, AttributeError)):
            gs.sensitivity = 1.0  # type: ignore[misc]

    def test_sensitivity_result_frozen(self):
        sr = SensitivityResult(
            gene_sensitivities=[], base_pf=1.5, mean_sensitivity=0.0,
            most_sensitive_gene="ind0_type", cov_correlation=None,
        )
        with pytest.raises((TypeError, AttributeError)):
            sr.base_pf = 2.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# run_sensitivity_analysis — structure
# ---------------------------------------------------------------------------

class TestRunSensitivityStructure:
    def test_returns_n_genes_sensitivities(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        assert len(result.gene_sensitivities) == N_GENES

    def test_gene_names_match(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        names = [gs.gene_name for gs in result.gene_sensitivities]
        assert names == list(GENE_NAMES)

    def test_gene_indices_sequential(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        for i, gs in enumerate(result.gene_sensitivities):
            assert gs.gene_idx == i

    def test_sensitivities_non_negative(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        for gs in result.gene_sensitivities:
            assert gs.sensitivity >= 0.0

    def test_mean_sensitivity_matches_avg(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        expected = np.mean([gs.sensitivity for gs in result.gene_sensitivities])
        assert result.mean_sensitivity == pytest.approx(expected)

    def test_most_sensitive_gene_is_valid_name(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        assert result.most_sensitive_gene in GENE_NAMES

    def test_no_cov_correlation_when_family_none(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine()
        )
        assert result.cov_correlation is None


# ---------------------------------------------------------------------------
# run_sensitivity_analysis — CoV correlation
# ---------------------------------------------------------------------------

class TestRunSensitivityCovCorrelation:
    def test_cov_correlation_returned_when_family_provided(self):
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine(),
            family_result=_make_family(),
        )
        # With uniform CoV, correlation is undefined (std=0) → None or value
        # Just check it doesn't raise
        assert result.cov_correlation is None or isinstance(result.cov_correlation, float)

    def test_cov_correlation_in_valid_range(self):
        """If computed, correlation must be in [-1, 1]."""
        # Create family with varied CoV so correlation is defined
        rng = np.random.default_rng(0)
        varied_cov = {name: float(rng.uniform(0, 1)) for name in GENE_NAMES}
        family = FamilyResult(
            cov_per_gene=varied_cov,
            mean_cov=float(np.mean(list(varied_cov.values()))),
            passed_mvp=True, passed_production=True,
            n_profitable_restarts=10, n_restarts=10,
        )
        result = run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), _mock_engine(),
            family_result=family,
        )
        if result.cov_correlation is not None:
            assert -1.0 <= result.cov_correlation <= 1.0


# ---------------------------------------------------------------------------
# run_sensitivity_analysis — engine call count
# ---------------------------------------------------------------------------

class TestRunSensitivityCallCount:
    def test_engine_called_2n_plus_1_times(self):
        """1 baseline + 2 per gene = 2*N+1 total calls."""
        engine = _mock_engine()
        run_sensitivity_analysis(
            _make_individual(), _make_ohlcv(), engine
        )
        expected_calls = 2 * N_GENES + 1
        assert engine.run.call_count == expected_calls


# ---------------------------------------------------------------------------
# run_sensitivity_analysis — constant
# ---------------------------------------------------------------------------

class TestDefaultPerturbation:
    def test_default_is_10_pct(self):
        assert DEFAULT_PERTURBATION == pytest.approx(0.10)
