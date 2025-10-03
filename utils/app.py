from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd

# -----------------------------
# Minimal, shared UI helpers
# -----------------------------

def is_missing(x: Any) -> bool:
    try:
        return pd.isna(x) or (isinstance(x, float) and not np.isfinite(x))
    except Exception:
        return False


def _trim_trailing_zeros(text: str) -> str:
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_compact_number(value: Any, *, decimals: int = 2) -> str:
    """
    Format large numbers to K/M/B/T; smaller numbers keep thousands separators.
    Examples: 1234 -> 1.23K, 1250000 -> 1.25M, 1.2 -> 1.2, 100 -> 100
    """
    try:
        x = float(value)
    except Exception:
        return "—"
    if not np.isfinite(x):
        return "—"

    sign = "-" if x < 0 else ""
    x = abs(x)

    thresholds = [
        (1e12, "T"),
        (1e9, "B"),
        (1e6, "M"),
        (1e3, "K"),
    ]
    for thr, suf in thresholds:
        if x >= thr:
            num = x / thr
            return f"{sign}{_trim_trailing_zeros(f'{num:.{decimals}f}')}{suf}"

    # < 1e3
    if x < 1:
        return f"{sign}{_trim_trailing_zeros(f'{x:.{decimals}f}')}"
    return f"{sign}{_trim_trailing_zeros(f'{x:,.{decimals}f}')}" if x % 1 else f"{sign}{int(x):,}"


def fmt_ratio(value: Any, suffix: str = "") -> str:
    """Generic numeric formatter (2 decimals). Use for ratios like P/E, PEG, margins, etc."""
    if is_missing(value):
        return "—"
    try:
        return f"{float(value):,.2f}{suffix}"
    except Exception:
        return "—"


def get_latest(series: Optional[pd.Series]) -> Any:
    """Return the first (most-recent) value of a time-indexed series, else NaN."""
    if isinstance(series, pd.Series) and not series.empty:
        return series.iloc[0]
    return np.nan
