"""Chromosome encoding for the 13-gene GA individual.

Genome layout (indices 0–12):
  0  ind1_type        int   [0, 14]    indicator ID
  1  ind1_period      int   [5, 100]   lookback bars
  2  ind1_weight      float [-1.0, 2.0] signal weight (neg = contrarian)
  3  ind2_type        int   [0, 14]
  4  ind2_period      int   [5, 100]
  5  ind2_weight      float [-1.0, 2.0]
  6  ind3_type        int   [0, 14]
  7  ind3_period      int   [5, 100]
  8  ind3_weight      float [-1.0, 2.0]
  9  entry_threshold  float [0.0, 50.0]   weighted-sum signal threshold
  10 stop_loss_pct    float [0.01, 0.20]  fraction of position value
  11 take_profit_pct  float [0.01, 0.50]  fraction of position value
  12 position_size_mult float [0.5, 2.0]   risk multiplier

Discrete genes: type and period for each indicator slot (int).
Continuous genes: weights, threshold, SL%, TP%, position size (float).

Duplicate indicator types across slots are intentional and allowed — the GA
may discover that RSI-14 + RSI-50 (same indicator, two timeframes) is a valid
multi-period strategy.
"""

from __future__ import annotations

import random
from typing import List

import numpy as np

# ---------------------------------------------------------------------------
# Gene metadata
# ---------------------------------------------------------------------------

GENE_NAMES: List[str] = [
    "ind1_type",   "ind1_period",   "ind1_weight",
    "ind2_type",   "ind2_period",   "ind2_weight",
    "ind3_type",   "ind3_period",   "ind3_weight",
    "entry_threshold",
    "stop_loss_pct",
    "take_profit_pct",
    "position_size_mult",
]

#: (lower_bound, upper_bound) for each gene, indexed by position.
GENE_BOUNDS: dict[str, tuple[float, float]] = {
    "ind1_type":          (0,    14),
    "ind1_period":        (5,   100),
    "ind1_weight":        (-1.0, 2.0),
    "ind2_type":          (0,    14),
    "ind2_period":        (5,   100),
    "ind2_weight":        (-1.0, 2.0),
    "ind3_type":          (0,    14),
    "ind3_period":        (5,   100),
    "ind3_weight":        (-1.0, 2.0),
    "entry_threshold":    (0.0, 50.0),
    "stop_loss_pct":      (0.01, 0.20),
    "take_profit_pct":    (0.01, 0.50),
    "position_size_mult": (0.5,  2.0),
}

#: Pre-computed gene ranges (hi - lo) for sigma scaling.
GENE_RANGES: dict[str, float] = {name: hi - lo for name, (lo, hi) in GENE_BOUNDS.items()}

#: Flat bounds lists (parallel to GENE_NAMES order).
_BOUNDS_LIST: List[tuple[float, float]] = [GENE_BOUNDS[n] for n in GENE_NAMES]
_LO: List[float] = [lo for lo, _ in _BOUNDS_LIST]
_HI: List[float] = [hi for _, hi in _BOUNDS_LIST]

#: Indices of integer genes (indicator type + period for each slot).
DISCRETE_GENES: List[int] = [0, 1, 3, 4, 6, 7]

#: Indices of float genes (weights, threshold, SL%, TP%, size mult).
CONTINUOUS_GENES: List[int] = [2, 5, 8, 9, 10, 11, 12]

#: Names of continuous genes (parallel to CONTINUOUS_GENES index list).
CONTINUOUS_GENE_NAMES: List[str] = [GENE_NAMES[i] for i in CONTINUOUS_GENES]

#: Names of discrete genes (parallel to DISCRETE_GENES index list).
DISCRETE_GENE_NAMES: List[str] = [GENE_NAMES[i] for i in DISCRETE_GENES]

#: Total chromosome length.
N_GENES: int = len(GENE_NAMES)

# ---------------------------------------------------------------------------
# OBV special handling
# ---------------------------------------------------------------------------

#: OBV indicator ID has no period (min_period == max_period == 0).
_OBV_ID: int = 12

