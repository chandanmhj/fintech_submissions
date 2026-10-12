import streamlit as st,pandas as pd,plotly.express as px,plotly.graph_objects as go
from src.dashboard.utils.db import get_companies,get_ratios,get_pl,get_pros_cons
st.title('Company Profile'); co=get_companies(); ticker=st.selectbox('Search company/ticker',co.company_id.tolist(),format_func=lambda x:f"{co.loc[co.company_id==x,'company_name'].iloc[0]} ({x})"); row=co[co.company_id==ticker].iloc[0]; st.subheader(row.company_name); st.write(row.get('about_company') or 'Description unavailable'); st.write('Sector:',row.get('broad_sector'),'| Sub-sector:',row.get('sub_sector'))
r=get_ratios(ticker); pl=get_pl(ticker)
if r.empty: st.warning('Ticker not found — please try another'); st.stop()
x=r.sort_values('year').iloc[-1]; cols=st.columns(6)
for c,(l,k) in zip(cols,[('ROE','return_on_equity_pct'),('ROCE','roce_pct'),('NPM','net_profit_margin_pct'),('D/E','debt_to_equity'),('Revenue CAGR 5Y','revenue_cagr_5yr'),('FCF','free_cash_flow_cr')]): c.metric(l,'N/A' if pd.isna(x.get(k)) else f"{x.get(k):.2f}")
if not pl.empty: st.plotly_chart(px.bar(pl,x='year',y=['sales','net_profit'],barmode='group'),use_container_width=True); st.plotly_chart(px.line(pl,x='year',y=['operating_profit','net_profit']),use_container_width=True)
pc=get_pros_cons(ticker)
for _,v in pc.iterrows():
 if v.get('pros'): st.success('✓ '+str(v['pros']))
 if v.get('cons'): st.error('✗ '+str(v['cons']))
if len(pl)<10: st.info(f'Only {len(pl)} financial years available.')
