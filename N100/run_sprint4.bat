@echo off
python -m src.analytics.valuation
streamlit run src/dashboard/app.py
