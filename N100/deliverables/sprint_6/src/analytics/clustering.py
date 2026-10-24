"""KMeans clustering and diagnostics for Nifty100 company financials."""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
FEATURES = ['return_on_equity_pct','debt_to_equity','revenue_cagr_5yr','fcf_cagr_5yr','operating_profit_margin_pct']

def connect(db_path=None):
    """Open the configured Nifty100 SQLite database."""
    p=Path(db_path or __import__('os').getenv('N100_DB','data/nifty100.db'))
    if not p.exists() and Path('db/nifty100.db').exists(): p=Path('db/nifty100.db')
    if not p.exists(): raise FileNotFoundError(f'Database not found: {p}; set N100_DB')
    return sqlite3.connect(p)

def load_features(db_path=None):
    """Load latest company financial ratios and sector labels."""
    c=connect(db_path)
    try:
        q="""WITH latest AS (SELECT company_id,MAX(year) year FROM financial_ratios GROUP BY company_id)
        SELECT co.id company_id,co.company_name,COALESCE(s.broad_sector,'Unknown') broad_sector,
        r.return_on_equity_pct,r.debt_to_equity,r.revenue_cagr_5yr,r.operating_profit_margin_pct
        FROM companies co LEFT JOIN latest l ON l.company_id=co.id
        LEFT JOIN financial_ratios r ON r.company_id=l.company_id AND r.year=l.year
        LEFT JOIN sectors s ON s.company_id=co.id"""
        df=pd.read_sql_query(q,c).drop_duplicates('company_id')
        cf=pd.read_sql_query('SELECT company_id,year,operating_activity,investing_activity FROM cashflow ORDER BY year',c)
        cf['fcf']=cf.operating_activity.fillna(0)+cf.investing_activity.fillna(0)
        fcf={}
        for cid,g in cf.groupby('company_id'):
            v=g.sort_values('year').fcf.tolist()
            fcf[cid]=((v[-1]/v[-6])**.2-1)*100 if len(v)>=6 and v[-1]>0 and v[-6]>0 else np.nan
        df['fcf_cagr_5yr']=df.company_id.map(fcf)
        return df
    finally: c.close()

def run(db_path=None,output_dir='output',reports_dir='reports'):
    """Fit five clusters and export cluster, outlier, statistics, and chart artifacts."""
    out=Path(output_dir); rep=Path(reports_dir); out.mkdir(parents=True,exist_ok=True); rep.mkdir(parents=True,exist_ok=True)
    df=load_features(db_path)
    if len(df)<5: raise ValueError('At least five company records are required')
    x=df[FEATURES].copy()
    for col in FEATURES:
        med=x[col].groupby(df.broad_sector).transform('median')
        x[col]=x[col].fillna(med).fillna(x[col].median()).fillna(0)
    scaler=StandardScaler(); X=scaler.fit_transform(x)
    inertia=[]
    for k in range(2,min(10,len(df)-1)+1): inertia.append((k,KMeans(n_clusters=k,random_state=42,n_init=20).fit(X).inertia_))
    model=KMeans(n_clusters=5,random_state=42,n_init=20); labels=model.fit_predict(X)
    profiles=x.assign(cluster_id=labels).groupby('cluster_id')[FEATURES].median().sort_values(['return_on_equity_pct','revenue_cagr_5yr'])
    archetypes=['Distressed or Turnaround','Value Cyclicals','Defensive Dividend Payers','Emerging Growth','High-Quality Compounders']
    name_map={cid:name for cid,name in zip(profiles.index,archetypes)}
    pd.DataFrame({'company_id':df.company_id,'cluster_id':labels,'cluster_name':[name_map[i] for i in labels],'distance_from_centroid':np.linalg.norm(X-model.cluster_centers_[labels],axis=1)}).to_csv(out/'cluster_labels.csv',index=False)
    pd.DataFrame(inertia,columns=['k','inertia']).to_csv(out/'elbow_inertia.csv',index=False)
    profiles=x.assign(cluster_id=labels).groupby('cluster_id')[FEATURES].agg(['mean','median']); profiles.to_csv(out/'cluster_profiles.csv')
    fig,ax=plt.subplots(figsize=(7,4)); ax.plot([i[0] for i in inertia],[i[1] for i in inertia],marker='o'); ax.set(xlabel='k',ylabel='Inertia',title='KMeans elbow curve'); fig.tight_layout(); fig.savefig(rep/'elbow_plot.png',dpi=150); plt.close(fig)
    c=connect(db_path)
    try:
        latest=pd.read_sql_query("SELECT r.* FROM financial_ratios r JOIN (SELECT company_id,MAX(year) year FROM financial_ratios GROUP BY company_id) x ON x.company_id=r.company_id AND x.year=r.year",c)
        cols=[m for m in ['net_profit_margin_pct','operating_profit_margin_pct','return_on_equity_pct','debt_to_equity','interest_coverage','asset_turnover','free_cash_flow_cr','capex_cr','earnings_per_share','roce_pct'] if m in latest and latest[m].notna().sum()>1]
        corr=latest[cols].corr(); fig,ax=plt.subplots(figsize=(10,8)); im=ax.imshow(corr,vmin=-1,vmax=1,cmap='coolwarm'); ax.set_xticks(range(len(cols)),cols,rotation=70,ha='right',fontsize=7); ax.set_yticks(range(len(cols)),cols,fontsize=7)
        for i in range(len(cols)):
            for j in range(len(cols)): ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=6)
        fig.colorbar(im,ax=ax); fig.tight_layout(); fig.savefig(rep/'correlation_heatmap.png',dpi=150); plt.close(fig)
        sec=pd.read_sql_query('SELECT company_id,broad_sector FROM sectors',c).drop_duplicates('company_id'); merged=latest.merge(sec,on='company_id',how='left'); rows=[]
        for col in cols:
            for sector,g in merged.groupby('broad_sector',dropna=False):
                s=pd.to_numeric(g[col],errors='coerce'); sd=s.std(ddof=0)
                if pd.isna(sd) or sd==0: continue
                z=(s-s.mean())/sd
                for ix in g.index[z.abs()>3]: rows.append({'company_id':merged.loc[ix,'company_id'],'broad_sector':sector,'metric':col,'value':merged.loc[ix,col],'z_score':z.loc[ix]})
        pd.DataFrame(rows,columns=['company_id','broad_sector','metric','value','z_score']).to_csv(out/'outlier_report.csv',index=False)
        st=latest[cols].agg(['mean','std']).T
        for label,q in [('P10',.1),('P25',.25),('P50',.5),('P75',.75),('P90',.9)]: st[label]=latest[cols].quantile(q)
        st[['P10','P25','P50','P75','P90','mean','std']].to_csv(out/'portfolio_stats.csv')
    finally: c.close()
    return len(df)
if __name__=='__main__': print(f'Clustered {run()} companies')
