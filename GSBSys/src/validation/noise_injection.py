"""Noise injection robustness testing — Phase 2, Layer 3.

Re-runs the backtest 8 times with perturbed input data to verify the
strategy is not brittle to small data imperfections.  A strategy that
fails on ±1% price noise is unlikely to survive live trading slippage.

Variants (8 total):
  Price noise:    +1%, -1%, +2%, -2% multiplicative perturbation on all bars
  Volume noise:   +10%, -10% on volume (affects OBV/MFI indicators)
  Entry shift:    +1 day, -1 day (simulates delayed execution)

Pass criteria (from PRD Section 3.4):
  MVP tier:        >= 5/8 variants profitable (62.5%)
  Production tier: >= 6/8 variants profitable (75.0%)

Each variant uses a fixed random seed for reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.backtesting.engine import BacktestEngine, BacktestResult
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum

# ---------------------------------------------------------------------------
# Variant definitions
# ---------------------------------------------------------------------------

#: (variant_name, price_noise, volume_noise, entry_shift_days, seed)
NOISE_VARIANTS: List[Tuple[str, float, float, int, int]] = [
    ("price_plus_1pct",    +0.01,  0.0,   0, 42),
    ("price_minus_1pct",   -0.01,  0.0,   0, 43),
    ("price_plus_2pct",    +0.02,  0.0,   0, 44),
    ("price_minus_2pct",   -0.02,  0.0,   0, 45),
    ("volume_plus_10pct",   0.0,  +0.10,  0, 46),
    ("volume_minus_10pct",  0.0,  -0.10,  0, 47),
    ("entry_shift_plus1",   0.0,   0.0,  +1, 48),
    ("entry_shift_minus1",  0.0,   0.0,  -1, 49),
]

PROFITABLE_PF: float = 1.0
MVP_MIN_PROFITABLE: int = 5      # 62.5%
PRODUCTION_MIN_PROFITABLE: int = 6  # 75.0%


@dataclass(frozen=True)
class VariantResult:
    """Backtest result for one noise variant.

    Attributes:
        name:          Variant identifier.
        profit_factor: PF from the perturbed backtest.
        n_trades:      Number of completed trades.
        total_pnl:     Net dollar P&L.
        profitable:    True if profit_factor >= 1.0.
    """

    name: str
    profit_factor: float
    n_trades: int
    total_pnl: float
    profitable: bool


@dataclass(frozen=True)
class NoiseResult:
    """Result of the full 8-variant noise injection test.

    Attributes:
        variant_results:    One VariantResult per variant.
        n_profitable:       Count of profitable variants.
        passed_mvp:         True if n_profitable >= 5.
        passed_production:  True if n_profitable >= 6.
    """

    variant_results: List[VariantResult]
    n_profitable: int
    passed_mvp: bool
    passed_production: bool


# ---------------------------------------------------------------------------
# Data perturbation helpers
# ---------------------------------------------------------------------------

def _perturb_prices(df: pd.DataFrame, price_noise: float, seed: int) -> pd.DataFrame:
    """Multiply all OHLCV price columns by (1 + noise), noise drawn per bar."""
    if price_noise == 0.0:
        return df
    rng = np.random.default_rng(seed)
    n = len(df)
    factors = 1.0 + rng.uniform(0.0, abs(price_noise), n) * np.sign(price_noise)
    out = df.copy()
    for col in ("open", "high", "low", "close"):
        out[col] = df[col] * factors
    # Enforce high >= low after perturbation
    out["high"] = np.maximum(out["high"], out["low"])
    return out


def _perturb_volume(df: pd.DataFrame, volume_noise: float, seed: int) -> pd.DataFrame:
    """Scale volume by (1 + volume_noise), clip to minimum 1."""
    if volume_noise == 0.0:
        return df
    rng = np.random.default_rng(seed)
    n = len(df)
    factors = 1.0 + rng.uniform(0.0, abs(volume_noise), n) * np.sign(volume_noise)
    out = df.copy()
    out["volume"] = np.maximum(1.0, df["volume"] * factors)
    return out


def _shift_signals(signals: np.ndarray, shift: int) -> np.ndarray:
    """Shift entry signals by `shift` bars (simulates delayed execution)."""
    if shift == 0:
        return signals
    out = np.zeros_like(signals)
    if shift > 0:
        out[shift:] = signals[:-shift]
    else:
        out[:shift] = signals[-shift:]
    return out


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_noise_injection(
    individual: list,
    df: pd.DataFrame,
    engine: BacktestEngine,
    normalization_window: int = 252,
    warmup_bars: int = 252,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
    position_size_mult: Optional[float] = None,
) -> NoiseResult:
    """Run all 8 noise variants and return profitability results.

    For each variant:
    1. Perturb the input DataFrame (price and/or volume noise)
    2. Rebuild the indicator cache from perturbed data
    3. Generate signals, apply entry shift if specified
    4. Run backtest and record profitability

    Args:
        individual:           13-gene chromosome.
        df:                   Full OHLCV DataFrame (must be pre-validated,
                              includes warmup rows at the top).
        engine:               BacktestEngine implementation.
        normalization_window: Indicator normalization window (default 252).
        warmup_bars:          Bars to discard before backtesting (default 252).
        stop_loss_pct:        Override SL% (default: gene 10).
        take_profit_pct:      Override TP% (default: gene 11).
        position_size_mult:   Override size mult (default: gene 12).

    Returns:
        NoiseResult with per-variant details and overall pass/fail.
    """
    sl_pct   = stop_loss_pct      if stop_loss_pct      is not None else float(individual[10])
    tp_pct   = take_profit_pct    if take_profit_pct    is not None else float(individual[11])
    pos_mult = position_size_mult if position_size_mult is not None else float(individual[12])

    variant_results: List[VariantResult] = []

    for name, price_noise, vol_noise, entry_shift, seed in NOISE_VARIANTS:
        # Apply perturbations
        perturbed = _perturb_prices(df, price_noise, seed)
        perturbed = _perturb_volume(perturbed, vol_noise, seed + 100)

        # Rebuild cache from perturbed data
        cache = build_indicator_cache(perturbed, normalization_window=normalization_window)
        sliced_cache = {k: v[warmup_bars:] for k, v in cache.items()}

        prices = perturbed["close"].values[warmup_bars:].astype(np.float32)
        if len(prices) < 10:
            variant_results.append(VariantResult(
                name=name, profit_factor=0.0, n_trades=0,
                total_pnl=0.0, profitable=False,
            ))
            continue

        signals = generate_signals_weighted_sum(individual, sliced_cache)
        signals = _shift_signals(signals, entry_shift)

        result: BacktestResult = engine.run(signals, prices, sl_pct, tp_pct, pos_mult)

        variant_results.append(VariantResult(
            name=name,
            profit_factor=result.profit_factor,
            n_trades=result.n_trades,
            total_pnl=result.total_pnl,
            profitable=result.profit_factor >= PROFITABLE_PF,
        ))

    n_profitable = sum(r.profitable for r in variant_results)
    return NoiseResult(
        variant_results=variant_results,
        n_profitable=n_profitable,
        passed_mvp=n_profitable >= MVP_MIN_PROFITABLE,
        passed_production=n_profitable >= PRODUCTION_MIN_PROFITABLE,
    )
