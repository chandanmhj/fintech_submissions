# Bluestock Mutual Fund Analytics

## Data Dictionary

**Project:** Bluestock Fintech — Mutual Fund Analytics
**Task:** Task 5 — Data Cleaning + SQL Database Design
**Database:** SQLite
**Version:** 1.0
**Source:** Bluestock Mutual Fund Analytics CSV datasets

---

## 1. Purpose

This data dictionary documents the datasets used in the Bluestock Mutual Fund Analytics project.

For each dataset, the dictionary defines:

* Column name
* Data type
* Business definition
* Source dataset
* Validation or transformation rules

The cleaned datasets are stored in `data/processed/` and loaded into the SQLite database `bluestock_mf.db`.

---

# 2. Dataset Overview

| Dataset                        | Description                         | Approx. Records |
| ------------------------------ | ----------------------------------- | --------------: |
| `01_fund_master.csv`           | Mutual fund master/reference data   |              40 |
| `02_nav_history.csv`           | Historical NAV observations         |          46,000 |
| `03_aum_by_fund_house.csv`     | Fund-house AUM history              |              90 |
| `04_monthly_sip_inflows.csv`   | Monthly SIP inflows                 |              48 |
| `06_industry_folio_count.csv`  | Industry-level folio statistics     |              21 |
| `07_scheme_performance.csv`    | Scheme performance and risk metrics |              40 |
| `08_investor_transactions.csv` | Investor transaction records        |          32,778 |
| `09_portfolio_holdings.csv`    | Scheme portfolio holdings           |             322 |
| `10_benchmark_indices.csv`     | Benchmark index history             |           8,050 |

> Note: Dataset `05_category_inflows.csv` was not present in the supplied source package. Category-inflow analysis should therefore only be performed if the missing source file is subsequently provided.

---

# 3. `01_fund_master.csv`

## Description

Master/reference table containing one record for each mutual fund scheme.

### Columns

| Column         | Data Type      | Definition                                        | Validation / Rule |
| -------------- | -------------- | ------------------------------------------------- | ----------------- |
| `amfi_code`    | INTEGER / TEXT | Unique AMFI identifier for the mutual fund scheme | Required; unique  |
| `fund_name`    | TEXT           | Official mutual fund scheme name                  | Required          |
| `fund_house`   | TEXT           | Asset Management Company managing the scheme      | Required          |
| `category`     | TEXT           | Mutual fund investment category                   | Required          |
| `sub_category` | TEXT           | More specific classification within the category  | Nullable          |
| `benchmark`    | TEXT           | Benchmark index used for scheme comparison        | Nullable          |
| `launch_date`  | DATE           | Scheme launch date                                | Valid date        |

### Primary Key

```text
amfi_code
```

---

# 4. `02_nav_history.csv`

## Description

Daily historical Net Asset Value (NAV) observations for mutual fund schemes.

### Columns

| Column      | Data Type      | Definition                    | Validation / Rule         |
| ----------- | -------------- | ----------------------------- | ------------------------- |
| `amfi_code` | INTEGER / TEXT | AMFI identifier of the scheme | Must exist in fund master |
| `date`      | DATE           | NAV observation date          | Valid date                |
| `nav`       | DECIMAL        | Net Asset Value of the scheme | Must be > 0               |

### Cleaning Rules

1. Convert date values to standard date format.
2. Sort by `amfi_code` and `date`.
3. Remove duplicate `amfi_code + date` combinations.
4. Reindex dates where required.
5. Forward-fill NAV across non-trading days after establishing the appropriate date range.
6. Validate that all final NAV values are greater than zero.

### Primary Key

```text
amfi_code + date
```

### Foreign Key

```text
amfi_code → dim_fund.amfi_code
```

---

# 5. `03_aum_by_fund_house.csv`

## Description

Historical Assets Under Management (AUM) for mutual fund houses.

### Columns

| Column        | Data Type | Definition                           | Validation / Rule    |
| ------------- | --------- | ------------------------------------ | -------------------- |
| `fund_house`  | TEXT      | Name of the Asset Management Company | Required             |
| `report_date` | DATE      | AUM reporting date                   | Valid date           |
| `aum_crore`   | DECIMAL   | Assets Under Management in ₹ crore   | Must be non-negative |

### Business Definition

AUM represents the value of assets managed by a fund house at the specified reporting date.

