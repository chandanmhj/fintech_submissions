from pathlib import Path
import logging, sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/"data/raw"; PROCESSED=ROOT/"data/processed"; DB=ROOT/"data/db/bluestock_mf.db"; SCHEMA=ROOT/"sql/schema.sql"
EXPECTED={"01_fund_master.csv","02_nav_history.csv","03_aum_by_fund_house.csv","04_monthly_sip_inflows.csv","05_category_inflows.csv","06_industry_folio_count.csv","07_scheme_performance.csv","08_investor_transactions.csv","09_portfolio_holdings.csv","10_benchmark_indices.csv"}
MAP={"01_fund_master":"dim_fund","02_nav_history":"fact_nav","03_aum_by_fund_house":"fact_aum_fund_house","04_monthly_sip_inflows":"fact_monthly_sip","06_industry_folio_count":"fact_folio_count","07_scheme_performance":"fact_scheme_performance","08_investor_transactions":"fact_investor_transactions","09_portfolio_holdings":"fact_portfolio_holdings","10_benchmark_indices":"fact_benchmark"}
logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
def clean(df):
 df=df.copy(); df.columns=[c.strip().lower().replace(' ','_').replace('-','_').replace('%','pct').replace('(','').replace(')','').replace('/','_') for c in df.columns]
 for c in df.columns:
  if df[c].dtype=='object': df[c]=df[c].map(lambda x:x.strip() if isinstance(x,str) else x)
  if 'date' in c or c in {'month','report_date'}:
   p=pd.to_datetime(df[c],errors='coerce');
   if p.notna().any(): df[c]=p.dt.strftime('%Y-%m-%d')
 return df.drop_duplicates().reset_index(drop=True)
def main():
 PROCESSED.mkdir(parents=True,exist_ok=True); DB.parent.mkdir(parents=True,exist_ok=True); files=sorted(RAW.glob('*.csv')); names={p.name for p in files}
 missing=EXPECTED-names
 if missing: logging.warning('Missing from supplied package: %s',sorted(missing))
 reports=[]; loaded={}
 for p in files:
  df=clean(pd.read_csv(p)); df.to_csv(PROCESSED/p.name,index=False); reports += [{'dataset':p.name,'check':'rows','value':len(df),'status':'PASS' if len(df) else 'FAIL'},{'dataset':p.name,'check':'duplicates','value':int(df.duplicated().sum()),'status':'PASS' if not df.duplicated().sum() else 'WARN'},{'dataset':p.name,'check':'missing_cells','value':int(df.isna().sum().sum()),'status':'INFO'}]; loaded[MAP.get(p.stem,p.stem)]=df
 if DB.exists(): DB.unlink()
 con=sqlite3.connect(DB); con.executescript(SCHEMA.read_text())
 for t,df in loaded.items():
  cols=[r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]; cols=[c for c in cols if c in df.columns]
  if not cols: continue
  sql=f'INSERT INTO "{t}" ({",".join(cols)}) VALUES ({",".join(["?"]*len(cols))})'; rows=[tuple(None if pd.isna(v) else v for v in r) for r in df[cols].itertuples(False,None)]; con.executemany(sql,rows); logging.info('Loaded %s: %d rows',t,len(rows))
 con.commit(); con.close(); pd.DataFrame(reports).to_csv(PROCESSED/'data_quality_report.csv',index=False); logging.info('Done: %s',DB)
if __name__=='__main__': main()
