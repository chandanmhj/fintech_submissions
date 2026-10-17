"""Cash-flow intelligence, capital-allocation patterns and distress flags."""
import argparse, math
from pathlib import Path
import pandas as pd
from src.common import connect, OUTPUT_DIR

def num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None

def calc(db_path=None, output_dir=None):
    out=Path(output_dir or OUTPUT_DIR); out.mkdir(parents=True,exist_ok=True)
    con=connect(db_path)
    companies=pd.read_sql_query('select id as company_id,company_name from companies',con)
    sectors=pd.read_sql_query('select company_id,broad_sector,sub_sector from sectors',con)
    pl=pd.read_sql_query('select company_id,year,sales,net_profit,eps,dividend_payout,opm_percentage from profitandloss',con)
    cf=pd.read_sql_query('select company_id,year,operating_activity,investing_activity,financing_activity,net_cash_flow from cashflow',con)
    bs=pd.read_sql_query('select company_id,year,borrowings,total_assets,equity_capital,reserves,other_liabilities from balancesheet',con)
    ratios=pd.read_sql_query('select * from financial_ratios',con)
    mc=pd.read_sql_query('select company_id,year,dividend_yield_pct from market_cap',con)
    con.close(); outrows=[]; distress=[]; yearrows=[]
    for _,co in companies.iterrows():
        cid=co.company_id; s=sectors[sectors.company_id==cid]; sector=s.broad_sector.iloc[0] if len(s) else 'Unknown'
        p=pl[pl.company_id==cid].sort_values('year'); c=cf[cf.company_id==cid].sort_values('year'); b=bs[bs.company_id==cid].sort_values('year'); r=ratios[ratios.company_id==cid].sort_values('year'); m=mc[mc.company_id==cid].sort_values('year')
        merged=p[['company_id','year','sales','net_profit']].merge(c,on=['company_id','year'],how='outer',suffixes=('','_cf')).sort_values('year')
        merged['fcf']=merged['operating_activity'].fillna(0)+merged['investing_activity'].fillna(0)
        valid=merged.dropna(subset=['year']).tail(5)
        q=[]
        for _,x in valid.iterrows():
            pat=num(x.get('net_profit')); cfo=num(x.get('operating_activity'))
            if pat is not None and abs(pat)>1e-9 and cfo is not None: q.append(cfo/pat)
        score=sum(q)/len(q) if q else None
        qlabel='High Quality' if score is not None and score>1 else ('Moderate' if score is not None and score>=0.5 else 'Accrual Risk')
        latest=merged.iloc[-1] if len(merged) else {}
        latest_year=str(latest.get('year',''))
        sales=num(latest.get('sales')); cfo=num(latest.get('operating_activity')); cfi=num(latest.get('investing_activity')); cff=num(latest.get('financing_activity')); pat=num(latest.get('net_profit'))
        capex=abs(cfi)/sales*100 if cfi is not None and sales not in (None,0) else None
        caplabel='Asset Light' if capex is not None and capex<3 else ('Moderate' if capex is not None and capex<=8 else 'Capital Intensive')
        distress_flag=bool(cfo is not None and cff is not None and cfo<0 and cff>0)
        if distress_flag: distress.append({'company_id':cid,'sector':sector,'year':latest_year,'cfo_value':cfo,'cff_value':cff,'latest_net_profit':pat})
        bb=b.sort_values('year'); debt=bb['borrowings'].dropna().tolist() if 'borrowings' in bb else []
        deleveraging=bool(cff is not None and cff<0 and len(debt)>=2 and debt[-1]<debt[-2])
        fcfseries=[num(x) for x in merged['fcf'].tolist() if num(x) is not None]
        fcf_cagr=None
        if len(fcfseries)>=6 and fcfseries[-6]>0 and fcfseries[-1]>0: fcf_cagr=((fcfseries[-1]/fcfseries[-6])**(1/5)-1)*100
        fcf_conversion=None
        if len(valid):
            cfos=pd.to_numeric(valid['operating_activity'],errors='coerce').sum(); pats=pd.to_numeric(valid['net_profit'],errors='coerce').sum()
            if abs(pats)>1e-9: fcf_conversion=cfos/pats*100
        latest_ratio=r.iloc[-1] if len(r) else {}
        pattern=latest_ratio.get('capital_allocation_pattern') if len(r) else None
        if not isinstance(pattern,str) or not pattern.strip():
            pattern='Distress Signal' if distress_flag else ('Deleveraging' if deleveraging else ('Reinvestor' if caplabel=='Capital Intensive' and cfo is not None and cfo>0 else ('Cash Generator' if cfo is not None and cfo>0 else 'Cash Consumer')))
        outrows.append({'company_id':cid,'sector':sector,'cfo_quality_score':round(score,4) if score is not None else None,'cfo_quality_label':qlabel,'capex_intensity_pct':round(capex,4) if capex is not None else None,'capex_label':caplabel,'fcf_cagr_5yr':round(fcf_cagr,4) if fcf_cagr is not None else None,'fcf_conversion_pct':round(fcf_conversion,4) if fcf_conversion is not None else None,'distress_flag':distress_flag,'deleveraging_flag':deleveraging,'capital_allocation_label':pattern})
        ratio_by_year={str(row['year']):row for _,row in r.iterrows()}
        prior_debt_by_year={str(row['year']):num(row.get('borrowings')) for _,row in bb.iterrows()}
        years_sorted=sorted(prior_debt_by_year)
        prev_debt={years_sorted[i]:prior_debt_by_year.get(years_sorted[i-1]) for i in range(1,len(years_sorted))}
        for _,x in merged.iterrows():
            yr=str(x.get('year','')); ry=ratio_by_year.get(yr,{})
            py=prev_debt.get(yr); curdebt=prior_debt_by_year.get(yr)
            cfo_y=num(x.get('operating_activity')); cfi_y=num(x.get('investing_activity')); cff_y=num(x.get('financing_activity'))
            label_y=ry.get('capital_allocation_pattern') if hasattr(ry,'get') else None
            if not isinstance(label_y,str) or not label_y.strip():
                if cfo_y is not None and cff_y is not None and cfo_y<0 and cff_y>0: label_y='Distress Signal'
                elif cff_y is not None and cff_y<0 and py is not None and curdebt is not None and curdebt<py: label_y='Deleveraging'
                elif cfo_y is not None and cfo_y>0 and cfi_y is not None and abs(cfi_y)>0.08*(num(x.get('sales')) or 0): label_y='Reinvestor'
                elif cfo_y is not None and cfo_y>0: label_y='Cash Generator'
                else: label_y='Cash Consumer'
            yearrows.append({'company_id':cid,'year':yr,'capital_allocation_label':label_y,'operating_activity':x.get('operating_activity'),'investing_activity':x.get('investing_activity'),'financing_activity':x.get('financing_activity')})
    df=pd.DataFrame(outrows); df.to_excel(out/'cashflow_intelligence.xlsx',index=False)
    pd.DataFrame(distress,columns=['company_id','sector','year','cfo_value','cff_value','latest_net_profit']).to_csv(out/'distress_alerts.csv',index=False)
    # Capital-allocation coverage, latest-year distribution and year-over-year transitions.
    cap_path=out/'capital_allocation.csv'
    cap=pd.DataFrame(yearrows)
    cap.to_csv(cap_path,index=False)
    latest=cap.sort_values('year').groupby('company_id').tail(1)
    latest.groupby('capital_allocation_label').size().rename('company_count').reset_index().to_csv(out/'capital_allocation_distribution.csv',index=False)
    changes=[]
    for cid,g in cap.sort_values('year').groupby('company_id'):
        g=g.dropna(subset=['capital_allocation_label']).drop_duplicates('year')
        prev=None; prevyear=None
        for _,x in g.iterrows():
            cur=x['capital_allocation_label']; yr=x['year']
            if prev is not None and cur!=prev: changes.append({'company_id':cid,'from_year':prevyear,'to_year':yr,'previous_pattern':prev,'new_pattern':cur})
            prev,prevyear=cur,yr
    pd.DataFrame(changes,columns=['company_id','from_year','to_year','previous_pattern','new_pattern']).to_csv(out/'pattern_changes.csv',index=False)
    return {'companies':len(df),'distress_alerts':len(distress),'allocation_patterns':len(latest),'pattern_changes':len(changes),'output':str(out/'cashflow_intelligence.xlsx')}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--db'); ap.add_argument('--output-dir'); a=ap.parse_args(); print(calc(a.db,a.output_dir))
