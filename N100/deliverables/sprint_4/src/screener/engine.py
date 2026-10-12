from pathlib import Path
import sqlite3,pandas as pd
ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'data'/'nifty100.db'
PRESETS={'Quality Compounder':{'roe_min':15,'de_max':1,'fcf_min':0,'revenue_cagr_5yr_min':10},'Value Pick':{'pe_max':20,'pb_max':3,'de_max':2,'dividend_yield_min':1},'Growth Accelerator':{'pat_cagr_5yr_min':20,'revenue_cagr_5yr_min':15,'de_max':2},'Dividend Champion':{'dividend_yield_min':2,'dividend_payout_ratio_pct_max':80,'fcf_min':0},'Debt-Free Blue Chip':{'de_min':0,'de_max':0,'roe_min':12,'sales_min':5000},'Turnaround Watch':{'revenue_cagr_3yr_min':10,'fcf_min':0}}
def load_screener_frame(db_path=DB):
 with sqlite3.connect(db_path) as c: df=pd.read_sql_query('SELECT c.id company_id,c.company_name,s.broad_sector,p.sales,p.net_profit,m.pe_ratio,m.pb_ratio,m.dividend_yield_pct,fr.* FROM companies c LEFT JOIN sectors s ON s.company_id=c.id LEFT JOIN financial_ratios fr ON fr.company_id=c.id LEFT JOIN profitandloss p ON p.company_id=c.id AND p.year=fr.year LEFT JOIN market_cap m ON m.company_id=c.id AND m.year=fr.year',c)
 return df.sort_values('year').groupby('company_id',as_index=False).tail(1)
def apply_filters(df,filters):
 x=df.copy(); mp={'roe_min':('return_on_equity_pct',1),'de_max':('debt_to_equity',-1),'de_min':('debt_to_equity',1),'fcf_min':('free_cash_flow_cr',1),'revenue_cagr_5yr_min':('revenue_cagr_5yr',1),'pat_cagr_5yr_min':('pat_cagr_5yr',1),'revenue_cagr_3yr_min':('revenue_cagr_3yr',1),'opm_min':('operating_profit_margin_pct',1),'pe_max':('pe_ratio',-1),'pb_max':('pb_ratio',-1),'dividend_yield_min':('dividend_yield_pct',1),'dividend_payout_ratio_pct_max':('dividend_payout_ratio_pct',-1),'icr_min':('interest_coverage',1),'sales_min':('sales',1)}
 for k,(col,sign) in mp.items():
  if k not in filters or col not in x: continue
  if k in ('de_max','de_min') and 'broad_sector' in x: x=x[x.broad_sector!='Financials']
  v=pd.to_numeric(x[col],errors='coerce'); x=x[v>=filters[k]] if sign==1 else x[v<=filters[k]]
 if 'icr_min' in filters and 'icr_label' in x: x=x[(x.icr_label=='Debt Free')|pd.to_numeric(x.interest_coverage,errors='coerce').ge(filters['icr_min'])]
 return x.sort_values('composite_quality_score',ascending=False) if 'composite_quality_score' in x else x
