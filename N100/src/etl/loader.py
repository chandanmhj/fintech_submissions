import os, sqlite3, glob, pandas as pd
from pathlib import Path
from .normaliser import normalize_dataframe, normalize_year, normalize_ticker
from .validator import validate_frames
ROOT=Path(__file__).resolve().parents[2]; RAW=ROOT/'data/raw'; SUPPORTING=ROOT/'data/supporting'; DB=ROOT/'data/nifty100.db'; OUT=ROOT/'output'
FILES={'companies':'companies.xlsx','profitandloss':'profitandloss.xlsx','balancesheet':'balancesheet.xlsx','cashflow':'cashflow.xlsx','analysis':'analysis.xlsx','documents':'documents.xlsx','prosandcons':'prosandcons.xlsx','sectors':'sectors.xlsx','stock_prices':'stock_prices.xlsx','market_cap':'market_cap.xlsx','financial_ratios':'financial_ratios.xlsx','peer_groups':'peer_groups.xlsx'}

def find_file(name):
    hits=list(RAW.glob(f'*{name}')) + list(SUPPORTING.glob(f'*{name}'))
    if not hits: raise FileNotFoundError(name)
    return hits[0]

def read_source(table):
    f=find_file(FILES[table]); df=pd.read_excel(f,header=1 if table in {'companies','profitandloss','balancesheet','cashflow','analysis','documents','prosandcons'} else 0)
    df=normalize_dataframe(df)
    if table=='companies': df=df.rename(columns={'id':'id'}); df['id']=df['id'].map(normalize_ticker)
    if 'company_id' in df: df['company_id']=df['company_id'].replace({'AGTL':'ATGL'})
    if table in {'profitandloss','balancesheet','cashflow'}: df=df.drop_duplicates(['company_id','year'],keep='last')
    if 'id' in df: df['id']=pd.to_numeric(df['id'],errors='coerce').astype('Int64') if table!='companies' else df['id']
    return df

def load():
    OUT.mkdir(exist_ok=True)
    frames={k:read_source(k) for k in FILES}
    ids=set(frames['companies']['id'].astype(str))
    rejection_audit={}
    for table,df in frames.items():
        if 'company_id' in df:
            before=len(df)
            frames[table]=df[df.company_id.isin(ids)].copy()
            rejection_audit[table]=before-len(frames[table])
        else: rejection_audit[table]=0
    failures=validate_frames(frames)
    failures.to_csv(OUT/'validation_failures.csv',index=False)
    DB.parent.mkdir(exist_ok=True)
    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB)
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript((ROOT/'db/schema.sql').read_text())
    audits=[]
    for table in FILES:
        df=frames[table].copy()
        df.to_sql(table,con,if_exists='append',index=False)
        audits.append({'table':table,'source_file':FILES[table],'rows_in':len(df)+rejection_audit.get(table,0),'rows_out':len(df),'rejected':rejection_audit.get(table,0),'critical_rejections':0})
    fk=list(con.execute('PRAGMA foreign_key_check'))
    con.commit(); con.close()
    pd.DataFrame(audits).to_csv(OUT/'load_audit.csv',index=False)
    if fk: raise RuntimeError(f'FK violations: {fk[:5]}')
    return DB
if __name__=='__main__': print(load())
