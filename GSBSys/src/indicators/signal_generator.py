"""Signal generator — weighted sum of indicator values from the GA chromosome.

Chromosome layout (13 genes, indices 0–12):
  [ind1_type, ind1_period, ind1_weight,
   ind2_type, ind2_period, ind2_weight,
   ind3_type, ind3_period, ind3_weight,
   entry_threshold, stop_loss_pct, take_profit_pct, position_size_mult]

Signal computation (for N indicator slots):
    composite[t] = Σ weight_i × normalized_indicator_i[t]

where each normalized_indicator is in [-100, +100] (NaN during warm-up).

The composite signal is NaN wherever any contributing indicator is NaN
(strict: all slots must have valid data before a signal is produced).
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

# Gene index constants for readability
_SLOT_STRIDE = 3        # (type, period, weight) per slot
_N_INDICATOR_SLOTS = 3  # Phase 1 fixed at 3 slots
_IDX_ENTRY_THRESHOLD = 9
_IDX_STOP_LOSS_PCT = 10
_IDX_TAKE_PROFIT_PCT = 11
_IDX_POSITION_SIZE_MULT = 12


def generate_signals_weighted_sum(
    individual: Sequence[float],
    cache: Dict[str, np.ndarray],
) -> np.ndarray:
    """Compute a composite signal array from a GA chromosome.

    Args:
        individual: List/array of 13 gene values.  Type and period genes are
                    treated as integers internally (floor applied).  Weight
                    genes are floats.
        cache:      Pre-computed indicator cache from
                    ``calculator.build_indicator_cache``.
                    Keys are ``f"{indicator_id}_{period}"``.

    Returns:
        float64 ndarray of length T (same as cached arrays).  NaN at any bar
        where at least one indicator slot has NaN.  Non-NaN values represent
        the weighted sum in the range roughly [-300, +300] (3 slots × [-100,
        +100] × weight ∈ [-1, 2]).

    Raises:
        KeyError: If a required cache key is missing (invalid ind_type or
                  period not pre-computed — indicates programmer error).
        ValueError: If ``individual`` does not have exactly 13 genes.
    """
    if len(individual) != 13:
        raise ValueError(f"Expected 13 genes, got {len(individual)}.")

    # Determine array length from first cache entry
    if not cache:
        raise ValueError("Cache is empty — run build_indicator_cache first.")
    T = len(next(iter(cache.values())))

    composite = np.zeros(T, dtype=np.float64)
    nan_mask = np.zeros(T, dtype=bool)

    for slot in range(_N_INDICATOR_SLOTS):
        base = slot * _SLOT_STRIDE
        ind_type = int(individual[base])       # indicator ID 0–14
        ind_period = int(individual[base + 1]) # period value
        weight = float(individual[base + 2])   # weight in [-1.0, 2.0]

        key = f"{ind_type}_{ind_period}"
        arr = cache[key].astype(np.float64)    # float32 → float64 for math

        nan_mask |= np.isnan(arr)
        composite += weight * np.where(np.isnan(arr), 0.0, arr)

    # Zero out any bar where at least one indicator was NaN
    composite[nan_mask] = np.nan

    return composite


def get_entry_signals(
    composite: np.ndarray,
    entry_threshold: float,
) -> np.ndarray:
    """Return boolean array: True where composite > entry_threshold.

    NaN bars always produce False (no entry on missing data).

    Args:
        composite:       Output of ``generate_signals_weighted_sum``.
        entry_threshold: Float, typically in [0, 50].

    Returns:
        bool ndarray, same length as composite.
    """
    valid = ~np.isnan(composite)
    signal = np.zeros(len(composite), dtype=bool)
    signal[valid] = composite[valid] > entry_threshold
    return signal
