import streamlit as st
from src.screener.engine import load_screener_frame,apply_filters,PRESETS
st.title('Financial Screener'); df=load_screener_frame(); preset=st.sidebar.selectbox('Preset',['Custom']+list(PRESETS)); filters={}
sliders=[('roe_min','ROE min',0,-100,100),('de_max','D/E max',5,0,20),('fcf_min','FCF min',0,-100000,100000),('revenue_cagr_5yr_min','Revenue CAGR 5Y min',0,-100,100),('pat_cagr_5yr_min','PAT CAGR 5Y min',0,-100,100),('opm_min','OPM min',0,-100,100),('pe_max','P/E max',100,0,300),('pb_max','P/B max',30,0,100),('dividend_yield_min','Dividend yield min',0,0,20),('icr_min','ICR min',0,0,100)]
for k,l,v,lo,hi in sliders: filters[k]=st.sidebar.slider(l,float(lo),float(hi),float(v))
if preset!='Custom': filters.update(PRESETS[preset])
out=apply_filters(df,filters); st.write(f'{len(out)} companies match your filters'); st.dataframe(out,use_container_width=True,hide_index=True); st.download_button('Download CSV',out.to_csv(index=False).encode('utf-8-sig'),'screener_results.csv','text/csv')
