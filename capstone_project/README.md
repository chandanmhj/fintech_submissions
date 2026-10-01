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
# Bluestock Mutual Fund Analytics

## Task 6 — Advanced Analytics + Risk Metrics

**Project:** Bluestock Fintech — Mutual Fund Analytics
**Task:** Task 6 — Advanced Analytics + Risk Metrics
**Version:** 1.0

---

## 1. Objective

This task extends the mutual fund analytics pipeline with advanced risk, investor-behaviour and portfolio-concentration analysis.

The analysis covers:

* Historical Value at Risk (VaR)
* Conditional Value at Risk (CVaR)
* Rolling 90-day Sharpe ratio
* Investor cohort analysis
* SIP continuity analysis
* Risk-based fund recommendations
* Sector concentration using the Herfindahl-Hirschman Index (HHI)
* Advanced analytical insights

---

# 2. Deliverables

| File                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `Advanced_Analytics.ipynb` | Complete advanced analytics notebook           |
| `var_cvar_report.csv`      | Historical VaR and CVaR for all schemes        |
| `recommender.py`           | Risk-appetite-based fund recommender           |
| `rolling_sharpe_chart.png` | Rolling 90-day Sharpe chart for selected funds |

---

# 3. Historical Value at Risk

## 3.1 Definition

Historical Value at Risk estimates the potential loss threshold based on the historical distribution of daily returns.

For a 95% confidence level:

```text
VaR₉₅ = 5th percentile of daily returns
```

The calculation uses the historical daily return distribution of each mutual fund.

## 3.2 Interpretation

A more negative VaR indicates that the fund has experienced larger downside returns within the historical observation period.

The VaR calculation is performed independently for all available schemes.

---

# 4. Conditional Value at Risk

## 4.1 Definition

Conditional Value at Risk (CVaR), also called Expected Shortfall, measures the average return during observations that fall below the VaR threshold.

```text
CVaR₉₅ = mean(returns < VaR₉₅)
```

## 4.2 Interpretation

While VaR identifies a downside threshold, CVaR describes the average severity of losses beyond that threshold.

A more negative CVaR indicates greater average loss in the historical tail of the return distribution.

---

# 5. VaR/CVaR Report

The file:

```text
var_cvar_report.csv
```

contains the calculated risk measures for all schemes.

Expected fields include:

| Column         | Definition                          |
| -------------- | ----------------------------------- |
| `amfi_code`    | Mutual fund scheme identifier       |
| `fund_name`    | Mutual fund scheme name             |
| `var_95`       | Historical 95% VaR threshold        |
| `cvar_95`      | Historical 95% CVaR                 |
| `observations` | Number of daily return observations |

### Validation

The report should contain one risk result for each eligible scheme.

The number of schemes is expected to be approximately:

```text
40
```

---

# 6. Rolling 90-Day Sharpe Ratio

## 6.1 Objective

The rolling Sharpe ratio evaluates the risk-adjusted performance of a fund over a moving 90-trading-day window.

Daily returns are first calculated from historical NAV.

The rolling statistics are then calculated using:

```text
Rolling Mean = returns.rolling(90).mean()

Rolling Std = returns.rolling(90).std()
```

The annualised rolling Sharpe ratio is:

```text
Rolling Sharpe =
(Rolling Mean / Rolling Std) × √252
```

where:

```text
252 = approximate number of trading days per year
```

## 6.2 Analysis

The rolling Sharpe ratio is plotted for five selected key funds.

The chart is saved as:

```text
rolling_sharpe_chart.png
```

The chart allows changes in risk-adjusted performance to be observed over time.

---

# 7. Investor Cohort Analysis

## 7.1 Cohort Definition

Investors are grouped according to the year of their first recorded transaction.

For each investor:

```text
First Transaction Year =
Year of earliest transaction date
```

Each investor is then assigned to the corresponding cohort.

Example:

| Investor   | First Transaction | Cohort |
| ---------- | ----------------- | ------ |
| Investor A | 2024-02-10        | 2024   |
| Investor B | 2024-08-21        | 2024   |
| Investor C | 2025-01-15        | 2025   |

