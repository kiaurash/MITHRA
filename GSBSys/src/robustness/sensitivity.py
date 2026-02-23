"""Sensitivity analysis — Phase 3, Module 2.

Measures how much each gene of the chromosome contributes to strategy
fragility.  For each gene we run two extra backtests (gene × 1.10 and
gene × 0.90) and record the change in test profit factor.

A gene with high sensitivity AND high family-grouping CoV is a red flag:
the GA found a "knife-edge" parameter that isn't stable and doesn't
generalise.

The optional FamilyResult argument enables Pearson correlation between
gene sensitivities and CoV values, providing a direct confirmation of
the instability hypothesis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

from src.backtesting.engine import BacktestEngine, BacktestResult
from src.ga.chromosome import GENE_NAMES, clip_to_bounds
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum
from src.utils.stats import pearsonr_fast
from src.validation.family_grouping import FamilyResult

#: Fraction by which each gene is perturbed (±10%).
DEFAULT_PERTURBATION: float = 0.10


@dataclass(frozen=True)
class GeneSensitivity:
    """Sensitivity of one gene to ±10% perturbation.

    Attributes:
        gene_name:   Human-readable gene identifier.
        gene_idx:    Position in the 13-gene chromosome.
        base_value:  Unperturbed gene value.
        plus_pf:     Test PF with gene multiplied by (1 + perturbation).
        minus_pf:    Test PF with gene multiplied by (1 - perturbation).
        sensitivity: abs(plus_pf - minus_pf) / max(base_pf, 1e-6).
    """

    gene_name: str
    gene_idx: int
    base_value: float
    plus_pf: float
    minus_pf: float
    sensitivity: float


@dataclass(frozen=True)
class SensitivityResult:
    """Result of the per-gene sensitivity sweep.

    Attributes:
        gene_sensitivities: One GeneSensitivity per gene.
        base_pf:            Test PF of the unperturbed individual.
        mean_sensitivity:   Mean sensitivity across all 13 genes.
        most_sensitive_gene: Name of the gene with highest sensitivity.
        cov_correlation:    Pearson r(sensitivity, CoV) when family provided.
                            None if FamilyResult not supplied or < 3 genes.
    """

    gene_sensitivities: List[GeneSensitivity]
    base_pf: float
    mean_sensitivity: float
    most_sensitive_gene: str
    cov_correlation: Optional[float]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_backtest_for_individual(
    individual: list,
    sliced_cache: dict,
    prices: np.ndarray,
    engine: BacktestEngine,
    sl_pct: float,
    tp_pct: float,
    pos_mult: float,
) -> float:
    """Return test profit factor for a given individual."""
    signals = generate_signals_weighted_sum(individual, sliced_cache)
    result: BacktestResult = engine.run(signals, prices, sl_pct, tp_pct, pos_mult)
    return result.profit_factor


def _perturb_gene(individual: list, gene_idx: int, factor: float) -> list:
    """Return a copy with individual[gene_idx] multiplied by factor."""
    perturbed = list(individual)
    perturbed[gene_idx] = float(individual[gene_idx]) * factor
    return clip_to_bounds(perturbed)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_sensitivity_analysis(
    individual: list,
    df: pd.DataFrame,
    engine: BacktestEngine,
    normalization_window: int = 252,
    warmup_bars: int = 252,
    train_fraction: float = 0.40,
    perturbation: float = DEFAULT_PERTURBATION,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
    position_size_mult: Optional[float] = None,
    family_result: Optional[FamilyResult] = None,
) -> SensitivityResult:
    """Sweep ±perturbation over each gene and measure PF change.

    Uses the same train/test split as the fitness function (40/60).

    Args:
        individual:           13-gene chromosome.
        df:                   Full OHLCV DataFrame (includes warmup rows).
        engine:               BacktestEngine implementation.
        normalization_window: Rolling indicator normalisation window.
        warmup_bars:          Bars to discard at start (default 252).
        train_fraction:       Train/test split fraction (default 0.40).
        perturbation:         Fractional gene perturbation (default 0.10).
        stop_loss_pct:        Override SL% (default: gene 10).
        take_profit_pct:      Override TP% (default: gene 11).
        position_size_mult:   Override size mult (default: gene 12).
        family_result:        Optional FamilyResult for CoV correlation.

    Returns:
        SensitivityResult with per-gene sensitivities and optional
        CoV-sensitivity correlation.
    """
    sl_pct   = stop_loss_pct      if stop_loss_pct      is not None else float(individual[10])
    tp_pct   = take_profit_pct    if take_profit_pct    is not None else float(individual[11])
    pos_mult = position_size_mult if position_size_mult is not None else float(individual[12])

    # Build indicator cache once
    cache = build_indicator_cache(df, normalization_window=normalization_window)
    post_warmup_len = len(df) - warmup_bars
    sliced_cache = {k: v[warmup_bars:] for k, v in cache.items()}
    prices_all   = df["close"].values[warmup_bars:].astype(np.float32)

    n_train = int(post_warmup_len * train_fraction)
    test_cache  = {k: v[n_train:] for k, v in sliced_cache.items()}
    test_prices = prices_all[n_train:]

    if len(test_prices) < 10:
        # Degenerate case: return zero-sensitivity result
        zero_gs = [
            GeneSensitivity(
                gene_name=name, gene_idx=i,
                base_value=float(individual[i]),
                plus_pf=0.0, minus_pf=0.0, sensitivity=0.0,
            )
            for i, name in enumerate(GENE_NAMES)
        ]
        return SensitivityResult(
            gene_sensitivities=zero_gs, base_pf=0.0,
            mean_sensitivity=0.0, most_sensitive_gene=GENE_NAMES[0],
            cov_correlation=None,
        )

    # Baseline PF
    base_pf = _run_backtest_for_individual(
        individual, test_cache, test_prices, engine, sl_pct, tp_pct, pos_mult
    )

    # Per-gene sweep
    gene_sensitivities: List[GeneSensitivity] = []
    for idx, name in enumerate(GENE_NAMES):
        plus_ind  = _perturb_gene(individual, idx, 1.0 + perturbation)
        minus_ind = _perturb_gene(individual, idx, 1.0 - perturbation)

        # Re-derive SL/TP/pos_mult for perturbed individual
        plus_sl  = plus_ind[10];  plus_tp  = plus_ind[11];  plus_pm  = plus_ind[12]
        minus_sl = minus_ind[10]; minus_tp = minus_ind[11]; minus_pm = minus_ind[12]

        plus_pf  = _run_backtest_for_individual(plus_ind,  test_cache, test_prices, engine, plus_sl,  plus_tp,  plus_pm)
        minus_pf = _run_backtest_for_individual(minus_ind, test_cache, test_prices, engine, minus_sl, minus_tp, minus_pm)

        sensitivity = abs(plus_pf - minus_pf) / max(abs(base_pf), 1e-6)

        gene_sensitivities.append(GeneSensitivity(
            gene_name=name,
            gene_idx=idx,
            base_value=float(individual[idx]),
            plus_pf=plus_pf,
            minus_pf=minus_pf,
            sensitivity=sensitivity,
        ))

    sensitivities = [gs.sensitivity for gs in gene_sensitivities]
    mean_sens = float(np.mean(sensitivities))
    most_sensitive = gene_sensitivities[int(np.argmax(sensitivities))].gene_name

    # Optional CoV correlation
    cov_correlation: Optional[float] = None
    if family_result is not None and len(GENE_NAMES) >= 3:
        covs = [family_result.cov_per_gene.get(name, 0.0) for name in GENE_NAMES]
        try:
            cov_correlation = float(pearsonr_fast(
                np.array(sensitivities, dtype=np.float64),
                np.array(covs, dtype=np.float64),
            ))
        except (ValueError, ZeroDivisionError):
            cov_correlation = None

    return SensitivityResult(
        gene_sensitivities=gene_sensitivities,
        base_pf=base_pf,
        mean_sensitivity=mean_sens,
        most_sensitive_gene=most_sensitive,
        cov_correlation=cov_correlation,
    )
