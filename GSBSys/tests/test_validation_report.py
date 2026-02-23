"""Tests for src/validation/report.py."""

import json
import os
import tempfile

import numpy as np
import pytest

from src.validation.family_grouping import FamilyResult
from src.validation.multi_period_oos import OOSResult, RegimeResult
from src.validation.noise_injection import NoiseResult, VariantResult
from src.validation.pearson_filter import PearsonResult
from src.validation.report import ValidationReport, build_report, save_report


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _pearson(r: float = 0.92) -> PearsonResult:
    return PearsonResult(
        pearson_r=r,
        passed_mvp=r >= 0.85,
        passed_production=r >= 0.90,
    )


def _oos(n_profitable: int = 4) -> OOSResult:
    regime_results = [
        RegimeResult(
            label=f"regime_{i}", start_date="2010-01-01", end_date="2012-12-31",
            profit_factor=1.5 if i < n_profitable else 0.8,
            n_trades=10, total_pnl=100.0 if i < n_profitable else -50.0,
            profitable=i < n_profitable, skipped=False,
        )
        for i in range(5)
    ]
    return OOSResult(
        regime_results=regime_results,
        n_profitable=n_profitable,
        passed_mvp=n_profitable >= 3,
        passed_production=n_profitable >= 4,
    )


def _noise(n_profitable: int = 6) -> NoiseResult:
    variant_results = [
        VariantResult(
            name=f"variant_{i}",
            profit_factor=1.5 if i < n_profitable else 0.8,
            n_trades=5, total_pnl=50.0 if i < n_profitable else -20.0,
            profitable=i < n_profitable,
        )
        for i in range(8)
    ]
    return NoiseResult(
        variant_results=variant_results,
        n_profitable=n_profitable,
        passed_mvp=n_profitable >= 5,
        passed_production=n_profitable >= 6,
    )


def _family(mean_cov: float = 0.30) -> FamilyResult:
    from src.ga.chromosome import GENE_NAMES
    return FamilyResult(
        cov_per_gene={name: mean_cov for name in GENE_NAMES},
        mean_cov=mean_cov,
        passed_mvp=mean_cov <= 0.60,
        passed_production=mean_cov <= 0.50,
        n_profitable_restarts=9,
        n_restarts=10,
    )


def _all_pass_report() -> ValidationReport:
    return build_report(_pearson(0.92), _oos(4), _noise(6), _family(0.30))


def _all_fail_report() -> ValidationReport:
    return build_report(_pearson(0.70), _oos(1), _noise(2), _family(0.80))


# ---------------------------------------------------------------------------
# ValidationReport dataclass
# ---------------------------------------------------------------------------

class TestValidationReportDataclass:
    def test_frozen(self):
        r = _all_pass_report()
        with pytest.raises((TypeError, AttributeError)):
            r.passed_mvp = False  # type: ignore[misc]

    def test_has_all_fields(self):
        r = _all_pass_report()
        assert hasattr(r, "pearson")
        assert hasattr(r, "oos")
        assert hasattr(r, "noise")
        assert hasattr(r, "family")
        assert hasattr(r, "passed_mvp")
        assert hasattr(r, "passed_production")
        assert hasattr(r, "summary")


# ---------------------------------------------------------------------------
# build_report — pass/fail logic
# ---------------------------------------------------------------------------

class TestBuildReportPassFail:
    def test_all_layers_pass_mvp(self):
        r = _all_pass_report()
        assert r.passed_mvp is True
        assert r.passed_production is True

    def test_all_layers_fail(self):
        r = _all_fail_report()
        assert r.passed_mvp is False
        assert r.passed_production is False

    def test_one_failing_layer_fails_overall_mvp(self):
        """If only OOS fails MVP, overall MVP should fail."""
        r = build_report(_pearson(0.92), _oos(1), _noise(6), _family(0.30))
        assert r.passed_mvp is False

    def test_one_failing_layer_fails_overall_production(self):
        """All MVP pass but one production fails → overall production fail."""
        r = build_report(_pearson(0.88), _oos(4), _noise(6), _family(0.30))
        # pearson 0.88 passes MVP but not production
        assert r.passed_production is False
        assert r.passed_mvp is True

    def test_passed_mvp_iff_all_layers_pass_mvp(self):
        p = _pearson(0.92)
        o = _oos(4)
        n = _noise(6)
        f = _family(0.30)
        r = build_report(p, o, n, f)
        expected = p.passed_mvp and o.passed_mvp and n.passed_mvp and f.passed_mvp
        assert r.passed_mvp == expected

    def test_passed_production_iff_all_layers_pass_production(self):
        p = _pearson(0.92)
        o = _oos(4)
        n = _noise(6)
        f = _family(0.30)
        r = build_report(p, o, n, f)
        expected = (p.passed_production and o.passed_production
                    and n.passed_production and f.passed_production)
        assert r.passed_production == expected


# ---------------------------------------------------------------------------
# build_report — summary content
# ---------------------------------------------------------------------------

class TestBuildReportSummary:
    def test_summary_is_string(self):
        assert isinstance(_all_pass_report().summary, str)

    def test_summary_non_empty(self):
        assert len(_all_pass_report().summary) > 0

    def test_summary_contains_pass_when_all_pass(self):
        r = _all_pass_report()
        assert "PASS" in r.summary

    def test_summary_contains_fail_when_all_fail(self):
        r = _all_fail_report()
        assert "FAIL" in r.summary

    def test_summary_contains_pearson_value(self):
        r = _all_pass_report()
        assert "0.92" in r.summary

    def test_summary_contains_layer_info(self):
        r = _all_pass_report()
        lower = r.summary.lower()
        # Should mention Pearson and some OOS/noise/family info
        assert "pearson" in lower or "layer" in lower


# ---------------------------------------------------------------------------
# save_report — JSON serialisation
# ---------------------------------------------------------------------------

class TestSaveReport:
    def test_save_creates_file(self):
        r = _all_pass_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            save_report(r, path)
            assert os.path.exists(path)

    def test_saved_json_is_valid(self):
        r = _all_pass_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            save_report(r, path)
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, dict)

    def test_saved_json_contains_passed_mvp(self):
        r = _all_pass_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            save_report(r, path)
            with open(path) as f:
                data = json.load(f)
            assert "passed_mvp" in data
            assert data["passed_mvp"] is True

    def test_saved_json_contains_pearson_r(self):
        r = _all_pass_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            save_report(r, path)
            with open(path) as f:
                data = json.load(f)
            assert "pearson" in data
            assert abs(data["pearson"]["pearson_r"] - 0.92) < 1e-6

    def test_save_creates_parent_dirs(self):
        r = _all_pass_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "deep", "nested", "report.json")
            save_report(r, path)
            assert os.path.exists(path)

    def test_save_roundtrip_n_profitable(self):
        r = _all_pass_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            save_report(r, path)
            with open(path) as f:
                data = json.load(f)
            assert data["oos"]["n_profitable"] == 4
            assert data["noise"]["n_profitable"] == 6
