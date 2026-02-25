"""Experiment 05: Phase 4 Export & Integration — end-to-end demo.

Demonstrates the full Phase 4 export pipeline on synthetic SPY-like data:
  1. Config   — load/save OptimizationConfig
  2. Codegen  — generate_backtest_code + YAML strategy round-trip
  3. Reporter — build_report + format_text + save_csv + load_csv
  4. Viz      — plot_equity_curves + plot_regime_performance
  5. CLI      — show available commands

Usage:
    python experiments/05_phase4_export.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backtesting.numba_engine import NumbaBacktestEngine, warmup_jit
from src.config import OptimizationConfig, DataConfig, GAConfig, BacktestConfig, OutputConfig
from src.export.codegen import export_strategy_yaml, generate_backtest_code, load_strategy_yaml
from src.export.reporter import build_report, format_text, load_csv, save_csv
from src.export.visualizer import plot_equity_curves, plot_regime_performance
from src.indicators.calculator import build_indicator_cache
from src.indicators.signal_generator import generate_signals_weighted_sum
from src.robustness.regime_classifier import run_regime_testing

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Synthetic data generator
# ---------------------------------------------------------------------------

def generate_synthetic_ohlcv(n_bars: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, 0.012, n_bars)
    close = 100.0 * np.exp(np.cumsum(returns))
    noise = rng.uniform(0.001, 0.005, n_bars)
    high  = close * (1 + noise)
    low   = close * (1 - noise)
    open_ = np.roll(close, 1); open_[0] = close[0]
    volume = rng.integers(500_000, 3_000_000, n_bars).astype(float)
    return pd.DataFrame({
        "date":   pd.date_range("2010-01-01", periods=n_bars, freq="D"),
        "open":   open_.astype(np.float32),
        "high":   high.astype(np.float32),
        "low":    low.astype(np.float32),
        "close":  close.astype(np.float32),
        "volume": volume,
    })


BEST_INDIVIDUAL = [0, 14, 1.2, 5, 9, 0.8, 13, 20, 1.0, 0.3, 0.04, 0.08, 1.0]
WARMUP_BARS = 252
NORM_WINDOW = 252
RESULTS_DIR = Path("results/phase4_demo")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Phase 4 export experiment starting …")

    warmup_jit()
    engine = NumbaBacktestEngine()
    df = generate_synthetic_ohlcv(WARMUP_BARS + 800, seed=42)

    # Build a quick backtest result for demo purposes
    cache = build_indicator_cache(df, normalization_window=NORM_WINDOW)
    sliced = {k: v[WARMUP_BARS:] for k, v in cache.items()}
    prices = df["close"].values[WARMUP_BARS:].astype(np.float32)
    n_train = int(len(prices) * 0.40)
    train_prices = prices[:n_train]
    test_prices  = prices[n_train:]
    train_cache  = {k: v[:n_train] for k, v in sliced.items()}
    test_cache   = {k: v[n_train:] for k, v in sliced.items()}

    sl = float(BEST_INDIVIDUAL[10])
    tp = float(BEST_INDIVIDUAL[11])
    pm = float(BEST_INDIVIDUAL[12])
    train_result = engine.run(
        generate_signals_weighted_sum(BEST_INDIVIDUAL, train_cache), train_prices, sl, tp, pm
    )
    test_result = engine.run(
        generate_signals_weighted_sum(BEST_INDIVIDUAL, test_cache), test_prices, sl, tp, pm
    )

    # -----------------------------------------------------------------------
    # 1. Config
    # -----------------------------------------------------------------------
    log.info("--- 1. Config ---")
    cfg = OptimizationConfig(
        data=DataConfig(ticker="SPY", start_date="2010-01-01", end_date="2024-12-31"),
        ga=GAConfig(population_size=200, n_generations=1000),
        backtest=BacktestConfig(train_fraction=0.40),
        output=OutputConfig(dir=str(RESULTS_DIR)),
    )
    from src.config import save_config, load_config
    cfg_path = str(RESULTS_DIR / "config.yaml")
    save_config(cfg, cfg_path)
    loaded_cfg = load_config(cfg_path)
    log.info("  Saved + loaded config  ticker=%s  pop=%d", loaded_cfg.data.ticker, loaded_cfg.ga.population_size)

    # -----------------------------------------------------------------------
    # 2. Code generation
    # -----------------------------------------------------------------------
    log.info("--- 2. Code generation ---")
    code = generate_backtest_code(BEST_INDIVIDUAL)
    code_path = RESULTS_DIR / "strategy.py"
    code_path.write_text(code, encoding="utf-8")
    log.info("  Generated strategy.py  (%d bytes)", len(code))

    yaml_path = str(RESULTS_DIR / "individual.yaml")
    export_strategy_yaml(BEST_INDIVIDUAL, yaml_path)
    reloaded = load_strategy_yaml(yaml_path)
    assert reloaded == [float(g) for g in BEST_INDIVIDUAL], "YAML round-trip mismatch"
    log.info("  Strategy YAML round-trip: OK")

    # -----------------------------------------------------------------------
    # 3. Performance report
    # -----------------------------------------------------------------------
    log.info("--- 3. Performance report ---")
    test_report = build_report(test_result)
    log.info("  Test  PF=%.4f  trades=%d  Sharpe=%.4f",
             test_report.profit_factor, test_report.n_trades, test_report.sharpe_ratio)

    print()
    print(format_text(test_report))
    print()

    csv_path = str(RESULTS_DIR / "report.csv")
    save_csv(test_report, csv_path)
    reloaded_report = load_csv(csv_path)
    assert abs(reloaded_report.profit_factor - test_report.profit_factor) < 1e-9
    log.info("  CSV round-trip: OK")

    # -----------------------------------------------------------------------
    # 4. Visualisation
    # -----------------------------------------------------------------------
    log.info("--- 4. Visualisation ---")
    equity_path = str(RESULTS_DIR / "equity_curves.png")
    plot_equity_curves(
        train_result.equity_curve,
        test_result.equity_curve,
        title="Phase 4 Demo — Equity Curves",
        save_path=equity_path,
    )
    log.info("  Equity curves saved: %s", equity_path)

    regime_result = run_regime_testing(
        BEST_INDIVIDUAL, df, engine,
        normalization_window=NORM_WINDOW, warmup_bars=WARMUP_BARS,
    )
    regime_path = str(RESULTS_DIR / "regime_performance.png")
    plot_regime_performance(regime_result, save_path=regime_path)
    log.info("  Regime chart saved : %s", regime_path)

    # -----------------------------------------------------------------------
    # 5. CLI preview
    # -----------------------------------------------------------------------
    log.info("--- 5. CLI commands available ---")
    log.info("  ga-trading-sys init     --output config.yaml")
    log.info("  ga-trading-sys optimize --config config.yaml")
    log.info("  ga-trading-sys validate --results %s", RESULTS_DIR)
    log.info("  ga-trading-sys backtest --individual %s", yaml_path)

    log.info("Phase 4 experiment complete. Results in %s", RESULTS_DIR)


if __name__ == "__main__":
    main()
