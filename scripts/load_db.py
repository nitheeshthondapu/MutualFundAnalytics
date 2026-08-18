import sqlite3
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

def main():
    db_path = Path("bluestock_mf.db")
    schema_path = Path("schema.sql")
    processed_dir = Path("data/processed")
    
    # 1. Connect to SQLite and execute schema.sql DDL
    print("Connecting to database and running schema DDL...")
    engine = create_engine(f"sqlite:///{db_path}")
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        
    # Split queries by semicolon to execute individually
    statements = schema_sql.split(';')
    with engine.begin() as conn:
        for stmt in statements:
            stmt_strip = stmt.strip()
            if stmt_strip:
                conn.execute(text(stmt_strip))
    print("Database tables created successfully according to schema.sql.")
    
    # 2. Populate dim_date Table
    print("Populating dim_date table...")
    # Generate dates from 2022-01-01 to 2026-12-31 to cover all possible date columns
    dates = pd.date_range(start='2022-01-01', end='2026-12-31', freq='D')
    dim_date_df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'year': dates.year,
        'month': dates.month,
        'day': dates.day,
        'quarter': dates.quarter,
        'day_of_week': dates.dayofweek, # 0 = Monday, 6 = Sunday
        'is_weekend': dates.dayofweek.map(lambda x: 1 if x in [5, 6] else 0)
    })
    
    with engine.begin() as conn:
        dim_date_df.to_sql('dim_date', con=conn, if_exists='append', index=False)
    print(f"dim_date table populated with {len(dim_date_df)} rows.")

    # 3. Load Cleaned CSVs into SQLite
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
    
    print("\nLoading datasets into database and verifying row counts...")
    verification_results = []
    
    for filename, table_name in mapping.items():
        file_path = processed_dir / filename
        if not file_path.exists():
            print(f"Error: Cleaned file {file_path} does not exist.")
            continue
            
        # Load CSV into DataFrame
        df = pd.read_csv(file_path)
        csv_row_count = len(df)
        
        # Load to SQL using append mode to preserve DDL constraints
        with engine.begin() as conn:
            df.to_sql(table_name, con=conn, if_exists='append', index=False)
            
        # Verify row counts
        with engine.connect() as conn:
            db_row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            
        match = (csv_row_count == db_row_count)
        verification_results.append({
            'File': filename,
            'Table': table_name,
            'CSV Rows': csv_row_count,
            'DB Rows': db_row_count,
            'Match': "Yes" if match else "No"
        })
        
    # Print results in a formatted table
    print("\n" + "="*70)
    print(f"{'Filename':<30} | {'Table Name':<20} | {'CSV Rows':<8} | {'DB Rows':<8} | Match")
    print("="*70)
    for res in verification_results:
        print(f"{res['File']:<30} | {res['Table']:<20} | {res['CSV Rows']:<8} | {res['DB Rows']:<8} | {res['Match']}")
    print("="*70 + "\n")
    
    # Enable foreign keys and verify constraints
    print("Verifying database integrity...")
    with engine.connect() as conn:
        # Check foreign keys
        fk_violations = conn.execute(text("PRAGMA foreign_key_check")).all()
        if fk_violations:
            print("WARNING: Foreign key violations detected!")
            for violation in fk_violations:
                print(f"  Violation: {violation}")
        else:
            print("No foreign key violations detected. Integrity verified.")
            
    print("\nDatabase loading and verification process complete.")

if __name__ == '__main__':
    main()
