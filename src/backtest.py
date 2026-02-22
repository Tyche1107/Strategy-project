"""
backtest.py — Vectorized backtester for the funding rate contrarian strategy.

Design principles:
- No Python loops over rows. All operations are vectorized pandas/numpy.
- Signals are generated at funding-rate timestamps (every 8h).
- Execution is assumed to happen at the next hourly OHLCV open price.
- Position is held for a fixed number of hours, or until stop loss.
- Fees: 0.04% taker each way (entry + exit).
- Initial capital: $10,000 (single contract, dollar-value PnL).
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
    Run a vectorized backtest of the funding-rate contrarian strategy.

    The backtest works in three stages:
    1. Map each signal observation to the next available OHLCV open (entry price).
    2. Compute exit price as the open `hold_hours` later (or stop if triggered).
    3. Aggregate to equity curve and performance metrics.

    Args:
        signal: Series of {-1, 0, +1} indexed by datetime (funding rate times)
        ohlcv: DataFrame with columns [open_time, open, high, low, close, volume]
               indexed by open_time
        hold_hours: target hold period in hours (default 8)
        stop_loss_pct: if not None, exit early if adverse move exceeds this fraction
                       (e.g., 0.005 = 0.5%). Applied to hourly closes.
        max_hold_hours: hard cap on hold duration regardless of other rules

    Returns:
        dict with keys:
          equity_curve: pd.Series indexed by time
          trade_log: pd.DataFrame with one row per trade
          calmar: float
          sharpe: float
          max_drawdown: float
          win_rate: float
          n_trades: int
          avg_hold_hours: float
    """
    # --- Prepare OHLCV indexed by open_time ---
    ohlcv = ohlcv.copy()
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        ohlcv = ohlcv.set_index("open_time")
    ohlcv = ohlcv.sort_index()

    # Filter to active signals only
    active = signal[signal != 0].dropna()
    if active.empty:
        return _empty_result()

    # For each signal, find the next OHLCV bar's open_time
    ohlcv_times = ohlcv.index
    trades = []

    for sig_time, direction in active.items():
        # Find next bar at or after signal time
        entry_idx_arr = ohlcv_times.searchsorted(sig_time, side="left")
        # The signal is generated at sig_time; we execute at the NEXT bar
        # (to avoid look-ahead bias — we don't know the current open until
        #  the bar actually opens)
        entry_idx = entry_idx_arr  # searchsorted gives first >= sig_time
        if entry_idx >= len(ohlcv_times):
            continue

        entry_time = ohlcv_times[entry_idx]
        entry_price = ohlcv["open"].iloc[entry_idx]

        # Determine exit index
        exit_idx = min(entry_idx + min(hold_hours, max_hold_hours), len(ohlcv_times) - 1)
        exit_time = ohlcv_times[exit_idx]
        exit_price = ohlcv["open"].iloc[exit_idx]

        # Stop loss check: scan hourly bars between entry and planned exit
        if stop_loss_pct is not None and exit_idx > entry_idx:
            # For longs, stop triggers when close falls below entry*(1-stop)
            # For shorts, stop triggers when close rises above entry*(1+stop)
            window_closes = ohlcv["close"].iloc[entry_idx:exit_idx]
            if direction == 1:
                stop_level = entry_price * (1 - stop_loss_pct)
                hit = window_closes[window_closes <= stop_level]
            else:
                stop_level = entry_price * (1 + stop_loss_pct)
                hit = window_closes[window_closes >= stop_level]

            if not hit.empty:
                stop_time = hit.index[0]
                stop_bar_idx = ohlcv_times.get_loc(stop_time)
                exit_time = stop_time
                exit_price = ohlcv["open"].iloc[stop_bar_idx + 1] if stop_bar_idx + 1 < len(ohlcv_times) else hit.iloc[0]

        hold_hrs = max((exit_time - entry_time).total_seconds() / 3600, 1)

        # PnL calculation (fractional return on capital allocated to trade)
        gross_return = direction * (exit_price - entry_price) / entry_price
        net_return = gross_return - 2 * FEE_RATE  # pay taker fee in and out
        pnl_dollar = net_return * INITIAL_CAPITAL  # simplification: full capital per trade

        trades.append({
            "entry_time": entry_time,
            "exit_time": exit_time,
            "direction": direction,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "hold_hours": hold_hrs,
            "gross_return": gross_return,
            "net_return": net_return,
            "pnl_dollar": pnl_dollar,
            "win": int(net_return > 0),
        })

    if not trades:
        return _empty_result()

    trade_log = pd.DataFrame(trades).set_index("entry_time")

    # --- Build equity curve ---
    # Equity at each trade exit: cumulative sum of dollar PnL
    equity = INITIAL_CAPITAL + trade_log["pnl_dollar"].cumsum()
    equity.index = pd.DatetimeIndex(trade_log["exit_time"])
    equity.name = "equity"

    # Performance metrics
    calmar = _calmar(equity, trade_log["net_return"])
    sharpe = _sharpe(trade_log["net_return"])
    mdd = _max_drawdown(equity)
    win_rate = trade_log["win"].mean()
    n_trades = len(trade_log)
    avg_hold = trade_log["hold_hours"].mean()

    return {
        "equity_curve": equity,
        "trade_log": trade_log,
        "calmar": calmar,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "win_rate": win_rate,
        "n_trades": n_trades,
        "avg_hold_hours": avg_hold,
    }