---

# 6. `04_monthly_sip_inflows.csv`

## Description

Monthly Systematic Investment Plan (SIP) inflow statistics.

### Columns

| Column             | Data Type   | Definition                                  | Validation / Rule                  |
| ------------------ | ----------- | ------------------------------------------- | ---------------------------------- |
| `month`            | DATE / TEXT | Month represented by the observation        | Valid month                        |
| `sip_inflow_crore` | DECIMAL     | Monthly SIP contribution in ₹ crore         | Must be non-negative               |
| `yoy_growth_pct`   | DECIMAL     | Year-over-year SIP inflow growth percentage | Nullable for first comparison year |

### Business Definition

SIP inflow represents the amount invested through systematic investment plans during a particular month.

---

# 7. `06_industry_folio_count.csv`

## Description

Industry-level mutual fund folio statistics.

### Columns

| Column                | Data Type | Definition                        | Validation / Rule |
| --------------------- | --------- | --------------------------------- | ----------------- |
| `date`                | DATE      | Reporting period                  | Valid date        |
| `total_folios_crore`  | DECIMAL   | Total mutual fund folios in crore | Non-negative      |
| `equity_folios_crore` | DECIMAL   | Equity-oriented folios            | Non-negative      |
| `debt_folios_crore`   | DECIMAL   | Debt-oriented folios              | Non-negative      |
| `hybrid_folios_crore` | DECIMAL   | Hybrid scheme folios              | Non-negative      |
| `other_folios_crore`  | DECIMAL   | Other scheme-category folios      | Non-negative      |

### Business Definition

A folio represents an investor account associated with a mutual fund investment.

---

# 8. `07_scheme_performance.csv`

## Description

Scheme-level performance, return, risk and fund characteristics.

### Columns

| Column                | Data Type      | Definition                                           | Validation / Rule                |
| --------------------- | -------------- | ---------------------------------------------------- | -------------------------------- |
| `amfi_code`           | INTEGER / TEXT | AMFI scheme identifier                               | Must exist in fund master        |
| `return_1y`           | DECIMAL        | Scheme return over 1 year (%)                        | Numeric                          |
| `return_3y`           | DECIMAL        | Annualised 3-year return (%)                         | Numeric                          |
| `return_5y`           | DECIMAL        | Annualised 5-year return (%)                         | Numeric                          |
| `benchmark_return_1y` | DECIMAL        | Benchmark return over 1 year (%)                     | Numeric                          |
| `alpha`               | DECIMAL        | Excess risk-adjusted return relative to benchmark    | Numeric                          |
| `beta`                | DECIMAL        | Sensitivity of scheme returns to benchmark movements | Numeric                          |
| `sharpe_ratio`        | DECIMAL        | Risk-adjusted return measured using Sharpe ratio     | Numeric                          |
| `sortino_ratio`       | DECIMAL        | Downside-risk-adjusted return                        | Numeric                          |
| `std_dev`             | DECIMAL        | Standard deviation of returns                        | Numeric                          |
| `max_drawdown`        | DECIMAL        | Maximum peak-to-trough decline                       | Numeric                          |
| `aum_crore`           | DECIMAL        | Scheme-level AUM in ₹ crore                          | Non-negative                     |
| `expense_ratio`       | DECIMAL        | Annual expense ratio (%)                             | Expected approximately 0.1%–2.5% |
| `morningstar_rating`  | INTEGER        | External rating assigned to the scheme               | Valid rating range               |
| `risk_grade`          | TEXT           | Risk classification of the scheme                    | Valid category                   |

### Validation Rules

* Return and risk metrics must be numeric.
* Missing or malformed numeric values must be flagged.
* `aum_crore >= 0`.
* Expense ratio should normally fall within **0.1%–2.5%**.
* Values outside the expected expense-ratio range should be flagged for review rather than silently deleted.
* `amfi_code` must exist in `dim_fund`.

---

# 9. `08_investor_transactions.csv`

## Description

Investor-level mutual fund transaction records.

### Columns

