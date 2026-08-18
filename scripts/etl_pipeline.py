"""
ETL Pipeline Master Orchestrator for Bluestock Mutual Fund Analytics.
This script performs the following steps:
1. (Optional) Fetches live NAV history for key mutual fund schemes.
2. Cleans all raw CSV datasets (standardizing types, filling dates, validating values).
3. Builds the SQLite Star Schema database.
4. Loads cleaned CSVs into the SQLite database.
5. Verifies row count consistency between CSVs and database tables.
"""

import os
import logging
import sqlite3
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import cleaning and fetching modules
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import cleaning and fetching modules
from scripts.live_nav_fetch import fetch_and_save_nav
from scripts.clean_data import clean_nav_history, clean_investor_transactions, clean_scheme_performance, clean_general_file

def run_nav_fetch(raw_dir: Path):
    """Fetches live NAV history for the 6 key schemes from mfapi.in."""
    logger.info("Step 1: Fetching live NAV data from mfapi.in...")
    key_schemes = [125497, 119551, 120503, 118632, 119092, 120841]
    success = 0
    for code in key_schemes:
        if fetch_and_save_nav(code, raw_dir):
            success += 1
    logger.info(f"Live NAV fetch completed: {success}/{len(key_schemes)} schemes successfully fetched.")

def run_data_cleaning(raw_dir: Path, processed_dir: Path):
    """Applies cleaning rules to all 10 raw datasets and saves to data/processed/."""
    logger.info("Step 2: Cleaning CSV datasets...")
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean nav_history
    clean_nav_history(raw_dir / "02_nav_history.csv", processed_dir / "02_nav_history.csv")
    
    # 2. Clean investor_transactions
    clean_investor_transactions(raw_dir / "08_investor_transactions.csv", processed_dir / "08_investor_transactions.csv")
    
    # 3. Clean scheme_performance
    clean_scheme_performance(raw_dir / "07_scheme_performance.csv", processed_dir / "07_scheme_performance.csv")
    
    # 4. Clean other datasets
    clean_general_file(raw_dir / "01_fund_master.csv", processed_dir / "01_fund_master.csv", date_cols=['launch_date'])
    clean_general_file(raw_dir / "03_aum_by_fund_house.csv", processed_dir / "03_aum_by_fund_house.csv", date_cols=['date'])
    clean_general_file(raw_dir / "04_monthly_sip_inflows.csv", processed_dir / "04_monthly_sip_inflows.csv")
    clean_general_file(raw_dir / "05_category_inflows.csv", processed_dir / "05_category_inflows.csv")
    clean_general_file(raw_dir / "06_industry_folio_count.csv", processed_dir / "06_industry_folio_count.csv")
    clean_general_file(raw_dir / "09_portfolio_holdings.csv", processed_dir / "09_portfolio_holdings.csv", date_cols=['portfolio_date'])
    clean_general_file(raw_dir / "10_benchmark_indices.csv", processed_dir / "10_benchmark_indices.csv", date_cols=['date'])
    
    logger.info("All 10 datasets cleaned and exported to data/processed/.")

def run_db_loading(db_path: Path, schema_path: Path, processed_dir: Path):
    """Sets up SQLite database, builds the schema, loads cleaned data, and validates."""
    logger.info("Step 3: Creating SQLite database and loading data...")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")

    # Build schema
    logger.info(f"Executing database schema definitions from {schema_path}...")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    statements = schema_sql.split(';')
    with engine.begin() as conn:
        for stmt in statements:
            stmt_strip = stmt.strip()
            if stmt_strip:
                conn.execute(text(stmt_strip))

    # Populate dim_date table
    logger.info("Populating dim_date dimension table (2022 to 2026)...")
    dates = pd.date_range(start='2022-01-01', end='2026-12-31', freq='D')
    dim_date_df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'year': dates.year,
        'month': dates.month,
        'day': dates.day,
        'quarter': dates.quarter,
        'day_of_week': dates.dayofweek,
        'is_weekend': dates.dayofweek.map(lambda x: 1 if x in [5, 6] else 0)
    })
    with engine.begin() as conn:
        dim_date_df.to_sql('dim_date', con=conn, if_exists='append', index=False)

    # Load Cleaned CSVs
    mapping = {
        '01_fund_master.csv': 'dim_fund',
        '02_nav_history.csv': 'fact_nav',
        '03_aum_by_fund_house.csv': 'fact_aum',
        '04_monthly_sip_inflows.csv': 'monthly_sip_inflows',
        '05_category_inflows.csv': 'category_inflows',
        '06_industry_folio_count.csv': 'industry_folio_count',
        '07_scheme_performance.csv': 'fact_performance',
        '08_investor_transactions.csv': 'fact_transactions',
        '09_portfolio_holdings.csv': 'portfolio_holdings',
        '10_benchmark_indices.csv': 'benchmark_indices'
    }

    verification_results = []
    logger.info("Loading cleaned files into SQLite tables...")
    for filename, table_name in mapping.items():
        file_path = processed_dir / filename
        if not file_path.exists():
            logger.error(f"Processed file {file_path} is missing.")
            continue
            
        df = pd.read_csv(file_path)
        csv_rows = len(df)
        
        with engine.begin() as conn:
            df.to_sql(table_name, con=conn, if_exists='append', index=False)
            
        with engine.connect() as conn:
            db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            
        match = "Yes" if csv_rows == db_rows else "No"
        verification_results.append((filename, table_name, csv_rows, db_rows, match))

    # Display verification report
    logger.info("=== ETL DATA INTEGRITY REPORT ===")
    logger.info(f"{'Filename':<30} | {'Table Name':<20} | {'CSV Rows':<8} | {'DB Rows':<8} | Match")
    logger.info("-" * 80)
    for res in verification_results:
        logger.info(f"{res[0]:<30} | {res[1]:<20} | {res[2]:<8} | {res[3]:<8} | {res[4]}")
    logger.info("=" * 80)

    # Verify foreign keys
    with engine.connect() as conn:
        violations = conn.execute(text("PRAGMA foreign_key_check")).all()
        if violations:
            logger.warning(f"Integrity check failed: {len(violations)} foreign key violations detected.")
        else:
            logger.info("Database foreign key integrity check passed successfully.")

def main():
    project_root = Path(__file__).resolve().parent.parent
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    db_path = project_root / "data" / "db" / "bluestock_mf.db"
    schema_path = project_root / "sql" / "schema.sql"

    logger.info("Starting Bluestock Mutual Fund ETL Pipeline...")
    
    # 1. Fetch live NAV (if needed, otherwise skips/loads existing)
    run_nav_fetch(raw_dir)
    
    # 2. Clean data
    run_data_cleaning(raw_dir, processed_dir)
    
    # 3. Load DB
    run_db_loading(db_path, schema_path, processed_dir)
    
    logger.info("ETL Pipeline completed successfully.")

if __name__ == '__main__':
    main()
