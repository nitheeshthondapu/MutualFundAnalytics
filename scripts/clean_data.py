import os
import logging
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_nav_history(raw_path: Path, processed_path: Path):
    """
    Clean nav_history.csv (02_nav_history.csv):
    - parse dates to datetime
    - sort by amfi_code + date
    - forward-fill missing NAV for holidays/weekends
    - remove duplicates
    - validate NAV > 0
    """
    logger.info("Cleaning 02_nav_history.csv...")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # 1. Parse date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Validate NAV > 0 (drop invalid rows)
    invalid_nav = df[df['nav'] <= 0]
    if len(invalid_nav) > 0:
        logger.warning(f"Found {len(invalid_nav)} rows with NAV <= 0. Dropping them.")
        df = df[df['nav'] > 0]
        
    # 3. Remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # 4. Sort and Forward-fill missing NAV for holidays/weekends per scheme
    cleaned_groups = []
    for amfi_code, group in df.groupby('amfi_code'):
        # Sort group by date
        group = group.sort_values('date')
        
        # Determine full date range from min to max date for this scheme
        min_date = group['date'].min()
        max_date = group['date'].max()
        full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Set date as index and reindex
        group = group.set_index('date')
        group_reindexed = group.reindex(full_date_range)
        
        # Fill amfi_code and forward-fill NAV
        group_reindexed['amfi_code'] = amfi_code
        group_reindexed['nav'] = group_reindexed['nav'].ffill()
        
        # Reset index and rename index column back to date
        group_cleaned = group_reindexed.reset_index().rename(columns={'index': 'date'})
        cleaned_groups.append(group_cleaned)
        
    df_clean = pd.concat(cleaned_groups).sort_values(['amfi_code', 'date']).reset_index(drop=True)
    
    # Format date back to string YYYY-MM-DD
    df_clean['date'] = df_clean['date'].dt.strftime('%Y-%m-%d')
    
    logger.info(f"02_nav_history cleaned: shape changed from {initial_rows} to {len(df_clean)} rows.")
    df_clean.to_csv(processed_path, index=False)

def clean_investor_transactions(raw_path: Path, processed_path: Path):
    """
    Clean investor_transactions.csv (08_investor_transactions.csv):
    - standardise transaction_type values (SIP/Lumpsum/Redemption)
    - validate amount > 0
    - fix date formats
    - check KYC status enum values
    """
    logger.info("Cleaning 08_investor_transactions.csv...")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # 1. Fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
    
    # 2. Standardise transaction_type values
    # Standard values: 'SIP', 'Lumpsum', 'Redemption'
    df['transaction_type'] = df['transaction_type'].astype(str).str.strip()
    type_mapping = {
        'sip': 'SIP',
        'sip ': 'SIP',
        'lumpsum': 'Lumpsum',
        'lumpsum ': 'Lumpsum',
        'redemption': 'Redemption',
        'redemption ': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].replace(type_mapping)
    # Casing map for title case/upper case
    df['transaction_type'] = df['transaction_type'].apply(lambda x: 'SIP' if x.upper() == 'SIP' else x.title())
    
    # 3. Validate amount > 0
    invalid_amount = df[df['amount_inr'] <= 0]
    if len(invalid_amount) > 0:
        logger.warning(f"Found {len(invalid_amount)} rows with amount_inr <= 0. Dropping them.")
        df = df[df['amount_inr'] > 0]
        
    # 4. Check KYC status enum values (Verified, Pending)
    df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.capitalize()
    invalid_kyc = df[~df['kyc_status'].isin(['Verified', 'Pending'])]
    if len(invalid_kyc) > 0:
        logger.warning(f"Found {len(invalid_kyc)} rows with invalid KYC status. Defaulting to 'Pending'.")
        df.loc[~df['kyc_status'].isin(['Verified', 'Pending']), 'kyc_status'] = 'Pending'
        
    logger.info(f"08_investor_transactions cleaned: shape changed from {initial_rows} to {len(df)} rows.")
    df.to_csv(processed_path, index=False)

