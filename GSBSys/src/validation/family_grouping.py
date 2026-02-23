"""Family grouping / parameter stability analysis — Phase 2, Layer 4.

Analyses the 10 restart results from Phase 1 to determine whether the GA
converged to a stable family of solutions.  Low coefficient of variation
(CoV = std / |mean|) across restarts means different starting points found
similar optima — a strong signal of a genuine strategy rather than overfitting.

Pass criteria (from PRD Section 3.5):
  MVP tier:        mean_cov <= 0.60
  Production tier: mean_cov <= 0.50

CoV is computed per gene across all n restart results, then averaged.
Genes with |mean| < 1e-6 are assigned CoV = 0.0 (consensus at near-zero).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from src.ga.chromosome import GENE_NAMES

#: MVP pass threshold (relaxed — proof-of-concept).
MVP_COV_THRESHOLD: float = 0.60

#: Production pass threshold (strict — commercial grade).
PRODUCTION_COV_THRESHOLD: float = 0.50


@dataclass(frozen=True)
class FamilyResult:
    """Result of the family grouping / parameter stability analysis.

    Attributes:
        cov_per_gene:          CoV for each of the 13 genes.
        mean_cov:              Mean CoV across all genes.
        passed_mvp:            True if mean_cov <= 0.60.
        passed_production:     True if mean_cov <= 0.50.
        n_profitable_restarts: Count of restarts with fitness > 0.
        n_restarts:            Total number of restart results analysed.
    """

    cov_per_gene: Dict[str, float]
    mean_cov: float
    passed_mvp: bool
    passed_production: bool
    n_profitable_restarts: int
    n_restarts: int


def run_family_grouping(restart_results: List[dict]) -> FamilyResult:
    """Compute per-gene CoV and mean CoV across restart results.

    Args:
        restart_results: List of dicts, each with at least:
            - ``best_individual``: list of 13 gene values
            - ``best_fitness``:    float fitness score (> 0 = profitable)

    Returns:
        FamilyResult with per-gene CoV, mean CoV, and pass/fail flags.

    Raises:
        ValueError: If restart_results is empty or any individual has wrong length.
    """
    if not restart_results:
        raise ValueError("restart_results must not be empty.")

    n = len(restart_results)
    n_genes = len(GENE_NAMES)

    # Build matrix: shape (n_restarts, n_genes)
    matrix = np.zeros((n, n_genes), dtype=np.float64)
    for i, res in enumerate(restart_results):
        ind = res["best_individual"]
        if len(ind) != n_genes:
            raise ValueError(
                f"Restart {i}: expected {n_genes} genes, got {len(ind)}."
            )
        matrix[i] = [float(g) for g in ind]

    # Per-gene CoV
    cov_per_gene: Dict[str, float] = {}
    for j, name in enumerate(GENE_NAMES):
        col = matrix[:, j]
        mu = np.mean(col)
        sigma = np.std(col, ddof=1) if n > 1 else 0.0
        if abs(mu) < 1e-6:
            cov = 0.0  # consensus at near-zero
        else:
            cov = sigma / abs(mu)
        cov_per_gene[name] = float(cov)

    mean_cov = float(np.mean(list(cov_per_gene.values())))

    n_profitable = sum(
        1 for r in restart_results if float(r.get("best_fitness", 0.0)) > 0.0
    )

    return FamilyResult(
        cov_per_gene=cov_per_gene,
        mean_cov=mean_cov,
        passed_mvp=mean_cov <= MVP_COV_THRESHOLD,
        passed_production=mean_cov <= PRODUCTION_COV_THRESHOLD,
        n_profitable_restarts=n_profitable,
        n_restarts=n,
    )
