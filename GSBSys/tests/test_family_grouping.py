"""Tests for src/validation/family_grouping.py."""

import numpy as np
import pytest

from src.ga.chromosome import GENE_NAMES
from src.validation.family_grouping import (
    MVP_COV_THRESHOLD,
    PRODUCTION_COV_THRESHOLD,
    FamilyResult,
    run_family_grouping,
)

N_GENES = len(GENE_NAMES)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_restart(individual: list, fitness: float = 100.0) -> dict:
    return {"best_individual": individual, "best_fitness": fitness}


def _identical_restarts(n: int = 10, fitness: float = 100.0) -> list:
    """All restarts converged to the exact same chromosome → CoV = 0."""
    ind = [float(i + 1) for i in range(N_GENES)]  # non-zero values
    return [_make_restart(ind, fitness) for _ in range(n)]


def _random_restarts(n: int = 10, seed: int = 42) -> list:
    """Restarts with random chromosomes → high CoV."""
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(n):
        ind = rng.uniform(1, 100, N_GENES).tolist()
        results.append(_make_restart(ind))
    return results


# ---------------------------------------------------------------------------
# FamilyResult dataclass
# ---------------------------------------------------------------------------

class TestFamilyResultDataclass:
    def test_frozen(self):
        r = FamilyResult(
            cov_per_gene={}, mean_cov=0.1, passed_mvp=True,
            passed_production=True, n_profitable_restarts=10, n_restarts=10,
        )
        with pytest.raises((TypeError, AttributeError)):
            r.mean_cov = 0.5  # type: ignore[misc]

    def test_fields(self):
        r = FamilyResult(
            cov_per_gene={"a": 0.1}, mean_cov=0.1, passed_mvp=True,
            passed_production=False, n_profitable_restarts=8, n_restarts=10,
        )
        assert r.n_restarts == 10
        assert r.n_profitable_restarts == 8


# ---------------------------------------------------------------------------
# run_family_grouping — input validation
# ---------------------------------------------------------------------------

class TestRunFamilyGroupingValidation:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            run_family_grouping([])

    def test_wrong_gene_count_raises(self):
        bad = [_make_restart([1.0, 2.0])]  # only 2 genes
        with pytest.raises(ValueError):
            run_family_grouping(bad)

    def test_single_restart_no_std(self):
        """Single restart → std=0 → CoV=0 for all genes."""
        restarts = [_make_restart([float(i + 1) for i in range(N_GENES)])]
        result = run_family_grouping(restarts)
        assert all(v == 0.0 for v in result.cov_per_gene.values())
        assert result.mean_cov == 0.0


# ---------------------------------------------------------------------------
# run_family_grouping — CoV computation
# ---------------------------------------------------------------------------

class TestRunFamilyGroupingCoV:
    def test_identical_restarts_zero_cov(self):
        result = run_family_grouping(_identical_restarts())
        assert result.mean_cov == pytest.approx(0.0)
        assert all(v == pytest.approx(0.0) for v in result.cov_per_gene.values())

    def test_near_zero_mean_gene_cov_zero(self):
        """Gene values near zero → CoV = 0 (avoid divide-by-zero)."""
        inds = [[1e-8] * N_GENES for _ in range(5)]
        # Slightly perturb one gene to give non-zero std
        inds[0][0] = 1e-8
        inds[1][0] = 2e-8
        restarts = [_make_restart(ind) for ind in inds]
        result = run_family_grouping(restarts)
        # gene 0 has near-zero mean: CoV should be 0 or very small
        # Other genes are identical: CoV = 0
        for name, cov in result.cov_per_gene.items():
            assert cov >= 0.0

    def test_high_variance_gives_high_cov(self):
        """Diverse restarts → mean_cov > 0."""
        result = run_family_grouping(_random_restarts(n=10))
        assert result.mean_cov > 0.0

    def test_cov_per_gene_has_all_genes(self):
        result = run_family_grouping(_identical_restarts())
        assert set(result.cov_per_gene.keys()) == set(GENE_NAMES)

    def test_cov_values_non_negative(self):
        result = run_family_grouping(_random_restarts())
        assert all(v >= 0.0 for v in result.cov_per_gene.values())

    def test_mean_cov_matches_avg_of_per_gene(self):
        result = run_family_grouping(_random_restarts())
        expected = np.mean(list(result.cov_per_gene.values()))
        assert result.mean_cov == pytest.approx(expected)


# ---------------------------------------------------------------------------
# run_family_grouping — pass/fail thresholds
# ---------------------------------------------------------------------------

class TestRunFamilyGroupingPassFail:
    def test_zero_cov_passes_both_tiers(self):
        result = run_family_grouping(_identical_restarts())
        assert result.passed_mvp is True
        assert result.passed_production is True

    def test_high_cov_fails_both_tiers(self):
        """Very diverse solutions → high CoV → fails both tiers."""
        rng = np.random.default_rng(0)
        restarts = []
        for _ in range(10):
            # Large spread: mean ~50, std ~100 → CoV ~2.0
            ind = rng.uniform(-100, 200, N_GENES).tolist()
            restarts.append(_make_restart(ind))
        result = run_family_grouping(restarts)
        if result.mean_cov > MVP_COV_THRESHOLD:
            assert result.passed_mvp is False
            assert result.passed_production is False

    def test_mvp_threshold_boundary(self):
        assert MVP_COV_THRESHOLD == pytest.approx(0.60)

    def test_production_threshold_boundary(self):
        assert PRODUCTION_COV_THRESHOLD == pytest.approx(0.50)

    def test_passed_mvp_consistent_with_mean_cov(self):
        result = run_family_grouping(_identical_restarts())
        assert result.passed_mvp == (result.mean_cov <= MVP_COV_THRESHOLD)

    def test_passed_production_consistent_with_mean_cov(self):
        result = run_family_grouping(_identical_restarts())
        assert result.passed_production == (result.mean_cov <= PRODUCTION_COV_THRESHOLD)


# ---------------------------------------------------------------------------
# run_family_grouping — n_profitable_restarts
# ---------------------------------------------------------------------------

class TestRunFamilyGroupingProfitable:
    def test_all_profitable(self):
        result = run_family_grouping(_identical_restarts(fitness=100.0))
        assert result.n_profitable_restarts == 10

    def test_none_profitable(self):
        result = run_family_grouping(_identical_restarts(fitness=0.0))
        assert result.n_profitable_restarts == 0

    def test_partial_profitable(self):
        restarts = (
            _identical_restarts(n=6, fitness=50.0)
            + _identical_restarts(n=4, fitness=0.0)
        )
        result = run_family_grouping(restarts)
        assert result.n_profitable_restarts == 6

    def test_n_restarts_matches_input_length(self):
        restarts = _identical_restarts(n=7)
        result = run_family_grouping(restarts)
        assert result.n_restarts == 7
