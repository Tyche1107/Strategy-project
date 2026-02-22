"""
overfitting.py — Overfitting diagnostics for the funding rate strategy.

Key idea: a Sharpe ratio computed after searching over many parameter combinations
is biased upward. The methods here quantify how much of the apparent performance
is real versus an artifact of our search process.

References:
- Bailey & Lopez de Prado (2014) — Deflated Sharpe Ratio
- Bailey et al. (2017) — Probability of Backtest Overfitting
"""

from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from scipy import stats


def deflated_sharpe_ratio(
    returns: pd.Series,
    n_trials: int,
    skewness: Optional[float] = None,
    excess_kurtosis: Optional[float] = None,
) -> float:
    """
    Compute the Deflated Sharpe Ratio (DSR) following Bailey & Lopez de Prado (2014).

    The DSR adjusts the observed Sharpe ratio for:
    1. The number of parameter combinations tried (selection bias)
    2. Non-normality of returns (skewness and kurtosis)

    Formula (simplified):
      SR_0 = E[max SR among N_trials IID standard normal trials]
           ~ sqrt(2) * Gamma((N+1)/2) / Gamma(N/2) * invnorm(1 - 1/N)
      DSR = Phi( (SR_obs * sqrt(T) - SR_0) / sqrt(1 - skew*SR_obs + (kurt-1)/4 * SR_obs^2) )

    A DSR > 0.5 means there's better than 50% chance the strategy is genuinely
    profitable after accounting for selection bias. We aim for DSR > 0.95.

    Args:
        returns: out-of-sample or per-trade returns
        n_trials: number of parameter combinations tested (our search space size)
        skewness: if None, computed from returns
        excess_kurtosis: if None, computed from returns (excess, i.e., normal = 0)

    Returns:
        DSR as a float in [0, 1]
    """
    if len(returns) < 4:
        return np.nan

    n = len(returns)
    sr_obs = returns.mean() / returns.std(ddof=1) if returns.std(ddof=1) > 0 else 0

    if skewness is None:
        skewness = float(stats.skew(returns.dropna()))
    if excess_kurtosis is None:
        excess_kurtosis = float(stats.kurtosis(returns.dropna()))  # scipy returns excess kurtosis

    # Expected maximum Sharpe from n_trials IID trials (from Bailey & Lopez de Prado eq. 2)
    # Using the approximation: SR_max ~ invnorm(1 - 1/n_trials)
    if n_trials <= 1:
        sr_max_expected = 0.0
    else:
        # Euler-Mascheroni constant approximation for the expected max of normals
        # E[max of n IID N(0,1)] ~ sqrt(2*ln(n)) - (ln(ln(n)) + ln(4*pi)) / (2*sqrt(2*ln(n)))
        log_n = np.log(n_trials)
        sr_max_expected = (
            (1 - np.euler_gamma) * stats.norm.ppf(1 - 1 / n_trials)
            + np.euler_gamma * stats.norm.ppf(1 - 1 / (n_trials * np.e))
        )
        # Simpler but decent approximation used in many implementations
        sr_max_expected = stats.norm.ppf(1 - 1.0 / n_trials)

    # Adjust SR_obs for observation count: annualized SR has extra sqrt(T) factor
    # Here we compute the per-observation SR and scale by sqrt(n) to get t-stat equivalent
    sr_scaled = sr_obs * np.sqrt(n)

    # Variance of SR estimator under non-normality (from Bailey 2014 eq. 4)
    # Var(SR_hat) = (1 - skew*SR + ((kurt-1)/4)*SR^2) / (n-1)
    var_sr = (1 - skewness * sr_obs + (excess_kurtosis / 4) * sr_obs ** 2) / (n - 1)
    if var_sr <= 0:
        var_sr = 1e-8

    # DSR: probability that observed SR exceeds the expected maximum from random search
    dsr = float(stats.norm.cdf((sr_obs - sr_max_expected) / np.sqrt(var_sr)))
    return dsr


def bootstrap_sharpe(
    trade_returns: pd.Series,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> np.ndarray:
    """
    Bootstrap distribution of the Sharpe ratio.

    We resample trades with replacement to get a sense of how much the Sharpe
    ratio could vary if we had seen a different sequence of trades. If the 5th
    percentile of the bootstrap is still positive, that's a good sign.

    Args:
        trade_returns: Series of per-trade returns
        n_bootstrap: number of bootstrap resamples
        seed: random seed

    Returns:
        Array of bootstrapped Sharpe ratios, length n_bootstrap
    """
    rng = np.random.default_rng(seed)
    returns_arr = trade_returns.dropna().values
    n = len(returns_arr)

    if n < 4:
        return np.array([np.nan] * n_bootstrap)

    sharpes = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sample = rng.choice(returns_arr, size=n, replace=True)
        std = sample.std(ddof=1)
        if std > 0:
            # Scale to annual equivalent (assuming ~3 trades per day for 8h hold)
            sharpes[i] = sample.mean() / std * np.sqrt(365 * 3)
        else:
            sharpes[i] = 0.0

    return sharpes


def top_n_removal_test(
    trade_returns: pd.Series,
    ns: Optional[List[int]] = None,
    initial_capital: float = 10_000.0,
) -> Dict[str, Dict]:
    """
    Test strategy robustness by removing the top N best trades.

    If removing the top 5 trades makes the strategy unprofitable, it means
    performance is concentrated in a few lucky trades rather than a systematic edge.
    A robust strategy should survive losing its best handful of outcomes.

    Args:
        trade_returns: Series of per-trade returns
        ns: list of N values to try (default [5, 10, 20])
        initial_capital: starting capital for Calmar calculation

    Returns:
        dict mapping N -> dict with {calmar, sharpe, n_remaining, total_return}
    """
    if ns is None:
        ns = [5, 10, 20]

    returns_clean = trade_returns.dropna().sort_values(ascending=False)
    results = {}

    for n in ns:
        if n >= len(returns_clean):
            results[n] = {
                "calmar": np.nan,
                "sharpe": np.nan,
                "n_remaining": 0,
                "total_return": np.nan,
            }
            continue

        remaining = returns_clean.iloc[n:]  # remove top N

        if remaining.empty or remaining.std(ddof=1) == 0:
            results[n] = {
                "calmar": 0.0,
                "sharpe": 0.0,
                "n_remaining": len(remaining),
                "total_return": float(remaining.sum()),
            }
            continue

        # Rebuild equity curve from remaining trades
        equity = initial_capital * (1 + remaining).cumprod()
        running_max = equity.cummax()
        mdd = float(((running_max - equity) / running_max).max())

        total_return = float((1 + remaining).prod() - 1)
        n_years = len(remaining) / (365 * 3)  # rough: 3 trades/day at 8h hold
        ann_return = (1 + total_return) ** (1 / max(n_years, 0.1)) - 1 if n_years > 0 else 0

        sharpe_val = remaining.mean() / remaining.std(ddof=1) * np.sqrt(365 * 3)
        calmar_val = ann_return / mdd if mdd > 0 else 0.0

        results[n] = {
            "calmar": round(calmar_val, 4),
            "sharpe": round(sharpe_val, 4),
            "n_remaining": len(remaining),
            "total_return": round(total_return, 4),
        }

    return results
