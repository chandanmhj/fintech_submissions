"""Cash-flow and capital-allocation KPI functions."""
from __future__ import annotations
from typing import Optional


def free_cash_flow(cfo: Optional[float], cfi: Optional[float]) -> Optional[float]:
    if cfo is None or cfi is None:
        return None
    return cfo + cfi


def cfo_quality_score(cfo: Optional[float], pat: Optional[float]) -> Optional[float]:
    if cfo is None or pat in (None, 0):
        return None
    return cfo / pat


def cfo_quality_label(score: Optional[float]) -> Optional[str]:
    if score is None:
        return None
    if score > 1.0:
        return "High Quality"
    if score >= 0.5:
        return "Moderate"
    return "Accrual Risk"


def capex_intensity(cfi: Optional[float], sales: Optional[float]) -> Optional[float]:
    if cfi is None or sales in (None, 0):
        return None
    return abs(cfi) / abs(sales) * 100.0


def capex_intensity_label(value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    if value < 3:
        return "Asset Light"
    if value <= 8:
        return "Moderate"
    return "Capital Intensive"


def fcf_conversion_rate(fcf: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
    if fcf is None or operating_profit in (None, 0):
        return None
    return fcf / operating_profit * 100.0


def capital_allocation_pattern(cfo: Optional[float], cfi: Optional[float], cff: Optional[float], cfo_pat: Optional[float] = None) -> str:
    def sign(x):
        if x is None or x == 0:
            return "0"
        return "+" if x > 0 else "-"
    key = (sign(cfo), sign(cfi), sign(cff))
    if key == ("+", "-", "-"):
        return "Shareholder Returns" if cfo_pat is not None and cfo_pat > 1.0 else "Reinvestor"
    mapping = {
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }
    return mapping.get(key, "Mixed")
