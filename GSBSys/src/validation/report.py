"""Validation report — Phase 2, Layer 5.

Aggregates results from all 4 validation layers into a single pass/fail
summary and serialises to JSON for archiving.

A system passes MVP tier if ALL 4 layers pass MVP.
A system passes Production tier if ALL 4 layers pass Production.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Optional

from src.validation.family_grouping import FamilyResult
from src.validation.multi_period_oos import OOSResult
from src.validation.noise_injection import NoiseResult
from src.validation.pearson_filter import PearsonResult


@dataclass(frozen=True)
class ValidationReport:
    """Unified validation report across all 4 layers.

    Attributes:
        pearson:            Pearson equity-curve correlation result.
        oos:                Multi-period OOS result.
        noise:              Noise injection result.
        family:             Family grouping / CoV result.
        passed_mvp:         True if ALL 4 layers pass MVP tier.
        passed_production:  True if ALL 4 layers pass Production tier.
        summary:            Human-readable pass/fail table.
    """

    pearson: PearsonResult
    oos: OOSResult
    noise: NoiseResult
    family: FamilyResult
    passed_mvp: bool
    passed_production: bool
    summary: str


def build_report(
    pearson: PearsonResult,
    oos: OOSResult,
    noise: NoiseResult,
    family: FamilyResult,
) -> ValidationReport:
    """Build a ValidationReport from the four layer results.

    Args:
        pearson: Result from run_pearson_filter().
        oos:     Result from run_multi_period_oos().
        noise:   Result from run_noise_injection().
        family:  Result from run_family_grouping().

    Returns:
        ValidationReport with aggregated pass/fail and human-readable summary.
    """
    passed_mvp = (
        pearson.passed_mvp
        and oos.passed_mvp
        and noise.passed_mvp
        and family.passed_mvp
    )
    passed_production = (
        pearson.passed_production
        and oos.passed_production
        and noise.passed_production
        and family.passed_production
    )

    summary = _build_summary(pearson, oos, noise, family, passed_mvp, passed_production)

    return ValidationReport(
        pearson=pearson,
        oos=oos,
        noise=noise,
        family=family,
        passed_mvp=passed_mvp,
        passed_production=passed_production,
        summary=summary,
    )


def save_report(report: ValidationReport, path: str) -> None:
    """Serialise a ValidationReport to a JSON file.

    Args:
        report: The ValidationReport to save.
        path:   Destination file path (directories are created if needed).
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def _to_dict(obj):
        """Recursively convert dataclasses and numpy scalars to plain types."""
        if hasattr(obj, "__dataclass_fields__"):
            return {k: _to_dict(v) for k, v in asdict(obj).items()}
        if isinstance(obj, (list, tuple)):
            return [_to_dict(i) for i in obj]
        if isinstance(obj, dict):
            return {k: _to_dict(v) for k, v in obj.items()}
        # numpy scalar guard
        try:
            return obj.item()  # type: ignore[union-attr]
        except AttributeError:
            return obj

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(_to_dict(report), fh, indent=2)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _tick(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def _build_summary(
    pearson: PearsonResult,
    oos: OOSResult,
    noise: NoiseResult,
    family: FamilyResult,
    passed_mvp: bool,
    passed_production: bool,
) -> str:
    lines = [
        "=" * 60,
        "  GA-TRADING-SYS — PHASE 2 VALIDATION REPORT",
        "=" * 60,
        "",
        f"  Layer 1 · Pearson r         : {pearson.pearson_r:.4f}"
        f"  [MVP {_tick(pearson.passed_mvp)} / PROD {_tick(pearson.passed_production)}]",
        f"  Layer 2 · OOS regimes       : {oos.n_profitable}/5 profitable"
        f"  [MVP {_tick(oos.passed_mvp)} / PROD {_tick(oos.passed_production)}]",
        f"  Layer 3 · Noise variants    : {noise.n_profitable}/8 profitable"
        f"  [MVP {_tick(noise.passed_mvp)} / PROD {_tick(noise.passed_production)}]",
        f"  Layer 4 · Family mean CoV   : {family.mean_cov:.4f}"
        f"  [MVP {_tick(family.passed_mvp)} / PROD {_tick(family.passed_production)}]",
        "",
        "-" * 60,
        f"  OVERALL MVP        : {_tick(passed_mvp)}",
        f"  OVERALL PRODUCTION : {_tick(passed_production)}",
        "=" * 60,
    ]
    return "\n".join(lines)
