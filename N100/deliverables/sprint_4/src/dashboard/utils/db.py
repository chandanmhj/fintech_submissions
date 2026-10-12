from pathlib import Path
import sqlite3, pandas as pd, streamlit as st
DB_PATH=Path(__file__).resolve().parents[3]/'data'/'nifty100.db'
def _q(sql,params=()):
 with sqlite3.connect(DB_PATH) as c: return pd.read_sql_query(sql,c,params=params)
@st.cache_data(ttl=600)
def get_companies(): return _q('SELECT c.id company_id,c.company_name,c.about_company,c.website,c.nse_profile,c.bse_profile,c.roce_percentage,c.roe_percentage,s.broad_sector,s.sub_sector FROM companies c LEFT JOIN sectors s ON s.company_id=c.id ORDER BY c.company_name')
@st.cache_data(ttl=600)
def get_ratios(ticker,year=None):
 sql='SELECT * FROM financial_ratios WHERE company_id=?'; p=[ticker]
 if year is not None: sql+=' AND year=?'; p.append(str(year))
 return _q(sql+' ORDER BY year',tuple(p))
@st.cache_data(ttl=600)
def get_pl(ticker): return _q('SELECT * FROM profitandloss WHERE company_id=? ORDER BY year',(ticker,))
@st.cache_data(ttl=600)
def get_bs(ticker): return _q('SELECT * FROM balancesheet WHERE company_id=? ORDER BY year',(ticker,))
@st.cache_data(ttl=600)
def get_cf(ticker): return _q('SELECT * FROM cashflow WHERE company_id=? ORDER BY year',(ticker,))
@st.cache_data(ttl=600)
def get_sectors(): return _q('SELECT * FROM sectors ORDER BY broad_sector')
@st.cache_data(ttl=600)
def get_peers(group_name): return _q('SELECT pg.*,c.company_name,fr.* FROM peer_groups pg LEFT JOIN companies c ON c.id=pg.company_id LEFT JOIN financial_ratios fr ON fr.company_id=pg.company_id WHERE pg.peer_group_name=?',(group_name,))
@st.cache_data(ttl=600)
def get_valuation(ticker): return _q('SELECT * FROM market_cap WHERE company_id=? ORDER BY year DESC',(ticker,))
@st.cache_data(ttl=600)
def get_market_cap(): return _q('SELECT * FROM market_cap')
@st.cache_data(ttl=600)
def get_documents(ticker): return _q('SELECT * FROM documents WHERE company_id=? ORDER BY year DESC',(ticker,))
@st.cache_data(ttl=600)
def get_pros_cons(ticker): return _q('SELECT * FROM prosandcons WHERE company_id=?',(ticker,))
