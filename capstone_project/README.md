# Bluestock Mutual Fund Analytics

## Capstone Project I — Mutual Fund Analytics

An end-to-end mutual fund analytics project developed as part of the **Bluestock Fintech Capstone Project**. The project covers data ingestion, ETL, database design, exploratory data analysis, performance analytics, risk analysis, investor analytics, and business intelligence dashboarding.

---

## Project Overview

The objective of this project is to transform multiple mutual-fund datasets into a structured analytical system that can be used to understand:

* Mutual fund NAV performance
* Fund-house AUM
* SIP inflows
* Investor demographics and transactions
* Industry folio growth
* Scheme performance
* Portfolio and sector allocation
* Risk and return characteristics
* Benchmark relationships

The project follows a complete analytics workflow:

```text
Raw CSV Data
     ↓
Data Ingestion
     ↓
ETL & Data Cleaning
     ↓
Data Validation
     ↓
SQLite Database
     ↓
EDA & Performance Analytics
     ↓
Advanced Analytics
     ↓
Power BI Dashboard
     ↓
Business Insights
```

---

## Project Objectives

1. Build an automated ETL pipeline for mutual-fund datasets.
2. Clean and standardize heterogeneous CSV data.
3. Design and populate a relational SQLite database.
4. Perform exploratory data analysis using Python.
5. Calculate mutual-fund return and risk metrics.
6. Analyze investor behavior and portfolio characteristics.
7. Build advanced analytics such as VaR, cohort analysis, and recommendation logic.
8. Create an interactive Power BI dashboard.
9. Produce a professional final report and presentation.

---

## Dataset Description

The supplied dataset package contains the following datasets:

| Dataset                        | Description                           |            Size |
| ------------------------------ | ------------------------------------- | --------------: |
| `01_fund_master.csv`           | Mutual-fund scheme master information |      40 schemes |
| `02_nav_history.csv`           | Historical daily NAV data             |     46,000 rows |
| `03_aum_by_fund_house.csv`     | Fund-house AUM observations           |         90 rows |
| `04_monthly_sip_inflows.csv`   | Monthly SIP inflows                   |       48 months |
| `06_industry_folio_count.csv`  | Industry folio statistics             | 21 observations |
| `07_scheme_performance.csv`    | Scheme-level return and risk metrics  |      40 schemes |
| `08_investor_transactions.csv` | Investor transaction records          |     32,778 rows |
| `09_portfolio_holdings.csv`    | Portfolio holdings                    |        322 rows |
| `10_benchmark_indices.csv`     | Benchmark index history               |      8,050 rows |

### Dataset Note

The project specification references a `05_category_inflows.csv` dataset. This file was not present in the supplied dataset package, so missing data was not fabricated.

---

## Technology Stack

### Programming

* Python
* Pandas
* NumPy

### Visualization

* Matplotlib
* Seaborn
* Plotly

### Database

* SQLite
* SQL

### Analytics

* Jupyter Notebook
* Statistical analysis
* Financial performance metrics

### Business Intelligence

* Microsoft Power BI

### Development & Version Control

* Visual Studio Code
* Git
* GitHub

---

## Project Structure

```text
capstone_project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
│
├── scripts/
│   ├── etl_pipeline.py
│   ├── compute_metrics.py
│
```
