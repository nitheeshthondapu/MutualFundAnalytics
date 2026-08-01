# Mutual Fund Analytics

A Python and Jupyter-based analytics project to ingest mutual fund data, fetch live Net Asset Value (NAV) data from `mfapi.in`, perform data validation, and assess data quality.

## Project Structure

```text
Mutual Fund Analytics/
│
├── data/
│   ├── raw/                # Contains raw CSVs and fetched NAV datasets
│   └── processed/          # Processed data outputs
│
├── src/
│   ├── data_ingestion.py   # Main data loading and fetching orchestrator
│   ├── live_nav_fetch.py   # Standalone fetch script for mfapi.in live NAVs
│   └── data_analysis.py    # Data quality check and anomaly detection script
│
├── notebooks/
│   └── mutual_fund_analysis.ipynb  # Interactive step-by-step EDA and validation
│
├── dashboard/              # Visualization dashboards
├── reports/                # PDF/Markdown quality reports
├── sql/                    # Analytical SQL queries
│
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
└── .gitignore              # Files excluded from git tracking
```

## Setup & Installation

1. **Virtual Environment Setup**:
   Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   Install all required libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Code

### 1. Ingest Data & Fetch Live NAV
To fetch live NAV data for the 5 key schemes and load the local datasets:
```bash
python src/data_ingestion.py
```

### 2. Standalone Live NAV Fetch
To fetch live NAV histories independently:
```bash
python src/live_nav_fetch.py
```

### 3. Data Quality & Audit Report
To calculate metrics, audit for anomalies, and print the Data Quality Summary:
```bash
python src/data_analysis.py
```
This prints the formatted **DATA QUALITY SUMMARY** block and checks for:
- Completeness and loaded dataset shape
- Missing values (e.g. math constraints on YoY growth)
- Duplicate records
- Referential integrity of AMFI codes
- API schema mapping discrepancies