def clean_scheme_performance(raw_path: Path, processed_path: Path):
    """
    Clean scheme_performance.csv (07_scheme_performance.csv):
    - validate all return values are numeric
    - flag anomalies
    - check expense_ratio range (0.1% – 2.5%)
    """
    logger.info("Cleaning 07_scheme_performance.csv...")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # 1. Validate all return values are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # If there are any nulls created, log them and fill with 0 or mean
        null_count = df[col].isnull().sum()
        if null_count > 0:
            logger.warning(f"Column {col} has {null_count} non-numeric values. Coercing and filling with 0.0.")
            df[col] = df[col].fillna(0.0)
            
    # 2. Check expense_ratio range (0.1% – 2.5%)
    df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
    out_of_range = df[(df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5)]
    if len(out_of_range) > 0:
        logger.warning(f"Found {len(out_of_range)} rows with expense ratio outside [0.1%, 2.5%]:\n{out_of_range[['amfi_code', 'scheme_name', 'expense_ratio_pct']]}")
        
    # 3. Flag anomalies (add is_anomalous flag column)
    # Anomalies include:
    # - Sharpe ratio > 3.0 or < -3.0 (Liquid funds are mathematical anomalies because of extremely low std dev)
    # - Sortino ratio > 4.0 or < -4.0
    # - Max drawdown > 0 (drawdown should always be negative)
    df['is_anomalous'] = 0
    df.loc[
        (df['sharpe_ratio'] > 3.0) | (df['sharpe_ratio'] < -3.0) |
        (df['sortino_ratio'] > 4.0) | (df['sortino_ratio'] < -4.0) |
        (df['max_drawdown_pct'] > 0),
        'is_anomalous'
    ] = 1
    
    anomaly_count = df['is_anomalous'].sum()
    logger.info(f"Flagged {anomaly_count} schemes as anomalous (typically Liquid funds due to low volatility).")
    
    logger.info(f"07_scheme_performance cleaned: shape {df.shape}")
    df.to_csv(processed_path, index=False)

def clean_general_file(raw_path: Path, processed_path: Path, date_cols=None):
    """
    Standard copy and date-formatting for general files.
    """
    logger.info(f"Processing {raw_path.name}...")
    df = pd.read_csv(raw_path)
    
    if date_cols:
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                
    df.to_csv(processed_path, index=False)
    logger.info(f"Successfully processed {raw_path.name} ({len(df)} rows).")

def main():
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Clean nav_history
    clean_nav_history(raw_dir / "02_nav_history.csv", processed_dir / "02_nav_history.csv")
    
    # 2. Clean investor_transactions
    clean_investor_transactions(raw_dir / "08_investor_transactions.csv", processed_dir / "08_investor_transactions.csv")
    
    # 3. Clean scheme_performance
    clean_scheme_performance(raw_dir / "07_scheme_performance.csv", processed_dir / "07_scheme_performance.csv")
    
    # 4. Process the other files
    clean_general_file(raw_dir / "01_fund_master.csv", processed_dir / "01_fund_master.csv", date_cols=['launch_date'])
    clean_general_file(raw_dir / "03_aum_by_fund_house.csv", processed_dir / "03_aum_by_fund_house.csv", date_cols=['date'])
    
    # monthly_sip_inflows (monthly format e.g. 2022-01, keep as string)
    clean_general_file(raw_dir / "04_monthly_sip_inflows.csv", processed_dir / "04_monthly_sip_inflows.csv")
    
    # category_inflows
    clean_general_file(raw_dir / "05_category_inflows.csv", processed_dir / "05_category_inflows.csv")
    
    # industry_folio_count
    clean_general_file(raw_dir / "06_industry_folio_count.csv", processed_dir / "06_industry_folio_count.csv")
    
    # portfolio_holdings
    clean_general_file(raw_dir / "09_portfolio_holdings.csv", processed_dir / "09_portfolio_holdings.csv", date_cols=['portfolio_date'])
    
    # benchmark_indices
    clean_general_file(raw_dir / "10_benchmark_indices.csv", processed_dir / "10_benchmark_indices.csv", date_cols=['date'])
    
    logger.info("All 10 CSV datasets successfully cleaned and saved to data/processed/.")

if __name__ == '__main__':
    main()
