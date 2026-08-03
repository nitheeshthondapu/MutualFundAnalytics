# Bluestock Mutual Fund Analytics Data Dictionary

This document details the database schema and columns for the SQLite database `bluestock_mf.db` populated from the cleaned CSV files under `data/processed/`.

---

## 1. Table: `dim_fund`
- **Source File**: `01_fund_master.csv`
- **Description**: Dimension table storing structural metadata about mutual fund schemes.
- **Primary Key**: `amfi_code`

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `amfi_code` | INTEGER | Unique 6-digit Association of Mutual Funds in India (AMFI) code representing the scheme. | Primary Key |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC) managing the fund (e.g., 'SBI Mutual Fund'). | Not Null |
| `scheme_name` | TEXT | Full name of the mutual fund scheme option (e.g., 'SBI Bluechip Fund - Regular Plan - Growth'). | Not Null |
| `category` | TEXT | Broad asset class category (e.g., 'Equity', 'Debt', 'Hybrid'). | |
| `sub_category` | TEXT | Granular investment style (e.g., 'Large Cap', 'Small Cap', 'Liquid'). | |
| `plan` | TEXT | Plan type: 'Regular' (distributor commission included) or 'Direct' (lower expense ratio). | |
| `launch_date` | TEXT | Date when the fund scheme was launched (format: 'YYYY-MM-DD'). | |
| `benchmark` | TEXT | Benchmark index against which fund performance is compared (e.g., 'NIFTY 100 TRI'). | |
| `expense_ratio_pct` | REAL | Annual operating expenses of the scheme expressed as a percentage of AUM. | Range: 0.1% – 2.5% |
| `exit_load_pct` | REAL | Fee charged to investors when redeeming units early, as a percentage of redemption value. | |
| `min_sip_amount` | REAL | Minimum contribution amount for Systematic Investment Plan (SIP) in INR. | |
| `min_lumpsum_amount` | REAL | Minimum initial investment amount for one-time lumpsum purchase in INR. | |
| `fund_manager` | TEXT | Name of the primary fund manager managing the portfolio. | |
| `risk_category` | TEXT | Risk classification of the fund (e.g., 'Very High', 'Moderate', 'Low'). | |
| `sebi_category_code` | TEXT | SEBI standard code for the scheme category (e.g., 'EC01'). | |

---

## 2. Table: `dim_date`
- **Source File**: Generated programmatically (2022-01-01 to 2026-12-31)
- **Description**: Date dimension table supporting time-series and window analysis.
- **Primary Key**: `date`

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `date` | TEXT | Calendar date (format: 'YYYY-MM-DD'). | Primary Key |
| `year` | INTEGER | Year number (e.g., 2024). | Not Null |
| `month` | INTEGER | Month number (1 to 12). | Not Null |
| `day` | INTEGER | Calendar day of month (1 to 31). | Not Null |
| `quarter` | INTEGER | Calendar quarter of year (1 to 4). | Not Null |
| `day_of_week` | INTEGER | Day index of week (0 = Monday, 6 = Sunday). | Not Null |
| `is_weekend` | INTEGER | Binary flag indicating if date is a weekend (1 = Saturday/Sunday, 0 = Weekday). | Not Null |

---

## 3. Table: `fact_nav`
- **Source File**: `02_nav_history.csv`
- **Description**: Fact table tracking Net Asset Value (NAV) of mutual fund schemes on a daily basis.
- **Composite Primary Key**: (`amfi_code`, `date`)

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `amfi_code` | INTEGER | Scheme code of the fund. | Composite PK, FK to `dim_fund(amfi_code)` |
| `date` | TEXT | Date of the NAV record (format: 'YYYY-MM-DD'). | Composite PK, FK to `dim_date(date)` |
| `nav` | REAL | Net Asset Value per unit of the scheme. Forward-filled for weekends/holidays. | Not Null, > 0 |

---

