"""
Simple Fund Recommender Script for Bluestock Mutual Fund Analytics.
This script provides recommendations based on investor risk appetite:
- Input: risk appetite (Low / Moderate / High)
- Output: top 3 funds by Sharpe ratio within the matching risk category.
Usage:
  python scripts/recommender.py --risk Moderate
  or run interactively:
  python scripts/recommender.py
"""

import sys
import os
import argparse
import sqlite3
import pandas as pd
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def get_db_connection():
    db_path = project_root / "data" / "db" / "bluestock_mf.db"
    return sqlite3.connect(db_path)

def recommend_funds(risk_appetite: str):
    """
    Finds and prints the top 3 funds matching the risk appetite sorted by Sharpe ratio.
    """
    risk_appetite = risk_appetite.strip().capitalize()
    if risk_appetite not in ['Low', 'Moderate', 'High']:
        print("Error: Risk appetite must be one of: 'Low', 'Moderate', 'High'")
        return None
        
    conn = get_db_connection()
    
    # Query performance and fund info
    query = """
        SELECT 
            f.amfi_code, 
            f.scheme_name, 
            f.category, 
            f.risk_category,
            p.sharpe_ratio,
            p.return_3yr_pct,
            p.expense_ratio_pct
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Map risk appetite to risk_categories in the database
    # Risk categories in dim_fund: 'Low', 'Moderate', 'Moderately High', 'High', 'Very High'
    if risk_appetite == 'Low':
        target_categories = ['Low']
    elif risk_appetite == 'Moderate':
        target_categories = ['Moderate', 'Moderately High']
    else: # High
        target_categories = ['High', 'Very High']
        
    # Filter and sort
    df_filtered = df[df['risk_category'].isin(target_categories)].copy()
    
    # Sort by Sharpe Ratio descending
    df_recommendations = df_filtered.sort_values('sharpe_ratio', ascending=False).head(3)
    
    if len(df_recommendations) == 0:
        # If no strict matches, fall back to matching risk categories contains the string
        df_filtered = df[df['risk_category'].str.contains(risk_appetite, case=False, na=False)].copy()
        df_recommendations = df_filtered.sort_values('sharpe_ratio', ascending=False).head(3)
        
    return df_recommendations

def main():
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund Recommender")
    parser.add_argument("--risk", type=str, help="Risk appetite (Low, Moderate, High)")
    args = parser.parse_args()
    
    risk = args.risk
    if not risk:
        # Interactive mode
        print("=== Welcome to the Bluestock Mutual Fund Recommender ===")
        print("Please choose your risk appetite:")
        print(" 1. Low (Focus on capital preservation and debt funds)")
        print(" 2. Moderate (Balanced growth with moderate volatility)")
        print(" 3. High (Aggressive growth seeking higher returns via equities)")
        choice = input("Enter choice (1, 2, 3 or type Low/Moderate/High): ").strip()
        
        if choice in ['1', 'Low', 'low']:
            risk = 'Low'
        elif choice in ['2', 'Moderate', 'moderate']:
            risk = 'Moderate'
        elif choice in ['3', 'High', 'high']:
            risk = 'High'
        else:
            print("Invalid input. Defaulting to 'Moderate'.")
            risk = 'Moderate'
            
    print(f"\nSearching for top 3 funds matching risk profile: {risk}...")
    recs = recommend_funds(risk)
    
    if recs is not None and len(recs) > 0:
        print("\n=========================================================================================")
        print(f"RECOMMENDED FUNDS FOR {risk.upper()} RISK PROFILE (Sorted by Sharpe Ratio)")
        print("=========================================================================================")
        print(f"{'AMFI Code':<10} | {'Scheme Name':<50} | {'Category':<10} | {'3Yr Return':<10} | {'Sharpe'}")
        print("-" * 93)
        for idx, row in recs.iterrows():
            print(f"{row['amfi_code']:<10} | {row['scheme_name'][:50]:<50} | {row['category']:<10} | {row['return_3yr_pct']:<9.2f}% | {row['sharpe_ratio']:.3f}")
        print("=========================================================================================\n")
    else:
        print("No matching funds found for this risk appetite.")

if __name__ == '__main__':
    main()
