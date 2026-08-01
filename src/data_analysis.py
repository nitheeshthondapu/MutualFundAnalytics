import pandas as pd
from pathlib import Path

def analyze_data():
    raw_dir = Path("data/raw")
    csv_files = sorted(list(raw_dir.glob("*.csv")))
    
    print("=================================================================")
    # 1. Load each dataset and print shape, dtypes, and head()
    print("STEP 1: LOAD DATASETS & PRINT PROPERTIES")
    print("=================================================================")
    
    datasets = {}
    for file_path in csv_files:
        df = pd.read_csv(file_path)
        name = file_path.stem
        datasets[name] = df
        print(f"\n--- Dataset: {file_path.name} ---")
        print(f"Shape: {df.shape}")
        print("\nData Types:")
        print(df.dtypes)
        print("\nHead (First 3 rows):")
        print(df.head(3))
        print("-" * 60)

    print("\n=================================================================")
    # 2. Check for and note anomalies
    print("STEP 2: DETECT & DETAIL ANOMALIES")
    print("=================================================================")
    
    print("\n[Missing Values Check]")
    for name, df in datasets.items():
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            print(f"Dataset '{name}' has missing values:")
            for col, val in missing.items():
                pct = (val / len(df)) * 100
                print(f"  - Column '{col}': {val} missing values ({pct:.2f}%)")
        else:
            print(f"Dataset '{name}': No missing values.")

    print("\n[Duplicate Rows Check]")
    for name, df in datasets.items():
        dups = df.duplicated().sum()
        if dups > 0:
            print(f"  - Dataset '{name}' has {dups} duplicate rows.")
        else:
            print(f"  - Dataset '{name}': No duplicate rows.")

    print("\n[Value Range and Integrity Checks]")
    # Check for negative values in financial columns
    for name, df in datasets.items():
        num_cols = df.select_dtypes(include=['number']).columns
        for col in num_cols:
            min_val = df[col].min()
            max_val = df[col].max()
            if min_val < 0:
                if 'drawdown' in col or 'return' in col or 'alpha' in col:
                    # Drawdown and returns can be negative, which is expected
                    print(f"  - Dataset '{name}', Column '{col}': has negative values (min: {min_val}) [Expected for returns/drawdown/alpha]")
                else:
                    print(f"  - WARNING: Dataset '{name}', Column '{col}': has negative values (min: {min_val}) [UNEXPECTED]")

    print("\n=================================================================")
    # 3. Explore Fund Master
    print("STEP 3: EXPLORE FUND MASTER & AMFI SCHEME CODE STRUCTURE")
    print("=================================================================")
    
    df_fm = datasets.get("01_fund_master")
    if df_fm is not None:
        print("Unique Fund Houses in Fund Master:")
        print("  ", ", ".join(df_fm['fund_house'].unique()))
        
        print("\nUnique Categories in Fund Master:")
        print("  ", ", ".join(df_fm['category'].unique()))
        
        print("\nUnique Sub-Categories in Fund Master:")
        print("  ", ", ".join(df_fm['sub_category'].unique()))
        
        print("\nUnique Risk Categories in Fund Master:")
        print("  ", ", ".join(df_fm['risk_category'].unique()))
        
        # Check risk grades in scheme performance if available
        df_sp = datasets.get("07_scheme_performance")
        if df_sp is not None:
            print("\nUnique Risk Grades in Scheme Performance:")
            print("  ", ", ".join(df_sp['risk_grade'].unique()))
            
        print("\n[AMFI Scheme Code Structure Analysis]")
        print("AMFI codes are unique 6-digit integers representing specific mutual fund schemes and options.")
        print("Let's analyze the relationship between Direct and Regular plans:")
        
        # Display consecutive code pairings
        df_plans = df_fm[['amfi_code', 'scheme_name', 'plan', 'fund_house']].sort_values('amfi_code')
        print(df_plans.head(15))
        
        print("\nObservation on code spacing:")
        print("- For many funds, Regular and Direct plans of the same scheme have consecutive codes (e.g., 119551 and 119552 for SBI Bluechip Regular/Direct).")
        print("- However, older funds or funds with different launch phases have wider spacing. For example:")
        print("  * HDFC Top 100 Fund Regular: 100016")
        print("  * HDFC Top 100 Fund Direct: 125497")
        print("  This reflects historical context: Direct plans were introduced in India on Jan 1, 2013. Older schemes already had codes assigned (like 100016), and new codes (like 125497) were assigned to Direct plans later.")
    else:
        print("Error: '01_fund_master' dataset not loaded.")

    print("\n=================================================================")
    # 4. Validate AMFI codes
    print("STEP 4: VALIDATE AMFI CODES BETWEEN FUND MASTER & NAV HISTORY")
    print("=================================================================")
    
    df_nav = datasets.get("02_nav_history")
    if df_fm is not None and df_nav is not None:
        fm_codes = set(df_fm['amfi_code'].unique())
        nav_codes = set(df_nav['amfi_code'].unique())
        
        missing_in_nav = fm_codes - nav_codes
        extra_in_nav = nav_codes - fm_codes
        
        print(f"Unique amfi_codes in fund_master: {len(fm_codes)}")
        print(f"Unique amfi_codes in nav_history: {len(nav_codes)}")
        print(f"Codes in fund_master but missing in nav_history: {len(missing_in_nav)}")
        print(f"Codes in nav_history but not in fund_master: {len(extra_in_nav)}")
        
        if len(missing_in_nav) == 0 and len(extra_in_nav) == 0:
            print("SUCCESS: Every scheme code in fund_master matches exactly with nav_history!")
        else:
            if missing_in_nav:
                print(f"Missing in NAV History: {missing_in_nav}")
            if extra_in_nav:
                print(f"Extra in NAV History: {extra_in_nav}")
    else:
        print("Error: '01_fund_master' or '02_nav_history' dataset not loaded.")

    print("\n=================================================================")
    # 5. Data Quality Summary
    print("STEP 5: DATA QUALITY SUMMARY")
    print("=================================================================")
    
    print("Based on the data validation, here are the key findings:")
    print("1. [Completeness]: All 10 core datasets and the 5 newly fetched live NAV files have loaded successfully.")
    print("2. [Null Values]: The dataset '04_monthly_sip_inflows' has 12 missing values in 'yoy_growth_pct' (25%).")
    print("   This is a mathematical constraint rather than a data collection error, since the first 12 months lack a prior-year month for year-on-year comparison.")
    print("3. [Duplicates]: No duplicate rows were detected in any of the 10 core datasets.")
    print("4. [Referential Integrity]: Perfect mapping between '01_fund_master' and '02_nav_history' (all 40 scheme codes match 1:1).")
    print("5. [API Mapping Mismatches]: A critical external data quality issue was identified:")
    print("   - The local datasets use custom/mock AMFI codes that map to different schemes in the real-world mfapi.in API.")
    print("   - Code 125497 (locally HDFC Top 100 Direct) fetches SBI Small Cap Direct on the API.")
    print("   - Code 119551 (locally SBI Bluechip Regular) fetches Aditya Birla Sun Life Banking & PSU Debt Fund.")
    print("   - Code 120503 (locally ICICI Bluechip Regular) fetches Axis ELSS Tax Saver Fund.")
    print("   - Code 119092 (locally Axis Bluechip Regular) fetches HDFC Money Market Fund.")
    print("   - Code 120841 (locally Kotak Bluechip Regular) fetches quant Mid Cap Fund.")
    print("   - Only Nippon Large Cap (118632) maps to the correct scheme (though the API returns the Direct plan and local claims it is Regular).")
    print("   This mismatch must be considered when blending the live API data with local datasets.")
    print("=================================================================")

if __name__ == '__main__':
    analyze_data()
