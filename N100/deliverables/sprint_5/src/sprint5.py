"""Run Sprint 5 pipelines from project root: python -m src.sprint5"""
from src.nlp.parser import parse_analysis
from src.nlp.pros_cons_generator import generate as generate_pros_cons
from src.analytics.cashflow_kpis import calc as generate_cashflow
from src.reports.batch_generate import run as generate_reports

def main():
    print('1/4 Parsing analysis workbook:',parse_analysis())
    print('2/4 Generating pros and cons:',generate_pros_cons())
    print('3/4 Calculating cash-flow intelligence:',generate_cashflow())
    print('4/4 Generating PDF reports:',generate_reports())
    print('Sprint 5 pipelines completed. Review output/ and reports/ before submission.')
if __name__=='__main__': main()
