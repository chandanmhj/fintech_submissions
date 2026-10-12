import streamlit as st,pandas as pd,plotly.express as px,sqlite3
from src.dashboard.utils.db import DB_PATH,get_companies
st.title('Sector Analysis'); c=get_companies(); sec=st.selectbox('Sector',sorted(c.broad_sector.dropna().unique()))
with sqlite3.connect(DB_PATH) as db: d=pd.read_sql_query('SELECT c.id company_id,c.company_name,s.broad_sector,s.sub_sector,p.sales,fr.return_on_equity_pct,m.market_cap_crore FROM companies c LEFT JOIN sectors s ON s.company_id=c.id LEFT JOIN profitandloss p ON p.company_id=c.id LEFT JOIN financial_ratios fr ON fr.company_id=c.id AND fr.year=p.year LEFT JOIN market_cap m ON m.company_id=c.id WHERE s.broad_sector=?',(db,),params=(sec,))
d=d.groupby('company_id').tail(1); st.plotly_chart(px.scatter(d,x='sales',y='return_on_equity_pct',size='market_cap_crore',color='sub_sector',hover_name='company_name'),use_container_width=True); st.dataframe(d.select_dtypes('number').median().to_frame('sector median'))
