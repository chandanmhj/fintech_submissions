from pathlib import Path
import sqlite3,pandas as pd
DB=Path(__file__).resolve().parents[1]/"data/db/bluestock_mf.db"
def recommend(category=None,risk_category=None):
 q="SELECT f.*,p.return_3y_pct,p.sharpe FROM dim_fund f LEFT JOIN fact_scheme_performance p USING(amfi_code) WHERE 1=1"; params=[]
 if category: q+=" AND f.category=?"; params.append(category)
 if risk_category: q+=" AND f.risk_category=?"; params.append(risk_category)
 q+=" ORDER BY p.sharpe DESC NULLS LAST"
 with sqlite3.connect(DB) as con: return pd.read_sql_query(q,con,params=params)
