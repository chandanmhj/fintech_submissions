@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  call .venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -r requirements-sprint5.txt
) else (
  call .venv\Scripts\activate.bat
)
python -m src.nlp.parser
python -m src.nlp.pros_cons_generator
python -m src.analytics.cashflow_kpis
python -m src.reports.batch_generate
echo Sprint 5 run finished. Check output and reports folders.
pause
