"""Sprint 3 peer percentile engine and SQLite persistence."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
DB_PATH=ROOT/"data"/"nifty100.db"
YEAR="2024-03"
METRICS={
    "ROE":"return_on_equity_pct","ROCE":"roce_pct","Net Profit Margin":"net_profit_margin_pct",
    "D/E":"debt_to_equity","FCF":"free_cash_flow_cr","PAT CAGR 5yr":"pat_cagr_5yr",
    "Revenue CAGR 5yr":"revenue_cagr_5yr","EPS CAGR 5yr":"eps_cagr_5yr",
    "Interest Coverage":"interest_coverage","Asset Turnover":"asset_turnover",
}


def ensure_schema(con):
    con.execute("""CREATE TABLE IF NOT EXISTS peer_percentiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id TEXT NOT NULL,
        peer_group_name TEXT NOT NULL,
        metric TEXT NOT NULL,
        value REAL,
        percentile_rank REAL,
        year TEXT NOT NULL,
        UNIQUE(company_id, peer_group_name, metric, year)
    )""")
    con.commit()


def percent_rank(s: pd.Series, higher_is_better=True) -> pd.Series:
    x=pd.to_numeric(s,errors="coerce")
    if not higher_is_better:
        x=-x
    n=x.notna().sum()
    if n<=1:
        return pd.Series(1.0,index=s.index).where(x.notna(),np.nan)
    return (x.rank(method="min",pct=False)-1)/(n-1)


def compute_peer_percentiles(db_path: Path=DB_PATH, year: str=YEAR):
    con=sqlite3.connect(db_path)
    ensure_schema(con)
    con.execute("DELETE FROM peer_percentiles WHERE year=?",(year,))
    ratios=pd.read_sql_query("SELECT * FROM financial_ratios WHERE year=?",con,params=[year])
    peers=pd.read_sql_query("SELECT peer_group_name, company_id, is_benchmark FROM peer_groups",con)
    rows=[]
    for group,pg in peers.groupby("peer_group_name"):
        merged=pg.merge(ratios,on="company_id",how="left")
        for metric,col in METRICS.items():
            pct=percent_rank(merged[col], higher_is_better=(metric!="D/E"))
            for i,r in merged.iterrows():
                rows.append((r.company_id,group,metric,None if pd.isna(r[col]) else float(r[col]),None if pd.isna(pct.loc[i]) else float(pct.loc[i]),year))
    con.executemany("INSERT INTO peer_percentiles(company_id,peer_group_name,metric,value,percentile_rank,year) VALUES(?,?,?,?,?,?)",rows)
    con.commit()
    count=con.execute("SELECT COUNT(*) FROM peer_percentiles WHERE year=?",(year,)).fetchone()[0]
    con.close()
    return count


def build_peer_frame(db_path: Path=DB_PATH, year: str=YEAR):
    con=sqlite3.connect(db_path)
    p=pd.read_sql_query("SELECT * FROM peer_percentiles WHERE year=?",con,params=[year])
    peers=pd.read_sql_query("SELECT peer_group_name,company_id,is_benchmark FROM peer_groups",con)
    names=pd.read_sql_query("SELECT id company_id,company_name FROM companies",con)
    con.close()
    return p.merge(peers,on=["peer_group_name","company_id"]).merge(names,on="company_id")

if __name__=="__main__":
    print({"rows":compute_peer_percentiles()})
