import os
import json
import argparse
import time
import requests
import pandas as pd
from datetime import datetime

DEFAULT_SCHEMES = {
   
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip"
}

def fetch_scheme_data(scheme_code, force_redownload=False):
    """
    Fetches raw mutual fund scheme JSON data from mfapi.in API and caches it locally.
    """
    json_dir = os.path.join("data", "raw", "json")
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, f"{scheme_code}.json")
    
    if os.path.exists(json_path) and not force_redownload:
        print(f"Loading scheme {scheme_code} from local cache...")
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching scheme {scheme_code} from API...")
    
    retries = 3
    backoff = 1.5
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if data and data.get("status") == "SUCCESS":
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    return data
                else:
                    print(f"API returned status {data.get('status')} for scheme {scheme_code}.")
            else:
                print(f"HTTP error {response.status_code} for scheme {scheme_code}.")
        except Exception as e:
            print(f"Error fetching scheme {scheme_code}: {e}")
        
        if attempt < retries - 1:
            wait_time = backoff ** attempt
            print(f"Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            
    raise RuntimeError(f"Failed to fetch data for scheme {scheme_code}")

def parse_and_clean_data(raw_data):
    """
    Parses the raw scheme response and returns a cleaned DataFrame.
    """
    meta = raw_data.get("meta", {})
    raw_nav_list = raw_data.get("data", [])
    
    scheme_code = meta.get("scheme_code")
    scheme_name = meta.get("scheme_name")
    fund_house = meta.get("fund_house")
    scheme_category = meta.get("scheme_category")
    
    df = pd.DataFrame(raw_nav_list)
    if df.empty:
        return pd.DataFrame()
        
    # Convert 'date' to YYYY-MM-DD
    # Input format from API: DD-MM-YYYY
    df["Date"] = pd.to_datetime(df["date"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")
    df["NAV"] = pd.to_numeric(df["nav"], errors="coerce")
    
    # Drop intermediate columns
    df = df.drop(columns=["date", "nav"])
    
    # Add metadata columns
    df["Scheme_Code"] = scheme_code
    df["Scheme_Name"] = scheme_name
    df["Fund_House"] = fund_house
    df["Scheme_Category"] = scheme_category
    
    # Sort chronologically
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Reorder columns
    cols = ["Date", "Scheme_Code", "Scheme_Name", "NAV", "Fund_House", "Scheme_Category"]
    df = df[cols]
    
    return df

def run_ingestion(schemes=None, force=False):
    """
    Orchestrates downloading and parsing multiple schemes, exporting them to individual
    and combined CSV datasets.
    """
    if schemes is None:
        schemes = list(DEFAULT_SCHEMES.keys())
        
    print(f"Starting ingestion for {len(schemes)} mutual fund schemes...")
    
    csv_dir = os.path.join("data", "raw", "csv")
    os.makedirs(csv_dir, exist_ok=True)
    
    all_dfs = []
    
    for code in schemes:
        try:
            raw_data = fetch_scheme_data(code, force_redownload=force)
            df = parse_and_clean_data(raw_data)
            
            if not df.empty:
                csv_path = os.path.join(csv_dir, f"{code}.csv")
                df.to_csv(csv_path, index=False)
                print(f"Saved cleaned data for {code} to {csv_path} ({len(df)} records)")
                all_dfs.append(df)
            else:
                print(f"No NAV records found for scheme {code}")
        except Exception as e:
            print(f"Skipping scheme {code} due to error: {e}")
            
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        # Sort combined data by Date and Scheme_Code
        combined_df = combined_df.sort_values(by=["Date", "Scheme_Code"]).reset_index(drop=True)
        
        combined_path = os.path.join("data", "raw", "combined_mutual_funds.csv")
        combined_df.to_csv(combined_path, index=False)
        print(f"\nSuccessfully created combined dataset at {combined_path} ({len(combined_df)} total records)")
    else:
        print("\nNo data was ingested successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mutual Fund Data Ingestion Pipeline")
    parser.add_argument("--schemes", nargs="+", help="AMFI Scheme Codes to ingest")
    parser.add_argument("--force", action="store_true", help="Force download even if cache JSON exists")
    args = parser.parse_args()
    
    run_ingestion(schemes=args.schemes, force=args.force)
