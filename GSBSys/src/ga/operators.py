"""GA genetic operators — crossover, mutation, and adaptive sigma schedule.

Design decisions (from research insights in the plan):
- Crossover: uniform for discrete genes, SBX (eta=15) for continuous genes.
  Uniform preserves integer semantics; SBX gives bounded offspring for floats.
- Mutation: random replacement for discrete; per-gene Gaussian for continuous.
  Per-gene sigma = sigma_fraction × gene_range (fixes POC flat sigma=0.2 bug).
- Adaptive sigma: anneals 0.20 → 0.10 → 0.05 across generations.
- All operators enforce bounds via clip_to_bounds after modification.
"""

from __future__ import annotations

import random
from typing import Tuple

from deap import tools

from src.ga.chromosome import (
    CONTINUOUS_GENE_NAMES,
    CONTINUOUS_GENES,
    DISCRETE_GENE_NAMES,
    DISCRETE_GENES,
    GENE_BOUNDS,
    GENE_RANGES,
    clip_to_bounds,
)


# ---------------------------------------------------------------------------
# Crossover
# ---------------------------------------------------------------------------


def crossover_hybrid(ind1: list, ind2: list) -> Tuple[list, list]:
    """Hybrid crossover: uniform for discrete genes, SBX for continuous.

    Operates in-place on both individuals.

    Discrete genes (indicator type + period):
      - Uniform crossover: each gene independently swapped with p=0.5.

    Continuous genes (weights, threshold, SL%, TP%, position size):
      - Simulated Binary Crossover (SBX), eta=15, with per-gene bounds.
      - eta=15 keeps offspring close to parents — appropriate given 10 restarts
        provide global diversity.

    Args:
        ind1, ind2: DEAP Individuals of length 13.

    Returns:
        (ind1, ind2) mutated in-place (DEAP operator convention).
    """
    # Uniform crossover on discrete genes
    for i in DISCRETE_GENES:
        if random.random() < 0.5:
            ind1[i], ind2[i] = ind2[i], ind1[i]

    # SBX on continuous genes — operate on extracted sublists
    cont1 = [ind1[i] for i in CONTINUOUS_GENES]
    cont2 = [ind2[i] for i in CONTINUOUS_GENES]

    lo_list = [GENE_BOUNDS[n][0] for n in CONTINUOUS_GENE_NAMES]
    hi_list = [GENE_BOUNDS[n][1] for n in CONTINUOUS_GENE_NAMES]

    tools.cxSimulatedBinaryBounded(cont1, cont2, eta=15, low=lo_list, up=hi_list)

    for j, i in enumerate(CONTINUOUS_GENES):
        ind1[i] = cont1[j]
        ind2[i] = cont2[j]

    clip_to_bounds(ind1)
    clip_to_bounds(ind2)

    return ind1, ind2


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------


def mutate_hybrid(ind: list, sigma_fraction: float = 0.10) -> Tuple[list]:
    """Hybrid mutation: random replacement for discrete, Gaussian for continuous.

    Discrete genes (indicator type + period):
      - Each gene independently replaced with a random valid value, prob=0.05.
      - Random replacement (not Gaussian) respects integer semantics.

    Continuous genes (weights, threshold, SL%, TP%, position size):
      - Gaussian perturbation, per-gene sigma = sigma_fraction × gene_range.
      - indpb=0.2: each continuous gene mutated independently with 20% chance.
      - Bounds enforced via clip_to_bounds after mutation.

    Args:
        ind:            DEAP Individual of length 13.
        sigma_fraction: Fraction of gene range to use as Gaussian sigma.
                        Anneals via get_sigma_fraction(). Default 0.10.

    Returns:
        (ind,) — single-element tuple (DEAP mutation convention).
    """
    # Discrete: random replacement with low probability
    for i, name in zip(DISCRETE_GENES, DISCRETE_GENE_NAMES):
        if random.random() < 0.05:
            lo, hi = GENE_BOUNDS[name]
            ind[i] = float(random.randint(int(lo), int(hi)))

    # Continuous: per-gene Gaussian perturbation
    cont_vals = [ind[i] for i in CONTINUOUS_GENES]
    sigmas = [sigma_fraction * GENE_RANGES[name] for name in CONTINUOUS_GENE_NAMES]

    # tools.mutGaussian expects a flat sigma scalar or list; use list form
    for j in range(len(cont_vals)):
        if random.random() < 0.2:  # indpb=0.2
            cont_vals[j] += random.gauss(0.0, sigmas[j])

    for j, i in enumerate(CONTINUOUS_GENES):
        ind[i] = cont_vals[j]

    clip_to_bounds(ind)
    return (ind,)


# ---------------------------------------------------------------------------
# Adaptive sigma schedule
# ---------------------------------------------------------------------------


def get_sigma_fraction(gen: int, total_gens: int = 1000) -> float:
    """Return mutation sigma fraction based on evolution progress.

    Anneals exploration strength:
      - 0–20%  of gens: 0.20 (strong exploration — wide range)
      - 20–60% of gens: 0.10 (moderate — balanced)
      - 60–100%of gens: 0.05 (fine refinement — converging)

    Args:
        gen:        Current generation (0-indexed).
        total_gens: Total planned generations (default 1000).

    Returns:
        sigma_fraction float.
    """
    progress = gen / max(1, total_gens)
    if progress < 0.2:
        return 0.20
    elif progress < 0.6:
        return 0.10
    else:
        return 0.05
