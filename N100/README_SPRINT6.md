# Sprint 6 — integration guide
1. Merge `to_add` into the existing N100 root; do not overwrite your database.
2. Activate your virtual environment and run `pip install -r requirements-sprint6.txt`.
3. Set `N100_DB` to the absolute path of your existing `nifty100.db` if it is not `data/nifty100.db`.
4. Run clustering: `python -m src.analytics.clustering`.
5. Start API: `python -m uvicorn src.api.main:app --reload --port 8000`.
6. Open `http://127.0.0.1:8000/docs`; export schema from `http://127.0.0.1:8000/openapi.json`.
7. Run `python -m pytest tests -v`.

The API includes health, company list/profile/P&L/BS/cashflow/ratios/tearsheet/peer compare/documents, screener, sector list/companies, peers, market-cap history, portfolio stats and document index. The API uses SQLite schema names found in the Sprint 4/5 reference DB. Review `/api/v1/sectors` before assuming the database contains exactly 11 sectors. Cluster names are heuristic and require team-lead review. CORS wildcard is for internal development only.
