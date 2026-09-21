from fastapi import FastAPI
import sqlite3
from pathlib import Path
app=FastAPI(title='Nifty100 Financial Intelligence API',version='1.0')
DB=Path(__file__).resolve().parents[2]/'data/nifty100.db'
@app.get('/health')
def health(): return {'status':'ok','database':DB.exists()}
@app.get('/companies')
def companies():
 con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; rows=[dict(r) for r in con.execute('select id,company_name from companies order by company_name')]; con.close(); return rows
@app.get('/companies/{company_id}')
def company(company_id:str):
 con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; r=con.execute('select * from companies where id=?',(company_id.upper(),)).fetchone(); con.close(); return dict(r) if r else {'error':'not found'}
