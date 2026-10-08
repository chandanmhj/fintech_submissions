"""Sprint 3 screener engine: configurable presets, custom filters and sector-relative composite score."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Mapping, Any
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "nifty100.db"
CONFIG_PATH = ROOT / "config" / "screener_config.yaml"
OUTPUT_DIR = ROOT / "output"

SCREEN_YEAR = "2024-03"  # common valuation snapshot supplied with the project


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _pct_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """P10/P90 winsorise then scale to 0-100."""
    x = pd.to_numeric(series, errors="coerce")
    valid = x.dropna()
    if valid.empty:
        return pd.Series(50.0, index=series.index)
    p10, p90 = valid.quantile([0.10, 0.90])
    if p90 == p10:
        score = pd.Series(50.0, index=series.index)
    else:
        capped = x.clip(lower=p10, upper=p90)
        score = (capped - p10) / (p90 - p10) * 100
    if not higher_is_better:
        score = 100 - score
    return score.fillna(50.0)


def _cagr_from_series(values, years):
    vals = [(int(str(y)[:4]), v) for y, v in zip(years, values) if pd.notna(v)]
    if len(vals) < 2:
        return np.nan
    vals = sorted(vals)
    start_y, start_v = vals[0]
    end_y, end_v = vals[-1]
    n = end_y - start_y
    if n <= 0 or start_v is None or end_v is None or start_v <= 0 or end_v <= 0:
        return np.nan
    return ((end_v / start_v) ** (1 / n) - 1) * 100


def _load_screen_data(con: sqlite3.Connection, screen_year: str = SCREEN_YEAR) -> pd.DataFrame:
    r = pd.read_sql_query("SELECT * FROM financial_ratios", con)
    r["year_num"] = pd.to_numeric(r["year"].str[:4], errors="coerce")
    # The supplied market-cap/valuation snapshot is 2024-03. Financial KPIs are taken from the same date.
    r = r[r["year"] == screen_year].copy()
    mc = pd.read_sql_query("SELECT * FROM market_cap", con)
    mc = mc[mc["year"] == screen_year].copy()
    pl = pd.read_sql_query("SELECT company_id, year, sales, net_profit FROM profitandloss", con)
    pl = pl[pl["year"] == screen_year].copy()
    sec = pd.read_sql_query("SELECT company_id, broad_sector, sub_sector FROM sectors", con)
    comp = pd.read_sql_query("SELECT id AS company_id, company_name FROM companies", con)
    df = r.merge(comp, on="company_id", how="left")
    df = df.merge(mc[["company_id","market_cap_crore","pe_ratio","pb_ratio","dividend_yield_pct"]], on="company_id", how="left")
    df = df.merge(pl[["company_id","sales","net_profit"]], on="company_id", how="left")
    df = df.merge(sec, on="company_id", how="left")
    # 5-year FCF CAGR ending at screen_year using annual FCF observations.
    cf = pd.read_sql_query("SELECT company_id, year, operating_activity, investing_activity FROM cashflow", con)
    cf["fcf"] = cf["operating_activity"] + cf["investing_activity"]
    cf["yn"] = pd.to_numeric(cf["year"].str[:4], errors="coerce")
    fcf_cagr = {}
    for cid, g in cf.groupby("company_id"):
        g = g.dropna(subset=["yn"]).sort_values("yn")
        g = g[g["yn"] <= int(screen_year[:4])].tail(6)
        fcf_cagr[cid] = _cagr_from_series(g["fcf"].tolist(), g["year"].tolist())
    df["fcf_cagr_5yr"] = df["company_id"].map(fcf_cagr)
    df["cfo_pat_ratio"] = df["cfo_quality_score"]
    df["fcf_positive_flag"] = (df["free_cash_flow_cr"] > 0).astype(int)
    # Latest prior D/E for turnaround preset.
    allr = pd.read_sql_query("SELECT company_id, year, debt_to_equity FROM financial_ratios", con)
    allr["yn"] = pd.to_numeric(allr["year"].str[:4], errors="coerce")
    prev = allr[allr["yn"] < int(screen_year[:4])].sort_values("yn").groupby("company_id").tail(1)
    prev = prev[["company_id","debt_to_equity"]].rename(columns={"debt_to_equity":"previous_debt_to_equity"})
    df = df.merge(prev, on="company_id", how="left")
    df["debt_declining"] = df["debt_to_equity"] < df["previous_debt_to_equity"]
    return df


def _normalise_composite(df: pd.DataFrame) -> pd.DataFrame:
    # Sector-relative normalisation: each component is P10/P90 winsorised within broad_sector.
    components = {}
    for metric, weight, high in [
        ("return_on_equity_pct", .15, True), ("roce_pct", .10, True), ("net_profit_margin_pct", .10, True),
        ("fcf_cagr_5yr", .15, True), ("cfo_pat_ratio", .10, True), ("fcf_positive_flag", .05, True),
        ("revenue_cagr_5yr", .10, True), ("pat_cagr_5yr", .10, True),
        ("debt_to_equity", .10, False), ("interest_coverage", .05, True),
    ]:
        components[metric] = pd.Series(index=df.index, dtype=float)
        for sector, idx in df.groupby(df["broad_sector"].fillna("Unknown")).groups.items():
            components[metric].loc[idx] = _pct_score(df.loc[idx, metric], high)
    score = sum(components[m] * w for m, w, _ in [
        ("return_on_equity_pct", .15, True), ("roce_pct", .10, True), ("net_profit_margin_pct", .10, True),
        ("fcf_cagr_5yr", .15, True), ("cfo_pat_ratio", .10, True), ("fcf_positive_flag", .05, True),
        ("revenue_cagr_5yr", .10, True), ("pat_cagr_5yr", .10, True), ("debt_to_equity", .10, False), ("interest_coverage", .05, True)])
    df["composite_quality_score"] = score.clip(0,100).round(2)
    return df


def apply_filters(df: pd.DataFrame, filters: Mapping[str, Any]) -> pd.DataFrame:
    out = df.copy()
    for metric, rule in filters.items():
        if rule is None:
            continue
        if isinstance(rule, dict):
            op = rule.get("op", "min")
            threshold = rule.get("value")
        else:
            op = "min" if metric.endswith("_min") else "max"
            threshold = rule
        col = metric.replace("_min", "").replace("_max", "")
        if col == "icr" and "interest_coverage" in out:
            s = out["interest_coverage"].copy()
            s = s.fillna(np.inf)
        else:
            s = out.get(col, pd.Series(np.nan, index=out.index))
        if op in ("min", ">"):
            out = out[s >= threshold]
        elif op in ("strict_min", ">"):
            out = out[s > threshold]
        elif op in ("max", "<"):
            out = out[s <= threshold]
        elif op == "strict_max":
            out = out[s < threshold]
        elif op == "eq":
            out = out[s == threshold]
    return out.sort_values("composite_quality_score", ascending=False)


def apply_filter_config(df: pd.DataFrame, filters: Mapping[str, Any]) -> pd.DataFrame:
    out = df.copy()
    aliases = {
        "roe_min":"return_on_equity_pct", "de_max":"debt_to_equity", "fcf_min":"free_cash_flow_cr",
        "revenue_cagr_5yr_min":"revenue_cagr_5yr", "pat_cagr_5yr_min":"pat_cagr_5yr",
        "opm_min":"operating_profit_margin_pct", "pe_max":"pe_ratio", "pb_max":"pb_ratio",
        "dividend_yield_min":"dividend_yield_pct", "icr_min":"interest_coverage",
        "market_cap_min":"market_cap_crore", "net_profit_min":"net_profit", "eps_cagr_min":"eps_cagr_5yr",
        "asset_turnover_min":"asset_turnover", "sales_min":"sales",
    }
    for key, threshold in filters.items():
        col = aliases[key]
        s = out[col].copy()
        if key == "icr_min":
            s = s.fillna(np.inf)
        if key == "de_max":
            mask_fin = out["broad_sector"].eq("Financials")
            out = out[mask_fin | s.lt(threshold)].copy()
        elif key.endswith("_min"):
            out = out[s.gt(threshold)].copy()
        elif key.endswith("_max"):
            out = out[s.lt(threshold)].copy()
    return out.sort_values("composite_quality_score", ascending=False)


def _turnaround_mask(df):
    return (df["revenue_cagr_3yr"] > 10) & (df["free_cash_flow_cr"] > 0) & (df["debt_declining"] == True)


def run_presets(df: pd.DataFrame, config: dict) -> dict[str,pd.DataFrame]:
    presets = config["presets"]
    results = {}
    for name, spec in presets.items():
        if name == "Turnaround Watch":
            strict = df[_turnaround_mask(df)].copy()
        else:
            strict = apply_filter_config(df, spec["filters"])
        strict["strict_match"] = True
        # The specification requires a usable 5-50 row review set. When source data makes a fixed preset too narrow,
        # retain strict matches and add nearest composite-score candidates, explicitly labelled as review fallback.
        min_rows = int(spec.get("minimum_results", 5))
        if len(strict) < min_rows and config.get("review_fallback", True):
            pool = df.loc[~df.index.isin(strict.index)].copy()
            pool["threshold_distance"] = 0.0
            if name == "Turnaround Watch":
                # rank by number of satisfied conditions, then composite score
                pool["threshold_distance"] = (
                    (pool["revenue_cagr_3yr"] <= 10).astype(int) +
                    (pool["free_cash_flow_cr"] <= 0).astype(int) +
                    (~pool["debt_declining"]).astype(int)
                )
                pool = pool.sort_values(["threshold_distance","composite_quality_score"], ascending=[True,False])
            else:
                # Count violated thresholds; then prefer higher composite score.
                violations=[]
                for _,row in pool.iterrows():
                    v=0
                    for k,t in spec["filters"].items():
                        col={"roe_min":"return_on_equity_pct","de_max":"debt_to_equity","fcf_min":"free_cash_flow_cr","revenue_cagr_5yr_min":"revenue_cagr_5yr","pat_cagr_5yr_min":"pat_cagr_5yr","opm_min":"operating_profit_margin_pct","pe_max":"pe_ratio","pb_max":"pb_ratio","dividend_yield_min":"dividend_yield_pct","icr_min":"interest_coverage","market_cap_min":"market_cap_crore","net_profit_min":"net_profit","eps_cagr_min":"eps_cagr_5yr","asset_turnover_min":"asset_turnover","sales_min":"sales"}[k]
                        val=row[col]
                        if pd.isna(val): v+=1; continue
                        if k.endswith('_min') and not (val>t): v+=1
                        if k.endswith('_max') and not (val<t): v+=1
                    violations.append(v)
                pool["threshold_distance"]=violations
                pool=pool.sort_values(["threshold_distance","composite_quality_score"],ascending=[True,False])
            need=min_rows-len(strict)
            add=pool.head(need).copy(); add["strict_match"]=False
            results[name]=pd.concat([strict,add]).sort_values("composite_quality_score",ascending=False).drop(columns=["threshold_distance"],errors="ignore")
        else:
            results[name]=strict.head(int(spec.get("maximum_results",50)))
    return results


def run(db_path: Path = DB_PATH, config_path: Path = CONFIG_PATH):
    OUTPUT_DIR.mkdir(exist_ok=True)
    con=sqlite3.connect(db_path)
    cfg=load_config(config_path)
    df=_load_screen_data(con)
    df=_normalise_composite(df)
    results=run_presets(df,cfg)
    # Persist the sector-relative composite back into financial_ratios for the screen year.
    for _,r in df[["company_id","year","composite_quality_score"]].iterrows():
        con.execute("UPDATE financial_ratios SET composite_quality_score=? WHERE company_id=? AND year=?", (float(r.composite_quality_score),r.company_id,r.year))
    con.commit()
    con.close()
    return df, results

if __name__ == "__main__":
    cfg=load_config(); df,results=run()
    for name,res in results.items():
        print(f"{name}: {len(res)} rows ({int(res.strict_match.sum())} strict, {int((~res.strict_match).sum())} review fallback)")
