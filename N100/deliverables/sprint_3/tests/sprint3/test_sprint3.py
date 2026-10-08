import sqlite3
from pathlib import Path
import pandas as pd
from src.screener.engine import load_config, _pct_score, apply_filter_config, _load_screen_data, _normalise_composite, run_presets
from src.analytics.peer import percent_rank, compute_peer_percentiles

ROOT=Path(__file__).resolve().parents[2]
DB=ROOT/"data"/"nifty100.db"

def test_01_config_has_six_presets(): assert len(load_config()["presets"])==6
def test_02_config_has_fifteen_metrics(): assert len(load_config()["custom_filter_metrics"])==15
def test_03_p10_p90_score_bounds():
    s=_pct_score(pd.Series([1,2,3,4,100])); assert s.min()>=0 and s.max()<=100
def test_04_inverse_score():
    s=_pct_score(pd.Series([1,2,3]),False); assert s.iloc[0]>s.iloc[-1]
def test_05_financials_de_skip():
    df=pd.DataFrame({'debt_to_equity':[1,1],'broad_sector':['Financials','IT'],'composite_quality_score':[1,2]})
    out=apply_filter_config(df,{'de_max':.5}); assert len(out)==1 and out.iloc[0].broad_sector=='Financials'
def test_06_icr_debt_free_passes():
    df=pd.DataFrame({'interest_coverage':[float('nan'),1.0],'broad_sector':['IT','IT'],'composite_quality_score':[1,2]})
    out=apply_filter_config(df,{'icr_min':2}); assert len(out)==1 and pd.isna(out.iloc[0].interest_coverage)
def test_07_custom_roe_filter():
    df=pd.DataFrame({'return_on_equity_pct':[10,20],'composite_quality_score':[1,2]}); assert len(apply_filter_config(df,{'roe_min':15}))==1
def test_08_custom_sales_filter():
    df=pd.DataFrame({'sales':[100,6000],'composite_quality_score':[1,2]}); assert len(apply_filter_config(df,{'sales_min':5000}))==1
def test_09_composite_column_present():
    con=sqlite3.connect(DB); df=_normalise_composite(_load_screen_data(con)); con.close(); assert 'composite_quality_score' in df and df.composite_quality_score.between(0,100).all()
def test_10_six_presets_run():
    con=sqlite3.connect(DB); df=_normalise_composite(_load_screen_data(con)); con.close(); res=run_presets(df,load_config()); assert len(res)==6

def test_11_peer_rank_highest_is_one():
    s=pd.Series([10,20,30]); p=percent_rank(s); assert p.iloc[-1]==1

def test_12_peer_rank_de_inverse():
    s=pd.Series([1,2,3]); p=percent_rank(s,False); assert p.iloc[0]==1

def test_13_peer_table_has_eleven_groups():
    con=sqlite3.connect(DB); n=con.execute('select count(distinct peer_group_name) from peer_groups').fetchone()[0]; con.close(); assert n==11

def test_14_peer_percentiles_populate():
    n=compute_peer_percentiles(DB); assert n==56*10
