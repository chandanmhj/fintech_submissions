"""Generate all company tearsheets, sector reports and portfolio summary."""
import argparse
from pathlib import Path
import pandas as pd
from src.common import connect, REPORTS_DIR, OUTPUT_DIR
from src.reports.tearsheet import generate_one
from src.reports.sector_report import generate_sector_reports
from src.reports.portfolio_summary import generate_portfolio_summary

def run(db_path=None, reports_dir=None, output_dir=None):
    reports=Path(reports_dir or REPORTS_DIR); out=Path(output_dir or OUTPUT_DIR); (reports/'tearsheets').mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
    con=connect(db_path); companies=pd.read_sql_query('select id from companies order by id',con); counts=pd.read_sql_query('select company_id,count(*) n from profitandloss group by company_id',con); con.close(); counts=dict(zip(counts.company_id,counts.n))
    skipped=[]; made=[]
    for ticker in companies.id:
        if counts.get(ticker,0)<3: skipped.append({'ticker':ticker,'reason':'fewer than 3 P&L years'}); continue
        try: made.append(str(generate_one(ticker,db_path=db_path,output_path=reports/'tearsheets'/f'{ticker}_tearsheet.pdf')))
        except Exception as e: skipped.append({'ticker':ticker,'reason':str(e)})
    pd.DataFrame(skipped,columns=['ticker','reason']).to_csv(out/'skipped_tearsheets.csv',index=False)
    sector=generate_sector_reports(db_path=db_path,output_dir=reports/'sector')
    portfolio=generate_portfolio_summary(db_path=db_path,output_path=reports/'portfolio'/'portfolio_summary.pdf')
    return {'tearsheets_generated':len(made),'skipped':len(skipped),'sector_pdfs':sector['reports'],'portfolio_pages':portfolio['pages'],'tearsheet_dir':str(reports/'tearsheets')}
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--db'); ap.add_argument('--reports-dir'); ap.add_argument('--output-dir'); a=ap.parse_args(); print(run(a.db,a.reports_dir,a.output_dir))
