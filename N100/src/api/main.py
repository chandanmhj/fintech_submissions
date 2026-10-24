"""Read-only FastAPI interface for Nifty100 analytics."""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlite3, os, time, logging
from pathlib import Path
START=time.time(); app=FastAPI(title='Nifty100 Analytics API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
logging.basicConfig(level=logging.INFO)
@app.middleware('http')
async def log_request(request,call_next):
    t=time.perf_counter(); response=await call_next(request)
    logging.info('%s %s %.2fms',request.method,request.url.path,(time.perf_counter()-t)*1000)
    return response

def db():
    p=os.getenv('N100_DB','data/nifty100.db')
    if not os.path.exists(p):
        for alt in ['db/nifty100.db','reference_data/nifty100.db']:
            if os.path.exists(alt): p=alt; break
    if not os.path.exists(p): raise HTTPException(503,f'Database not found: {p}. Set N100_DB.')
    c=sqlite3.connect(p); c.row_factory=sqlite3.Row; return c

def allrows(c,q,args=()): return [dict(x) for x in c.execute(q,args).fetchall()]
def exists(c,t): return c.execute('SELECT 1 FROM companies WHERE id=?',(t.upper(),)).fetchone() is not None
def latest_sql(): return """WITH l AS (SELECT company_id,MAX(year) year FROM financial_ratios GROUP BY company_id) SELECT co.id company_id,co.company_name,co.roe_percentage,s.broad_sector,s.sub_sector,s.market_cap_category,r.* FROM companies co LEFT JOIN sectors s ON s.company_id=co.id LEFT JOIN l ON l.company_id=co.id LEFT JOIN financial_ratios r ON r.company_id=l.company_id AND r.year=l.year"""
@app.get('/api/v1/health')
def health():
 c=db()
 try:
  ts=[x['name'] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
  return {'status':'ok','db_row_counts':{t:c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in ts},'uptime_seconds':round(time.time()-START,2),'version':'1.0.0'}
 finally:c.close()
@app.get('/api/v1/companies')
def companies(sector:str|None=None,market_cap_category:str|None=None,search:str|None=None):
 c=db()
 try:
  q=latest_sql()+' WHERE 1=1'; a=[]
  if sector:q+=' AND s.broad_sector LIKE ?';a.append(sector)
  if market_cap_category:q+=' AND s.market_cap_category=?';a.append(market_cap_category)
  if search:q+=' AND (co.id LIKE ? OR co.company_name LIKE ?)';a += [f'%{search}%',f'%{search}%']
  return allrows(c,q+' ORDER BY co.id',a)
 finally:c.close()
@app.get('/api/v1/companies/{ticker}')
def company(ticker:str):
 c=db()
 try:
  r=allrows(c,latest_sql()+' WHERE co.id=?',(ticker.upper(),))
  if not r:raise HTTPException(404,'Ticker not found')
  return r[0]
 finally:c.close()
def history(ticker,table,from_year=None,to_year=None):
 c=db()
 try:
  if not exists(c,ticker):raise HTTPException(404,'Ticker not found')
  q=f'SELECT * FROM {table} WHERE company_id=?';a=[ticker.upper()]
  if from_year:q+=' AND year>=?';a.append(from_year)
  if to_year:q+=' AND year<=?';a.append(to_year)
  return {'ticker':ticker.upper(),'history':allrows(c,q+' ORDER BY year',a)}
 finally:c.close()
@app.get('/api/v1/companies/{ticker}/pl')
def pl(ticker:str,from_year:str|None=None,to_year:str|None=None):return history(ticker,'profitandloss',from_year,to_year)
@app.get('/api/v1/companies/{ticker}/bs')
def bs(ticker:str,from_year:str|None=None,to_year:str|None=None):return history(ticker,'balancesheet',from_year,to_year)
@app.get('/api/v1/companies/{ticker}/cashflow')
def cashflow(ticker:str,from_year:str|None=None,to_year:str|None=None):return history(ticker,'cashflow',from_year,to_year)
@app.get('/api/v1/companies/{ticker}/ratios')
def ratios(ticker:str,year:str|None=None):
 c=db()
 try:
  if not exists(c,ticker):raise HTTPException(404,'Ticker not found')
  q='SELECT * FROM financial_ratios WHERE company_id=?';a=[ticker.upper()]
  if year:q+=' AND year=?';a.append(year)
  return {'ticker':ticker.upper(),'history':allrows(c,q+' ORDER BY year',a)}
 finally:c.close()
@app.get('/api/v1/companies/{ticker}/tearsheet')
def tearsheet(ticker:str):
 p=Path('reports/tearsheets')/f'{ticker.upper()}_tearsheet.pdf'
 if not p.exists():p=Path('reports/tearsheets')/f'{ticker.upper()}.pdf'
 if not p.exists():raise HTTPException(404,'Tearsheet not found')
 return FileResponse(p,media_type='application/pdf',filename=p.name)
@app.get('/api/v1/screener')
def screener(min_roe:float|None=None,max_de:float|None=None,min_fcf:float|None=None,sector:str|None=None,min_rev_cagr_5yr:float|None=None,min_pat_cagr_5yr:float|None=None,max_pe:float|None=None):
 if min_roe is not None and not -100<=min_roe<=200:raise HTTPException(400,'min_roe must be between -100 and 200')
 if max_de is not None and max_de<0:raise HTTPException(400,'max_de must be >= 0')
 c=db()
 try:
  q=latest_sql()+' WHERE 1=1';a=[]
  for col,op,v in [('return_on_equity_pct','>=',min_roe),('debt_to_equity','<=',max_de),('free_cash_flow_cr','>=',min_fcf),('revenue_cagr_5yr','>=',min_rev_cagr_5yr),('pat_cagr_5yr','>=',min_pat_cagr_5yr)]:
   if v is not None:q+=f' AND r.{col}{op}?';a.append(v)
  if sector:q+=' AND s.broad_sector=?';a.append(sector)
  if max_pe is not None:q+=' AND EXISTS(SELECT 1 FROM market_cap m WHERE m.company_id=co.id AND m.year=(SELECT MAX(year) FROM market_cap WHERE company_id=co.id) AND m.pe_ratio<=?)';a.append(max_pe)
  return allrows(c,q+' ORDER BY r.composite_quality_score DESC',a)
 finally:c.close()
@app.get('/api/v1/sectors')
def sectors():
 c=db()
 try:return allrows(c,"SELECT s.broad_sector sector,COUNT(DISTINCT s.company_id) company_count,AVG(r.return_on_equity_pct) median_roe,AVG(m.pe_ratio) median_pe,AVG(r.debt_to_equity) median_de FROM sectors s LEFT JOIN financial_ratios r ON r.company_id=s.company_id AND r.year=(SELECT MAX(year) FROM financial_ratios WHERE company_id=s.company_id) LEFT JOIN market_cap m ON m.company_id=s.company_id AND m.year=(SELECT MAX(year) FROM market_cap WHERE company_id=s.company_id) GROUP BY s.broad_sector ORDER BY s.broad_sector")
 finally:c.close()
@app.get('/api/v1/sectors/{sector}/companies')
def sector_companies(sector:str):
 c=db()
 try:
  r=allrows(c,latest_sql()+' WHERE s.broad_sector=?',(sector,))
  if not r:raise HTTPException(404,'Unknown sector')
  return r
 finally:c.close()
@app.get('/api/v1/peers/{group_name}')
def peers(group_name:str):
 c=db()
 try:
  r=allrows(c,'SELECT p.*,co.company_name FROM peer_percentiles p LEFT JOIN companies co ON co.id=p.company_id WHERE p.peer_group_name=?',(group_name,))
  if not r:raise HTTPException(404,'Unknown peer group')
  return {'peer_group':group_name,'records':r}
 finally:c.close()
@app.get('/api/v1/companies/{ticker}/peers/compare')
def peer_compare(ticker:str):
 c=db()
 try:
  if not exists(c,ticker):raise HTTPException(404,'Ticker not found')
  return {'ticker':ticker.upper(),'axes':allrows(c,'SELECT metric,value,percentile_rank,peer_group_name FROM peer_percentiles WHERE company_id=? LIMIT 8',(ticker.upper(),))}
 finally:c.close()
@app.get('/api/v1/market-cap/{ticker}')
def market_cap(ticker:str):return history(ticker,'market_cap')
@app.get('/api/v1/portfolio/stats')
def portfolio_stats():
 c=db()
 try:
  import pandas as pd
  d=pd.DataFrame(allrows(c,"SELECT r.* FROM financial_ratios r JOIN (SELECT company_id,MAX(year) year FROM financial_ratios GROUP BY company_id) x ON x.company_id=r.company_id AND x.year=r.year")); out={}
  for m in ['net_profit_margin_pct','operating_profit_margin_pct','return_on_equity_pct','debt_to_equity','interest_coverage','asset_turnover','free_cash_flow_cr','capex_cr','earnings_per_share','roce_pct']:
   if m in d:
    s=pd.to_numeric(d[m],errors='coerce').dropna()
    if len(s):
     vals={'P10':s.quantile(.1),'P25':s.quantile(.25),'P50':s.quantile(.5),'P75':s.quantile(.75),'P90':s.quantile(.9),'mean':s.mean(),'std':s.std()}
     out[m]={k:(None if pd.isna(v) else float(v)) for k,v in vals.items()}
  return out
 finally:c.close()
@app.get('/api/v1/companies/{ticker}/documents')
def documents(ticker:str):
 c=db()
 try:
  if not exists(c,ticker):raise HTTPException(404,'Ticker not found')
  d=allrows(c,'SELECT year,annual_report url FROM documents WHERE company_id=? ORDER BY year DESC',(ticker.upper(),))
  return {'ticker':ticker.upper(),'documents':[dict(x,is_url_valid=str(x.get('url') or '').startswith(('https://','http://'))) for x in d]}
 finally:c.close()
@app.get('/api/v1/documents')
def documents_index():return {'status':'ok','note':'Use /companies/{ticker}/documents for company-specific links'}
