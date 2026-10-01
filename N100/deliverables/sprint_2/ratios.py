"""Sprint 2 financial ratio engine for the Nifty100 database."""
from __future__ import annotations
import csv
import sqlite3
from pathlib import Path
from typing import Optional

from .cagr import cagr_from_series
from .cashflow_kpis import (
    capital_allocation_pattern, capex_intensity, capex_intensity_label,
    cfo_quality_label, cfo_quality_score, fcf_conversion_rate, free_cash_flow,
)

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "nifty100.db"
OUTPUT = ROOT / "output"


def safe_div(num: Optional[float], den: Optional[float], multiplier: float = 1.0) -> Optional[float]:
    if num is None or den is None or den == 0:
        return None
    return num / den * multiplier


def net_profit_margin(net_profit, sales): return safe_div(net_profit, sales, 100)
def operating_profit_margin(op_profit, sales): return safe_div(op_profit, sales, 100)
def return_on_equity(net_profit, equity, reserves):
    den = (equity or 0) + (reserves or 0)
    return None if den <= 0 else safe_div(net_profit, den, 100)
def return_on_assets(net_profit, assets): return safe_div(net_profit, assets, 100)
def debt_to_equity(borrowings, equity, reserves):
    den = (equity or 0) + (reserves or 0)
    if borrowings == 0: return 0.0
    return safe_div(borrowings, den)
def interest_coverage(op_profit, other_income, interest): return safe_div((op_profit or 0) + (other_income or 0), interest)
def net_debt(borrowings, investments): return (borrowings or 0) - (investments or 0) if borrowings is not None or investments is not None else None
def asset_turnover(sales, assets): return safe_div(sales, assets)
def book_value_per_share(equity, reserves, eps):
    # EPS is used only as a fallback signal; actual share count is not present in source data.
    return None


def _year_num(year):
    try: return int(str(year)[:4])
    except (TypeError, ValueError): return None


def ensure_schema(con: sqlite3.Connection) -> None:
    columns = {
        "roce_pct": "REAL", "roa_pct": "REAL", "net_debt_cr": "REAL",
        "icr_label": "TEXT", "high_leverage_flag": "INTEGER", "icr_warning_flag": "INTEGER",
        "roce_benchmark_pct": "REAL", "roce_vs_sector_benchmark": "TEXT", "roce_vs_sector_gap_pct": "REAL",
        "cfo_quality_score": "REAL", "cfo_quality_label": "TEXT",
        "capex_intensity_pct": "REAL", "capex_intensity_label": "TEXT",
        "fcf_conversion_rate_pct": "REAL", "capital_allocation_pattern": "TEXT",
        "revenue_cagr_3yr": "REAL", "revenue_cagr_3yr_flag": "TEXT",
        "revenue_cagr_5yr": "REAL", "revenue_cagr_5yr_flag": "TEXT",
        "revenue_cagr_10yr": "REAL", "revenue_cagr_10yr_flag": "TEXT",
        "pat_cagr_3yr": "REAL", "pat_cagr_3yr_flag": "TEXT",
        "pat_cagr_5yr": "REAL", "pat_cagr_5yr_flag": "TEXT",
        "pat_cagr_10yr": "REAL", "pat_cagr_10yr_flag": "TEXT",
        "eps_cagr_3yr": "REAL", "eps_cagr_3yr_flag": "TEXT",
        "eps_cagr_5yr": "REAL", "eps_cagr_5yr_flag": "TEXT",
        "eps_cagr_10yr": "REAL", "eps_cagr_10yr_flag": "TEXT",
        "composite_quality_score": "REAL",
        "opm_crosscheck_diff_pct": "REAL", "opm_crosscheck_flag": "INTEGER",
    }
    for name, typ in columns.items():
        try: con.execute(f'ALTER TABLE financial_ratios ADD COLUMN "{name}" {typ}')
        except sqlite3.OperationalError:
            pass


