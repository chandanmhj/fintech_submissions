import re
import pandas as pd

def normalize_year(value):
    if pd.isna(value): return None
    s=str(value).strip()
    if s.upper() == 'TTM': return '2025-03'
    if re.fullmatch(r'\d{4}', s): return s+'-03'
    m=re.search(r'(\d{4})[-/]?(\d{1,2})', s)
    if m: return f'{int(m.group(1)):04d}-{int(m.group(2)):02d}'
    m=re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]*(\d{2,4})', s, re.I)
    if m:
        months={'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
        y=int(m.group(2)); y=2000+y if y<100 else y; return f"{y:04d}-{months[m.group(1)[:3].lower()]:02d}"
    m=re.search(r'(\d{4})', s)
    return f'{m.group(1)}-03' if m else None

def normalize_ticker(value):
    if pd.isna(value): return None
    return str(value).strip().upper()

def normalize_dataframe(df, year_columns=('year',), ticker_columns=('company_id',)):
    df=df.copy()
    for c in year_columns:
        if c in df: df[c]=df[c].map(normalize_year)
    for c in ticker_columns:
        if c in df: df[c]=df[c].map(normalize_ticker)
    return df
