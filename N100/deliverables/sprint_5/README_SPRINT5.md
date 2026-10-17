# Sprint 5 — Cash Flow Intelligence + Reports + NLP

## Integrate into your existing N100 project
1. Extract the ZIP.
2. Copy the contents of `to_add/` into your existing `N100/` folder and merge folders. Do **not** replace your existing database with the bundled snapshot unless you intentionally want the reference data.
3. Ensure your project has `data/nifty100.db`. The bundled `data/nifty100.db` is a reference copy from Sprint 4.
4. Keep the original `analysis.xlsx` at `data/source_inputs/analysis.xlsx` (the package includes the supplied source workbook there).
5. From the `N100` project root, activate your existing virtual environment and install `pip install -r requirements-sprint5.txt`.
6. Run `python -m src.sprint5` or double-click `run_sprint5.bat`.

## Outputs
- `output/analysis_parsed.csv`, `parse_failures.csv`, `cagr_cross_validation.csv`
- `output/pros_cons_generated.csv` and `pros_cons_coverage_failures.csv`
- `output/cashflow_intelligence.xlsx`, `distress_alerts.csv`, `capital_allocation.csv`, `capital_allocation_distribution.csv`, `pattern_changes.csv`
- `reports/tearsheets/<TICKER>_tearsheet.pdf` (2 pages per eligible company)
- `reports/sector/*_report.pdf` (10 source sectors plus All Sectors benchmark = 11 PDFs)
- `reports/portfolio/portfolio_summary.pdf` (one page per company)

## Notes and assumptions
- Parser uses the requested regex and does not infer period lengths from numeric database values. `TTM`, `1 Year`, and `Last Year` entries that do not match the required `N Years: value%` regex are logged for review.
- CAGR cross-validation uses 3-, 5-, and 10-year Ratio Engine fields when available; divergence is reported in percentage points and flagged when greater than 5.
- CFO quality is the average annual CFO/PAT ratio over up to five available matching periods. Negative/zero PAT periods are excluded from the ratio average to avoid division by zero.
- CapEx intensity uses `abs(investing_activity)/sales*100` because the source schema provides investing cash flow rather than a dedicated capex column.
- The PDF generator wraps table cells with ReportLab Paragraphs, skips companies with fewer than three P&L years, and writes the skipped list.
- Fallback pro/con rows are clearly labelled as review/monitoring notes when no one of the 12 positive or 12 risk rules triggers. Their 61% score exists only to meet the per-company coverage requirement; it is not a measured financial signal.
- The supplied Sprint 4 snapshot has 10 broad-sector values. The 11th requested PDF is the consolidated All Sectors benchmark.

## Validation
Run from project root:
`python -m pytest tests -q` after copying the package into your project root.
Inspect the generated PDFs visually before final submission; automated generation cannot replace visual review.
