import os
import logging
from pathlib import Path
import pandas as pd
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.live_nav_fetch import fetch_and_save_nav

def load_raw_data(data_dir: str | Path = 'data/raw') -> dict[str, pd.DataFrame]:
    """
    Reads all CSV files from the specified raw data directory and loads them into Pandas DataFrames.

    Args:
        data_dir (str or Path): Path to the directory containing raw CSV files.

    Returns:
        dict[str, pd.DataFrame]: A dictionary mapping CSV filenames (without extension) 
                                 to their corresponding Pandas DataFrames.
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.warning(f"Data directory '{data_path}' does not exist. Creating it.")
        data_path.mkdir(parents=True, exist_ok=True)
        return {}

    csv_files = list(data_path.glob("*.csv"))
    
    if not csv_files:
        logger.warning(f"No CSV files found in directory: {data_path.absolute()}")
        return {}

    dataframes = {}
    
    for file_path in csv_files:
        try:
            logger.info(f"Ingesting {file_path.name}...")
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Use the stem (filename without extension) as the dictionary key
            key = file_path.stem
            dataframes[key] = df
            
            logger.info(f"Successfully loaded '{key}' with {df.shape[0]} rows and {df.shape[1]} columns.")
        except Exception as e:
            logger.error(f"Error reading CSV file '{file_path.name}': {e}")
            
    return dataframes

if __name__ == '__main__':
    # Find the project root relative to this script location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_data_dir = project_root / 'data' / 'raw'
    
    logger.info("Starting live NAV fetching from API...")
    # The 6 key schemes specified by the user (including HDFC Top 100: 125497)
    key_schemes = [125497, 119551, 120503, 118632, 119092, 120841]
    
    success_count = 0
    for code in key_schemes:
        if fetch_and_save_nav(code, raw_data_dir):
            success_count += 1
            
    logger.info(f"Completed fetching live NAVs. Successfully fetched {success_count}/{len(key_schemes)} schemes.")
    
    logger.info("Starting data ingestion process...")
    dfs = load_raw_data(raw_data_dir)
    
    if dfs:
        logger.info(f"Ingestion complete. Loaded {len(dfs)} datasets.")
        for name, df in dfs.items():
            print(f"\n=========================================")
            print(f"Dataset: {name}")
            print(f"=========================================")
            print("Shape:")
            print(df.shape)
            print("\nData Types:")
            print(df.dtypes)
            print("\nHead (Sample Records):")
            print(df.head())
    else:
        logger.info("No datasets loaded. Please add CSV files to data/raw/ to begin.")



