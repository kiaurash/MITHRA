"""Pearson equity curve filter — Phase 2, Layer 1.

Measures train/test equity curve correlation as a hard pass/fail gate.
A low Pearson r means the equity curve in the test set diverges from the
training set — a strong overfitting signal.

Note: The fitness function (Phase 1) already applies a *penalty* when
Pearson < 0.85.  This module provides a standalone *gate* for post-run
validation: systems below the threshold are rejected entirely.

Thresholds (from PRD Section 3.2):
  MVP tier:        r >= 0.85
  Production tier: r >= 0.90
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.utils.stats import pearsonr_fast

#: MVP pass threshold (relaxed — proof-of-concept).
MVP_THRESHOLD: float = 0.85

#: Production pass threshold (strict — commercial grade).
PRODUCTION_THRESHOLD: float = 0.90


@dataclass(frozen=True)
class PearsonResult:
    """Result of the Pearson equity curve filter.

    Attributes:
        pearson_r:          Pearson correlation coefficient in [-1, 1].
        passed_mvp:         True if pearson_r >= 0.85.
        passed_production:  True if pearson_r >= 0.90.
    """

    pearson_r: float
    passed_mvp: bool
    passed_production: bool


def run_pearson_filter(
    train_equity: np.ndarray,
    test_equity: np.ndarray,
) -> PearsonResult:
    """Compute Pearson r between train and test equity curves.

    When the arrays have different lengths (train 40% / test 60%), both are
    resampled to the shorter length via linear interpolation so the shapes
    are comparable.

    Args:
        train_equity: float array of equity values over the training period.
        test_equity:  float array of equity values over the test period.

    Returns:
        PearsonResult with r value and tier pass/fail flags.

    Raises:
        ValueError: If either array is empty or has length < 2.
    """
    train = np.asarray(train_equity, dtype=np.float64)
    test  = np.asarray(test_equity,  dtype=np.float64)

    if len(train) < 2 or len(test) < 2:
        raise ValueError(
            f"Equity arrays must have length >= 2. "
            f"Got train={len(train)}, test={len(test)}."
        )

    # Resample to equal length via linear interpolation
    if len(train) != len(test):
        target_len = min(len(train), len(test))
        train = np.interp(
            np.linspace(0, 1, target_len),
            np.linspace(0, 1, len(train)),
            train,
        )
        test = np.interp(
            np.linspace(0, 1, target_len),
            np.linspace(0, 1, len(test)),
            test,
        )

    r = pearsonr_fast(train, test)
    return PearsonResult(
        pearson_r=r,
        passed_mvp=r >= MVP_THRESHOLD,
        passed_production=r >= PRODUCTION_THRESHOLD,
    )