def _sector_benchmarks(rows):
    grouped = {}
    for r in rows:
        sector = r["broad_sector"] or "Unknown"
        
        if r["roce_pct"] is not None:
            grouped.setdefault(sector, []).append(r["roce_pct"])
    return {k: sorted(v)[len(v)//2] for k, v in grouped.items() if v}


def _cagr_for(hist, company_id, field, year, n):
    series = [(_year_num(y), r[field]) for y, r in hist.get(company_id, {}).items() if _year_num(y) is not None]
    return cagr_from_series(series, n, _year_num(year))


def _five_year_cfo_quality(hist, company_id, end_year):
    """Average CFO/PAT across up to five fiscal observations ending at end_year."""
    end_num = _year_num(end_year)
    if end_num is None:
        return None
    ratios = []
    for y, row in hist.get(company_id, {}).items():
        yn = _year_num(y)
        if yn is not None and end_num - 4 <= yn <= end_num and row["operating_activity"] is not None and row["net_profit"] not in (None, 0):
            ratios.append(row["operating_activity"] / row["net_profit"])
    return sum(ratios) / len(ratios) if ratios else None


def run() -> dict:
    OUTPUT.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    ensure_schema(con)
    con.execute("DELETE FROM financial_ratios")

    query = """
    SELECT p.company_id,p.year,p.sales,p.operating_profit,p.opm_percentage,p.other_income,p.interest,
           p.profit_before_tax,p.net_profit,p.eps,p.dividend_payout,
           b.equity_capital,b.reserves,b.borrowings,b.investments,b.total_assets,
           cf.operating_activity,cf.investing_activity,cf.financing_activity,
           c.book_value,c.roce_percentage AS source_roce,c.roe_percentage AS source_roe,
           s.broad_sector
    FROM profitandloss p
    LEFT JOIN balancesheet b ON b.company_id=p.company_id AND b.year=p.year
    LEFT JOIN cashflow cf ON cf.company_id=p.company_id AND cf.year=p.year
    LEFT JOIN companies c ON c.id=p.company_id
    LEFT JOIN sectors s ON s.company_id=p.company_id
    ORDER BY p.company_id,p.year
    """
    rows = [dict(r) for r in con.execute(query).fetchall()]
    hist = {}
    for r in rows:
        hist.setdefault(r["company_id"], {})[r["year"]] = r

    computed = []
    # First pass for ROCE sector benchmarks.
    for r in rows:
        equity = (r["equity_capital"] or 0) + (r["reserves"] or 0)
        capital = equity + (r["borrowings"] or 0)
        ebit = (r["profit_before_tax"] or 0) + (r["interest"] or 0)
        r["roce_pct"] = safe_div(ebit, capital, 100) if capital > 0 else None
        r["roa_pct"] = return_on_assets(r["net_profit"], r["total_assets"])
    benchmarks = _sector_benchmarks(rows)

    edge_path = OUTPUT / "ratio_edge_cases.log"
    edge_lines = ["Sprint 2 ratio edge-case log", "=" * 80]
    allocations = []
    insert_cols = [x[1] for x in con.execute('PRAGMA table_info(financial_ratios)').fetchall() if x[1] != 'id']

    for r in rows:
        company, year, sector = r["company_id"], r["year"], r["broad_sector"] or "Unknown"
        den_eq = (r["equity_capital"] or 0) + (r["reserves"] or 0)
        roe = return_on_equity(r["net_profit"], r["equity_capital"], r["reserves"])
        de = debt_to_equity(r["borrowings"], r["equity_capital"], r["reserves"])
        icr = interest_coverage(r["operating_profit"], r["other_income"], r["interest"])
        cfo = r["operating_activity"]; cfi = r["investing_activity"]; cff = r["financing_activity"]
        fcf = free_cash_flow(cfo, cfi)
        cfo_score = _five_year_cfo_quality(hist, company, year)
        capint = capex_intensity(cfi, r["sales"])
        pattern = capital_allocation_pattern(cfo, cfi, cff, cfo_score)
        cagr = {}
        for prefix, field in [("revenue", "sales"), ("pat", "net_profit"), ("eps", "eps")]:
            for n in (3,5,10):
                cagr[f"{prefix}_cagr_{n}yr"], cagr[f"{prefix}_cagr_{n}yr_flag"] = _cagr_for(hist, company, field, year, n)
        benchmark = benchmarks.get(sector)
        values = {
            "company_id":company,"year":year,
            "net_profit_margin_pct":net_profit_margin(r["net_profit"],r["sales"]),
            "operating_profit_margin_pct":operating_profit_margin(r["operating_profit"],r["sales"]),
            "return_on_equity_pct":roe,"debt_to_equity":de,
            "interest_coverage":icr,"asset_turnover":asset_turnover(r["sales"],r["total_assets"]),
            "free_cash_flow_cr":fcf,"capex_cr":abs(cfi) if cfi is not None else None,
            "earnings_per_share":r["eps"],"book_value_per_share":r["book_value"],
            "dividend_payout_ratio_pct":r["dividend_payout"],"total_debt_cr":r["borrowings"],
            "cash_from_operations_cr":cfo,"roce_pct":r["roce_pct"],"roa_pct":r["roa_pct"],
            "net_debt_cr":net_debt(r["borrowings"],r["investments"]),
            "icr_label":"Debt Free" if icr is None else "Covered" ,
            "high_leverage_flag":int(de is not None and de > 5 and sector != "Financials"),
            "icr_warning_flag":int(icr is not None and icr < 1.5),
            "roce_benchmark_pct":benchmark,
            "roce_vs_sector_benchmark": ("Above" if r["roce_pct"] is not None and benchmark is not None and r["roce_pct"] >= benchmark else "Below") if benchmark is not None and r["roce_pct"] is not None else None,
            "roce_vs_sector_gap_pct": (r["roce_pct"] - benchmark) if benchmark is not None and r["roce_pct"] is not None else None,
            "cfo_quality_score":cfo_score,"cfo_quality_label":cfo_quality_label(cfo_score),
            "capex_intensity_pct":capint,"capex_intensity_label":capex_intensity_label(capint),
            "fcf_conversion_rate_pct":fcf_conversion_rate(fcf,r["operating_profit"]),
            "capital_allocation_pattern":pattern,
            **cagr,
            "composite_quality_score":None,
            "opm_crosscheck_diff_pct": abs((r["opm_percentage"] or 0) - (operating_profit_margin(r["operating_profit"],r["sales"]) or 0)) if r["opm_percentage"] is not None else None,
            "opm_crosscheck_flag":int(r["opm_percentage"] is not None and operating_profit_margin(r["operating_profit"],r["sales"]) is not None and abs(r["opm_percentage"]-operating_profit_margin(r["operating_profit"],r["sales"])) > 1),
        }
        # A transparent 0-100 composite from available normalized signals.
        components=[]
        for x in [values["net_profit_margin_pct"], values["return_on_equity_pct"], values["roce_pct"], values["cfo_quality_score"]]:
            if x is not None: components.append(max(0.0, min(100.0, float(x))))
        values["composite_quality_score"] = sum(components)/len(components) if components else None

        # DQ/logging: OPM mismatch and source ROE/ROCE differences >5 percentage points.
        if values["opm_crosscheck_flag"]:
            edge_lines.append(f"{company}|{year}|OPM cross-check|formula={values['operating_profit_margin_pct']:.4f}|source={r['opm_percentage']:.4f}|category=data source issue|difference > 1%")
        for metric, calc, source in [("ROCE",values["roce_pct"],r["source_roce"]),("ROE",roe,r["source_roe"])]:
            if calc is not None and source is not None and abs(calc-source) > 5:
                # Source values live at company level while calculated values are annual, so historical mismatches are normally version differences.
                category = "data source issue" if (metric == "ROE" and source < 1 and abs(calc) > 5) else "version difference"
                edge_lines.append(f"{company}|{year}|{metric}|computed={calc:.4f}|source={source:.4f}|category={category}|difference > 5 percentage points")
        allocations.append([company,year,"+" if cfo and cfo>0 else "-" if cfo and cfo<0 else "0","+" if cfi and cfi>0 else "-" if cfi and cfi<0 else "0","+" if cff and cff>0 else "-" if cff and cff<0 else "0",pattern])
        computed.append(values)

    # Composite quality is intentionally transparent rather than a hidden ML score.
    placeholders=','.join('?' for _ in insert_cols)
    sql=f'INSERT INTO financial_ratios ({",".join(insert_cols)}) VALUES ({placeholders})'
    for v in computed:
        con.execute(sql,[v.get(c) for c in insert_cols])
    con.commit()
    with open(OUTPUT/'capital_allocation.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(["company_id","year","cfo_sign","cfi_sign","cff_sign","pattern_label"]); w.writerows(allocations)
    edge_lines.append("=" * 80)
    edge_lines.append(f"Total ratio rows: {len(computed)}")
    edge_lines.append("Each anomaly includes a category and explanation basis.")
    edge_path.write_text("\n".join(edge_lines),encoding="utf-8")
    count=con.execute('select count(*) from financial_ratios').fetchone()[0]
    con.close()
    return {"rows":count,"edge_cases":len(edge_lines)-4,"allocation_rows":len(allocations)}

if __name__ == "__main__":
    print(run())
