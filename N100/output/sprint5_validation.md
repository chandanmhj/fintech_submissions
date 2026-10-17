# Sprint 5 Validation Report

Generated from the Sprint 4 reference database included with the package. Run the pipeline against your local N100 database before final submission.

## Automated checks
- Companies in reference database: **92**
- Pros/cons output rows: **401**; every company has at least one pro and one con: **True**; coverage failures: **0**
- Analysis parser rows: **63**; parse-failure rows: **17**
- CAGR cross-validation comparisons: **24**; manual-review flags (>5 percentage points): **2**
- Cash-flow intelligence rows: **92**; distress alerts: **0**
- Capital-allocation output rows: **1164**; latest-year distribution covers **92** companies; year-over-year pattern changes recorded: **547**
- Company tearsheets: **92**; minimum PDF size: **84.9 KB**; PDFs below 30 KB: **0**; page-count errors: **0**
- Sector PDFs: **11** (10 observed broad sectors plus one All Sectors benchmark)
- Portfolio summary pages: **92**

## Manual review still required
- Open at least five tearsheets (TCS, HDFCBANK, RELIANCE, SUNPHARMA, TATASTEEL) and verify no clipping, blank pages, or unreadable charts. The TCS sample was visually inspected and showed no overflow; inspect the remaining four locally.
- Inspect every row in `output/parse_failures.csv`; the source workbook contains TTM / 1 Year / Last Year formats that do not match the exact required `N Years: value%` regex.
- Review `output/cagr_cross_validation.csv` entries flagged for manual review.
- The supplied snapshot has 10 broad sectors, so `all_sectors_report.pdf` is the 11th requested report.
- `distress_alerts.csv` is empty because no latest-year CFO < 0 and CFF > 0 cases were present in the reference snapshot.

## Status
Core outputs were generated and structural checks passed. This does **not** constitute team-lead sign-off or substitute for the remaining visual PDF review.
