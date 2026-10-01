"""CAGR calculations with explicit edge-case flags for Sprint 2."""
from __future__ import annotations
from math import isfinite
from typing import Iterable, Optional, Tuple

POSITIVE_POSITIVE = "NORMAL"
DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
TURNAROUND = "TURNAROUND"
BOTH_NEGATIVE = "BOTH_NEGATIVE"
ZERO_BASE = "ZERO_BASE"
INSUFFICIENT = "INSUFFICIENT"


def cagr_value(start: Optional[float], end: Optional[float], periods: int) -> Tuple[Optional[float], str]:
    """Return CAGR percentage and one of the six required edge-case flags."""
    if periods <= 0:
        raise ValueError("periods must be positive")
    if start is None or end is None:
        return None, INSUFFICIENT
    try:
        start, end = float(start), float(end)
    except (TypeError, ValueError):
        return None, INSUFFICIENT
    if not isfinite(start) or not isfinite(end):
        return None, INSUFFICIENT
    if start == 0:
        return None, ZERO_BASE
    if start > 0 and end > 0:
        return ((end / start) ** (1.0 / periods) - 1.0) * 100.0, POSITIVE_POSITIVE
    if start > 0 and end < 0:
        return None, DECLINE_TO_LOSS
    if start < 0 and end > 0:
        return None, TURNAROUND
    if start < 0 and end < 0:
        return None, BOTH_NEGATIVE
    return None, INSUFFICIENT


def cagr_from_series(series: Iterable[Tuple[int, float]], periods: int, end_year: Optional[int] = None) -> Tuple[Optional[float], str]:
    """Use observations exactly `periods` fiscal years apart when available."""
    values = {int(year): value for year, value in series if year is not None and value is not None}
    if not values:
        return None, INSUFFICIENT
    end_year = max(values) if end_year is None else int(end_year)
    if end_year not in values:
        return None, INSUFFICIENT
    start_year = end_year - periods
    if start_year not in values:
        return None, INSUFFICIENT
    return cagr_value(values[start_year], values[end_year], periods)
