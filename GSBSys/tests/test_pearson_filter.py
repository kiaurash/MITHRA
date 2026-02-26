"""Tests for src/validation/pearson_filter.py."""

import numpy as np
import pytest

from src.validation.pearson_filter import (
    MVP_THRESHOLD,
    PRODUCTION_THRESHOLD,
    PearsonResult,
    run_pearson_filter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _linear(n: int, slope: float = 1.0) -> np.ndarray:
    return np.arange(n, dtype=float) * slope


# ---------------------------------------------------------------------------
# PearsonResult dataclass
# ---------------------------------------------------------------------------

class TestPearsonResultDataclass:
    def test_frozen(self):
        r = PearsonResult(pearson_r=0.9, passed_mvp=True, passed_production=True)
        with pytest.raises((TypeError, AttributeError)):
            r.pearson_r = 0.5  # type: ignore[misc]

    def test_fields(self):
        r = PearsonResult(pearson_r=0.87, passed_mvp=True, passed_production=False)
        assert r.pearson_r == 0.87
        assert r.passed_mvp is True
        assert r.passed_production is False


# ---------------------------------------------------------------------------
# run_pearson_filter — basic correctness
# ---------------------------------------------------------------------------

class TestRunPearsonFilterBasic:
    def test_identical_curves_r1(self):
        arr = _linear(100)
        result = run_pearson_filter(arr, arr.copy())
        assert abs(result.pearson_r - 1.0) < 1e-9

    def test_perfectly_anticorrelated_r_neg1(self):
        a = _linear(100)
        b = _linear(100, slope=-1.0)
        result = run_pearson_filter(a, b)
        assert abs(result.pearson_r + 1.0) < 1e-9

    def test_high_r_passes_both_tiers(self):
        a = _linear(200)
        b = _linear(200) + np.random.default_rng(0).normal(0, 0.01, 200)
        result = run_pearson_filter(a, b)
        assert result.pearson_r >= PRODUCTION_THRESHOLD
        assert result.passed_mvp is True
        assert result.passed_production is True

    def test_low_r_fails_both_tiers(self):
        rng = np.random.default_rng(42)
        a = _linear(100)
        b = rng.random(100)  # pure noise
        result = run_pearson_filter(a, b)
        assert result.passed_mvp is False
        assert result.passed_production is False

    def test_r_between_thresholds_passes_mvp_fails_prod(self):
        # Construct arrays whose true r is approx 0.87 (between 0.85 and 0.90)
        rng = np.random.default_rng(7)
        a = _linear(500)
        noise = rng.normal(0, 40, 500)
        b = a + noise
        result = run_pearson_filter(a, b)
        if MVP_THRESHOLD <= result.pearson_r < PRODUCTION_THRESHOLD:
            assert result.passed_mvp is True
            assert result.passed_production is False


# ---------------------------------------------------------------------------
# run_pearson_filter — resampling behaviour
# ---------------------------------------------------------------------------

class TestRunPearsonFilterResampling:
    def test_unequal_lengths_does_not_raise(self):
        a = _linear(200)
        b = _linear(300)
        # Should not raise; resamples both to 200
        result = run_pearson_filter(a, b)
        assert isinstance(result.pearson_r, float)

    def test_equal_vs_resampled_similar_r(self):
        """Resampling a perfectly linear curve should preserve high r."""
        a = _linear(250)
        b = _linear(100)  # shorter; resampled to 100
        result = run_pearson_filter(a, b)
        # Both are linear with positive slope → r should be ~1
        assert result.pearson_r > 0.99

    def test_train_shorter_than_test(self):
        a = _linear(100)
        b = _linear(250)
        result = run_pearson_filter(a, b)
        assert result.pearson_r > 0.99


# ---------------------------------------------------------------------------
# run_pearson_filter — edge cases & errors
# ---------------------------------------------------------------------------

class TestRunPearsonFilterEdgeCases:
    def test_length_1_raises(self):
        with pytest.raises(ValueError):
            run_pearson_filter(np.array([1.0]), np.array([1.0, 2.0]))

    def test_empty_raises(self):
        with pytest.raises((ValueError, IndexError)):
            run_pearson_filter(np.array([]), np.array([1.0, 2.0]))

    def test_list_input_accepted(self):
        result = run_pearson_filter([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert abs(result.pearson_r - 1.0) < 1e-9

    def test_returns_pearson_result_instance(self):
        result = run_pearson_filter(_linear(50), _linear(50))
        assert isinstance(result, PearsonResult)

    def test_r_in_valid_range(self):
        rng = np.random.default_rng(99)
        for _ in range(5):
            a = rng.random(100)
            b = rng.random(100)
            result = run_pearson_filter(a, b)
            assert -1.0 <= result.pearson_r <= 1.0
