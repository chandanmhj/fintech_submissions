import streamlit as st
from src.dashboard.utils.db import get_companies,get_documents
st.title('Annual Reports'); c=get_companies(); t=st.selectbox('Company',c.company_id.tolist()); d=get_documents(t)
if d.empty: st.warning('No annual reports are listed for this company.')
for _,r in d.iterrows():
 u=r.get('annual_report'); y=r.get('year') or 'Year unavailable'
 if isinstance(u,str) and u.startswith(('http://','https://')): st.markdown(f"- **{y}** · [Open annual report]({u})")
 else: st.markdown(f'- **{y}** · :red[Report unavailable]')
