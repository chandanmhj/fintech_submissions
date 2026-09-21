PYTHON=python
load:
	$(PYTHON) -m src.etl.loader
ratios:
	$(PYTHON) -m src.analytics.ratios
test:
	pytest tests/ -q
report:
	@echo "Sprint 1 report generation placeholder"
dashboard:
	streamlit run src/dashboard/app.py
api:
	uvicorn src.api.main:app --port 8000
clean:
	rm -f data/nifty100.db output/*.csv
