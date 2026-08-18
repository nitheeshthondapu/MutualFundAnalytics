import sqlite3
import pandas as pd
import numpy as np

def test_calculations():
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "db" / "bluestock_mf.db"
    conn = sqlite3.connect(db_path)
    
    print("--- Testing fact_nav ---")
    nav_df = pd.read_sql("SELECT * FROM fact_nav", conn)
    print("NAV shape:", nav_df.shape)
    print(nav_df.head(3))
    
    print("\n--- Testing dim_fund ---")
    fund_df = pd.read_sql("SELECT * FROM dim_fund", conn)
    print("Fund shape:", fund_df.shape)
    print(fund_df.head(3))
    
    print("\n--- Testing fact_transactions ---")
    tx_df = pd.read_sql("SELECT * FROM fact_transactions", conn)
    print("Transactions shape:", tx_df.shape)
    print(tx_df.head(3))
    
    print("\n--- Testing portfolio_holdings ---")
    holdings_df = pd.read_sql("SELECT * FROM portfolio_holdings", conn)
    print("Holdings shape:", holdings_df.shape)
    print(holdings_df.head(3))
    
    print("\n--- Testing fact_performance ---")
    perf_df = pd.read_sql("SELECT * FROM fact_performance", conn)
    print("Performance shape:", perf_df.shape)
    print(perf_df.head(3))

    conn.close()

if __name__ == "__main__":
    test_calculations()
