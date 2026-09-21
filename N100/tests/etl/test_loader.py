import sqlite3
from pathlib import Path

def test_database_exists(): assert Path('data/nifty100.db').exists()
def test_company_count():
 con=sqlite3.connect('data/nifty100.db'); assert con.execute('select count(*) from companies').fetchone()[0]==92; con.close()
def test_foreign_keys():
 con=sqlite3.connect('data/nifty100.db'); assert con.execute('pragma foreign_key_check').fetchall()==[]; con.close()
def test_expected_tables():
 con=sqlite3.connect('data/nifty100.db'); names={r[0] for r in con.execute("select name from sqlite_master where type='table'")}; con.close(); assert {'companies','profitandloss','balancesheet','cashflow','analysis','documents','prosandcons','sectors','stock_prices','market_cap','financial_ratios','peer_groups'} <= names
def test_load_audit_exists(): assert Path('output/load_audit.csv').exists()
