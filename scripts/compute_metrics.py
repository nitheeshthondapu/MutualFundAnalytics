"""
Compute Metrics Script for Bluestock Mutual Fund Analytics.
This script performs quantitative calculations for:
1. VaR (95%) and CVaR (95%) for all 40 schemes.
2. Rolling 90-day Sharpe ratio for 5 key schemes and saves the plot.
3. Investor cohort analysis (group by first transaction year).
4. SIP continuity analysis (average gap, flagging at-risk investors).
5. Sector HHI concentration for all equity funds.
All outputs are saved as CSVs/plots in data/processed/, reports/, and root workspace.
"""

import sys
import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def get_db_connection():
    db_path = project_root / "data" / "db" / "bluestock_mf.db"
    return sqlite3.connect(db_path)

def compute_var_cvar():
    """Computes daily VaR (95%) and CVaR (95%) for all 40 schemes."""
    print("Computing Historical VaR (95%) and CVaR for all schemes...")
    conn = get_db_connection()
    
    # Load daily NAV history
    df_nav = pd.read_sql("SELECT amfi_code, date, nav FROM fact_nav", conn)
    df_funds = pd.read_sql("SELECT amfi_code, scheme_name, category FROM dim_fund", conn)
    conn.close()
    
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav = df_nav.sort_values(['amfi_code', 'date'])
    
    # Calculate daily returns
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    # Compute VaR and CVaR per scheme
    results = []
    for amfi, group in df_nav.groupby('amfi_code'):
        returns = group['daily_return'].dropna()
        if len(returns) < 30:
            continue
            
        # 5th percentile of return distribution
        var_95 = np.percentile(returns, 5)
        # CVaR is the mean of returns below or equal to VaR
        cvar_95 = returns[returns <= var_95].mean()
        
        results.append({
            'amfi_code': amfi,
            'var_95_pct': var_95 * 100, # as percentage
            'cvar_95_pct': cvar_95 * 100 # as percentage
        })
        
    df_results = pd.DataFrame(results)
    df_report = pd.merge(df_funds, df_results, on='amfi_code')
    df_report = df_report.sort_values('var_95_pct') # most negative return (highest risk) first
    
    # Save reports
    df_report.to_csv(project_root / "var_cvar_report.csv", index=False)
    df_report.to_csv(project_root / "data" / "processed" / "var_cvar_report.csv", index=False)
    print(f"VaR/CVaR report saved. Calculated for {len(df_report)} schemes.")
    return df_report

