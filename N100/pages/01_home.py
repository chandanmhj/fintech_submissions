import streamlit as st,pandas as pd,plotly.express as px,sqlite3
from src.dashboard.utils.db import DB_PATH,get_companies
st.title('Home — Nifty 100 overview'); co=get_companies()
with sqlite3.connect(DB_PATH) as c: r=pd.read_sql_query('SELECT * FROM financial_ratios',c); m=pd.read_sql_query('SELECT * FROM market_cap',c)
r=r.sort_values('year').groupby('company_id').tail(1); d=co.merge(r,on='company_id',how='left').merge(m.sort_values('year').groupby('company_id').tail(1)[['company_id','pe_ratio']],on='company_id',how='left')
cols=st.columns(6); vals=[('Average ROE',d.return_on_equity_pct.mean()),('Median P/E',d.pe_ratio.median()),('Median D/E',d.debt_to_equity.median()),('Companies',d.company_id.nunique()),('Median Revenue CAGR 5Y',d.revenue_cagr_5yr.median()),('Debt-free companies',(d.debt_to_equity==0).sum())]
for c,(label,v) in zip(cols,vals): c.metric(label,'N/A' if pd.isna(v) else f'{v:.2f}')
a,b=st.columns(2); a.plotly_chart(px.pie(co.groupby('broad_sector').size().reset_index(name='count'),names='broad_sector',values='count',hole=.4),use_container_width=True); b.dataframe(d.sort_values('composite_quality_score',ascending=False).head(5),use_container_width=True)
