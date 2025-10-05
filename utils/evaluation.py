#utils/evaluation.py
import numpy as np
import pandas as pd
from math import erf, sqrt

def _mann_kendall(series: pd.Series) -> tuple[float, float]:
    """
    Compute the Mann–Kendall trend test (tau, p-value) for a time series.

    Assumptions & behavior
    ----------------------
    - Input is expected to be ordered *latest → older* (your project convention).
      The function reverses to chronological order internally.
    - NaNs are removed before computation.
    - Uses the classic (non-seasonal) Mann–Kendall test with tie correction and
      normal approximation for p-value (two-sided).
    - No external dependencies (SciPy not required).

    Parameters
    ----------
    series : pd.Series
        Time series values. Index is ignored except for ordering; values are used.

    Returns
    -------
    (tau, p_value) : (float, float)
        Kendall's tau and the two-sided p-value. If not computable (n<3 or zero variance),
        returns (0.0, 1.0).

    Notes
    -----
    - S = sum_{i<j} sign(x_j - x_i)
    - Var(S) accounts for ties:
        Var(S) = [ n(n-1)(2n+5) - sum(t_k*(t_k-1)*(2*t_k+5)) ] / 18
      where t_k are tie-group sizes.
    - Z = (S-1)/sqrt(Var) if S>0; 0 if S==0; (S+1)/sqrt(Var) if S<0
    - tau = S / [n*(n-1)/2]
    """
    if series is None:
        return 0.0, 1.0

    # Reverse to chronological order (older → newer), drop NaNs
    x = pd.to_numeric(series, errors="coerce").dropna().iloc[::-1].to_numpy()
    n = x.size
    if n < 3:
        return 0.0, 1.0

    # Compute S efficiently using pairwise comparisons in chunks to keep memory reasonable
    # For typical financial macro/statement lengths, an O(n^2) loop is acceptable.
    S = 0
    for i in range(n - 1):
        diffs = x[i+1:] - x[i]
        S += np.sum(diffs > 0) - np.sum(diffs < 0)
    S = float(S)

    # Tie correction for Var(S)
    # Count tie group sizes by value
    _, counts = np.unique(x, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))
    varS = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0

    # If variance is zero (all identical), no trend detectable
    if varS <= 0:
        return 0.0, 1.0

    # Continuity-corrected Z
    sdS = sqrt(varS)
    if S > 0:
        Z = (S - 1.0) / sdS
    elif S < 0:
        Z = (S + 1.0) / sdS
    else:
        Z = 0.0

    # Two-sided p-value from normal CDF using erf
    # Phi(z) = 0.5*(1 + erf(z / sqrt(2)))
    Phi = lambda z: 0.5 * (1.0 + erf(z / sqrt(2.0)))
    p_value = 2.0 * (1.0 - Phi(abs(Z)))

    # Kendall's tau
    denom = n * (n - 1) / 2.0
    if denom <= 0:
        return 0.0, 1.0
    tau = S / denom

    return float(tau), float(p_value)