## 4. Table: `fact_transactions`
- **Source File**: `08_investor_transactions.csv`
- **Description**: Fact table capturing individual investor purchase and redemption transactions.
- **Primary Key**: `transaction_id` (Autoincrement)

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `transaction_id` | INTEGER | Unique sequential transaction identifier. | Primary Key |
| `investor_id` | TEXT | Unique code identifying the individual investor (e.g., 'INV003054'). | Not Null |
| `transaction_date` | TEXT | Date the transaction took place (format: 'YYYY-MM-DD'). | FK to `dim_date(date)` |
| `amfi_code` | INTEGER | Scheme code of the mutual fund transacted. | FK to `dim_fund(amfi_code)` |
| `transaction_type` | TEXT | Type of transaction (SIP, Lumpsum, or Redemption). | CHECK IN ('SIP', 'Lumpsum', 'Redemption') |
| `amount_inr` | REAL | Total financial value of the transaction in Indian Rupees. | Not Null, > 0 |
| `state` | TEXT | Indian state where the investor resides (e.g., 'Telangana'). | |
| `city` | TEXT | City where the investor resides (e.g., 'Hyderabad'). | |
| `city_tier` | TEXT | Tier classification of investor city: 'T30' (Top 30 cities) or 'B30' (Beyond 30 cities). | |
| `age_group` | TEXT | Age range of the investor (e.g., '18-25', '56+'). | |
| `gender` | TEXT | Gender of the investor ('Male', 'Female'). | |
| `annual_income_lakh` | REAL | Annual income of the investor in Lakhs INR (e.g., 7.1 represents 710,000 INR). | |
| `payment_mode` | TEXT | Payment method used (e.g., 'UPI', 'Net Banking', 'Cheque'). | |
| `kyc_status` | TEXT | Know Your Customer verification status ('Verified' or 'Pending'). | CHECK IN ('Verified', 'Pending') |

---

## 5. Table: `fact_performance`
- **Source File**: `07_scheme_performance.csv`
- **Description**: Fact table tracking scheme risk metrics, historical returns, and current AUM.
- **Primary Key**: `amfi_code`

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `amfi_code` | INTEGER | Scheme code of the fund. | Primary Key, FK to `dim_fund(amfi_code)` |
| `scheme_name` | TEXT | Full name of the scheme. | |
| `fund_house` | TEXT | Fund house managing the scheme. | |
| `category` | TEXT | Scheme category (e.g., 'Large Cap', 'Liquid'). | |
| `plan` | TEXT | Scheme plan ('Regular' or 'Direct'). | |
| `return_1yr_pct` | REAL | Total historical return of the scheme over the past 1 year in %. | Numeric |
| `return_3yr_pct` | REAL | Annualised historical return of the scheme over the past 3 years in %. | Numeric |
| `return_5yr_pct` | REAL | Annualised historical return of the scheme over the past 5 years in %. | Numeric |
| `benchmark_3yr_pct` | REAL | Annualised return of the scheme's benchmark index over 3 years in %. | Numeric |
| `alpha` | REAL | Outperformance of the fund relative to its benchmark index. | Numeric |
| `beta` | REAL | Measure of the fund's volatility relative to its benchmark. | Numeric |
| `sharpe_ratio` | REAL | Risk-adjusted return metric (Excess Return per unit of standard deviation). | Numeric |
| `sortino_ratio` | REAL | Risk-adjusted return metric focusing only on negative downside risk. | Numeric |
| `std_dev_ann_pct` | REAL | Annualised standard deviation of weekly returns indicating overall volatility. | Numeric |
| `max_drawdown_pct` | REAL | Maximum peak-to-trough decline of the fund in %. | Numeric |
| `aum_crore` | REAL | Assets Under Management of the scheme in Crores INR. | |
| `expense_ratio_pct` | REAL | Scheme expense ratio in %. | Range: 0.1% – 2.5% |
| `morningstar_rating`| INTEGER | Performance rating from 1 (lowest) to 5 (highest) stars. | |
| `risk_grade` | TEXT | Volatility risk grade relative to category (e.g., 'High', 'Moderate', 'Low'). | |
| `is_anomalous` | INTEGER | Binary flag identifying statistical outliers (e.g., Liquid funds with extreme Sharpe/Sortino ratios). | Default: 0 |

---

## 6. Table: `fact_aum`
- **Source File**: `03_aum_by_fund_house.csv`
- **Description**: Fact table tracking quarterly Assets Under Management (AUM) by fund house.
- **Primary Key**: `aum_id` (Autoincrement)

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `aum_id` | INTEGER | Unique sequential identifier. | Primary Key |
| `date` | TEXT | Last date of the quarter for the AUM report (format: 'YYYY-MM-DD'). | FK to `dim_date(date)` |
| `fund_house` | TEXT | Name of the fund house. | Not Null |
| `aum_lakh_crore` | REAL | Assets Under Management in Lakh Crores INR. | |
| `aum_crore` | REAL | Assets Under Management in Crores INR. | Not Null |
| `num_schemes` | INTEGER | Total active mutual fund schemes offered by the fund house. | |