def compute_rolling_sharpe():
    """Computes rolling 90-day Sharpe ratio for 5 key schemes and saves plot."""
    print("Computing rolling 90-day Sharpe for 5 key schemes...")
    conn = get_db_connection()
    df_nav = pd.read_sql("SELECT amfi_code, date, nav FROM fact_nav", conn)
    df_funds = pd.read_sql("SELECT amfi_code, scheme_name FROM dim_fund", conn)
    conn.close()
    
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    
    # 5 key funds
    key_codes = [125497, 119551, 120503, 118632, 119092]
    df_key_funds = df_funds[df_funds['amfi_code'].isin(key_codes)]
    key_names = dict(zip(df_key_funds['amfi_code'], df_key_funds['scheme_name']))
    
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="white")
    
    # Style constants matching Bluestock styling
    colors = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed']
    
    for i, amfi in enumerate(key_codes):
        group = df_nav[df_nav['amfi_code'] == amfi].sort_values('date').copy()
        group['daily_return'] = group['nav'].pct_change()
        
        # Rolling mean and std of daily return (90 trading days)
        rolling_mean = group['daily_return'].rolling(90).mean()
        rolling_std = group['daily_return'].rolling(90).std()
        
        # Annualized Sharpe (Rf assumed 6.5% annual / 252 daily)
        rf_daily = 0.065 / 252
        rolling_sharpe = ((rolling_mean - rf_daily) / rolling_std) * np.sqrt(252)
        
        plt.plot(group['date'], rolling_sharpe, label=key_names[amfi], color=colors[i], linewidth=1.5)
        
    plt.title("Rolling 90-Day Sharpe Ratio Over Time (Key Funds)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, color='#4b5563')
    plt.ylabel("Rolling Sharpe Ratio", fontsize=11, color='#4b5563')
    plt.grid(True, linestyle='--', alpha=0.5, color='#e5e7eb')
    plt.legend(frameon=True, facecolor='white', edgecolor='#e5e7eb', fontsize=9, loc='upper left')
    plt.tight_layout()
    
    # Save chart
    chart_path = project_root / "rolling_sharpe_chart.png"
    chart_path_processed = project_root / "data" / "processed" / "rolling_sharpe_chart.png"
    chart_path_reports = project_root / "reports" / "rolling_sharpe_chart.png"
    
    plt.savefig(chart_path, dpi=300)
    plt.savefig(chart_path_processed, dpi=300)
    plt.savefig(chart_path_reports, dpi=300)
    plt.close()
    print("Rolling Sharpe chart saved.")

def compute_investor_cohorts():
    """Performs investor cohort analysis grouped by first transaction year."""
    print("Performing investor cohort analysis...")
    conn = get_db_connection()
    df_tx = pd.read_sql("SELECT investor_id, transaction_date, transaction_type, amount_inr, amfi_code FROM fact_transactions", conn)
    df_funds = pd.read_sql("SELECT amfi_code, scheme_name FROM dim_fund", conn)
    conn.close()
    
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    df_tx['year'] = df_tx['transaction_date'].dt.year
    
    # Find cohort (first transaction year) for each investor
    df_first_tx = df_tx.groupby('investor_id')['transaction_date'].min().reset_index()
    df_first_tx['cohort_year'] = df_first_tx['transaction_date'].dt.year
    df_cohort_map = dict(zip(df_first_tx['investor_id'], df_first_tx['cohort_year']))
    
    # Map cohorts back to transactions
    df_tx['cohort'] = df_tx['investor_id'].map(df_cohort_map)
    
    # Analysis per cohort
    cohorts = sorted(df_tx['cohort'].unique())
    cohort_results = []
    
    for cohort in cohorts:
        cohort_tx = df_tx[df_tx['cohort'] == cohort]
        
        # Unique investors in this cohort
        num_investors = cohort_tx['investor_id'].nunique()
        
        # Total invested (SIP + Lumpsum purchases)
        purchases = cohort_tx[cohort_tx['transaction_type'].isin(['SIP', 'Lumpsum'])]
        total_invested = purchases['amount_inr'].sum()
        
        # Avg SIP amount
        sip_tx = cohort_tx[cohort_tx['transaction_type'] == 'SIP']
        avg_sip_amount = sip_tx['amount_inr'].mean() if len(sip_tx) > 0 else 0
        
        # Top fund preference (by total transaction amount)
        fund_volume = cohort_tx.groupby('amfi_code')['amount_inr'].sum().reset_index()
        if len(fund_volume) > 0:
            top_fund_code = fund_volume.sort_values('amount_inr', ascending=False).iloc[0]['amfi_code']
            top_fund_name = df_funds[df_funds['amfi_code'] == top_fund_code].iloc[0]['scheme_name']
        else:
            top_fund_name = "None"
            
        cohort_results.append({
            'cohort_year': cohort,
            'unique_investors': num_investors,
            'total_invested_inr': total_invested,
            'avg_sip_amount_inr': avg_sip_amount,
            'top_fund_preference': top_fund_name
        })
        
    df_cohort_report = pd.DataFrame(cohort_results)
    df_cohort_report.to_csv(project_root / "data" / "processed" / "investor_cohort_analysis.csv", index=False)
    print("Investor cohort analysis complete.")
    print(df_cohort_report)
    return df_cohort_report

def compute_sip_continuity():
    """Performs SIP continuity analysis (gaps between transactions)."""
    print("Performing SIP continuity analysis...")
    conn = get_db_connection()
    df_tx = pd.read_sql("SELECT investor_id, transaction_date, transaction_type, amount_inr FROM fact_transactions WHERE transaction_type = 'SIP'", conn)
    conn.close()
    
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    
    # Filter investors with 6+ SIP transactions
    sip_counts = df_tx['investor_id'].value_counts()
    keep_investors = sip_counts[sip_counts >= 6].index
    df_filtered = df_tx[df_tx['investor_id'].isin(keep_investors)].copy()
    
    # Calculate gaps
    df_filtered = df_filtered.sort_values(['investor_id', 'transaction_date'])
    df_filtered['prev_date'] = df_filtered.groupby('investor_id')['transaction_date'].shift(1)
    df_filtered['gap_days'] = (df_filtered['transaction_date'] - df_filtered['prev_date']).dt.days
    
    # Avg gap per investor
    investor_gaps = df_filtered.groupby('investor_id')['gap_days'].mean().reset_index()
    investor_gaps = investor_gaps.rename(columns={'gap_days': 'avg_gap_days'})
    
    # Flag investors with avg gap > 35 days as "at-risk"
    investor_gaps['status'] = np.where(investor_gaps['avg_gap_days'] > 35, 'at-risk', 'active')
    
    # Save detailed gap analysis
    investor_gaps.to_csv(project_root / "data" / "processed" / "sip_continuity_analysis.csv", index=False)
    
    at_risk_count = (investor_gaps['status'] == 'at-risk').sum()
    total_investors = len(investor_gaps)
    at_risk_pct = (at_risk_count / total_investors) * 100 if total_investors > 0 else 0
    
    print(f"SIP Continuity Summary:")
    print(f"  Total investors analyzed (6+ SIPs): {total_investors}")
    print(f"  At-risk investors (avg gap > 35 days): {at_risk_count} ({at_risk_pct:.2f}%)")
    return investor_gaps

def compute_sector_hhi():
    """Computes Herfindahl-Hirschman Index (HHI) for all equity funds."""
    print("Computing Herfindahl-Hirschman Index for all equity funds...")
    conn = get_db_connection()
    df_holdings = pd.read_sql("SELECT amfi_code, weight_pct, sector FROM portfolio_holdings", conn)
    df_funds = pd.read_sql("SELECT amfi_code, scheme_name, category FROM dim_fund", conn)
    conn.close()
    
    # Filter equity funds
    df_equity_funds = df_funds[df_funds['category'] == 'Equity']
    equity_amfi = df_equity_funds['amfi_code'].unique()
    
    hhi_results = []
    for amfi in equity_amfi:
        fund_holdings = df_holdings[df_holdings['amfi_code'] == amfi]
        if len(fund_holdings) == 0:
            continue
            
        # Sector weights sum
        sector_weights = fund_holdings.groupby('sector')['weight_pct'].sum()
        
        # Herfindahl-Hirschman Index = sum(w_i ^ 2)
        hhi = np.sum(sector_weights ** 2)
        
        # Classification
        # High concentration > 2500, Moderate 1500-2500, Low < 1500
        if hhi > 2500:
            concentration = "High Concentration"
        elif hhi >= 1500:
            concentration = "Moderate Concentration"
        else:
            concentration = "Low Concentration"
            
        hhi_results.append({
            'amfi_code': amfi,
            'sector_hhi': hhi,
            'concentration_level': concentration,
            'num_sectors_held': len(sector_weights)
        })
        
    df_hhi = pd.DataFrame(hhi_results)
    df_hhi_report = pd.merge(df_equity_funds[['amfi_code', 'scheme_name']], df_hhi, on='amfi_code')
    df_hhi_report = df_hhi_report.sort_values('sector_hhi', ascending=False)
    
    df_hhi_report.to_csv(project_root / "data" / "processed" / "sector_hhi_concentration.csv", index=False)
    print("Sector HHI Concentration complete.")
    print(df_hhi_report.head(5))
    return df_hhi_report

def main():
    print("=== Bluestock Mutual Fund Analytics Calculations ===")
    compute_var_cvar()
    compute_rolling_sharpe()
    compute_investor_cohorts()
    compute_sip_continuity()
    compute_sector_hhi()
    print("All quantitative metrics calculated and saved successfully.")

if __name__ == '__main__':
    main()
