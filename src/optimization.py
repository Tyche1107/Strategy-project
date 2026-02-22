"""
optimization.py — Parameter optimization for the funding rate contrarian strategy.

Two approaches:
1. Grid search over all parameter combinations — exhaustive, gives us the full landscape.
2. Simulated annealing via scipy — fast exploration of continuous parameter space.

We cache grid search results to disk so we don't re-run it every time the notebook
is executed. Simulated annealing is fast enough (500 iterations) to run live.
"""

import os
import pickle
import itertools
from typing import Callable, Dict, Any, List, Optional

import numpy as np
import pandas as pd
from scipy.optimize import dual_annealing

# Default cache file location
CACHE_FILE = "data/grid_search_cache.pkl"


def grid_search(
    param_grid: Dict[str, List],
    objective_fn: Callable[[Dict], float],
    cache_file: Optional[str] = CACHE_FILE,
    force_rerun: bool = False,
) -> pd.DataFrame:
    """
    Exhaustive grid search over all parameter combinations.

    We try every combination in param_grid and call objective_fn(params) to get
    the score. Results are cached to disk so re-running the notebook is fast.

    The grid is typically:
      - threshold: [1.0, 1.2, 1.5, 1.8, 2.0]
      - window: [60, 90, 120, 180]
      - hold_hours: [4, 8, 16, 24, 48]
      - stop_loss: [None, 0.003, 0.005]
    That's 5 * 4 * 5 * 3 = 300 combinations, or ~120 if we use fewer options.

    Args:
        param_grid: dict mapping param names to lists of values
        objective_fn: function that takes a param dict and returns a float score
                      (higher is better; use negative for minimization objectives)
        cache_file: path to cache file; None to disable caching
        force_rerun: if True, ignore cache and re-run everything

    Returns:
        DataFrame with one row per combination, columns = param names + 'score'
        sorted descending by score
    """
    # Try to load from cache
    if cache_file and not force_rerun and os.path.exists(cache_file):
        print(f"Loading grid search results from cache: {cache_file}")
        with open(cache_file, "rb") as f:
            cached = pickle.load(f)
        # Verify the param grid matches
        if cached.get("param_grid") == {k: list(v) for k, v in param_grid.items()}:
            return cached["results"]
        else:
            print("  Cache param grid doesn't match. Re-running.")

    # Build all combinations
    keys = list(param_grid.keys())
    values = [param_grid[k] for k in keys]
    combos = list(itertools.product(*values))
    print(f"Running grid search: {len(combos)} combinations...")

    rows = []
    for i, combo in enumerate(combos):
        params = dict(zip(keys, combo))
        try:
            score = objective_fn(params)
        except Exception as e:
            score = np.nan
        row = {**params, "score": score}
        rows.append(row)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(combos)} done, best so far: {max(r['score'] for r in rows if not np.isnan(r['score'])):.3f}")

    results = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

    # Save to cache
    if cache_file:
        os.makedirs(os.path.dirname(cache_file) if os.path.dirname(cache_file) else ".", exist_ok=True)
        with open(cache_file, "wb") as f:
            pickle.dump({
                "param_grid": {k: list(v) for k, v in param_grid.items()},
                "results": results,
            }, f)
        print(f"  Cached to {cache_file}")

    print(f"Grid search complete. Best score: {results['score'].iloc[0]:.4f}")
    return results


def simulated_annealing(
    objective_fn: Callable[[List[float]], float],
    bounds: List[tuple],
    n_iter: int = 500,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Simulated annealing via scipy.optimize.dual_annealing.

    Unlike grid search, SA can handle continuous parameters and doesn't require
    discretizing the search space. We use it as a sanity check — if SA finds
    roughly the same optimum as grid search, we're more confident the optimum
    is real rather than a grid artifact.

    Args:
        objective_fn: function that takes a list of floats [p1, p2, ...] and
                      returns a NEGATIVE score (scipy minimizes, so negate Calmar)
        bounds: list of (min, max) tuples for each parameter
        n_iter: max number of objective function evaluations (default 500)
        seed: random seed for reproducibility

    Returns:
        dict with keys:
          x: optimal parameter vector (list of floats)
          fun: final objective value (negative of best score)
          message: solver message
          n_evals: number of evaluations used
    """
    print(f"Running simulated annealing ({n_iter} max evaluations)...")
    result = dual_annealing(
        objective_fn,
        bounds=bounds,
        maxiter=n_iter,
        seed=seed,
        # No restart after local minimum — we want global exploration
        no_local_search=False,
    )
    print(f"  SA complete. Best objective: {result.fun:.4f} (best score: {-result.fun:.4f})")
    return {
        "x": result.x.tolist(),
        "fun": result.fun,
        "message": result.message,
        "n_evals": result.nfev,
    }


def sensitivity_analysis(
    results: pd.DataFrame,
    param_col: str,
    score_col: str = "score",
) -> pd.DataFrame:
    """
    Summarize how sensitive the score is to a single parameter.

    Useful for the 1D sensitivity plots in Section 7: for each value of param_col,
    compute mean/std/max score across all other parameter settings.

    Args:
        results: grid search output DataFrame
        param_col: which parameter to vary
        score_col: column containing the objective value

    Returns:
        DataFrame indexed by param values with columns [mean, std, max, min]
    """
    grouped = results.groupby(param_col)[score_col].agg(["mean", "std", "max", "min"])
    return grouped
