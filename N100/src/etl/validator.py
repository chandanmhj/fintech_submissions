import os, re, sqlite3, pandas as pd, numpy as np
from .normaliser import normalize_year, normalize_ticker

RULES={
'DQ-01':('Company PK Uniqueness','CRITICAL'),'DQ-02':('Annual PK Uniqueness','CRITICAL'),'DQ-03':('FK Integrity','CRITICAL'),'DQ-04':('Balance Sheet Balance','WARNING'),'DQ-05':('OPM Cross-Check','WARNING'),'DQ-06':('Positive Sales','WARNING'),'DQ-07':('Year Format','CRITICAL'),'DQ-08':('Ticker Format','CRITICAL'),'DQ-09':('Net Cash Check','WARNING'),'DQ-10':('Non-Negative Fixed Assets','WARNING'),'DQ-11':('Tax Rate Range','WARNING'),'DQ-12':('Dividend Payout Cap','WARNING'),'DQ-13':('URL Validity','WARNING'),'DQ-14':('EPS Sign Consistency','WARNING'),'DQ-15':('BSE/ASE Balance','INFO'),'DQ-16':('Coverage Check','WARNING')}

def _issue(rule, table, row, company, year, message):
    name,severity=RULES[rule]; return {'rule_id':rule,'rule_name':name,'severity':severity,'table':table,'row':row,'company_id':company,'year':year,'message':message}

def validate_frames(frames):
    issues=[]; companies=frames['companies']; ids=set(companies['id'].astype(str))
    if companies['id'].duplicated().any():
        for i in companies.index[companies['id'].duplicated(keep=False)]: issues.append(_issue('DQ-01','companies',i,companies.loc[i,'id'],None,'duplicate company primary key'))
    for t in ['profitandloss','balancesheet','cashflow']:
        df=frames.get(t); 
        if df is None: continue
        if df.duplicated(['company_id','year']).any():
            for i in df.index[df.duplicated(['company_id','year'],keep=False)]: issues.append(_issue('DQ-02',t,i,df.loc[i,'company_id'],df.loc[i,'year'],'duplicate company/year key'))
        for i,r in df.iterrows():
            if r.get('company_id') not in ids: issues.append(_issue('DQ-03',t,i,r.get('company_id'),r.get('year'),'orphan company_id'))
            if t=='profitandloss':
                if pd.notna(r.get('sales')) and r['sales']<=0: issues.append(_issue('DQ-06',t,i,r['company_id'],r['year'],'sales <= 0'))
                if pd.notna(r.get('sales')) and r['sales']!=0 and pd.notna(r.get('operating_profit')) and pd.notna(r.get('opm_percentage')) and abs(r['opm_percentage']-r['operating_profit']/r['sales']*100)>=1: issues.append(_issue('DQ-05',t,i,r['company_id'],r['year'],'OPM mismatch'))
                if pd.notna(r.get('tax_percentage')) and not 0<=r['tax_percentage']<=60: issues.append(_issue('DQ-11',t,i,r['company_id'],r['year'],'tax percentage outside 0-60'))
                if pd.notna(r.get('dividend_payout')) and r['dividend_payout']>200: issues.append(_issue('DQ-12',t,i,r['company_id'],r['year'],'dividend payout > 200%'))
                if pd.notna(r.get('net_profit')) and pd.notna(r.get('eps')) and r['net_profit']>0 and r['eps']<=0: issues.append(_issue('DQ-14',t,i,r['company_id'],r['year'],'EPS sign inconsistent with profit'))
            if t=='balancesheet':
                if pd.notna(r.get('total_assets')) and r['total_assets']!=0 and pd.notna(r.get('total_liabilities')):
                    if abs(r['total_assets']-r['total_liabilities'])/abs(r['total_assets'])>=.01: issues.append(_issue('DQ-04',t,i,r['company_id'],r['year'],'assets/liabilities differ by >=1%'))
                if pd.notna(r.get('fixed_assets')) and r['fixed_assets']<0: issues.append(_issue('DQ-10',t,i,r['company_id'],r['year'],'negative fixed assets'))
                if pd.notna(r.get('total_assets')) and pd.notna(r.get('total_liabilities')) and r['total_assets']!=r['total_liabilities']: issues.append(_issue('DQ-15',t,i,r['company_id'],r['year'],'strict balance mismatch'))
            if t=='cashflow':
                vals=[r.get('operating_activity'),r.get('investing_activity'),r.get('financing_activity')]
                if all(pd.notna(x) for x in vals) and pd.notna(r.get('net_cash_flow')) and abs(r['net_cash_flow']-sum(vals))>10: issues.append(_issue('DQ-09',t,i,r['company_id'],r['year'],'net cash differs from components by >10'))
            if t in ['profitandloss','balancesheet','cashflow'] and not re.fullmatch(r'\d{4}-\d{2}',str(r.get('year'))): issues.append(_issue('DQ-07',t,i,r.get('company_id'),r.get('year'),'invalid normalized year'))
    for t,df in frames.items():
        if 'company_id' in df:
            for i,v in df['company_id'].items():
                s=normalize_ticker(v) or ''
                if not 2<=len(s)<=12: issues.append(_issue('DQ-08',t,i,v,None,'ticker length outside 2-12'))
    docs=frames.get('documents')
    if docs is not None and 'annual_report' in docs:
        for i,r in docs.iterrows():
            url=str(r.get('annual_report') or '')
            if not re.match(r'^https?://[^\s]+$', url): issues.append(_issue('DQ-13','documents',i,r.get('company_id'),r.get('year'),'invalid annual report URL format'))
    for cid in ids:
        counts=[]
        for t in ['profitandloss','balancesheet','cashflow']:
            counts.append(len(frames[t][frames[t].company_id==cid]) if t in frames else 0)
        if min(counts)<5: issues.append(_issue('DQ-16','coverage',None,cid,None,f'coverage below 5 years: {counts}'))
    return pd.DataFrame(issues,columns=['rule_id','rule_name','severity','table','row','company_id','year','message'])
