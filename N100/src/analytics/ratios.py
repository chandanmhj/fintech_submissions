import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run():
 con=sqlite3.connect(ROOT/'data/nifty100.db'); con.execute('PRAGMA foreign_keys=ON');
 con.execute('''CREATE TABLE IF NOT EXISTS financial_ratios_computed AS SELECT p.id,p.company_id,p.year, CASE WHEN p.sales!=0 THEN p.net_profit*100.0/p.sales END net_profit_margin_pct, CASE WHEN p.sales!=0 THEN p.operating_profit*100.0/p.sales END operating_profit_margin_pct, CASE WHEN (b.equity_capital+b.reserves)!=0 THEN p.net_profit*100.0/(b.equity_capital+b.reserves) END return_on_equity_pct, CASE WHEN (b.equity_capital+b.reserves)!=0 THEN b.borrowings*1.0/(b.equity_capital+b.reserves) END debt_to_equity FROM profitandloss p LEFT JOIN balancesheet b ON p.company_id=b.company_id AND p.year=b.year''')
 con.commit(); con.close()
if __name__=='__main__': run()