def _empty_result() -> Dict[str, Any]:
    """Return a result dict with all-zero metrics for the no-trades case."""
    return {
        "equity_curve": pd.Series(dtype=float),
        "trade_log": pd.DataFrame(),
        "calmar": 0.0,
        "sharpe": 0.0,
        "max_drawdown": 0.0,
        "win_rate": 0.0,
        "n_trades": 0,
        "avg_hold_hours": 0.0,
    }


def _max_drawdown(equity: pd.Series) -> float:
    """
    Compute maximum drawdown as a positive fraction.

    MDD = max((peak - trough) / peak) over the equity curve.
    """
    if equity.empty:
        return 0.0
    running_max = equity.cummax()
    drawdown = (running_max - equity) / running_max
    return float(drawdown.max())


def _annualized_return(equity: pd.Series) -> float:
    """
    Annualized return based on total capital growth and time span.

    Uses the start/end of the equity curve to get the holding period in years.
    """
    if len(equity) < 2:
        return 0.0
    total_return = equity.iloc[-1] / INITIAL_CAPITAL - 1
    n_days = (equity.index[-1] - equity.index[0]).total_seconds() / 86400
    if n_days <= 0:
        return 0.0
    ann_return = (1 + total_return) ** (365 / n_days) - 1
    return float(ann_return)


def _calmar(equity: pd.Series, returns: pd.Series) -> float:
    """Calmar ratio: annualized return / max drawdown."""
    mdd = _max_drawdown(equity)
    if mdd == 0:
        return 0.0
    ann_ret = _annualized_return(equity)
    return float(ann_ret / mdd)


def _sharpe(returns: pd.Series, periods_per_year: int = 8760) -> float:
    """
    Annualized Sharpe ratio on per-trade returns.

    We scale by sqrt(8760) assuming each trade corresponds to ~1h of exposure
    (very rough), but for cross-strategy comparison the relative ranking is
    what matters more than the absolute number.
    """
    if returns.empty or returns.std() == 0:
        return 0.0
    # Assume each return is per-trade, and trades happen roughly every 8h on average
    # Annualize by the number of 8h intervals in a year
    periods_per_year = 8760 / 8  # ~1095 8h periods per year
    sharpe = returns.mean() / returns.std(ddof=1) * np.sqrt(periods_per_year)
    return float(sharpe)


def compute_benchmark(ohlcv: pd.DataFrame, start: str, end: str) -> pd.Series:
    """
    Compute BTC buy-and-hold equity curve for the given period.

    Args:
        ohlcv: OHLCV DataFrame (indexed by open_time or with open_time column)
        start: start date string
        end: end date string

    Returns:
        Series of equity values indexed by time, starting at INITIAL_CAPITAL
    """
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        ohlcv = ohlcv.set_index("open_time")
    mask = (ohlcv.index >= start) & (ohlcv.index <= end)
    subset = ohlcv[mask]["close"]
    if subset.empty:
        return pd.Series(dtype=float)
    equity = INITIAL_CAPITAL * subset / subset.iloc[0]
    equity.name = "btc_buyhold"
    return equity