---

## 7. Table: `monthly_sip_inflows`
- **Source File**: `04_monthly_sip_inflows.csv`
- **Description**: Auxiliary table containing monthly industry-wide SIP inflows and accounts.
- **Primary Key**: `month`

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `month` | TEXT | Calendar month of the record (format: 'YYYY-MM'). | Primary Key |
| `sip_inflow_crore` | REAL | Monthly SIP inflow in Crores INR. | |
| `active_sip_accounts_crore`| REAL| Number of active SIP accounts in Crores. | |
| `new_sip_accounts_lakh`| REAL | Number of new SIP accounts registered in Lakhs. | |
| `sip_aum_lakh_crore` | REAL | Total SIP Assets Under Management in Lakh Crores INR. | |
| `yoy_growth_pct` | REAL | Year-on-Year percentage growth of SIP inflow. | Null for the first 12 months |

---

## 8. Table: `category_inflows`
- **Source File**: `05_category_inflows.csv`
- **Description**: Auxiliary table tracking net inflows into different fund categories per month.
- **Primary Key**: `inflow_id` (Autoincrement)

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `inflow_id` | INTEGER | Unique record identifier. | Primary Key |
| `month` | TEXT | Calendar month of the record (format: 'YYYY-MM'). | Not Null |
| `category` | TEXT | Mutual fund scheme category (e.g., 'Large Cap', 'Small Cap'). | Not Null |
| `net_inflow_crore` | REAL | Net financial inflow in Crores INR (can be negative for net outflows).| |

---

## 9. Table: `industry_folio_count`
- **Source File**: `06_industry_folio_count.csv`
- **Description**: Auxiliary table tracking industry-wide folio count distributions across different asset classes.
- **Primary Key**: `month`

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `month` | TEXT | Calendar month of the record (format: 'YYYY-MM'). | Primary Key |
| `total_folios_crore` | REAL | Total mutual fund folios across the industry in Crores. | |
| `equity_folios_crore`| REAL | Folios in equity schemes in Crores. | |
| `debt_folios_crore` | REAL | Folios in debt schemes in Crores. | |
| `hybrid_folios_crore`| REAL | Folios in hybrid schemes in Crores. | |
| `others_folios_crore`| REAL | Folios in other scheme types (Gold ETF, FOFs) in Crores. | |

---

## 10. Table: `portfolio_holdings`
- **Source File**: `09_portfolio_holdings.csv`
- **Description**: Auxiliary table containing stock-level holdings for each mutual fund scheme.
- **Primary Key**: `holding_id` (Autoincrement)

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `holding_id` | INTEGER | Unique record identifier. | Primary Key |
| `amfi_code` | INTEGER | Scheme code of the fund holding the stock. | FK to `dim_fund(amfi_code)` |
| `stock_symbol` | TEXT | Ticker symbol of the stock (e.g., 'POWERGRID'). | |
| `stock_name` | TEXT | Official corporate name of the company. | Not Null |
| `sector` | TEXT | Industry sector of the stock (e.g., 'Utilities', 'Banking'). | |
| `weight_pct` | REAL | Portfolio allocation weight of the stock in %. | Not Null |
| `market_value_cr` | REAL | Market value of the stock holdings in Crores INR. | |
| `current_price_inr` | REAL | Current share price of the stock in INR. | |
| `portfolio_date` | TEXT | Date of the portfolio statement (format: 'YYYY-MM-DD'). | Not Null |

---

## 11. Table: `benchmark_indices`
- **Source File**: `10_benchmark_indices.csv`
- **Description**: Auxiliary table tracking closing prices of key benchmark indices over time.
- **Primary Key**: `benchmark_id` (Autoincrement)

| Column Name | SQLite Data Type | Business Definition | Source reference / Constraint |
|---|---|---|---|
| `benchmark_id` | INTEGER | Unique closing price record identifier. | Primary Key |
| `date` | TEXT | Date of index closing value (format: 'YYYY-MM-DD'). | FK to `dim_date(date)` |
| `index_name` | TEXT | Name of the benchmark index (e.g., 'NIFTY50', 'SENSEX'). | Not Null |
| `close_value` | REAL | Closing price value of the index. | Not Null |
