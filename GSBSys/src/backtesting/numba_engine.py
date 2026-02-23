"""Numba-accelerated backtest engine.

The core loop (_backtest_core) is JIT-compiled with nopython=True for maximum
speed.  With NUMBA_DISABLE_JIT=1 (set in conftest.py), it runs as pure Python
— slow but correct, enabling fast unit tests.

Performance targets:
  - <50ms p95 per fitness evaluation on ~3,750 post-warmup daily bars
  - float32 arrays halve memory bandwidth vs float64
  - fastmath=True safe: no NaN after signal generation (NaN bars → signal=0)
  - cache=True: compiled bytecode persisted to disk, instant after first run

Position sizing (percentage-based, scales across tickers):
  contracts = equity × risk_per_trade × position_size_mult
              / (price × stop_loss_pct)
  Example: $100k equity, 2% risk, 6% SL, SPY=$500
    → contracts = 100000 × 0.02 × 1.0 / (500 × 0.06) = 66.7 shares
  Same formula on IWM=$200: → 166.7 shares (correct — same dollar risk)
"""

from __future__ import annotations

import logging
import os

import numpy as np

try:
    from numba import jit as _numba_jit
    _NUMBA_AVAILABLE = True
except ImportError:
    _NUMBA_AVAILABLE = False

from src.backtesting.engine import BacktestEngine, BacktestResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JIT decorator — falls back to identity decorator when Numba unavailable
# ---------------------------------------------------------------------------

if _NUMBA_AVAILABLE and os.environ.get("NUMBA_DISABLE_JIT", "0") != "1":
    def _jit(**kwargs):
        return _numba_jit(**kwargs)
else:
    # Pure-Python fallback: ignore all numba kwargs
    def _jit(**kwargs):
        def _passthrough(fn):
            return fn
        return _passthrough


# ---------------------------------------------------------------------------
# Core backtest loop
# ---------------------------------------------------------------------------

@_jit(nopython=True, cache=True, fastmath=True, nogil=True)
def _backtest_core(
    signals: np.ndarray,
    prices: np.ndarray,
    stop_loss_pct: float,
    take_profit_pct: float,
    position_size_mult: float,
    slippage_bps: float,
    starting_capital: float,
    risk_per_trade: float,
) -> tuple:
    """Bar-by-bar backtest loop (Numba nopython).

    Entry logic:
      - Enter long when signals[i] > 0 and no open position.
      - No short entries in Phase 1 (long-only).

    Exit logic (checked before entry on same bar):
      - SL: price return from entry ≤ -stop_loss_pct
      - TP: price return from entry ≥ +take_profit_pct
      - End-of-data: close any open position on final bar.

    Args:
        signals:            float32 shape (T,). Positive = long signal.
        prices:             float32 shape (T,). Close prices.
        stop_loss_pct:      Fraction, e.g. 0.06 = 6%.
        take_profit_pct:    Fraction, e.g. 0.10 = 10%.
        position_size_mult: Risk multiplier [0.5, 2.0].
        slippage_bps:       Slippage fraction per side (5 bps = 0.0005).
        starting_capital:   Initial equity ($100,000 default).
        risk_per_trade:     Fraction of equity risked per trade (0.02 = 2%).

    Returns:
        Tuple: (sharpe, profit_factor, n_trades, total_pnl, avg_trade_pnl,
                equity_curve, returns_arr)
    """
    n = len(prices)
    equity = starting_capital
    equity_curve = np.zeros(n, dtype=np.float32)
    equity_curve[0] = np.float32(equity)

    position = 0.0
    entry_price = 0.0

    # Pre-allocate trade P&L storage (max possible = n/2 trades)
    max_trades = n // 2 + 1
    trade_pnls = np.zeros(max_trades, dtype=np.float32)
    n_trades = 0

    for i in range(1, n):
        # --- Check exit conditions for open position ---
        if position != 0.0:
            price_return = (prices[i] - entry_price) / entry_price
            hit_sl = price_return <= -stop_loss_pct
            hit_tp = price_return >= take_profit_pct

            if hit_sl or hit_tp:
                pnl = (prices[i] - entry_price) * position
                slip = prices[i] * abs(position) * slippage_bps
                net_pnl = pnl - slip
                equity += net_pnl
                if n_trades < max_trades:
                    trade_pnls[n_trades] = np.float32(net_pnl)
                n_trades += 1
                position = 0.0

        # --- Check entry conditions ---
        if position == 0.0 and signals[i] > 0.0:
            sl_dollars = prices[i] * stop_loss_pct
            if sl_dollars > 0.0:
                contracts = (equity * risk_per_trade * position_size_mult) / sl_dollars
                contracts = max(1.0, contracts)
            else:
                contracts = 1.0
            slip = prices[i] * contracts * slippage_bps
            equity -= slip
            position = contracts
            entry_price = prices[i]

        # --- Update equity curve (mark-to-market) ---
        if position != 0.0:
            equity_curve[i] = np.float32(equity + (prices[i] - entry_price) * position)
        else:
            equity_curve[i] = np.float32(equity)

    # --- Close any remaining position at end of data ---
    if position != 0.0:
        pnl = (prices[n - 1] - entry_price) * position
        slip = prices[n - 1] * abs(position) * slippage_bps
        net_pnl = pnl - slip
        equity += net_pnl
        if n_trades < max_trades:
            trade_pnls[n_trades] = np.float32(net_pnl)
        n_trades += 1
        equity_curve[n - 1] = np.float32(equity)

    # --- Degenerate: no trades ---
    if n_trades == 0:
        empty = np.zeros(1, dtype=np.float32)
        return 0.0, 1.0, 0, 0.0, 0.0, equity_curve, empty

    trades_arr = trade_pnls[:n_trades]
    returns_arr = trades_arr / np.float32(starting_capital)

    mean_r = np.mean(returns_arr)
    std_r = np.std(returns_arr)
    sharpe = (mean_r / (std_r + 1e-10)) * np.sqrt(252.0)

    total_pnl = float(np.sum(trades_arr))
    avg_trade = total_pnl / n_trades

    # Profit factor
    gross_profit = 0.0
    gross_loss = 0.0
    for k in range(n_trades):
        if trades_arr[k] > 0.0:
            gross_profit += trades_arr[k]
        elif trades_arr[k] < 0.0:
            gross_loss -= trades_arr[k]

    if gross_loss < 1e-10:
        pf = 999.0
    else:
        pf = gross_profit / gross_loss

    return float(sharpe), float(pf), n_trades, total_pnl, float(avg_trade), equity_curve, returns_arr


