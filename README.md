# Bluestock Mutual Fund Analytics Capstone

A comprehensive Python, Jupyter, and SQLite-based data engineering and portfolio analytics platform for evaluating mutual fund performance, risk profiles, and investor behavior across 40 schemes.

---

## 📁 Repository Structure

```text
bluestock_mf_capstone/
├── data/
│   ├── raw/                 # Original raw CSVs and fetched API NAV histories
│   ├── processed/           # Cleaned and processed CSV datasets
│   └── db/                  # bluestock_mf.db (SQLite database)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py      # Master ETL orchestrator (clean + DB load)
│   ├── live_nav_fetch.py    # Fetch live NAV histories from mfapi.in
│   ├── compute_metrics.py   # Computes CAGR, risk ratios, VaR, HHI, and cohorts
│   ├── recommender.py       # Rule-based fund recommendation CLI engine
│   └── schedule_etl.py      # Schedules weekday ETL fetches (B1)
├── sql/
│   ├── schema.sql           # SQLite Star Schema DDL
│   └── queries.sql          # 10 Analytical SQL Queries
├── dashboard/
│   ├── server.py            # Flask API Server (B2)
│   ├── templates/
│   │   └── index.html       # HTML/CSS/JS Dashboard Client (B2)
│   └── bluestock_mf.pbix    # Power BI Dashboard file template
├── reports/
│   ├── Final_Report.pdf     # 18-page PDF report with embedded charts
│   └── Presentation.pptx    # 12-slide presentation deck
├── data_dictionary.md       # Full documentation of database fields
├── requirements.txt         # Python package dependencies
└── README.md                # Project README documentation
```

---

## 📊 Dataset Descriptions

The project blends 10 structured raw datasets:
1. **`01_fund_master.csv`**: Contains structural properties of 40 schemes (fund house, category, plan type, SEBI categories).
2. **`02_nav_history.csv`**: Historical daily NAVs for all schemes (contains 46,000 raw business-day records, which cleans and reindexes to 64,320 rows after adding calendar dates and applying forward-fill).
3. **`03_aum_by_fund_house.csv`**: Quarterly Asset Under Management trends per AMC.
4. **`04_monthly_sip_inflows.csv`**: Industry-wide monthly SIP inflows and active accounts.
5. **`05_category_inflows.csv`**: Category-specific net inflows per month.
6. **`06_industry_folio_count.csv`**: Aggregate folio counts categorized by asset class.
7. **`07_scheme_performance.csv`**: Historical returns, standard deviation, expense ratios, and risk categories.
8. **`08_investor_transactions.csv`**: Transaction history for 32,778 investors.
9. **`09_portfolio_holdings.csv`**: Weighted stock allocations and sector holding lists.
10. **`10_benchmark_indices.csv`**: Historical closing values of Nifty 50 and Nifty 100 indices.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Environment Setup
Create and activate a virtual environment:
```bash
python -m venv .venv

# Windows (Command Prompt)
.venv\Scripts\activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries (including pandas, numpy, scipy, plotly, sqlalchemy, flask, reportlab, and python-pptx):
```bash
pip install -r requirements.txt
# (Optional) If reportlab, python-pptx, and flask are not in the requirements:
pip install flask reportlab python-pptx
```

---

## 🚀 Execution Guide

### 1. Master Pipeline Execution (Orchestrates All Steps)
You can run the entire pipeline—data ingestion, cleaning, metric calculations, report compilation, and slide deck generation—using a single command:
```bash
python run_pipeline.py
```

### 2. Run the ETL Pipeline Separately
The master ETL script cleans the 10 CSV files, resolves NAV holiday gaps via forward-fill, normalizes investor demographics, compiles the SQLite database, and populates the star schema:
```bash
python scripts/etl_pipeline.py
```
*Output database is created at:* `data/db/bluestock_mf.db`.

### 3. Calculate Quantitative Metrics Separately
Run the compute script to calculate Value at Risk (VaR 95%), Conditional VaR (CVaR), Rolling Sharpe ratios, Investor cohorts, and HHI. Note that base metrics (returns CAGR, static Sharpe/Sortino ratios, Alpha, Beta, and Maximum Drawdowns) are calculated in notebooks/04_performance_analytics.ipynb during notebook execution:
```bash
python scripts/compute_metrics.py
```
*Outputs generated:* `var_cvar_report.csv`, `rolling_sharpe_chart.png`, `benchmark_comparison_chart.png`, and processed tables in `data/processed/`.

### 4. Launch the Interactive Web Dashboard (Flask - B2)
Launch our custom HTML/JS/CSS interactive dashboard backend server (developed as a premium alternative to Streamlit):
```bash
python dashboard/server.py
```
*Open your web browser and navigate to:* [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 4. Query Recommendations via Recommender
Select the top 3 mutual funds by Sharpe ratio within matching risk categories:
```bash
python scripts/recommender.py --risk Moderate
```

### 5. Weekday ETL Scheduler (B1)
Register the ETL pipeline to automatically fetch updated NAVs from `mfapi.in` every weekday at 8:00 PM:
```bash
python scripts/schedule_etl.py
```
*Registers a task named `BluestockMF_ETL` in Windows Task Scheduler or adds a Unix Crontab entry.*

---

## 📊 Analytical SQL Queries

10 SQL queries are stored in `sql/queries.sql`. You can execute them directly on the SQLite database at `data/db/bluestock_mf.db` to retrieve:
- Top 5 funds by AUM.
- Average NAV per month for each scheme.
- Year-over-Year (YoY) monthly SIP growth.
- Total transaction counts and volumes by state.
- Schemes with an expense ratio below 1.0%.
- Demographic investment behaviors (age groups/gender).
- AMC quarterly growth trends.
- Sector holding values.
- Fund returns against Nifty index benchmark.
- Highly concentrated stock holdings (>10% weight).
