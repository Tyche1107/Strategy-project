"""
indicators.py — Feature engineering for the funding rate contrarian strategy.

All functions operate on pandas Series/DataFrames and return pandas objects
so they compose naturally with the rest of the pipeline.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from scipy import stats


def funding_zscore(fr: pd.Series, window: int = 90) -> pd.Series:
    """
    Compute a rolling z-score of the funding rate.

    The z-score measures how many standard deviations the current funding rate
    is from its recent mean. A large positive z-score means funding is unusually
    high (longs are paying shorts), which historically predicts a short-term
    price pullback as levered longs reduce exposure.

    We use a rolling window rather than an expanding one so the signal stays
    calibrated to recent volatility — funding regime changes between bull and
    bear markets, and a static normalization would lose that.

    Args:
        fr: Series of funding rates (8h intervals typical)
        window: lookback period in funding-rate observations (default 90 ~ 30 days)

    Returns:
        Series of z-scores, NaN for the first `window` observations
    """
    mu = fr.rolling(window=window, min_periods=window).mean()
    sigma = fr.rolling(window=window, min_periods=window).std(ddof=1)
    zscore = (fr - mu) / sigma.replace(0, np.nan)
    zscore.name = f"funding_zscore_{window}"
    return zscore


def funding_cumulative(fr: pd.Series, periods: int = 3) -> pd.Series:
    """
    Compute the sum of the last N funding rate observations.

    This captures the cumulative cost of holding a position over several
    funding intervals. Three 8h periods = 24h of funding costs, which is
    roughly the horizon where mean reversion kicks in.

    Args:
        fr: Series of funding rates
        periods: number of periods to sum (default 3 = 24h)

    Returns:
        Series of rolling sums
    """
    result = fr.rolling(window=periods, min_periods=periods).sum()
    result.name = f"funding_cum_{periods}"
    return result


def oi_change_pct(oi: pd.Series) -> pd.Series:
    """
    Compute percentage change in open interest.

    Rising OI alongside extreme funding suggests new money is flowing in
    on the dominant side, making the crowding trade more fragile. A sudden
    drop in OI often accompanies the unwind we're trying to trade.

    Args:
        oi: Series of open interest values (e.g., in BTC or USD)

    Returns:
        Series of percentage changes (fractional, not multiplied by 100)
    """
    result = oi.pct_change()
    result.name = "oi_change_pct"
    return result


def information_coefficient(
    signal: pd.Series,
    forward_return: pd.DataFrame,
    periods: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Compute the Information Coefficient (IC) between a signal and forward returns.

    IC is Spearman rank correlation between the signal at time t and the asset
    return over [t, t+h]. We use Spearman rather than Pearson because funding
    rate signals have heavy tails and the rank correlation is more robust.

    A positive IC means the signal has predictive power in the right direction.
    Typical rule of thumb: IC > 0.05 is meaningful for high-frequency signals.

    Args:
        signal: Series of signal values (e.g., z-score)
        forward_return: DataFrame with one column per horizon (e.g., ret_8h, ret_24h)
                        OR a Series for a single horizon
        periods: list of horizon labels in hours (used only for column naming
                 if forward_return is provided as a dict-style input)

    Returns:
        DataFrame with columns [IC, t_stat, p_value] and one row per horizon
    """
    if periods is None:
        periods = [1, 3, 8, 24]

    # Accept either a DataFrame of pre-computed forward returns or compute them
    if isinstance(forward_return, pd.Series):
        # Treat as a single-horizon input
        forward_return = forward_return.to_frame(name="return")

    results = {}
    for col in forward_return.columns:
        fwd = forward_return[col]
        # Align on common index, drop NaN pairs
        aligned = pd.concat([signal, fwd], axis=1).dropna()
        if len(aligned) < 10:
            results[col] = {"IC": np.nan, "t_stat": np.nan, "p_value": np.nan, "n": 0}
            continue

        ic, pval = stats.spearmanr(aligned.iloc[:, 0], aligned.iloc[:, 1])
        n = len(aligned)
        # t-stat for correlation: t = IC * sqrt((n-2)/(1-IC^2))
        # Guard against perfect correlation edge case
        denom = max(1 - ic**2, 1e-10)
        t_stat = ic * np.sqrt((n - 2) / denom)
        results[col] = {"IC": ic, "t_stat": t_stat, "p_value": pval, "n": n}

    ic_df = pd.DataFrame(results).T
    ic_df.index.name = "horizon"
    return ic_df
