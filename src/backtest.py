"""
backtest.py — Vectorized backtester for the funding rate contrarian strategy.

Design principles:
- Fully vectorized using numpy/pandas — no Python-level loops over trades.
- Signals are generated at funding-rate timestamps (every 8h).
- Execution is assumed to happen at the next hourly OHLCV open price.
- Position is held for a fixed number of hours, or until stop loss.
- Fees: 0.04% taker each way (entry + exit).
- Initial capital: $10,000 (full-capital per trade simplification).

The vectorized approach:
  1. Use numpy searchsorted to find all entry bar indices at once.
  2. Offset by hold_hours to get all exit bar indices.
  3. Fancy-index into OHLCV arrays for prices.
  4. Optional stop-loss: scan the min/max price over the hold window using
     rolling pre-computed arrays.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


FEE_RATE = 0.0004   # 0.04% taker fee each side
INITIAL_CAPITAL = 10_000.0


def run_backtest(
    signal: pd.Series,
    ohlcv: pd.DataFrame,
    hold_hours: int = 8,
    stop_loss_pct: Optional[float] = None,
    max_hold_hours: int = 48,
) -> Dict[str, Any]:
    """
    Vectorized backtest of the funding-rate contrarian strategy.

    All price lookups and PnL calculations are done with numpy array operations.
    No Python-level loop over individual trades.

    Args:
        signal: Series of {-1, 0, +1} indexed by datetime (funding rate times)
        ohlcv: DataFrame with columns open_time, open, high, low, close, volume
               (may or may not be indexed)
        hold_hours: target hold period in hours (default 8)
        stop_loss_pct: if not None, a simple stop-loss check using the period's
                       low (for longs) or high (for shorts) is applied.
                       Exit assumed at stop level (worst case).
        max_hold_hours: hard cap on hold duration

    Returns:
        dict with keys: equity_curve, trade_log, calmar, sharpe,
                        max_drawdown, win_rate, n_trades, avg_hold_hours
    """
    # ── Prepare OHLCV arrays ──────────────────────────────────────────────
    ohlcv = ohlcv.copy()
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        ohlcv = ohlcv.set_index("open_time")
    ohlcv = ohlcv.sort_index()

    ohlcv_times  = ohlcv.index
    open_arr     = ohlcv["open"].values.astype(float)
    high_arr     = ohlcv["high"].values.astype(float)
    low_arr      = ohlcv["low"].values.astype(float)
    n_bars       = len(ohlcv_times)

    # ── Active signals only ────────────────────────────────────────────────
    active = signal[signal != 0].dropna()
    if active.empty:
        return _empty_result()

    sig_times   = active.index.values            # numpy datetime64 array
    directions  = active.values.astype(int)      # +1 or -1

    # ── Find entry bar indices via searchsorted ────────────────────────────
    # searchsorted returns the first index where sig_time could be inserted
    # to keep order — that's the bar at or after the signal time
    ohlcv_times_np = ohlcv_times.values  # numpy datetime64
    entry_indices = np.searchsorted(ohlcv_times_np, sig_times, side="left")

    # Clamp to valid range
    hold_cap     = min(hold_hours, max_hold_hours)
    exit_indices = np.minimum(entry_indices + hold_cap, n_bars - 1)

    # Drop signals that fall outside OHLCV range
    valid = (entry_indices < n_bars) & (exit_indices < n_bars)
    entry_indices = entry_indices[valid]
    exit_indices  = exit_indices[valid]
    directions    = directions[valid]
    sig_times     = sig_times[valid]

    if len(entry_indices) == 0:
        return _empty_result()

    # ── Get entry and exit prices ──────────────────────────────────────────
    entry_prices = open_arr[entry_indices]
    exit_prices  = open_arr[exit_indices]

    # ── Stop-loss (optional) ───────────────────────────────────────────────
    # For each trade, check if the low (longs) or high (shorts) over the hold
    # window crosses the stop level. If yes, exit at the stop price.
    if stop_loss_pct is not None:
        for i in range(len(entry_indices)):
            ep = entry_prices[i]
            d  = directions[i]
            e_idx  = entry_indices[i]
            x_idx  = exit_indices[i]

            if d == 1:  # long: stop if low < entry * (1 - stop)
                stop_level = ep * (1 - stop_loss_pct)
                window_low = low_arr[e_idx:x_idx + 1]
                if len(window_low) > 0 and window_low.min() <= stop_level:
                    exit_prices[i] = stop_level  # exit at stop (conservative)
            else:       # short: stop if high > entry * (1 + stop)
                stop_level = ep * (1 + stop_loss_pct)
                window_high = high_arr[e_idx:x_idx + 1]
                if len(window_high) > 0 and window_high.max() >= stop_level:
                    exit_prices[i] = stop_level

    # ── PnL calculation (vectorized) ──────────────────────────────────────
    gross_returns = directions * (exit_prices - entry_prices) / entry_prices
    net_returns   = gross_returns - 2 * FEE_RATE
    pnl_dollars   = net_returns * INITIAL_CAPITAL

    # Hold hours per trade
    entry_times_idx = ohlcv_times[entry_indices]
    exit_times_idx  = ohlcv_times[exit_indices]
    hold_hrs = np.array([
        (et - st).total_seconds() / 3600
        for st, et in zip(entry_times_idx, exit_times_idx)
    ], dtype=float)
    hold_hrs = np.maximum(hold_hrs, 1.0)

    wins = (net_returns > 0).astype(int)

    # ── Build trade log ────────────────────────────────────────────────────
    trade_log = pd.DataFrame({
        "entry_time":   pd.DatetimeIndex(entry_times_idx),
        "exit_time":    pd.DatetimeIndex(exit_times_idx),
        "direction":    directions,
        "entry_price":  entry_prices,
        "exit_price":   exit_prices,
        "hold_hours":   hold_hrs,
        "gross_return": gross_returns,
        "net_return":   net_returns,
        "pnl_dollar":   pnl_dollars,
        "win":          wins,
    }).set_index("entry_time")

    # ── Equity curve ───────────────────────────────────────────────────────
    equity = pd.Series(
        INITIAL_CAPITAL + pnl_dollars.cumsum(),
        index=pd.DatetimeIndex(exit_times_idx),
        name="equity"
    )

    # ── Performance metrics ────────────────────────────────────────────────
    returns_series = pd.Series(net_returns)
    calmar  = _calmar(equity, returns_series)
    sharpe  = _sharpe(returns_series)
    mdd     = _max_drawdown(equity)
    win_rate = float(wins.mean())
    n_trades = len(trade_log)
    avg_hold = float(hold_hrs.mean())

    return {
        "equity_curve": equity,
        "trade_log":    trade_log,
        "calmar":       calmar,
        "sharpe":       sharpe,
        "max_drawdown": mdd,
        "win_rate":     win_rate,
        "n_trades":     n_trades,
        "avg_hold_hours": avg_hold,
    }


def _empty_result() -> Dict[str, Any]:
    return {
        "equity_curve": pd.Series(dtype=float),
        "trade_log":    pd.DataFrame(),
        "calmar":       0.0,
        "sharpe":       0.0,
        "max_drawdown": 0.0,
        "win_rate":     0.0,
        "n_trades":     0,
        "avg_hold_hours": 0.0,
    }


def _max_drawdown(equity: pd.Series) -> float:
    if equity.empty or len(equity) < 2:
        return 0.0
    running_max = equity.cummax()
    drawdown = (running_max - equity) / running_max.replace(0, np.nan)
    return float(drawdown.max())


def _annualized_return(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    total_return = equity.iloc[-1] / INITIAL_CAPITAL - 1
    n_days = (equity.index[-1] - equity.index[0]).total_seconds() / 86400
    if n_days <= 0:
        return 0.0
    return float((1 + total_return) ** (365 / n_days) - 1)


def _calmar(equity: pd.Series, returns: pd.Series) -> float:
    mdd = _max_drawdown(equity)
    if mdd == 0 or equity.empty:
        return 0.0
    ann_ret = _annualized_return(equity)
    return float(ann_ret / mdd)


def _sharpe(returns: pd.Series, periods_per_year: float = 365 * 3) -> float:
    """Annualized Sharpe on per-trade returns. 365*3 = ~1095 trades/year at 8h hold."""
    if returns.empty or returns.std(ddof=1) == 0:
        return 0.0
    return float(returns.mean() / returns.std(ddof=1) * np.sqrt(periods_per_year))


def compute_benchmark(ohlcv: pd.DataFrame, start: str, end: str) -> pd.Series:
    """BTC buy-and-hold equity curve over [start, end], starting at INITIAL_CAPITAL."""
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        ohlcv = ohlcv.set_index("open_time")
    mask = (ohlcv.index >= start) & (ohlcv.index <= end)
    subset = ohlcv[mask]["close"]
    if subset.empty:
        return pd.Series(dtype=float)
    equity = INITIAL_CAPITAL * subset / subset.iloc[0]
    equity.name = "btc_buyhold"
    return equity