# ---------------------------------------------------------------------------
# Engine class
# ---------------------------------------------------------------------------


class NumbaBacktestEngine:
    """BacktestEngine implementation backed by the Numba JIT core.

    Satisfies the BacktestEngine Protocol.

    Args:
        starting_capital: Initial equity. Default $100,000.
        risk_per_trade:   Fraction of equity risked per trade. Default 0.02.
        slippage_bps:     One-way slippage in basis points. Default 5 bps.
    """

    def __init__(
        self,
        starting_capital: float = 100_000.0,
        risk_per_trade: float = 0.02,
        slippage_bps: float = 0.0005,
    ) -> None:
        self.starting_capital = starting_capital
        self.risk_per_trade = risk_per_trade
        self.slippage_bps = slippage_bps

    def run(
        self,
        signals: np.ndarray,
        prices: np.ndarray,
        stop_loss_pct: float,
        take_profit_pct: float,
        position_size_mult: float,
    ) -> BacktestResult:
        """Run the backtest and return a BacktestResult.

        Args:
            signals:            float32/float64 array; NaN values treated as 0.
            prices:             float32/float64 close prices.
            stop_loss_pct:      Fraction, e.g. 0.06 = 6%.
            take_profit_pct:    Fraction, e.g. 0.10 = 10%.
            position_size_mult: Multiplier [0.5, 2.0].
        """
        # Ensure correct dtype and replace NaN signals with 0
        sig = np.where(np.isnan(signals), 0.0, signals).astype(np.float32)
        pri = np.asarray(prices, dtype=np.float32)

        sharpe, pf, n_trades, total_pnl, avg_trade, equity_curve, returns_arr = _backtest_core(
            sig, pri,
            float(stop_loss_pct),
            float(take_profit_pct),
            float(position_size_mult),
            self.slippage_bps,
            self.starting_capital,
            self.risk_per_trade,
        )

        return BacktestResult(
            sharpe_ratio=sharpe,
            profit_factor=pf,
            n_trades=n_trades,
            total_pnl=total_pnl,
            avg_trade_pnl=avg_trade,
            equity_curve=equity_curve,
            returns=returns_arr,
        )


# ---------------------------------------------------------------------------
# JIT pre-warm
# ---------------------------------------------------------------------------


def warmup_jit() -> None:
    """Trigger Numba JIT compilation with dummy arrays.

    Call once at program startup.  Subsequent calls use cached compiled code
    (no overhead).  First call: ~2–10 seconds (one-time cost, then cached
    to disk by Numba's cache=True).

    With NUMBA_DISABLE_JIT=1, this is a no-op (pure Python, instant).
    """
    logger.info("Pre-warming Numba JIT (first call may take 2–10 s)...")
    dummy_signals = np.zeros(100, dtype=np.float32)
    dummy_prices = np.ones(100, dtype=np.float32) * 100.0
    _backtest_core(
        dummy_signals, dummy_prices,
        0.06, 0.10, 1.0,
        0.0005, 100_000.0, 0.02,
    )
    logger.info("Numba JIT warm-up complete.")
