import os
import pandas as pd
import numpy as np

def explore_mutual_funds():
    csv_dir = os.path.join("data", "raw", "csv")
    if not os.path.exists(csv_dir):
        print(f"Error: Directory {csv_dir} does not exist.")
        return

    csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]
    print(f"Found {len(csv_files)} CSV files in {csv_dir}.\n")

    # Mapping expected filenames/codes to expected names to report anomalies
    expected_mappings = {
        "125497": "HDFC Top 100 Direct",
        "119551": "SBI Bluechip",
        "120503": "ICICI Bluechip",
        "118632": "Nippon Large Cap",
        "119092": "Axis Bluechip",
        "120841": "Kotak Bluechip"
    }

    raw_dataframes = {}
    anomalies = []

    print("=" * 80)
    print("STEP 1: LOAD ALL CSV FILES & PRINT SHAPE, DTYPES, AND HEAD")
    print("=" * 80)

    for file_name in sorted(csv_files):
        path = os.path.join(csv_dir, file_name)
        scheme_code_str = os.path.splitext(file_name)[0]
        
        try:
            df = pd.read_csv(path)
            raw_dataframes[scheme_code_str] = df
            
            print(f"\nFile: {file_name}")
            print(f"Shape: {df.shape}")
            print(f"Columns & Dtypes:")
            for col, dtype in df.dtypes.items():
                print(f"  - {col}: {dtype}")
            print("Head (First 2 rows):")
            print(df.head(2).to_string(index=False))
            print("-" * 50)
            
            # Simple data quality checks for anomalies
            print(f"\n--- Data Quality Checks for {file_name} ---")
            print("Missing values:")
            print(df.isnull().sum())
            print("Duplicate rows:")
            print(df.duplicated().sum())

            # 1. Null values
            null_counts = df.isnull().sum()
            if null_counts.any():
                anomalies.append(f"File {file_name} has null values: {null_counts[null_counts > 0].to_dict()}")
                
            # 2. Date format and sorting
            try:
                pd.to_datetime(df["Date"], format="%Y-%m-%d")
                is_sorted = df["Date"].is_monotonic_increasing
                if not is_sorted:
                    anomalies.append(f"File {file_name} dates are not sorted chronologically.")
            except Exception as e:
                anomalies.append(f"File {file_name} Date column has invalid date format: {e}")
                
            # 3. Scheme name anomaly (code vs metadata)
            if scheme_code_str in expected_mappings:
                actual_name = df["Scheme_Name"].iloc[0] if not df.empty else "Empty"
                expected_name = expected_mappings[scheme_code_str]
                if expected_name.lower() not in actual_name.lower():
                    anomalies.append(
                        f"Scheme Code Mismatch: Code {scheme_code_str} expected '{expected_name}' "
                        f"but actual name is '{actual_name}'."
                    )
            
            # 4. Numeric NAV
            if not np.issubdtype(df["NAV"].dtype, np.number):
                anomalies.append(f"File {file_name} NAV column is not numeric.")
                
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            anomalies.append(f"Could not load file {file_name}: {e}")

    print("\n" + "=" * 80)
    print("STEP 2: EXPLORE FUND MASTER")
    print("=" * 80)

    # Building fund_master and nav_history
    master_records = []
    nav_history_records = []

    # Risk grade mapping based on categories/sub-categories
    def get_risk_grade(category, sub_category):
        cat = category.lower()
        sub = sub_category.lower()
        if "small cap" in sub or "mid cap" in sub:
            return "Very High"
        elif "large cap" in sub or "flexi cap" in sub or "elss" in sub or "fof" in cat or "gold" in sub:
            return "High"
        elif "money market" in sub or "banking" in sub or "psu" in sub or "income" in cat:
            return "Moderate"
        else:
            return "High" # Default high risk for equity/debt/hybrid generic

    for code, df in raw_dataframes.items():
        if df.empty:
            continue
            
        # Extract metadata from the first row
        first_row = df.iloc[0]
        scheme_code = int(code)
        scheme_name = first_row["Scheme_Name"]
        fund_house = first_row["Fund_House"]
        raw_category = first_row["Scheme_Category"]
        
        # Parse Category & Sub-Category
        if " - " in raw_category:
            category, sub_category = raw_category.split(" - ", 1)
        else:
            category = raw_category
            sub_category = "General"
            
        risk_grade = get_risk_grade(category, sub_category)
        
        master_records.append({
            "Scheme_Code": scheme_code,
            "Scheme_Name": scheme_name,
            "Fund_House": fund_house,
            "Category": category.strip(),
            "Sub_Category": sub_category.strip(),
            "Risk_Grade": risk_grade
        })
        
        # Extract NAV history records
        sub_df = df[["Date", "NAV"]].copy()
        sub_df["Scheme_Code"] = scheme_code
        nav_history_records.append(sub_df)

    fund_master = pd.DataFrame(master_records)
    nav_history = pd.concat(nav_history_records, ignore_index=True)

    print("\n--- FUND MASTER ---")
    print(fund_master.to_string(index=False))
    
    print("\n--- EXPLORE FUND MASTER UNIQUE VALUES ---")
    print(fund_master["Fund_House"].unique())
    print(fund_master["Category"].unique())
    print(fund_master["Sub_Category"].unique())
    print(fund_master["Risk_Grade"].unique())

    print("\n--- UNIQUE VALUES IN FUND MASTER ---")
    print(f"Unique Fund Houses ({len(fund_master['Fund_House'].unique())}):")
    for fh in sorted(fund_master["Fund_House"].unique()):
        print(f"  - {fh}")
        
    print(f"Unique Categories ({len(fund_master['Category'].unique())}):")
    for c in sorted(fund_master["Category"].unique()):
        print(f"  - {c}")
        
    print(f"Unique Sub-Categories ({len(fund_master['Sub_Category'].unique())}):")
    for sc in sorted(fund_master["Sub_Category"].unique()):
        print(f"  - {sc}")
        
    print(f"Unique Risk Grades ({len(fund_master['Risk_Grade'].unique())}):")
    for rg in sorted(fund_master["Risk_Grade"].unique()):
        print(f"  - {rg}")

    print("\n--- AMFI SCHEME CODE STRUCTURE ---")
    print("AMFI Scheme Codes are 5 to 6 digit unique sequential integer codes assigned by AMFI.")
    print("They act as primary keys to uniquely identify mutual fund schemes, options, and plans.")
    print(f"Min Scheme Code in dataset: {fund_master['Scheme_Code'].min()}")
    print(f"Max Scheme Code in dataset: {fund_master['Scheme_Code'].max()}")

    print("\n" + "=" * 80)
    print("STEP 3: VALIDATE AMFI CODES")
    print("=" * 80)

    # Check if every code in fund_master exists in nav_history
    master_codes = set(fund_master["Scheme_Code"])
    history_codes = set(nav_history["Scheme_Code"])

    missing_in_history = master_codes - history_codes
    missing_in_master = history_codes - master_codes

    print(f"Codes in fund_master: {len(master_codes)}")
    print(f"Codes in nav_history: {len(history_codes)}")

    validation_ok = True
    if len(missing_in_history) > 0:
        print(f"WARNING: Scheme codes in fund_master missing from nav_history: {missing_in_history}")
        validation_ok = False
    else:
        print("Success: Every scheme code in fund_master exists in nav_history.")

    if len(missing_in_master) > 0:
        print(f"WARNING: Scheme codes in nav_history missing from fund_master: {missing_in_master}")
        validation_ok = False

    # Check if there are any codes in nav_history with no NAV values
    null_nav_history = nav_history[nav_history["NAV"].isnull()]
    if not null_nav_history.empty:
        print(f"WARNING: Found {len(null_nav_history)} records in nav_history with null NAV values.")
        validation_ok = False
    else:
        print("Success: No null NAV values found in nav_history.")

    print("\n" + "=" * 80)
    print("STEP 4: DATA QUALITY SUMMARY")
    print("=" * 80)
    
    print(f"Total Mutual Fund Schemes Loaded: {len(fund_master)}")
    print(f"Total NAV History Records: {len(nav_history)}")
    print(f"NAV History Date Range: {nav_history['Date'].min()} to {nav_history['Date'].max()}")
    print(f"Validation Status: {'PASSED' if validation_ok else 'FAILED'}")
    
    print("\nIdentified Anomalies / Issues:")
    if anomalies:
        for idx, anomaly in enumerate(anomalies, 1):
            print(f"  {idx}. {anomaly}")
    else:
        print("  None detected.")

    # Write summaries to reports folder
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    dq_report_path = os.path.join(reports_dir, "data_quality_summary.txt")
    with open(dq_report_path, "w", encoding="utf-8") as f:
        f.write("DATA QUALITY SUMMARY\n")
        f.write("="*30 + "\n")
        f.write(f"Total Schemes: {len(fund_master)}\n")
        f.write(f"Total NAV Records: {len(nav_history)}\n")
        f.write(f"NAV Date Range: {nav_history['Date'].min()} to {nav_history['Date'].max()}\n")
        f.write(f"Validation Status: {'PASSED' if validation_ok else 'FAILED'}\n\n")
        f.write("Identified Anomalies:\n")
        for anomaly in anomalies:
            f.write(f"- {anomaly}\n")

    fund_master.to_csv(os.path.join(reports_dir, "fund_master.csv"), index=False)
    nav_history.to_csv(os.path.join(reports_dir, "nav_history.csv"), index=False)
    print(f"\nSaved fund_master.csv and nav_history.csv to {reports_dir}/")

if __name__ == "__main__":
    explore_mutual_funds()
