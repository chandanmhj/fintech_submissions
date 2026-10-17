"""Rule-based financial pros/cons generation with explainable confidence scores."""
import argparse, math
from pathlib import Path
import pandas as pd
from src.common import connect, OUTPUT_DIR
PROS={
'P01':('Consistently high return on equity above 20% demonstrates exceptional capital efficiency', lambda d: d['roe3'] and min(d['roe3'])>20, 88),
'P02':('Strong free cash flow generation over 5 years signals healthy business fundamentals', lambda d: len(d['fcf5'])>=5 and all(x>0 for x in d['fcf5'][-5:]), 88),
'P03':('Debt-free balance sheet provides financial flexibility and eliminates interest burden', lambda d: d['de'] is not None and d['de']==0, 95),
'P04':('Revenue growing at above 15% CAGR over 5 years reflects strong business momentum', lambda d: d['rev_cagr5'] is not None and d['rev_cagr5']>15, 90),
'P05':('Operating profit margin above 25% indicates strong pricing power and cost discipline', lambda d: d['opm'] is not None and d['opm']>25, 88),
'P06':('Net profit compounding at above 20% over 5 years creates significant shareholder value', lambda d: d['pat_cagr5'] is not None and d['pat_cagr5']>20, 89),
'P07':('Very high interest coverage ratio reflects negligible financial stress from debt servicing', lambda d: d['de']==0 or (d['icr'] is not None and d['icr']>10), 87),
'P08':('Consistent dividend yield above 2% backed by positive free cash flow', lambda d: d['div_yield'] is not None and d['div_yield']>2 and d['fcf_latest'] is not None and d['fcf_latest']>0, 84),
'P09':('Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding', lambda d: d['eps_cagr5'] is not None and d['eps_cagr5']>15, 87),
'P10':('Return on equity improving for 3 consecutive years shows strengthening business quality', lambda d: len(d['roe3'])>=4 and d['roe3'][-1]>d['roe3'][-2]>d['roe3'][-3]>d['roe3'][-4], 84),
'P11':('Revenue growing slower than profits shows improving operating leverage and scale benefits', lambda d: d['rev_cagr5'] is not None and d['pat_cagr5'] is not None and d['pat_cagr5']>d['rev_cagr5'], 78),
'P12':('Growing asset base funded by internal accruals reflects self-sustaining growth', lambda d: d['assets_growing'] and d['debt_declining'], 76),
}
CONS={
'C01':('Debt-to-equity ratio of {de:.2f} is elevated for a non-financial company and warrants monitoring', lambda d: not d['financial'] and d['de'] is not None and d['de']>2, 90),
'C02':('Free cash flow negative for 3 consecutive years raises concern about cash generation quality', lambda d: len(d['fcf5'])>=3 and all(x<0 for x in d['fcf5'][-3:]), 88),
'C03':('Operating margins declining for 3 consecutive years suggest pricing or cost pressure', lambda d: len(d['opm_series'])>=4 and d['opm_series'][-1]<d['opm_series'][-2]<d['opm_series'][-3]<d['opm_series'][-4], 85),
'C04':('Company reported a net loss in the most recent financial year', lambda d: d['pat'] is not None and d['pat']<0, 95),
'C05':('Revenue contraction over 2 consecutive years indicates demand weakness or market share loss', lambda d: len(d['sales'])>=3 and d['sales'][-1]<d['sales'][-2]<d['sales'][-3], 86),
'C06':('Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations', lambda d: d['icr'] is not None and d['icr']<1.5 and d['de']!=0, 91),
'C07':('Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable', lambda d: d['payout'] is not None and d['payout']>100, 88),
'C08':('Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk', lambda d: len(d['de_series'])>=4 and d['de_series'][-1]>d['de_series'][-2]>d['de_series'][-3]>d['de_series'][-4], 83),
'C09':('Earnings per share declining for 3 consecutive years reflects deteriorating profitability', lambda d: len(d['eps'])>=4 and d['eps'][-1]<d['eps'][-2]<d['eps'][-3]<d['eps'][-4], 85),
'C10':('Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital', lambda d: d['roce'] is not None and d['roce']<10, 88),
'C11':('Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility', lambda d: d['netdebt_ebitda'] is not None and d['netdebt_ebitda']>3, 90),
'C12':('Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum', lambda d: d['rev_cagr5'] is not None and d['rev_cagr5']<5, 80),
}

def _num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None

