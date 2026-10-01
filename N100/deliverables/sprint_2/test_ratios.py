import pytest
from src.analytics.ratios import (
    net_profit_margin, operating_profit_margin, return_on_equity,
    return_on_assets, debt_to_equity, interest_coverage, asset_turnover,
    net_debt,
)
from src.analytics.cagr import cagr_value
from src.analytics.cashflow_kpis import (
    free_cash_flow, cfo_quality_score, cfo_quality_label,
    capex_intensity, capex_intensity_label, fcf_conversion_rate,
    capital_allocation_pattern,
)

# Profitability / leverage / efficiency: 10 tests

def test_npm_normal(): assert net_profit_margin(100, 1000) == 10

def test_npm_zero_sales(): assert net_profit_margin(100, 0) is None

def test_opm_normal(): assert operating_profit_margin(150, 1000) == 15

def test_roe_normal(): assert return_on_equity(100, 200, 300) == 20

def test_roe_negative_equity(): assert return_on_equity(100, -400, 100) is None

def test_roa_zero_assets(): assert return_on_assets(100, 0) is None

def test_debt_free_returns_zero(): assert debt_to_equity(0, 100, 100) == 0

def test_icr_zero_interest(): assert interest_coverage(100, 10, 0) is None

def test_asset_turnover_zero_assets(): assert asset_turnover(100, 0) is None

def test_net_debt_uses_investments_as_liquid_proxy(): assert net_debt(500, 120) == 380

# CAGR edge cases: 6 tests

def test_cagr_normal(): assert cagr_value(100, 121, 2)[0] == pytest.approx(10, abs=0.01)

def test_cagr_zero_base(): assert cagr_value(0, 100, 3) == (None, "ZERO_BASE")

def test_cagr_turnaround(): assert cagr_value(-100, 100, 3) == (None, "TURNAROUND")

def test_cagr_decline_to_loss(): assert cagr_value(100, -100, 3) == (None, "DECLINE_TO_LOSS")

def test_cagr_both_negative(): assert cagr_value(-100, -120, 3) == (None, "BOTH_NEGATIVE")

def test_cagr_insufficient(): assert cagr_value(None, 100, 5) == (None, "INSUFFICIENT")

# Cash-flow / classification: 4 tests

def test_fcf_allows_negative(): assert free_cash_flow(100, -150) == -50

def test_cfo_quality_high():
    assert cfo_quality_score(120, 100) == 1.2
    assert cfo_quality_label(1.2) == "High Quality"

def test_capex_intensity_label():
    assert capex_intensity(-20, 1000) == 2
    assert capex_intensity_label(2) == "Asset Light"

def test_capital_allocation_high_quality_shareholder_returns():
    assert capital_allocation_pattern(200, -100, -50, 1.5) == "Shareholder Returns"
