"""Lightweight statistical utilities for the hot path.

pearsonr_fast() is 3–5× faster than scipy.stats.pearsonr for 1-D arrays of
the sizes used in the fitness function (~1,500 bars per split), making it
worthwhile in the 2M-call inner loop.
"""

from __future__ import annotations

import numpy as np


def pearsonr_fast(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson correlation coefficient — faster than scipy for 1-D arrays.

    Uses NumPy dot product formulation:
        r = (a - mean(a)) · (b - mean(b))
            / (‖a - mean(a)‖ × ‖b - mean(b)‖)

    A small epsilon (1e-10) prevents division by zero on constant arrays.

    Args:
        a, b: 1-D float arrays of equal length.

    Returns:
        Pearson r in [-1.0, 1.0].

    Raises:
        ValueError: If a and b have different lengths.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if len(a) != len(b):
        raise ValueError(f"Arrays must have equal length: {len(a)} vs {len(b)}.")

    a_c = a - np.mean(a)
    b_c = b - np.mean(b)
    denom = np.linalg.norm(a_c) * np.linalg.norm(b_c) + 1e-10
    return float(np.dot(a_c, b_c) / denom)
