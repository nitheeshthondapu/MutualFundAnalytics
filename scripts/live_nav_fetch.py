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

def fetch_and_save_nav(scheme_code: int, output_dir: str | Path = 'data/raw') -> bool:
    """
    Fetches live NAV data for a mutual fund scheme from mfapi.in, 
    parses it, formats the date to YYYY-MM-DD, and saves it as a CSV.

    Args:
        scheme_code (int): AMFI code of the mutual fund scheme.
        output_dir (str or Path): Path to the directory where the CSV should be saved.

    Returns:
        bool: True if fetch and save were successful, False otherwise.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / f"{scheme_code}_nav.csv"
    
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        logger.info(f"Fetching NAV data for scheme {scheme_code} from API...")
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch scheme {scheme_code}. HTTP Status: {response.status_code}")
            return False
            
        json_data = response.json()
        nav_list = json_data.get("data", [])
        meta = json_data.get("meta", {})
        
        if not nav_list:
            logger.warning(f"No NAV data found in the response for scheme {scheme_code}.")
            return False
            
        # Convert to DataFrame
        df = pd.DataFrame(nav_list)
        
        # Standardize date format: DD-MM-YYYY to YYYY-MM-DD
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')
        
        # Add scheme_code for context
        df.insert(0, 'amfi_code', scheme_code)
        
        # Reorder and keep relevant columns
        df = df[['amfi_code', 'date', 'nav']]
        
        # Save as CSV
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully saved NAV data for {meta.get('scheme_name')} (Code: {scheme_code}) to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error fetching/saving NAV for scheme {scheme_code}: {e}")
        return False

if __name__ == '__main__':
    # Find project root and raw data directory
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    raw_data_dir = project_root / 'data' / 'raw'
    
    logger.info("Executing standalone live NAV fetching process...")
    # The 6 key schemes specified by the user (including HDFC Top 100: 125497)
    key_schemes = [125497, 119551, 120503, 118632, 119092, 120841]
    
    success_count = 0
    for code in key_schemes:
        if fetch_and_save_nav(code, raw_data_dir):
            success_count += 1
            
    logger.info(f"Standalone live NAV fetch completed. Successfully fetched {success_count}/{len(key_schemes)} schemes.")