## 7.2 Cohort Metrics

For each cohort, calculate:

* Average SIP amount
* Total invested amount
* Number of investors
* Number of transactions
* Preferred fund

## 7.3 Top Fund Preference

The top fund preference is determined from the frequency or transaction activity of funds within each investor cohort.

This identifies which schemes attract the highest participation from investors who entered the market during each year.

---

# 8. SIP Continuity Analysis

## 8.1 Objective

SIP continuity analysis evaluates whether investors maintain relatively regular SIP contributions.

Only investors with at least six SIP transactions are included.

```text
Minimum SIP transactions = 6
```

## 8.2 Average SIP Gap

For every eligible investor:

1. Sort SIP transactions chronologically.
2. Calculate the number of days between consecutive SIP transactions.
3. Calculate the average gap.

Conceptually:

```text
Average Gap =
mean(days between consecutive SIP transactions)
```

## 8.3 At-Risk Classification

Investors are flagged as:

```text
At-Risk
```

when:

```text
Average SIP Gap > 35 days
```

Investors with an average gap of 35 days or less are classified as:

```text
Regular
```

## 8.4 SIP Continuity Rate

The analysis can report:

```text
Continuity Rate =
Regular Investors / Eligible Investors × 100
```

This provides an overall indication of SIP persistence within the dataset.

---

# 9. Risk-Based Fund Recommender

## 9.1 Objective

A simple rule-based recommender is implemented using:

* Investor risk appetite
* Scheme risk grade
* Sharpe ratio

The supported risk appetites are:

```text
Low
Moderate
High
```

## 9.2 Recommendation Logic

The user's selected risk appetite is matched with the corresponding `risk_grade`.

Eligible funds are then sorted by Sharpe ratio.

The top three eligible schemes are returned.

Conceptually:

```text
Input:
    Risk Appetite

        ↓

Match risk_grade

        ↓

Filter eligible funds

        ↓

Sort by Sharpe Ratio descending

        ↓

Return Top 3 Funds
```

## 9.3 Output

The recommendation table contains:

| Field           | Description                |
| --------------- | -------------------------- |
| `fund_name`     | Scheme name                |
| `amfi_code`     | AMFI identifier            |
| `risk_grade`    | Scheme risk classification |
| `sharpe_ratio`  | Sharpe ratio               |
| `return_1y`     | One-year return            |
| `expense_ratio` | Expense ratio              |

The implementation is contained in:

```text
recommender.py
```

### Important

This is a **rule-based analytical recommender**, not personalised financial advice. The output is based solely on the project's historical dataset and predefined risk-grade mapping.

---

# 10. Sector Concentration — HHI

## 10.1 Objective

The Herfindahl-Hirschman Index (HHI) is used to measure portfolio concentration.

For portfolio sector weights:

```text
HHI = Σ(weightᵢ²)
```

where each `weightᵢ` represents the portfolio weight of sector `i`.

If weights are expressed as decimals:

```text
0 ≤ weightᵢ ≤ 1
```

then:

```text
0 ≤ HHI ≤ 1
```

## 10.2 Interpretation

A lower HHI generally indicates greater diversification across sectors.

A higher HHI indicates that portfolio exposure is concentrated in fewer sectors.

The analysis compares HHI across equity-oriented funds.

## 10.3 Example

For a hypothetical portfolio:

```text
Technology = 40%
Banking = 30%
Healthcare = 20%
Other = 10%
```

Using decimal weights:

```text
HHI =
0.40² + 0.30² + 0.20² + 0.10²
```

The resulting value represents the portfolio's sector concentration.

---

# 11. Advanced Insights

The notebook contains at least five analytical insights covering the following areas.

## Insight 1 — Downside Risk

Identify schemes with the most negative historical 95% VaR and CVaR.

The analysis distinguishes between:

* VaR threshold
* Average tail loss represented by CVaR

---

## Insight 2 — Risk-Adjusted Performance

Compare rolling Sharpe ratios across selected schemes.

