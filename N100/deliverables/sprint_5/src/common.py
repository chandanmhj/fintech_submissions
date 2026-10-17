from pathlib import Path
import os, sqlite3
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get('N100_DB_PATH', PROJECT_ROOT / 'data' / 'nifty100.db'))
OUTPUT_DIR = PROJECT_ROOT / 'output'
REPORTS_DIR = PROJECT_ROOT / 'reports'

def connect(db_path=None):
    path = Path(db_path or DB_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}. Set N100_DB_PATH or place data/nifty100.db in project root.")
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    return con

def table_exists(con, table):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is not None

def columns(con, table):
    if not table_exists(con, table): return []
    return [r['name'] for r in con.execute(f'PRAGMA table_info("{table}")')]

def pick(cols, *candidates):
    lower={c.lower():c for c in cols}
    for x in candidates:
        if x.lower() in lower: return lower[x.lower()]
    return None

def clean(v):
    if v is None: return ''
    return str(v).strip()
