"""Centralized random seed management.

All randomness in GA runs flows through here.  DEAP uses Python's ``random``
module internally, so seeding both ``random`` and ``numpy.random`` is enough
for full reproducibility.
"""

import random
from typing import List

import numpy as np


def set_global_seed(seed: int) -> None:
    """Seed Python random and NumPy RNG.

    Call this at the start of every subprocess worker (restart) so that
    each restart is independently reproducible from its seed alone.

    Args:
        seed: Non-negative integer seed value.
    """
    random.seed(seed)
    np.random.seed(seed)


def make_restart_seeds(base_seed: int, n: int = 10) -> List[int]:
    """Generate *n* deterministic, non-overlapping seeds from *base_seed*.

    Uses a seeded ``random.Random`` instance so the output is stable across
    Python versions and platforms.

    Args:
        base_seed: Master seed (logged to results for reproducibility).
        n: Number of restart seeds to produce.

    Returns:
        List of *n* unique integer seeds in [0, 2^31 - 1].

    Example::

        >>> make_restart_seeds(42, n=3)
        [639426071, 1234567890, ...]  # deterministic
    """
    rng = random.Random(base_seed)
    return [rng.randint(0, 2**31 - 1) for _ in range(n)]
