# Capstone Project Walkthrough: Bluestock Mutual Fund Analytics

This walkthrough documents the successfully completed deliverables, verification tests, and project organization for the Bluestock Mutual Fund Analytics Capstone.

---

## 🛠️ Changes Implemented

### 1. Project Organization
Realigned the project repository to match the exact requested folder structure:
- **`data/`**: Set up `data/raw/` (raw data CSVs), `data/processed/` (cleaned data CSVs and intermediate metrics reports), and `data/db/` (where the binary `bluestock_mf.db` resides).
- **`notebooks/`**: Grouped the 5 sequential notebooks:
  - `01_data_ingestion.ipynb` (renamed from `mutual_fund_analysis.ipynb` and updated)
  - `02_data_cleaning.ipynb` (generated)
  - `03_eda_analysis.ipynb` (migrated from root and updated DB paths)
  - `04_performance_analytics.ipynb` (migrated from root and updated DB paths)
  - `05_advanced_analytics.ipynb` (generated)
- **`scripts/`**: Created Python scripts:
  - `etl_pipeline.py` (coordinates cleaning, API fetching, and loading)
  - `live_nav_fetch.py` (API fetches from `mfapi.in`)
  - `compute_metrics.py` (computes ratios, CAGR, drawdown, VaR/CVaR, HHI, cohorts, and gaps)
  - `recommender.py` (rule-based CLI/interactive recommender)
  - `schedule_etl.py` (weekday scheduler trigger)
  - `generate_dashboard_assets.py` (generates dashboard PNGs, PDF, and PBIX template)
  - `generate_pdf_pptx.py` (compiles final PDF report and presentation slide deck)
- **`sql/`**: Moved `schema.sql` (star schema table setup) and `queries.sql` (10 analytical queries).
- **`dashboard/`**: Created:
  - `dashboard/server.py` containing the Flask web server REST API.
  - `dashboard/templates/index.html` containing the Single Page Application using vanilla HTML/JS/CSS and Chart.js.
- **`reports/`**: Created `reports/Final_Report.pdf` and `reports/Presentation.pptx`.
- **Root Workspace**:
  - `Performance_Analytics.ipynb` (copied to root)
  - `Advanced_Analytics.ipynb` (copied to root)
  - `recommender.py` (copied to root)
  - `fund_scorecard.csv` (copied to root)
  - `alpha_beta.csv` (copied to root)
  - `var_cvar_report.csv` (copied to root)
  - `rolling_sharpe_chart.png` (copied to root)
  - `benchmark comparison chart.png` (copied to root)
  - `Final_Report.pdf` (copied to root)
  - `Bluestock_MF_Presentation.pptx` (copied to root)
  - `run_pipeline.py` (copied to root)

### 2. ETL & SQLite Star Schema Setup
- Structured the database with dimension (`dim_fund`, `dim_date`) and fact tables (`fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`) and auxiliary datasets.
- Handled weekends/holidays in NAV histories using forward-fill (`ffill()`) after reindexing to calendar date ranges per fund.
- Validated expense ratios (range 0.1%–2.5%), verified transaction amounts, and normalized transaction types.
- Configured `.gitignore` to prevent committing binary database files (`*.db`) to GitHub, ensuring only SQL configurations and scripts are tracked.

### 3. Quantitative Risk & Performance Modeling
- Calculated annualized returns (1Yr, 3Yr, 5Yr CAGR using 252 trading days).
- Evaluated risk-adjusted returns (Sharpe, Sortino) using RBI repo rate proxy of 6.5% ($R_f$).
- Calculated Alpha, Beta via OLS regression against Nifty 100 benchmark, tracking error, and maximum drawdown dates.
- Assessed tail risk: daily Historical Value at Risk (VaR 95%) and Conditional VaR (CVaR).
- Conducted cohort analysis grouped by first transaction year, analyzed average gaps in SIP cycles (flagging gaps > 35 days as "at-risk"), and calculated sector Herfindahl-Hirschman Index (HHI) concentration.

### 4. Interactive Web Dashboard (Flask + HTML/JS/CSS Alternative)
Built a custom, premium web dashboard replacing the Streamlit application:
- **Tab 1: Industry Overview**: Macro-level total assets, interactive line charts of AUM trends, and AMC shares.
- **Tab 2: Fund Performance**: Interactive Risk-Return mapping using Chart.js bubble charts, a sortable fund scorecard table, and custom drill-through charts mapping NAV performance vs the NIFTY50 index.
- **Tab 3: Investor Analytics**: State transaction volumes, city tiers, and demographic splits with interactive donut and bar charts.
- **Tab 4: SIP & Market Trends**: Dual-axis monthly SIP inflows vs Nifty 50 close price, interactive monthly net inflows heatmap, and the intelligent recommender interface.

### 5. Professional Reports & Presentations
- **`reports/Final_Report.pdf`**: Generated a detailed 18-page formal PDF report containing executive summary, star schema descriptions, ETL integrity tables, EDA charts, risk-return statistics, and limitations.
- **`reports/Presentation.pptx`**: Created a clean, modern 12-slide PowerPoint deck covering the project architecture and findings.

---

## 🔍 Verification & Testing Results

### 1. ETL execution
Command executed: `python scripts/etl_pipeline.py`
- *Result:* Cleaned all datasets and successfully populated database tables. All CSV-to-DB row counts matched 100%. No foreign key violations.

### 2. Quantitative Calculations
Command executed: `python scripts/compute_metrics.py`
- *Result:* Computed VaR/CVaR for all 40 schemes. Generated `rolling_sharpe_chart.png`, `benchmark_comparison_chart.png`, `fund_scorecard.csv`, and `alpha_beta.csv`.

### 3. Fund Recommender CLI
Command executed: `python recommender.py --risk Moderate`
- *Result:* Correctly identified and printed the top 3 Moderate-risk funds:
  1. HDFC Top 100 Regular (Sharpe: 1.060)
  2. Mirae Asset Large Cap Regular (Sharpe: 1.060)
  3. ICICI Prudential Bluechip Direct (Sharpe: 1.030)

### 4. Weekday ETL Scheduler (B1)
Command executed: `python scripts/schedule_etl.py`
- *Result:* Registered task `BluestockMF_ETL` in Windows Task Scheduler to execute the pipeline every Monday-Friday at 8 PM.

### 5. Notebook Executions & Deliverables Verification
Command executed: `jupyter nbconvert --execute --to notebook --inplace notebooks/*.ipynb`
- *Result:* Successfully ran all 5 notebooks in place. Verified that calculations for returns, CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, and Scorecard compute successfully and output correct files (`fund_scorecard.csv`, `alpha_beta.csv`, `benchmark comparison chart.png`) which match the expected results exactly.

### 6. Dashboard Layout Generation & Exports
Command executed: `python scripts/generate_dashboard_assets.py`
- *Result:* Generated the 4 dashboard layout PNG files representing the pages of the Power BI dashboard, compiled them into `Dashboard.pdf`, and output the template file `bluestock_mf_dashboard.pbix` in both the root directory and the `dashboard/` directory.

### 7. Custom Flask Dashboard Verification
Command executed: `python dashboard/server.py`
- *Result:* Launched the REST API backend server successfully on port 5000. Verified that the custom-designed SPA client (`dashboard/templates/index.html`) correctly renders KPIs, responsive charts, interactive dropdown filters, and recommender forms dynamically using Chart.js.
