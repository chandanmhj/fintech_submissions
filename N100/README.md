# Nifty 100 Financial Intelligence Platform

**An end-to-end financial data engineering, screening, valuation,
cash-flow intelligence, and reporting platform.**

The Nifty 100 Financial Intelligence Platform transforms financial
source files into a normalized SQLite database and builds analytical
layers for financial ratios, historical growth, cash-flow quality,
company screening, peer benchmarking, valuation, natural-language
financial summaries, and automated reporting.

> **Status note:** Sprint 1 and Sprint 2 are documented as completed in
> the existing project README. Sprint 3--5 content below records the
> full project specification and intended deliverables; mark those
> sprints complete only after confirming the code, outputs, and tests in
> the repository.

## Table of Contents

1.  [Project Overview](#1-project-overview)
2.  [Technology Stack](#2-technology-stack)
3.  [Architecture](#3-architecture)
4.  [Sprint Roadmap](#4-sprint-roadmap)
5.  [Sprint 1 --- Data Foundation](#5-sprint-1--data-foundation)
6.  [Sprint 2 --- Financial Ratio
    Engine](#6-sprint-2--financial-ratio-engine)
7.  [Sprint 3 --- Screener and Peer
    Engine](#7-sprint-3--screener-and-peer-engine)
8.  [Sprint 4 --- Streamlit Dashboard and
    Valuation](#8-sprint-4--streamlit-dashboard-and-valuation)
9.  [Sprint 5 --- Cash Flow Intelligence, Reports, and
    NLP](#9-sprint-5--cash-flow-intelligence-reports-and-nlp)
10. [Installation and Quick Start](#10-installation-and-quick-start)
11. [Testing and Validation](#11-testing-and-validation)
12. [Consolidated Project Structure](#12-consolidated-project-structure)
13. [Deliverable Tracker](#13-deliverable-tracker)
14. [Data Quality and Financial Calculation
    Principles](#14-data-quality-and-financial-calculation-principles)
15. [Limitations and Disclaimer](#15-limitations-and-disclaimer)

------------------------------------------------------------------------

## 1. Project Overview

The platform is organized into five development sprints, moving from
source-data ingestion to a complete financial analytics and reporting
workflow.

### Objectives

-   Ingest and normalize multiple financial Excel source files.
-   Apply data-quality checks and persist validated data in SQLite.
-   Maintain ingestion audit and validation-failure outputs.
-   Calculate 50+ financial and derived key performance indicators
    (KPIs).
-   Compute Revenue, Profit After Tax (PAT), and Earnings Per Share
    (EPS) growth over multiple periods.
-   Handle financial formula edge cases explicitly.
-   Classify cash-flow and capital-allocation patterns.
-   Screen companies using configurable financial criteria.
-   Compare companies against peer groups using percentile rankings.
-   Provide an interactive dashboard and valuation functionality.
-   Generate rule-based financial pros and cons.
-   Produce company, sector, and portfolio-level reports.

### Sprint Summary

  -------------------------------------------------------------------------------
  Sprint           Planned Days Focus               Story Points Status in this
                                                                 README
  ------------ ---------------- --------------- ---------------- ----------------
  Sprint 1               01--07 Data Foundation               34 Completed
                                and ETL                          

  Sprint 2               08--14 Financial Ratio               42 Completed
                                Engine                           

  Sprint 3               15--21 Screener and                  49 Verify
                                Peer Engine                      implementation

  Sprint 4               22--28 Streamlit                     55 Verify
                                Dashboard and                    implementation
                                Valuation                        

  Sprint 5               29--35 Cash Flow                     70 Verify
                                Intelligence,                    implementation
                                Reports, and                     
                                NLP                              

  **Total**         **35 days** **Financial              **250** 
                                Intelligence                     
                                Platform**                       
  -------------------------------------------------------------------------------

The sprint schedule and story points are project-plan figures, not
measures of independently verified completion.

## 2. Technology Stack

  Area                           Technology
  ------------------------------ -------------------------------------------
  Language                       Python
  Data manipulation              Pandas and NumPy
  Relational persistence         SQLite
  Ingestion and transformation   Custom Python ETL modules
  Testing                        pytest
  Dashboard                      Streamlit
  API layer                      Python API module under `src/api/`
  Financial analytics            Custom ratio, CAGR, and cash-flow modules
  Data exchange                  CSV and Excel workbooks
  Reporting                      PDF report-generation modules
  Version control                Git and GitHub

The exact dependency versions should be taken from `requirements.txt`.
The actual API framework and report-generation libraries should be
confirmed against the installed code.

## 3. Architecture

``` text
Financial Excel Source Files
             |
             v
+-----------------------------+
| ETL and Data Normalization   |
| Schema and DQ Validation     |
| Ingestion Audit              |
+-----------------------------+
             |
             v
+-----------------------------+
| SQLite: data/nifty100.db     |
| Source-backed relational    |
| tables                      |
+-----------------------------+
             |
             v
+-----------------------------+
| Financial Analytics          |
| Ratios, CAGR, Cash Flow      |
+-----------------------------+
             |
             v
+-----------------------------+
| Screener and Peer Engine     |
+-----------------------------+
             |
             v
+-----------------------------+
| Dashboard and Valuation      |
+-----------------------------+
             |
             v
+-----------------------------+
| NLP, Intelligence, Reports   |
| CSV, XLSX, PDF outputs       |
+-----------------------------+
```

SQLite is the central persistence layer. Downstream modules use
normalized financial data to calculate derived metrics and generate
analytical outputs.

------------------------------------------------------------------------

## 5. Sprint 1 --- Data Foundation

**Planned duration:** Days 01--07\
**Story points:** 34\
**Status:** **COMPLETED**

Sprint 1 establishes the data foundation through normalized Excel
ingestion, data-quality validation, SQLite persistence, audit outputs,
and exploratory SQL.

### 5.1 Scope and tasks

-   Configure the Python environment and project dependencies.
-   Load the supplied Excel source files.
-   Normalize source columns and data representations.
-   Validate source schemas and financial data quality.
-   Define the SQLite database schema.
-   Load normalized records into the database.
-   Produce ingestion audit and validation-failure outputs.
-   Write exploratory SQL queries.
-   Add tests for the ETL pipeline.

The specification calls for **16 data-quality checks**.

### 5.2 Main components

  -------------------------------------------------------------------------------------
  Component               Path                                  Responsibility
  ----------------------- ------------------------------------- -----------------------
  ETL loader              `src/etl/loader.py`                   Loads source data and
                                                                persists normalized
                                                                records

  Normalizer              `src/etl/normaliser.py`               Standardizes source
                                                                data before validation
                                                                and loading

  Validator               `src/etl/validator.py`                Applies data-quality
                                                                and schema checks

  Database schema         `db/schema.sql`                       Defines relational
                                                                tables

  Exploratory SQL         `notebooks/exploratory_queries.sql`   Provides SQL-based
                                                                exploration

  ETL tests               `tests/etl/`                          Tests ingestion and
                                                                normalization
  -------------------------------------------------------------------------------------

### 5.3 Key outputs

-   `data/nifty100.db`
-   `output/load_audit.csv`
-   `output/validation_failures.csv`
-   `src/etl/loader.py`
-   `src/etl/validator.py`
-   `src/etl/normaliser.py`
-   `db/schema.sql`
-   `tests/etl/`
-   `notebooks/exploratory_queries.sql`
-   `docs/sprint1_retro.md`

### 5.4 Data-table count note

The specification refers to 10 tables, while the supplied dataset
contains 12 source files. When `market_cap` is preserved, the
implementation has 11 source-backed relational tables. The
computed-ratio helper table is added when the ratio module is run. This
distinction preserves the supplied data rather than dropping a source
solely to match the original table-count statement.

### 5.5 Quick start

Run these commands from the project root.

``` bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

``` powershell
.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

``` bash
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

Create the environment file on Windows:

``` powershell
Copy-Item config/.env.template .env
```

Run the ETL pipeline:

``` bash
python -m src.etl.loader
```

Run ETL tests:

``` bash
pytest tests/etl/ -q
```

**Sprint 1 outcome:** A normalized, validated SQLite data foundation
with ingestion audit outputs and exploratory SQL.

------------------------------------------------------------------------

## 6. Sprint 2 --- Financial Ratio Engine

**Planned duration:** Days 08--14\
**Story points:** 42\
**Status:** **COMPLETED**

Sprint 2 extends the data foundation with financial ratios, CAGR
calculations, cash-flow KPIs, capital-allocation classifications, and
financial formula edge-case handling.

### 6.1 Sprint goal

Populate the `financial_ratios` SQLite table with **50+ computed and
derived KPI fields** across the available company-year records.

The implementation must handle:

-   Negative equity.
-   Debt-free companies.
-   Zero denominators.
-   CAGR turnarounds.
-   Declines into losses.
-   Both-negative CAGR cases.
-   Insufficient historical coverage.
-   Financial-sector leverage carve-outs.
-   Source-versus-computed ratio discrepancies.

### 6.2 Financial ratio engine

**Path:** `src/analytics/ratios.py`

Implemented metrics and indicators:

-   Net Profit Margin.
-   Operating Profit Margin.
-   Return on Equity (ROE).
-   Return on Capital Employed (ROCE).
-   Return on Assets (ROA).
-   Debt-to-Equity.
-   Interest Coverage Ratio.
-   Net Debt.
-   Asset Turnover.
-   High-leverage flag.
-   Interest-coverage warning.
-   Financial-sector ROCE benchmarking.
-   Composite quality score.

### 6.3 CAGR engine

**Path:** `src/analytics/cagr.py`

Computes:

-   Revenue CAGR.
-   PAT CAGR.
-   EPS CAGR.

Supported periods:

-   3 years.
-   5 years.
-   10 years.

Supported classifications and edge cases:

  Condition                            Meaning
  ------------------------------------ ----------------------------------------------
  Normal positive-to-positive growth   Conventional CAGR calculation
  `DECLINE_TO_LOSS`                    Performance declines into a loss
  `TURNAROUND`                         Performance changes from a loss to a profit
  `BOTH_NEGATIVE`                      Both starting and ending values are negative
  `ZERO_BASE`                          Starting value is zero
  `INSUFFICIENT`                       Historical coverage is insufficient

Conventional CAGR is not mathematically meaningful for all sign
combinations. The engine classifies those cases rather than forcing
invalid inputs into the standard formula.

### 6.4 Cash-flow KPI engine

**Path:** `src/analytics/cashflow_kpis.py`

Metrics and classifications:

-   Free Cash Flow (FCF).
-   CFO Quality Score.
-   Capital Expenditure Intensity.
-   FCF Conversion Rate.
-   Capital Allocation Pattern Classification.

Capital-allocation patterns:

-   Reinvestor.
-   Shareholder Returns.
-   Liquidating Assets.
-   Distress Signal.
-   Growth Funded by Debt.
-   Cash Accumulator.
-   Pre-Revenue.
-   Mixed.

These classifications are analytical signals and should be interpreted
with company and sector context.

### 6.5 Financial-sector leverage carve-out

High Debt-to-Equity warnings are suppressed for companies classified in
the `Financials` broad sector because elevated leverage is structurally
common in banks, NBFCs, and insurance companies. The implementation uses
sector classifications in the supplied dataset rather than hard-coding a
fixed list of company names.

### 6.6 Source-versus-computed ratio anomalies

Anomalies are recorded in `output/ratio_edge_cases.log`, including
classifications such as:

-   Data source issue.
-   Version difference.
-   Formula discrepancy.

Computed ratio-engine values are used for analytics where source values
are classified as anomalous.

### 6.7 Run the ratio engine

From the `N100` project root:

``` bash
python -m src.analytics.ratios
```

The engine updates:

-   `data/nifty100.db`

It also generates:

-   `output/capital_allocation.csv`
-   `output/ratio_edge_cases.log`
-   `output/manual_spot_check.csv`

### 6.8 Tests

Run the dedicated KPI tests:

``` bash
pytest -q tests/kpi
```

Run the full test suite:

``` bash
pytest -q
```

The Sprint 2 implementation includes 20 dedicated KPI formula tests.

### 6.9 Recorded Sprint 2 validation

  Acceptance criterion                        Recorded result
  ---------------------------------------- ------------------
  Companies in database                                    92
  `financial_ratios` rows                               1,164
  Required minimum ratio rows                          1,100+
  Computed/derived KPI fields                             50+
  Dedicated KPI tests                            20/20 passed
  Full project tests                                60 passed
  Manual ROE spot checks                           3/3 passed
  Manual 5-year Revenue CAGR spot checks           3/3 passed
  Manual calculation tolerance                 Less than 0.1%
  Capital-allocation records                            1,164
  Screener preview result                        37 companies
  Required screener preview range            15--50 companies

These are the recorded results supplied for Sprint 2. Rerun the relevant
tests and checks after code or source-data changes.

### 6.10 Manual spot checks

Three companies are used to validate ROE and 5-year Revenue CAGR:

-   ABB.
-   ADANIENSOL.
-   ADANIENT.

Results are stored in `output/manual_spot_check.csv` and compared with
corresponding values in `financial_ratios`.

### 6.11 Sprint 2 deliverables

-   `data/nifty100.db`
-   `output/capital_allocation.csv`
-   `output/ratio_edge_cases.log`
-   `output/manual_spot_check.csv`
-   `src/analytics/ratios.py`
-   `src/analytics/cagr.py`
-   `src/analytics/cashflow_kpis.py`
-   `tests/kpi/test_ratios.py`
-   `db/schema.sql`
-   `docs/sprint2_retro.md`

**Sprint 2 outcome:** A financial analytics layer for profitability,
leverage, efficiency, historical growth, cash-flow metrics, and
capital-allocation patterns.

------------------------------------------------------------------------

## 7. Sprint 3 --- Screener and Peer Engine

**Planned duration:** Days 15--21\
**Story points:** 49\
**Status:** **Verify against repository and deliverable tracker**

Sprint 3 builds a company screener and peer benchmarking engine on top
of the financial ratio data created in Sprint 2.

### 7.1 Screener

The specification calls for **six preset screening filters**. The
screener should filter the available companies using configurable
financial criteria and the metrics stored in the database.

The intended screening areas include:

-   Profitability.
-   Historical growth.
-   Leverage and debt risk.
-   Return metrics.
-   Operational efficiency.
-   Combined financial quality.

The precise criteria, thresholds, and output fields should match the
implementation in the repository. The categories above describe the
intended scope, not a claim that six specific filters have been verified
in code.

### 7.2 Peer benchmarking engine

The specification targets:

-   **11 peer groups**.
-   **10 financial comparison metrics**.
-   Peer-relative percentile rankings.

The engine should assign companies to relevant peer groups and calculate
rankings against those peers. Peer comparisons should account for sector
differences; for example, financial-sector leverage should not
automatically be interpreted using the same standards as non-financial
companies.

### 7.3 Expected capabilities

-   Load financial metrics from the Sprint 2 database.
-   Apply the six screening presets.
-   Return companies matching the selected criteria.
-   Assign companies to the supported peer groups.
-   Calculate percentile rankings for the specified metrics.
-   Make screener and peer results available to downstream dashboard
    components.
-   Test filter logic, peer assignments, and percentile calculations.

### 7.4 Sprint 3 deliverables

-   Screener implementation with six preset filters.
-   Peer-group classification for 11 peer groups.
-   Percentile rankings across 10 metrics.
-   Integration with `financial_ratios`.
-   Tests for screening and peer-ranking behavior.
-   Documented execution instructions and generated outputs, where
    applicable.

**Planned outcome:** A reusable screening and peer-comparison layer for
ranking and filtering companies using financial data.

------------------------------------------------------------------------

## 8. Sprint 4 --- Streamlit Dashboard and Valuation

**Planned duration:** Days 22--28\
**Story points:** 55\
**Status:** **Verify against repository and deliverable tracker**

Sprint 4 introduces an interactive dashboard and valuation functionality
so users can explore financial analytics without directly querying the
database.

### 8.1 Streamlit dashboard

**Planned entry point:** `src/dashboard/app.py`

The specification calls for **eight dashboard pages** covering the
platform's primary analytical areas:

1.  **Market and Universe Overview** --- overview of the companies and
    available financial data.
2.  **Company Financials** --- company-level financial statement
    analysis.
3.  **Financial Ratios** --- profitability, returns, leverage, and
    efficiency metrics.
4.  **Growth Analysis** --- Revenue, PAT, and EPS growth, including
    supported CAGR periods.
5.  **Stock Screener** --- filter companies using preset financial
    criteria.
6.  **Peer Benchmarking** --- compare companies with their peer groups.
7.  **Valuation Analysis** --- display supported valuation model outputs
    and assumptions.
8.  **Cash Flow and Intelligence** --- present cash-flow quality,
    capital-allocation patterns, and financial signals.

These names describe a proposed organization for the eight pages.
Confirm actual page names and behavior against the implemented dashboard
before marking each one complete.

### 8.2 Valuation module

The sprint includes a valuation component integrated with the platform's
financial data.

Depending on the implemented models and available inputs, the module may
use:

-   Historical financial performance.
-   Revenue and earnings growth.
-   Cash-flow metrics.
-   Profitability and return measures.
-   Explicit valuation assumptions.
-   Scenario-based estimates.
-   Sensitivity analysis.

The final documentation should name the actual valuation methods
implemented in the repository. Valuation estimates depend on assumptions
and should not be represented as guaranteed market prices.

### 8.3 Export functionality

The sprint calls for CSV export so users can save relevant analytical
results for further investigation and reporting.

### 8.4 Sprint 4 deliverables

-   Streamlit application scaffold.
-   Eight dashboard pages.
-   Integration with financial ratios.
-   Integration with screener and peer-engine outputs.
-   Valuation module.
-   CSV export functionality.
-   Dashboard and valuation tests.
-   Run instructions for the dashboard.

### 8.5 Launch command

If Streamlit is installed and the specified entry point exists, launch
the dashboard from the project root with:

``` bash
streamlit run src/dashboard/app.py
```

**Planned outcome:** An interactive financial analysis interface
combining company data, ratios, growth, screening, peer benchmarking,
valuation, and cash-flow analytics.

------------------------------------------------------------------------

## 9. Sprint 5 --- Cash Flow Intelligence, Reports, and NLP

**Planned duration:** Days 29--35\
**Story points:** 70\
**Status:** **Verify against repository and deliverable tracker**

Sprint 5 extends the platform with financial interpretation, batch
reporting, cash-flow intelligence, and natural-language processing.

### 9.1 Financial NLP parser

**Planned path:** `src/nlp/parser.py`

Responsibilities:

-   Parse supported financial-analysis inputs.
-   Normalize extracted information.
-   Prepare structured analytical records.
-   Supply parsed information to downstream insight generation and
    reporting.

Expected output:

-   `output/analysis_parsed.csv`

### 9.2 Pros-and-cons generator

**Planned path:** `src/nlp/pros_cons_generator.py`

The generator uses defined financial rules and available metrics to
produce readable company-level observations.

Potential insight categories include:

-   Profitability strengths and weaknesses.
-   Historical growth characteristics.
-   Leverage concerns.
-   Cash-flow quality.
-   Capital-allocation patterns.
-   Financial-risk indicators.

Expected output:

-   `output/pros_cons_generated.csv`

The specification targets pros-and-cons generation for **92 companies**.
The output count should be checked after execution.

These are rule-based analytical observations, not independent
verification of a company's financial condition or personalized
investment recommendations.

### 9.3 Cash-flow intelligence

Sprint 5 extends the cash-flow metrics developed in Sprint 2 into a more
consolidated analytical output.

Expected outputs:

-   `output/cashflow_intelligence.xlsx`
-   `output/distress_alerts.csv`

The analysis may bring together the implemented metrics for:

-   Operating cash flow.
-   Free cash flow.
-   Capital expenditure intensity.
-   FCF conversion.
-   Cash accumulation.
-   Debt-funded growth.
-   Potential distress indicators.
-   Capital-allocation patterns.

A distress alert is a signal for further investigation, not a definitive
finding of financial distress.

### 9.4 Company tear sheets

**Planned path:** `src/reports/tearsheet.py`

Expected output directory:

-   `reports/tearsheets/`

The specification targets **92 company-level PDF tear sheets**.

A tear sheet should summarize the company-level information supported by
the implementation, potentially including:

-   Company identification.
-   Financial performance.
-   Key ratios.
-   Historical growth.
-   Cash-flow indicators.
-   Capital-allocation observations.
-   Generated pros and cons.
-   Relevant analytical flags.

The exact sections should follow the actual report template.

### 9.5 Sector reports

**Planned path:** `src/reports/sector_report.py`

Expected output directory:

-   `reports/sector/`

The specification targets **11 sector PDFs**. Reports should summarize
the sector-level financial information available in the dataset and
support comparisons within the appropriate peer groups.

### 9.6 Portfolio summary

Expected output:

-   `reports/portfolio/portfolio_summary.pdf`

The portfolio summary is intended to consolidate information about the
analyzed company universe. Depending on the report implementation, it
may include financial-quality distributions, growth and profitability
characteristics, leverage indicators, cash-flow observations, sector
summaries, and selected risk alerts.

### 9.7 Sprint 5 deliverables

  -------------------------------------------------------------------------------
  Deliverable                         Expected location
  ----------------------------------- -------------------------------------------
  Generated pros and cons             `output/pros_cons_generated.csv`

  Parsed analysis                     `output/analysis_parsed.csv`

  Cash-flow intelligence workbook     `output/cashflow_intelligence.xlsx`

  Distress alerts                     `output/distress_alerts.csv`

  Company tear sheets                 `reports/tearsheets/`

  Sector reports                      `reports/sector/`

  Portfolio summary                   `reports/portfolio/portfolio_summary.pdf`

  NLP parser                          `src/nlp/parser.py`

  Pros-and-cons generator             `src/nlp/pros_cons_generator.py`

  Tear-sheet generator                `src/reports/tearsheet.py`

  Sector report generator             `src/reports/sector_report.py`
  -------------------------------------------------------------------------------

### 9.8 Sprint 5 acceptance checks

Before marking Sprint 5 complete, verify:

-   The parser generates the expected structured output.
-   Pros-and-cons output covers the intended company universe.
-   The cash-flow workbook is generated and contains expected fields.
-   Distress alerts are generated according to the implemented rules.
-   Company PDF generation produces the expected number of files.
-   Sector report generation produces the expected number of files.
-   The portfolio summary PDF is created.
-   Report generation handles missing or incomplete company data safely.
-   Relevant tests pass and generated files can be opened.

**Planned outcome:** A financial intelligence and reporting layer that
turns structured financial analytics into company-, sector-, and
portfolio-level outputs.

------------------------------------------------------------------------

## 10. Installation and Quick Start

### Prerequisites

-   Python compatible with `requirements.txt`.
-   Git.
-   Access to the supplied source datasets.
-   A terminal such as PowerShell, Command Prompt, or Bash.

### Step 1 --- Clone the repository

``` bash
git clone YOUR_REPOSITORY_URL
cd N100
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL and adjust
`cd N100` if the project folder has a different name.

### Step 2 --- Create a virtual environment

``` bash
python -m venv .venv
```

Windows PowerShell:

``` powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

``` bash
source .venv/bin/activate
```

### Step 3 --- Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 --- Configure the environment

Windows PowerShell:

``` powershell
Copy-Item config/.env.template .env
```

Linux/macOS:

``` bash
cp config/.env.template .env
```

Configure any required variables according to the project configuration.
Do not commit API keys, passwords, or private credentials.

### Step 5 --- Run the data foundation

``` bash
python -m src.etl.loader
```

Verify that the database and audit outputs are created.

### Step 6 --- Run financial analytics

``` bash
python -m src.analytics.ratios
```

Verify that the `financial_ratios` table is populated and the expected
Sprint 2 outputs are generated.

### Step 7 --- Run tests

``` bash
pytest -q
```

The test result should be evaluated against the current test suite and
acceptance criteria.

### Additional component commands

  --------------------------------------------------------------------------
  Component                           Command
  ----------------------------------- --------------------------------------
  ETL pipeline                        `python -m src.etl.loader`

  Financial ratios                    `python -m src.analytics.ratios`

  ETL tests                           `pytest -q tests/etl`

  KPI tests                           `pytest -q tests/kpi`

  Full test suite                     `pytest -q`

  Streamlit dashboard, if implemented `streamlit run src/dashboard/app.py`
  at the specified path               
  --------------------------------------------------------------------------

Use the module-specific execution instructions for the Sprint 3
screener, valuation, NLP, and reporting components. Do not assume a
module is executable until its entry point is implemented.

------------------------------------------------------------------------

## 11. Testing and Validation

### Sprint 1 validation

-   Source ingestion and normalization.
-   Schema and data-quality checks.
-   SQLite persistence.
-   Audit and validation-failure outputs.
-   ETL unit tests.
-   Exploratory SQL.

### Sprint 2 validation

Recorded acceptance results:

-   92 companies.
-   1,164 financial-ratio records.
-   50+ computed and derived KPI fields.
-   20/20 dedicated KPI tests passed.
-   60 full-project tests passed.
-   3/3 manual ROE spot checks passed.
-   3/3 manual 5-year Revenue CAGR spot checks passed.
-   Less than 0.1% manual calculation tolerance.
-   1,164 capital-allocation records.
-   37 companies in the screener preview, within the 15--50 target
    range.

### Sprint 3 validation checklist

-   Six preset filters return expected results.
-   Filter thresholds and null handling are tested.
-   Peer-group assignments are valid.
-   Percentile rankings cover the specified metrics.
-   Financial-sector comparisons are interpreted appropriately.
-   Screener and peer outputs are available to downstream components.

### Sprint 4 validation checklist

-   The eight dashboard pages load.
-   Database queries and filters return expected results.
-   Charts and metrics handle missing data.
-   Valuation formulas and assumptions are tested.
-   CSV exports contain the expected columns and records.
-   The dashboard can be launched using documented instructions.

### Sprint 5 validation checklist

-   NLP parsing produces valid structured records.
-   Pros-and-cons generation produces expected company coverage.
-   Cash-flow outputs are generated.
-   Distress rules handle missing and unusual values.
-   Company and sector PDF counts meet the specification.
-   Portfolio PDF generation succeeds.
-   Generated reports can be opened and reviewed.

The Sprint 3--5 lists are acceptance checklists, not assertions that
these tests have already passed.

------------------------------------------------------------------------

## 12. Consolidated Project Structure

The following is the **target structure consolidated from the sprint
specifications**. Files and directories associated with later sprints
should be treated as planned until verified in the repository.

``` text
N100/
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
├── src/
│   ├── etl/
│   │   ├── loader.py
│   │   ├── normaliser.py
│   │   └── validator.py
│   │
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
│   ├── nlp/
│   │   ├── parser.py
│   │   └── pros_cons_generator.py
│   │
│   └── reports/
│       ├── tearsheet.py
│       └── sector_report.py
│
├── tests/
│   ├── etl/
│   │   ├── test_loader.py
│   │   └── test_normalise.py
│   │
│   └── kpi/
│       └── test_ratios.py
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   ├── capital_allocation.csv
│   ├── ratio_edge_cases.log
│   ├── manual_spot_check.csv
│   ├── pros_cons_generated.csv
│   ├── analysis_parsed.csv
│   ├── cashflow_intelligence.xlsx
│   └── distress_alerts.csv
│
├── reports/
│   ├── tearsheets/
│   ├── sector/
│   └── portfolio/
│       └── portfolio_summary.pdf
│
├── deliverables/
│   ├── task1/
│   └── task2/
│
├── Makefile
├── README.md
└── requirements.txt
```

------------------------------------------------------------------------

## 13. Deliverable Tracker

Use the tracker below to review the main acceptance deliverables across
all five sprints. The authoritative project tracker should retain any
finer-grained deliverable IDs, owners, and status history.

  -------------------------------------------------------------------------------------------------
  Sprint            Deliverable       Expected artifact or evidence               Status
  ----------------- ----------------- ------------------------------------------- -----------------
  1                 SQLite database   `data/nifty100.db`                          Completed

  1                 Ingestion audit   `output/load_audit.csv`                     Completed

  1                 Validation        `output/validation_failures.csv`            Completed
                    failures                                                      

  1                 ETL loader,       `src/etl/`                                  Completed
                    normalizer,                                                   
                    validator                                                     

  1                 Database schema   `db/schema.sql`,                            Completed
                    and exploratory   `notebooks/exploratory_queries.sql`         
                    SQL                                                           

  1                 ETL tests         `tests/etl/`                                Completed

  2                 Financial ratios  `financial_ratios` in SQLite                Completed
                    and computed KPIs                                             

  2                 CAGR engine       `src/analytics/cagr.py`                     Completed

  2                 Cash-flow KPIs    `src/analytics/cashflow_kpis.py`,           Completed
                    and allocation    `output/capital_allocation.csv`             
                    classifications                                               

  2                 Edge-case log and `output/ratio_edge_cases.log`,              Completed
                    manual spot check `output/manual_spot_check.csv`              

  2                 KPI tests and     `tests/kpi/test_ratios.py` and acceptance   Completed
                    recorded          results                                     
                    validation                                                    

  3                 Six preset        Screener module and tests                   Verify
                    screener filters                                              

  3                 Peer groups and   11 groups, 10 metrics                       Verify
                    percentile                                                    
                    rankings                                                      

  4                 Eight-page        `src/dashboard/app.py` and page             Verify
                    dashboard         implementations                             

  4                 Valuation module  Valuation code and tests                    Verify

  4                 CSV export        Export functionality and sample output      Verify

  5                 NLP parsing and   `src/nlp/`, generated CSVs                  Verify
                    pros/cons                                                     

  5                 Cash-flow         XLSX and CSV outputs                        Verify
                    intelligence and                                              
                    distress alerts                                               

  5                 Company tear      Target: 92 PDFs                             Verify
                    sheets                                                        

  5                 Sector reports    Target: 11 PDFs                             Verify

  5                 Portfolio summary `reports/portfolio/portfolio_summary.pdf`   Verify
  -------------------------------------------------------------------------------------------------

**Definition of done:** Mark a deliverable complete only after the
artifact exists, the relevant functionality has been exercised, and
applicable tests or manual checks have passed.

------------------------------------------------------------------------

## 14. Data Quality and Financial Calculation Principles

### Data integrity

-   Preserve supplied source data.
-   Validate schema and data quality before downstream analysis.
-   Maintain ingestion audit and validation-failure outputs.
-   Avoid silently replacing missing values with zero.
-   Preserve traceability between source data and derived analytics
    where supported.

### Formula integrity

-   Handle zero denominators explicitly.
-   Do not force invalid sign combinations into conventional CAGR
    calculations.
-   Distinguish missing historical coverage from zero growth.
-   Interpret ROE carefully when equity is negative.
-   Interpret leverage in the context of the company's sector.
-   Record discrepancies between source-reported and computed ratios.

### Reproducibility

-   Keep formulas in dedicated modules.
-   Test important calculations.
-   Store generated outputs in documented locations.
-   Revalidate changes to source data and formulas.
-   Document assumptions, edge cases, and exceptions.

------------------------------------------------------------------------

## 15. Limitations and Disclaimer

This project is intended for financial analytics, educational purposes,
and research.

Financial ratios, growth metrics, screening outputs, valuation
estimates, cash-flow classifications, and generated pros and cons are
analytical tools. They do not guarantee future performance and should
not be interpreted as personalized investment advice. Data quality,
reporting conventions, sector differences, and model assumptions can
materially affect results.

Users should independently verify financial data, review analytical
assumptions, and consider relevant business and market risks before
making investment decisions.

------------------------------------------------------------------------

## Project Summary

The Nifty 100 Financial Intelligence Platform is designed as a modular
system that converts financial source data into structured, comparable,
and reportable insights.

Its five-sprint plan covers:

1.  **Data engineering:** Ingestion, normalization, validation, and
    SQLite persistence.
2.  **Financial analytics:** Ratios, CAGR, cash-flow KPIs, and
    capital-allocation patterns.
3.  **Comparative analytics:** Six screening presets and peer-relative
    percentile rankings.
4.  **Interactive analysis:** Eight-page dashboard, valuation, and CSV
    exports.
5.  **Financial intelligence:** NLP parsing, pros-and-cons generation,
    cash-flow analysis, distress alerts, and automated reporting.

Sprint 1 and Sprint 2 are documented as completed. Sprint 3 through
Sprint 5 are fully specified above and should be marked complete only
after their implementation and acceptance criteria are verified.