#: Valid period range per indicator ID (matches registry.py).
_INDICATOR_PERIOD_BOUNDS: dict[int, tuple[int, int]] = {
    0: (5,  50),   # RSI
    1: (10, 100),  # CCI
    2: (5,  50),   # STOCH
    3: (10, 30),   # ADX
    4: (10, 50),   # ATR
    5: (8,  20),   # MACD
    6: (10, 30),   # BBANDS
    7: (5,  50),   # ROC
    8: (10, 30),   # WILLR
    9: (5,  50),   # MOM
    10:(10, 100),  # EMA
    11:(10, 100),  # SMA
    12:(0,  0),    # OBV — no period
    13:(10, 50),   # MFI
    14:(10, 30),   # DMI
}


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


def _random_gene(index: int) -> float:
    """Sample a single gene uniformly within its bounds."""
    lo, hi = _BOUNDS_LIST[index]
    if index in DISCRETE_GENES:
        return float(random.randint(int(lo), int(hi)))
    return random.uniform(lo, hi)


def _fix_period_for_type(ind: list) -> None:
    """Adjust period genes so they fall within the valid range for their indicator type.

    Each indicator has its own valid period range (see registry.py).  The
    generic period bounds [5, 100] cover all indicators, but individual
    indicators may have narrower ranges.  After random init or crossover,
    clamp the period to the indicator's actual range.
    """
    for slot in range(3):
        type_idx = slot * 3        # 0, 3, 6
        period_idx = slot * 3 + 1  # 1, 4, 7
        ind_type = int(ind[type_idx])
        lo, hi = _INDICATOR_PERIOD_BOUNDS.get(ind_type, (5, 100))
        if hi == 0:  # OBV
            ind[period_idx] = 0.0
        else:
            ind[period_idx] = float(int(np.clip(int(ind[period_idx]), lo, hi)))


def init_individual(creator_individual) -> list:
    """Create a single random individual within gene bounds.

    Args:
        creator_individual: DEAP ``creator.Individual`` class.

    Returns:
        A DEAP Individual (list subclass) of length 13.
    """
    ind = creator_individual(_random_gene(i) for i in range(N_GENES))
    _fix_period_for_type(ind)
    return ind


def init_population_lhs(creator_individual, n: int = 200) -> list:
    """Latin Hypercube Sampling population for restart 0.

    LHS divides each gene's range into ``n`` equal strata and picks one
    sample per stratum, guaranteeing better initial coverage of the search
    space than pure random sampling.  Use for restart 0 only; restarts 1–9
    use random init (diversity via different seeds).

    Args:
        creator_individual: DEAP ``creator.Individual`` class.
        n:                  Population size (default 200).

    Returns:
        List of ``n`` DEAP Individuals.
    """
    from scipy.stats import qmc

    sampler = qmc.LatinHypercube(d=N_GENES, seed=None)  # seed from global RNG
    samples = sampler.random(n=n)  # shape (n, 13), values in [0, 1]

    population = []
    for sample in samples:
        genes = []
        for i, (lo, hi) in enumerate(_BOUNDS_LIST):
            scaled = lo + sample[i] * (hi - lo)
            if i in DISCRETE_GENES:
                genes.append(float(int(round(scaled))))
            else:
                genes.append(float(scaled))
        ind = creator_individual(genes)
        _fix_period_for_type(ind)
        clip_to_bounds(ind)
        population.append(ind)

    return population


# ---------------------------------------------------------------------------
# Bounds enforcement
# ---------------------------------------------------------------------------


def clip_to_bounds(ind: list) -> list:
    """Clip all genes to their valid bounds in-place and return the individual.

    Discrete genes are also rounded to the nearest integer.

    Args:
        ind: DEAP Individual (list of 13 floats).

    Returns:
        The same individual (mutated in-place).
    """
    for i, (lo, hi) in enumerate(_BOUNDS_LIST):
        val = float(ind[i])
        val = float(np.clip(val, lo, hi))
        if i in DISCRETE_GENES:
            val = float(int(round(val)))
        ind[i] = val
    _fix_period_for_type(ind)
    return ind