The analysis identifies periods where risk-adjusted performance changed materially.

---

## Insight 3 — Investor Cohorts

Compare cohorts based on:

* Investor count
* Total invested amount
* Average SIP amount
* Preferred schemes

This reveals differences in investment behaviour across entry-year cohorts.

---

## Insight 4 — SIP Continuity

Measure:

* Number of eligible SIP investors
* Number of regular investors
* Number of at-risk investors
* Average SIP gap
* Overall SIP continuity rate

Investors with average SIP gaps above 35 days are classified as at-risk according to the project rule.

---

## Insight 5 — Portfolio Concentration

Compare HHI values across equity funds.

The analysis identifies funds with relatively higher and lower sector concentration and examines the relationship between concentration and fund characteristics.

---

# 12. Input Data

The analysis uses the cleaned datasets produced during the data-cleaning and SQL database task.

Primary inputs include:

```text
02_nav_history.csv
07_scheme_performance.csv
08_investor_transactions.csv
09_portfolio_holdings.csv
01_fund_master.csv
```

---

# 13. Data Validation

Before calculations, the notebook validates:

* Valid dates
* Positive NAV values
* Positive transaction amounts
* Valid AMFI codes
* Numeric return values
* Valid risk grades
* Valid Sharpe ratios
* Valid portfolio weights
* Sufficient observations for rolling calculations

---

# 14. Handling Missing Data

Missing observations are handled according to the analytical requirement.

### NAV

NAV data is sorted chronologically by fund and date before return calculations.

### Returns

Daily returns require consecutive NAV observations.

### Rolling Sharpe

The first 89 observations do not have a complete 90-day window and therefore produce missing rolling Sharpe values.

### SIP Cohorts

Only investors with sufficient transaction history are included in the SIP continuity analysis.

### HHI

Only valid sector weights are included in sector concentration calculations.

---

# 15. Analytical Assumptions

The following assumptions are used:

1. Historical returns are representative only of the supplied observation period.
2. Historical VaR does not guarantee future loss thresholds.
3. CVaR describes historical tail behaviour and does not predict future losses.
4. Sharpe ratio calculations use 252 trading days for annualisation.
5. SIP continuity is evaluated using transaction dates available in the dataset.
6. An average SIP gap greater than 35 days defines an at-risk investor for this project.
7. Risk recommendations are based on the supplied risk grades and historical Sharpe ratios.
8. HHI calculations use sector weights available in the portfolio holdings dataset.
9. Portfolio weights may contain minor rounding differences.

---

# 16. Output Summary

The task produces four primary deliverables.

### `Advanced_Analytics.ipynb`

Contains:

* VaR/CVaR calculations
* Rolling Sharpe analysis
* Cohort analysis
* SIP continuity analysis
* Fund recommender analysis
* HHI concentration analysis
* Five advanced insights

### `var_cvar_report.csv`

Contains historical 95% VaR and CVaR for eligible schemes.

### `recommender.py`

Contains the rule-based risk-appetite fund recommendation logic.

### `rolling_sharpe_chart.png`

Visualises rolling 90-day Sharpe ratios for five selected funds.

---

# 17. Quality Checks

The final analysis should verify:

* Approximately 40 schemes have VaR/CVaR calculations.
* VaR corresponds to the 5th percentile of daily returns.
* CVaR is calculated from observations below the VaR threshold.
* Rolling Sharpe uses a 90-observation window.
* Sharpe is annualised using √252.
* Cohorts are based on first transaction year.
* SIP continuity includes only investors with at least six SIP transactions.
* Investors with average gaps greater than 35 days are classified as at-risk.
* Recommender returns a maximum of three schemes.
* HHI is calculated from sector weights.
* Five analytical insights are documented in notebook Markdown.

---

# 18. Disclaimer

This analysis is intended for educational and analytical purposes as part of the Bluestock Fintech capstone project.

Historical performance and risk metrics should not be interpreted as guarantees of future investment performance. The recommender is a rule-based demonstration using project data and is not personalised financial advice.

---

## End of Task 6 Documentation
