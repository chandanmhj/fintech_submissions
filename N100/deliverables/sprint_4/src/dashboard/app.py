from pathlib import Path
import streamlit as st
st.set_page_config(page_title='Nifty 100 Analytics',layout='wide',initial_sidebar_state='expanded')
st.title('Nifty 100 Analytics')
p=Path(__file__).resolve().parents[2]/'pages'
names=['01_home.py','02_profile.py','03_screener.py','04_peers.py','05_trends.py','06_sectors.py','07_capital.py','08_reports.py']
titles=['Home','Company Profile','Screener','Peer Comparison','Trend Analysis','Sector Analysis','Capital Allocation','Annual Reports']
missing=[n for n in names if not (p/n).exists()]
if missing: st.error('Missing pages: '+', '.join(missing)); st.stop()
st.navigation([st.Page(p/n,title=t) for n,t in zip(names,titles)]).run()