| Column             | Data Type      | Definition                      | Validation / Rule          |
| ------------------ | -------------- | ------------------------------- | -------------------------- |
| `investor_id`      | TEXT / INTEGER | Unique investor identifier      | Required                   |
| `date`             | DATE           | Transaction date                | Valid date                 |
| `amfi_code`        | INTEGER / TEXT | Mutual fund scheme identifier   | Must exist in fund master  |
| `transaction_type` | TEXT           | Type of transaction             | SIP, Lumpsum or Redemption |
| `amount`           | DECIMAL        | Transaction amount in ₹         | Must be > 0                |
| `state`            | TEXT           | Investor state                  | Standardised text          |
| `city`             | TEXT           | Investor city                   | Standardised text          |
| `city_tier`        | TEXT           | Classification of investor city | T30 / B30                  |
| `age_group`        | TEXT           | Investor age classification     | Valid category             |
| `gender`           | TEXT           | Investor gender                 | Standardised category      |
| `income`           | DECIMAL        | Investor income value           | Numeric where available    |
| `payment_mode`     | TEXT           | Method used for the transaction | Standardised category      |
| `kyc`              | TEXT           | KYC verification status         | Valid enum                 |

### Transaction Type Standardisation

The following canonical values are used:

```text
SIP
Lumpsum
Redemption
```

Different capitalisation or formatting variants are converted to these standard values.

### Amount Validation

```text
amount > 0
```

Transactions with zero or negative amounts are flagged or removed according to the cleaning procedure.

### KYC Validation

KYC values are checked against the accepted status categories present in the source dataset. Unexpected values are flagged for review.

### Foreign Key

```text
amfi_code → dim_fund.amfi_code
```

---

# 10. `09_portfolio_holdings.csv`

## Description

Portfolio holdings of mutual fund schemes.

### Columns

| Column            | Data Type      | Definition                          | Validation / Rule         |
| ----------------- | -------------- | ----------------------------------- | ------------------------- |
| `amfi_code`       | INTEGER / TEXT | Mutual fund scheme identifier       | Must exist in fund master |
| `holding_name`    | TEXT           | Name of security held by the scheme | Required                  |
| `sector`          | TEXT           | Sector classification of holding    | Standardised text         |
| `instrument_type` | TEXT           | Type of financial instrument        | Standardised category     |
| `weight_pct`      | DECIMAL        | Portfolio allocation percentage     | Normally 0–100            |
| `as_of_date`      | DATE           | Portfolio reporting date            | Valid date                |

### Business Rule

For each scheme and reporting date, portfolio weights should approximately sum to 100%, subject to rounding and excluded cash/other assets.

---

# 11. `10_benchmark_indices.csv`

## Description

Historical benchmark index observations used for performance comparison.

### Columns

| Column       | Data Type | Definition             | Validation / Rule |
| ------------ | --------- | ---------------------- | ----------------- |
| `index_name` | TEXT      | Benchmark index name   | Required          |
| `date`       | DATE      | Index observation date | Valid date        |
| `close`      | DECIMAL   | Closing index value    | Must be > 0       |

### Benchmark Examples

The dataset includes benchmarks such as:

* NIFTY 50
* NIFTY 100
* NIFTY 500
* NIFTY Midcap 150
* BSE SmallCap
* CRISIL Gilt
* CRISIL Liquid

---

# 12. SQLite Star Schema

The cleaned datasets are represented in SQLite using a dimensional/star-schema design.

## Dimension Tables

### `dim_fund`

Contains static/reference information about mutual fund schemes.

**Primary Key:**

```text
amfi_code
```

### `dim_date`

Contains calendar-level attributes used for time-based analysis.

**Primary Key:**

```text
date
```

Typical attributes include:

* date
* year
* quarter
* month
* month_name
* day
* day_of_week
* is_weekend

---

# 13. Fact Tables

## `fact_nav`

Stores daily NAV observations.

| Column      | Type         | Key |
| ----------- | ------------ | --- |
| `amfi_code` | INTEGER/TEXT | FK  |
| `date`      | DATE         | FK  |
| `nav`       | DECIMAL      | —   |

Primary key:

```text
(amfi_code, date)
```

---

## `fact_transactions`

Stores investor transaction events.

| Column             | Type         | Key |
| ------------------ | ------------ | --- |
| `investor_id`      | TEXT         | —   |
| `date`             | DATE         | FK  |
| `amfi_code`        | INTEGER/TEXT | FK  |
| `transaction_type` | TEXT         | —   |
| `amount`           | DECIMAL      | —   |
| `state`            | TEXT         | —   |
| `city`             | TEXT         | —   |
| `city_tier`        | TEXT         | —   |
| `age_group`        | TEXT         | —   |
| `gender`           | TEXT         | —   |
| `income`           | DECIMAL      | —   |
| `payment_mode`     | TEXT         | —   |
| `kyc`              | TEXT         | —   |

