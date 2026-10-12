import streamlit as st,plotly.express as px
from src.dashboard.utils.db import _q
st.title('Capital Allocation Map'); d=_q("SELECT fr.company_id,c.company_name,COALESCE(fr.capital_allocation_pattern,'Unknown') pattern,fr.free_cash_flow_cr,fr.composite_quality_score FROM financial_ratios fr LEFT JOIN companies c ON c.id=fr.company_id WHERE fr.year=(SELECT MAX(year) FROM financial_ratios)")
if d.empty: st.info('Capital allocation data unavailable'); st.stop()
st.plotly_chart(px.treemap(d,path=['pattern','company_name'],values=d.free_cash_flow_cr.abs().fillna(1),color='composite_quality_score'),use_container_width=True); p=st.selectbox('Pattern',sorted(d.pattern.unique())); st.dataframe(d[d.pattern==p],use_container_width=True)
