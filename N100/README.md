# Nifty 100 Financial Intelligence Platform

## Sprint 1 — Data Foundation

Sprint 1 establishes the data foundation: normalized Excel ingestion, 16 DQ checks, SQLite persistence, audit outputs and exploratory SQL.

### Quick start

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt

# Windows
copy config\.env.template .env

python -m src.etl.loader

pytest tests/ -q
```

### Sprint 1 Key Outputs

* `data/nifty100.db`
* `output/load_audit.csv`
* `output/validation_failures.csv`
* `src/etl/loader.py`
* `src/etl/validator.py`
* `src/etl/normaliser.py`
* `db/schema.sql`
* `tests/etl/`
* `notebooks/exploratory_queries.sql`

### Data Note

The specification says “10 tables”, while the supplied dataset contains 12 source files and 11 source-backed relational tables when `market_cap` is preserved. This implementation preserves all supplied data and therefore creates 11 source-backed tables plus the computed-ratio helper table when the ratio module is run.

---

# Sprint 2 — Financial Ratio Engine

Sprint 2 extends the Sprint 1 data foundation with a financial ratio and KPI engine. The engine computes profitability, leverage, efficiency, growth, cash-flow and capital-allocation metrics for the Nifty 100 companies across available financial years.

### Sprint 2 Goal

The Sprint 2 objective is to populate the `financial_ratios` SQLite table with 50+ computed and derived KPI fields across all available company-year records, while correctly handling formula edge cases such as:

* Negative equity
* Debt-free companies
* Zero denominators
* CAGR turnarounds
* Declines into losses
* Both-negative CAGR cases
* Insufficient historical coverage
* Financial-sector leverage carve-out
* Source-vs-computed ratio discrepancies

### Sprint 2 Implementation

#### Financial Ratios

`src/analytics/ratios.py`

Implements:

* Net Profit Margin
* Operating Profit Margin
* Return on Equity (ROE)
* Return on Capital Employed (ROCE)
* Return on Assets (ROA)
* Debt-to-Equity
* Interest Coverage Ratio
* Net Debt
* Asset Turnover
* High leverage flag
* Interest coverage warning
* Financial-sector ROCE benchmarking
* Composite quality score

#### CAGR Engine

`src/analytics/cagr.py`

Computes:

* Revenue CAGR
* PAT CAGR
* EPS CAGR

for:

* 3-year periods
* 5-year periods
* 10-year periods

The engine handles the following CAGR conditions:

* Normal positive-to-positive growth
* `DECLINE_TO_LOSS`
* `TURNAROUND`
* `BOTH_NEGATIVE`
* `ZERO_BASE`
* `INSUFFICIENT`

#### Cash Flow KPIs

`src/analytics/cashflow_kpis.py`

Implements:

* Free Cash Flow
* CFO Quality Score
* CapEx Intensity
* FCF Conversion Rate
* Capital Allocation Pattern Classification

Capital allocation patterns include:

* Reinvestor
* Shareholder Returns
* Liquidating Assets
* Distress Signal
* Growth Funded by Debt
* Cash Accumulator
* Pre-Revenue
* Mixed

### Sprint 2 Quick Start

From the `N100` project root:

```bash
python -m src.analytics.ratios
```

This runs the complete ratio engine and updates:

```text
data/nifty100.db
```

and generates:

```text
output/capital_allocation.csv
output/ratio_edge_cases.log
output/manual_spot_check.csv
```

### Sprint 2 Testing

Run the dedicated KPI tests:

```bash
pytest -q tests/kpi
```

Run the complete project test suite:

```bash
pytest -q
```

The Sprint 2 implementation includes 20 dedicated KPI formula tests.

### Sprint 2 Key Outputs

* `data/nifty100.db`
* `output/capital_allocation.csv`
* `output/ratio_edge_cases.log`
* `output/manual_spot_check.csv`
* `src/analytics/ratios.py`
* `src/analytics/cagr.py`
* `src/analytics/cashflow_kpis.py`
* `tests/kpi/test_ratios.py`
* `db/schema.sql`
* `docs/sprint2_retro.md`

### Sprint 2 Validation

The completed Sprint 2 implementation was validated against the following acceptance criteria:

* Companies in database: **92**
* `financial_ratios` rows: **1,164**
* Required minimum: **1,100+**
* Computed/derived KPI fields: **50+**
* Dedicated KPI tests: **20/20 passed**
* Full project tests: **60 passed**
* Manual ROE spot checks: **3/3 passed**
* Manual 5-year Revenue CAGR spot checks: **3/3 passed**
* Manual calculation tolerance: **less than 0.1%**
* Capital allocation records: **1,164**
* Screener preview result: **37 companies**
* Required screener range: **15–50 companies**

### Manual Spot Check

Three companies are used for manual validation of ROE and 5-year Revenue CAGR:

* ABB
* ADANIENSOL
* ADANIENT

The manual calculations are compared against the corresponding values stored in `financial_ratios`.

The detailed results are available in:

```text
output/manual_spot_check.csv
```

### Ratio Edge Cases

Source-vs-computed ratio anomalies are recorded in:

```text
output/ratio_edge_cases.log
```

The log documents anomalies and their classification, including:

* Data source issue
* Version difference
* Formula discrepancy

The computed ratio-engine values are used for analytics where source values are anomalous.

### Financial Sector Carve-Out

The high Debt-to-Equity warning is suppressed for companies classified in the `Financials` broad sector because elevated leverage is structurally normal for banks, NBFCs and insurance companies.

The implementation uses the sector classification contained in the supplied dataset rather than hard-coding a fixed number of companies.

---

# Project Structure

```text
N100/
│
├── config/
│   └── .env.template
│
├── data/
│   ├── nifty100.db
│   ├── raw/
│   └── supporting/
│
├── db/
│   └── schema.sql
│
├── docs/
│   ├── Nifty100_Project_Document_FINAL.pdf
│   ├── sprint1_retro.md
│   └── sprint2_retro.md
│
├── notebooks/
│   └── exploratory_queries.sql
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   ├── capital_allocation.csv
│   ├── ratio_edge_cases.log
│   └── manual_spot_check.csv
│
├── src/
│   ├── analytics/
│   │   ├── ratios.py
│   │   ├── cagr.py
│   │   └── cashflow_kpis.py
│   │
│   ├── api/
│   │   └── main.py
│   │
│   ├── dashboard/
│   │   └── app.py
│   │
│   └── etl/
│       ├── loader.py
│       ├── normaliser.py
│       └── validator.py
│
├── tests/
│   ├── etl/
│   │   ├── test_loader.py
│   │   └── test_normalise.py
│   │
│   └── kpi/
│       └── test_ratios.py
│
├── deliverables/
│   ├── task1/
│   └── task2/
│
├── Makefile
├── README.md
└── requirements.txt
```

---

# Sprint 1 + Sprint 2 Status

### Sprint 1 — Data Foundation

**Status: COMPLETED**

The normalized data ingestion pipeline, validation framework, SQLite persistence, audit outputs and exploratory queries are implemented.

### Sprint 2 — Financial Ratio Engine

**Status: COMPLETED**

The financial ratio engine, CAGR engine, cash-flow KPI calculations, capital-allocation classification, edge-case handling, KPI tests and manual validation are implemented.