---

## `fact_performance`

Stores scheme-level performance and risk metrics.

Key relationships:

```text
amfi_code → dim_fund.amfi_code
```

---

## `fact_aum`

Stores fund-house or scheme AUM observations.

Typical fields:

```text
fund_house
report_date
aum_crore
```

---

# 14. Key Relationships

The central relationship in the database is the mutual fund scheme identified by `amfi_code`.

```text
                    ┌──────────────┐
                    │   dim_fund   │
                    │--------------│
                    │ PK amfi_code │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   ┌────────────┐   ┌───────────────┐  ┌────────────────┐
   │  fact_nav  │   │fact_transactions│ │fact_performance│
   └──────┬─────┘   └───────────────┘  └────────────────┘
          │
          │
          ▼
    ┌────────────┐
    │  dim_date  │
    └────────────┘
```

---

# 15. Data Cleaning Standards

The following standards were applied during data preparation.

## Dates

All date fields are converted to a consistent date representation.

```text
YYYY-MM-DD
```

Invalid date values are identified and flagged.

## Numeric Values

Numeric columns are converted to appropriate numeric types.

Malformed numeric values are treated as missing and flagged for review.

## Duplicate Records

Duplicate records are identified using the appropriate business key.

For NAV:

```text
amfi_code + date
```

## NAV Validation

Every final NAV observation should satisfy:

```text
NAV > 0
```

## Transaction Validation

Every transaction should satisfy:

```text
amount > 0
```

## Transaction Types

Transaction types are standardised to:

```text
SIP
Lumpsum
Redemption
```

## Expense Ratio

Expense ratios are checked against the expected range:

```text
0.1% – 2.5%
```

Outliers are flagged rather than automatically assumed to be incorrect.

---

# 16. Source-to-Database Mapping

| Source Dataset                 | Database Table      |
| ------------------------------ | ------------------- |
| `01_fund_master.csv`           | `dim_fund`          |
| Calendar-generated date data   | `dim_date`          |
| `02_nav_history.csv`           | `fact_nav`          |
| `08_investor_transactions.csv` | `fact_transactions` |
| `07_scheme_performance.csv`    | `fact_performance`  |
| `03_aum_by_fund_house.csv`     | `fact_aum`          |

Supporting datasets such as SIP inflows, folio counts, portfolio holdings and benchmark indices remain available in the processed data layer for EDA and advanced analytics.

---

# 17. Data Quality Checks

The ETL and database loading process validates:

* Row counts
* Duplicate records
* Missing values
* Invalid dates
* Invalid numeric values
* NAV values less than or equal to zero
* Transaction amounts less than or equal to zero
* Invalid transaction types
* Invalid KYC values
* Expense-ratio anomalies
* Orphan AMFI codes
* Referential integrity
* Portfolio-weight consistency

---

# 18. Expected Source Row Counts

| Dataset               | Expected Records |
| --------------------- | ---------------: |
| Fund Master           |               40 |
| NAV History           |           46,000 |
| AUM by Fund House     |               90 |
| Monthly SIP Inflows   |               48 |
| Industry Folio Count  |               21 |
| Scheme Performance    |               40 |
| Investor Transactions |           32,778 |
| Portfolio Holdings    |              322 |
| Benchmark Indices     |            8,050 |

Minor differences may occur after cleaning if invalid or duplicate records are removed. Any difference between source and cleaned row counts should be documented in the data-quality report.

---

# 19. Data Governance Notes

The database is intended for analytical and educational purposes.

The datasets contain synthetic or project-provided investor information and should not be interpreted as a production financial database.

Personally identifiable information should not be introduced into the project beyond the identifiers already supplied in the project dataset.

Database files containing potentially sensitive transactional information should not be committed to a public Git repository unless explicitly permitted.

---

# 20. Version Information

**Project:** Bluestock Mutual Fund Analytics
**Task:** Task 5 — Data Cleaning + SQL Database Design
**Schema Version:** 1.0
**Documentation Version:** 1.0

---

## End of Data Dictionary