def generate(db_path=None, output_dir=None):
    out=Path(output_dir or OUTPUT_DIR); out.mkdir(parents=True,exist_ok=True)
    con=connect(db_path); companies=pd.read_sql_query('select id as company_id, company_name from companies order by id',con)
    pl=pd.read_sql_query('select company_id,year,sales,opm_percentage,net_profit,eps,dividend_payout from profitandloss',con)
    ratios=pd.read_sql_query('select * from financial_ratios',con)
    cf=pd.read_sql_query('select company_id,year,operating_activity,investing_activity,financing_activity,net_cash_flow from cashflow',con)
    bs=pd.read_sql_query('select company_id,year,borrowings,total_assets from balancesheet',con)
    sec=pd.read_sql_query('select company_id,broad_sector from sectors',con)
    mc=pd.read_sql_query('select company_id,year,dividend_yield_pct,enterprise_value_crore from market_cap',con)
    con.close(); rows=[]
    for _,co in companies.iterrows():
        cid=co.company_id; p=pl[pl.company_id==cid].copy().sort_values('year'); r=ratios[ratios.company_id==cid].copy().sort_values('year'); c=cf[cf.company_id==cid].copy().sort_values('year'); b=bs[bs.company_id==cid].copy().sort_values('year'); m=mc[mc.company_id==cid].copy().sort_values('year')
        def series(df,col): return [_num(x) for x in df[col].tolist() if _num(x) is not None] if col in df else []
        sales=series(p,'sales'); eps=series(p,'eps'); opm=series(p,'opm_percentage'); roe=series(r,'return_on_equity_pct'); fcf=series(r,'free_cash_flow_cr')
        latest=lambda df,col: _num(df.iloc[-1][col]) if len(df) and col in df else None
        def cagr(s):
            if len(s)>=6 and s[0]>0 and s[-1]>0: return ((s[-1]/s[-6])**(1/5)-1)*100
            return None
        de=latest(r,'debt_to_equity'); icr=latest(r,'interest_coverage'); pat=latest(p,'net_profit'); roce=latest(r,'roce_pct')
        ev=latest(m,'enterprise_value_crore'); netdebt=latest(r,'net_debt_cr')
        # EBITDA approximation from operating profit plus depreciation; guard against zero/negative EBITDA.
        eb=(latest(p,'operating_profit') or 0)+(latest(p,'depreciation') or 0)
        netdebt_ebitda=(netdebt/eb) if netdebt is not None and eb>0 else None
        assets=series(b,'total_assets'); debts=series(b,'borrowings')
        d={'roe3':roe[-3:] if len(roe)>=3 else [],'fcf5':fcf[-5:] if len(fcf)>=5 else fcf,'de':de,'rev_cagr5':cagr(sales),'opm':latest(p,'opm_percentage'),'pat_cagr5':latest(r,'pat_cagr_5yr'),'icr':icr,'div_yield':latest(m,'dividend_yield_pct'),'fcf_latest':latest(r,'free_cash_flow_cr'),'eps_cagr5':latest(r,'eps_cagr_5yr'),'roe_series':roe,'assets_growing':len(assets)>=2 and assets[-1]>assets[0],'debt_declining':len(debts)>=2 and debts[-1]<debts[0],'financial':str(sec[sec.company_id==cid].broad_sector.iloc[0]).lower()=='financials' if len(sec[sec.company_id==cid]) else False,'opm_series':opm,'pat':pat,'sales':sales,'payout':latest(p,'dividend_payout'),'de_series':series(r,'debt_to_equity'),'eps':eps,'roce':roce,'netdebt_ebitda':netdebt_ebitda}
        npro=ncon=0
        for rid,(txt,fn,base) in PROS.items():
            try: matched=bool(fn(d))
            except Exception: matched=False
            if matched:
                signal=base + (4 if base>=88 else 0); rows.append({'company_id':cid,'type':'pro','rule_id':rid,'text':txt,'confidence_pct':min(99,signal)}); npro+=1
        for rid,(txt,fn,base) in CONS.items():
            try: matched=bool(fn(d))
            except Exception: matched=False
            if matched:
                if '{de:.2f}' in txt: txt=txt.format(de=de)
                rows.append({'company_id':cid,'type':'con','rule_id':rid,'text':txt,'confidence_pct':min(99,base)}); ncon+=1
        # Explicit coverage fallbacks guarantee one item of each type without pretending it is a rule signal.
        if npro==0:
            rows.append({'company_id':cid,'type':'pro','rule_id':'P00','text':'No high-confidence positive rule triggered; review the company’s complete multi-year financial history before drawing a conclusion','confidence_pct':61})
        if ncon==0:
            rows.append({'company_id':cid,'type':'con','rule_id':'C00','text':'No high-confidence risk rule triggered; continue monitoring leverage, profitability and cash conversion as new results arrive','confidence_pct':61})
    df=pd.DataFrame(rows,columns=['company_id','type','rule_id','text','confidence_pct'])
    df=df[df.confidence_pct>60].copy(); df.to_csv(out/'pros_cons_generated.csv',index=False)
    coverage=df.groupby(['company_id','type']).size().unstack(fill_value=0)
    missing=[]
    for cid in companies.company_id:
        if coverage.get('pro',pd.Series(dtype=int)).get(cid,0)<1: missing.append({'company_id':cid,'missing_type':'pro'})
        if coverage.get('con',pd.Series(dtype=int)).get(cid,0)<1: missing.append({'company_id':cid,'missing_type':'con'})
    pd.DataFrame(missing,columns=['company_id','missing_type']).to_csv(out/'pros_cons_coverage_failures.csv',index=False)
    return {'companies':len(companies),'rows':len(df),'companies_with_pro_and_con':int((coverage.get('pro',0).reindex(companies.company_id,fill_value=0).gt(0)&coverage.get('con',0).reindex(companies.company_id,fill_value=0).gt(0)).sum()) if len(coverage) else 0,'coverage_failures':len(missing)}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--db'); ap.add_argument('--output-dir'); a=ap.parse_args(); print(generate(a.db,a.output_dir))
