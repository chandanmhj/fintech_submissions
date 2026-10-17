"""Parse narrative growth fields from analysis.xlsx without fabricating periods."""
from pathlib import Path
import re, argparse, os
import pandas as pd
from src.common import connect, DB_PATH, OUTPUT_DIR, PROJECT_ROOT
PATTERN = re.compile(r'(\d+)\s*Years?:?\s*([\d.]+)%', re.I)
METRICS = ['compounded_sales_growth','compounded_profit_growth','stock_price_cagr','roe']

def locate_workbook(path=None):
    candidates = [Path(path)] if path else [
        PROJECT_ROOT/'data'/'source_inputs'/'analysis.xlsx',
        PROJECT_ROOT/'data'/'analysis.xlsx',
        PROJECT_ROOT/'analysis.xlsx',
    ]
    return next((p for p in candidates if p.exists()), None)

def parse_analysis(workbook=None, db_path=None, output_dir=None):
    out=Path(output_dir or OUTPUT_DIR); out.mkdir(parents=True,exist_ok=True)
    wb=locate_workbook(workbook)
    rows=[]; failures=[]
    if wb:
        raw=pd.read_excel(wb, header=None)
        # The provided export has a title row, then the real headers on row 2.
        header_idx=0
        for i in range(min(8,len(raw))):
            vals=[str(x).strip().lower() for x in raw.iloc[i].tolist()]
            if 'company_id' in vals: header_idx=i; break
        raw.columns=[str(x).strip() for x in raw.iloc[header_idx].tolist()]
        df=raw.iloc[header_idx+1:].copy()
        # Normalise the accidental unnamed / duplicate heading structure.
        rename={}
        for c in df.columns:
            cc=str(c).strip().lower()
            if cc=='company_id': rename[c]='company_id'
            elif cc in METRICS: rename[c]=cc
        df=df.rename(columns=rename)
        if 'company_id' not in df.columns:
            failures.append({'company_id':'','metric_type':'','raw_text':'','reason':'Could not find company_id header in analysis workbook'})
        else:
            for _,r in df.iterrows():
                cid=str(r.get('company_id','')).strip()
                if not cid or cid.lower()=='nan': continue
                for metric in METRICS:
                    if metric not in df.columns: continue
                    value=r.get(metric)
                    if pd.isna(value) or str(value).strip()=='':
                        failures.append({'company_id':cid,'metric_type':metric,'raw_text':'','reason':'blank source value'}); continue
                    m=PATTERN.search(str(value))
                    if m:
                        rows.append({'company_id':cid,'metric_type':metric,'period_years':int(m.group(1)),'value_pct':float(m.group(2))})
                    else:
                        failures.append({'company_id':cid,'metric_type':metric,'raw_text':str(value),'reason':'does not match period-and-percent regex'})
    else:
        # No workbook found: report the limitation and do not infer period years from numeric DB fields.
        failures.append({'company_id':'','metric_type':'','raw_text':'','reason':'analysis.xlsx not found; expected data/source_inputs/analysis.xlsx'})
    parsed=pd.DataFrame(rows,columns=['company_id','metric_type','period_years','value_pct'])
    parsed.to_csv(out/'analysis_parsed.csv',index=False)
    pd.DataFrame(failures,columns=['company_id','metric_type','raw_text','reason']).to_csv(out/'parse_failures.csv',index=False)
    # Cross-validate parsed sales/profit CAGR values against Ratio Engine values when periods match.
    cross=[]
    db_candidate=Path(db_path or os.environ.get('N100_DB_PATH', DB_PATH))
    con=connect(db_path) if rows and db_candidate.exists() else None
    if con:
        try:
            ratio_cols={r['name'] for r in con.execute('pragma table_info(financial_ratios)')}
            metric_map={'compounded_sales_growth':{3:'revenue_cagr_3yr',5:'revenue_cagr_5yr',10:'revenue_cagr_10yr'},'compounded_profit_growth':{3:'pat_cagr_3yr',5:'pat_cagr_5yr',10:'pat_cagr_10yr'}}
            for x in rows:
                col=metric_map.get(x['metric_type'],{}).get(x['period_years'])
                if not col or col not in ratio_cols: continue
                got=con.execute(f'SELECT "{col}" FROM financial_ratios WHERE company_id=? ORDER BY year DESC LIMIT 1',(x['company_id'],)).fetchone()
                if got and got[0] is not None:
                    diff=abs(float(got[0])-x['value_pct'])
                    cross.append({'company_id':x['company_id'],'metric_type':x['metric_type'],'period_years':x['period_years'],'parsed_value_pct':x['value_pct'],'ratio_engine_value_pct':got[0],'absolute_divergence_pct_points':round(diff,4),'manual_review_flag':diff>5})
        finally: con.close()
    pd.DataFrame(cross,columns=['company_id','metric_type','period_years','parsed_value_pct','ratio_engine_value_pct','absolute_divergence_pct_points','manual_review_flag']).to_csv(out/'cagr_cross_validation.csv',index=False)
    return {'parsed_rows':len(rows),'parse_failures':len(failures),'cross_checks':len(cross),'manual_reviews':sum(bool(x['manual_review_flag']) for x in cross),'workbook':str(wb) if wb else None}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--workbook'); ap.add_argument('--db'); ap.add_argument('--output-dir'); a=ap.parse_args()
    print(parse_analysis(a.workbook,a.db,a.output_dir))
