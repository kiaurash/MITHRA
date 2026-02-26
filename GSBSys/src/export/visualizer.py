"""Equity-curve and regime-performance visualisations via Matplotlib.

Matplotlib is treated as an optional dependency — if it is not installed
the module still imports and all functions raise ``ImportError`` with a
helpful message only when called.

Usage::

    from src.export.visualizer import plot_equity_curves
    plot_equity_curves(train_equity, test_equity, save_path="results/equity.png")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend (safe for headless environments)
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except ImportError:  # pragma: no cover
    _MATPLOTLIB_AVAILABLE = False


def _require_matplotlib() -> None:
    if not _MATPLOTLIB_AVAILABLE:  # pragma: no cover
        raise ImportError(
            "matplotlib is required for visualisation. "
            "Install it with: pip install matplotlib"
        )


def plot_equity_curves(
    train_equity: np.ndarray,
    test_equity: np.ndarray,
    title: str = "Equity Curves",
    save_path: Optional[Union[str, Path]] = None,
    show: bool = False,
) -> None:
    """Plot train and test equity curves side-by-side.

    Args:
        train_equity: 1-D array of equity values (training period).
        test_equity:  1-D array of equity values (test / OOS period).
        title:        Figure title.
        save_path:    If provided, save PNG to this path (parent dirs created).
        show:         If True, call ``plt.show()`` (interactive mode).

    Raises:
        ImportError: If matplotlib is not installed.
    """
    _require_matplotlib()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(title)

    for ax, equity, label, color in zip(
        axes,
        [train_equity, test_equity],
        ["Train", "Test (OOS)"],
        ["steelblue", "darkorange"],
    ):
        ax.plot(equity, color=color, linewidth=1.5)
        ax.set_title(label)
        ax.set_xlabel("Bar")
        ax.set_ylabel("Equity ($)")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        os.makedirs(save_path.parent, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()  # pragma: no cover

    plt.close(fig)


def plot_regime_performance(
    regime_result,
    save_path: Optional[Union[str, Path]] = None,
    show: bool = False,
) -> None:
    """Bar chart of per-regime profit factors.

    Args:
        regime_result: ``RegimeTestResult`` from regime_classifier.
        save_path:     If provided, save PNG to this path.
        show:          If True, call ``plt.show()``.

    Raises:
        ImportError: If matplotlib is not installed.
    """
    _require_matplotlib()

    perfs = [regime_result.bull, regime_result.bear, regime_result.sideways]
    labels = [p.label.value.capitalize() for p in perfs]
    pf_values = []
    for p in perfs:
        pf = p.profit_factor if p.profit_factor != float("inf") else 10.0
        pf_values.append(pf)

    colors = ["steelblue" if pf >= 1.0 else "tomato" for pf in pf_values]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, pf_values, color=colors, edgecolor="black", linewidth=0.8)
    ax.axhline(1.0, color="black", linewidth=1.0, linestyle="--", alpha=0.6)
    ax.set_title("Profit Factor by Market Regime")
    ax.set_ylabel("Profit Factor")
    ax.set_ylim(bottom=0)
    ax.grid(True, axis="y", alpha=0.3)

    for bar, pf in zip(bars, pf_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{pf:.2f}",
            ha="center", va="bottom", fontsize=9,
        )

    plt.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        os.makedirs(save_path.parent, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()  # pragma: no cover

    plt.close(fig)
