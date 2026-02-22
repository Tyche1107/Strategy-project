"""
signals.py — Signal generation for the funding rate contrarian strategy.

The core idea: when funding rates are at extreme z-score levels, the crowded side
of the trade (longs or shorts paying funding) tends to unwind. We trade against that
crowding — so extreme positive funding -> short signal, extreme negative -> long signal.
"""

from typing import Optional
import numpy as np
import pandas as pd


def generate_signal(
    zscore: pd.Series,
    threshold: float = 1.5,
    oi_change: Optional[pd.Series] = None,
    oi_min_change: float = 0.01,
) -> pd.Series:
    """
    Generate a directional trading signal from funding rate z-score.

    Signal logic:
      +1 (long)  when zscore < -threshold  — funding unusually negative,
                                              shorts are crowded, expect mean reversion up
      -1 (short) when zscore > +threshold  — funding unusually positive,
                                              longs are crowded, expect mean reversion down
       0 (flat)  otherwise

    Optional OI filter: if oi_change is provided, we only generate a signal when
    |oi_change| >= oi_min_change, filtering out periods where the crowded trade
    hasn't seen meaningful new position building.

    Args:
        zscore: rolling z-score of funding rate (from indicators.funding_zscore)
        threshold: how many std devs from mean to trigger a signal (default 1.5)
        oi_change: optional pct change in open interest for filtering
        oi_min_change: minimum |OI change| to allow a signal through (default 1%)

    Returns:
        Series of {-1, 0, +1} signals indexed the same as zscore
    """
    # Start with everything flat
    signal = pd.Series(0, index=zscore.index, dtype=int, name="signal")

    # Contrarian directional signal — note the sign flip
    signal[zscore > threshold] = -1   # funding too high -> fade the longs
    signal[zscore < -threshold] = 1   # funding too low  -> fade the shorts

    # OI filter: require meaningful position build-up to confirm the crowding
    if oi_change is not None:
        # Where OI change is insufficient, zero out the signal
        # We align on common index first
        aligned_oi = oi_change.reindex(signal.index)
        insufficient_oi = aligned_oi.abs() < oi_min_change
        signal[insufficient_oi] = 0

    return signal


def signal_summary(signal: pd.Series, price: Optional[pd.Series] = None) -> dict:
    """
    Compute basic diagnostics on a generated signal.

    Useful for Section 5 of the notebook — checking how often the signal fires
    before we commit to a full backtest.

    Args:
        signal: Series of {-1, 0, +1}
        price: optional price series for alignment checks

    Returns:
        dict with firing_rate, n_long, n_short, n_flat
    """
    n_total = len(signal.dropna())
    n_long = (signal == 1).sum()
    n_short = (signal == -1).sum()
    n_flat = (signal == 0).sum()

    return {
        "n_total": n_total,
        "n_long": int(n_long),
        "n_short": int(n_short),
        "n_flat": int(n_flat),
        "firing_rate": round((n_long + n_short) / n_total, 4) if n_total > 0 else 0.0,
        "long_rate": round(n_long / n_total, 4) if n_total > 0 else 0.0,
        "short_rate": round(n_short / n_total, 4) if n_total > 0 else 0.0,
    }
