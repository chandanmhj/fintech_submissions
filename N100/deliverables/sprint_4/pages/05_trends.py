import streamlit as st,plotly.express as px
from src.dashboard.utils.db import get_companies,get_pl,get_ratios
st.title('Trend Analysis'); c=get_companies(); t=st.selectbox('Company',c.company_id.tolist()); pl=get_pl(t); r=get_ratios(t); choices=['sales','net_profit','operating_profit','eps']; sel=st.multiselect('Up to 3 metrics',choices,default=choices[:3],max_selections=3)
if sel and not pl.empty: st.plotly_chart(px.line(pl,x='year',y=sel,markers=True),use_container_width=True)
if not r.empty: st.plotly_chart(px.line(r,x='year',y=[x for x in ['return_on_equity_pct','roce_pct','free_cash_flow_cr'] if x in r],markers=True),use_container_width=True)
