from pathlib import Path
import sqlite3, numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'data'/'nifty100.db'; OUT=ROOT/'output'
def build_valuation(db_path=DB,output_dir=OUT):
 output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect(db_path) as c:
  df=pd.read_sql_query('SELECT c.id company_id,c.company_name,s.broad_sector sector,m.year,m.pe_ratio pe,m.pb_ratio pb,m.ev_ebitda,m.market_cap_crore,fr.free_cash_flow_cr FROM companies c LEFT JOIN sectors s ON s.company_id=c.id LEFT JOIN market_cap m ON m.company_id=c.id LEFT JOIN financial_ratios fr ON fr.company_id=c.id AND fr.year=m.year',c)
 df['yr']=pd.to_numeric(df.year.astype(str).str.extract(r'(\d{4})')[0],errors='coerce'); df=df.sort_values(['company_id','yr']).drop_duplicates('company_id',keep='last')
 df['FCF_yield_pct']=np.where(df.market_cap_crore>0,df.free_cash_flow_cr/df.market_cap_crore*100,np.nan)
 df['5yr_median_PE']=df.groupby('sector').pe.transform('median'); df['PE_vs_sector_median_pct']=np.where(df['5yr_median_PE']>0,(df.pe/df['5yr_median_PE']-1)*100,np.nan)
 df['flag']=np.select([df.pe.notna()&(df.pe>df['5yr_median_PE']*1.5),df.pe.notna()&(df.pe<df['5yr_median_PE']*.7)],['Caution','Discount'],'Fair')
 out=df[['company_id','company_name','sector','pe','pb','ev_ebitda','FCF_yield_pct','5yr_median_PE','PE_vs_sector_median_pct','flag']].rename(columns={'pe':'P/E','pb':'P/B','ev_ebitda':'EV/EBITDA'})
 out.to_excel(output_dir/'valuation_summary.xlsx',index=False); out[out.flag.isin(['Caution','Discount'])].to_csv(output_dir/'valuation_flags.csv',index=False); return out
if __name__=='__main__': print('Generated',len(build_valuation()),'valuation rows')
