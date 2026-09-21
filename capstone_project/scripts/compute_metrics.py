from pathlib import Path
import sqlite3,pandas as pd
DB=Path(__file__).resolve().parents[1]/"data/db/bluestock_mf.db"
with sqlite3.connect(DB) as con: print(pd.read_sql_query("SELECT * FROM fact_nav LIMIT 5",con))
