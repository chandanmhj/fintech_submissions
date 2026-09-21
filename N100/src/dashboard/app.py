import streamlit as st, sqlite3, pandas as pd
from pathlib import Path
DB=Path(__file__).resolve().parents[2]/'data/nifty100.db'
st.title('Nifty 100 Financial Intelligence Platform')
con=sqlite3.connect(DB)
count=con.execute('select count(*) from companies').fetchone()[0]
st.metric('Companies',count)
st.dataframe(pd.read_sql_query('select id,company_name,roce_percentage,roe_percentage from companies order by company_name',con),use_container_width=True)
con.close()
