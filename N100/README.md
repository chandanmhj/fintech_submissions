# Nifty 100 Financial Intelligence Platform — Sprint 1

Sprint 1 establishes the data foundation: normalized Excel ingestion, 16 DQ checks, SQLite persistence, audit outputs and exploratory SQL.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy config\.env.template .env  # Windows
python -m src.etl.loader
pytest tests/ -q
```

## Key outputs
- `data/nifty100.db`
- `output/load_audit.csv`
- `output/validation_failures.csv`
- `src/etl/loader.py`
- `src/etl/validator.py`
- `src/etl/normaliser.py`
- `db/schema.sql`
- `tests/etl/`
- `notebooks/exploratory_queries.sql`

## Data note
The specification says “10 tables”, while the supplied dataset contains 12 source files and 11 source-backed relational tables when `market_cap` is preserved. This implementation preserves all supplied data and therefore creates 11 source-backed tables plus the computed-ratio helper table only when the ratio module is run.
