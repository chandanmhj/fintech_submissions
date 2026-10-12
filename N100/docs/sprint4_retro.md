# Sprint 4 Retrospective

Implemented the Streamlit entry point and eight screen files, cached SQLite accessors, screener filters and CSV export, plus valuation summary generation. Data snapshots can differ by year; dashboard pages therefore show available history and valuation uses the latest available market-cap row per company. Browser smoke testing, timing measurements and team-lead sign-off must be completed locally.

Run: `streamlit run src/dashboard/app.py`
Valuation: `python -m src.analytics.valuation`
