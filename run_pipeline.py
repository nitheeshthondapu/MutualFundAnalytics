"""
Master Execution Pipeline for Bluestock Mutual Fund Analytics.
This script orchestrates the entire pipeline:
1. Ingestion, Cleaning, and Star Schema Database Loading (etl_pipeline.py)
2. Quantitative and Risk Metrics Calculation (compute_metrics.py)
3. Dashboard Screenshot and PBIX Template Generation (generate_dashboard_assets.py)
4. PDF Report and PPTX Slide Deck compilation (generate_pdf_pptx.py)
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def run_script(script_name: str):
    """Helper to execute python scripts within the scripts directory."""
    script_path = project_root / "scripts" / script_name
    logger.info(f"Executing script: {script_name}...")
    try:
        # Run python process using current python executable
        subprocess.run([sys.executable, str(script_path)], check=True)
        logger.info(f"Successfully completed: {script_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing {script_name}: {e}")
        sys.exit(1)

def main():
    logger.info("=================================================================")
    logger.info("STARTING BLUESTOCK MUTUAL FUND ANALYTICS MASTER PIPELINE")
    logger.info("=================================================================")

    # 1. Run Ingestion, Cleaning, and DB Load
    run_script("etl_pipeline.py")
    
    # 2. Compute Performance and Risk Metrics
    run_script("compute_metrics.py")
    
    # 3. Generate Dashboard Assets (PNGs, PDF, and PBIX)
    run_script("generate_dashboard_assets.py")
    
    # 4. Generate PDF Report and Presentation Deck
    run_script("generate_pdf_pptx.py")
    
    logger.info("=================================================================")
    logger.info("MASTER PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("All raw CSVs cleaned and loaded to data/db/bluestock_mf.db.")
    logger.info("All CSV reports, charts, and dashboards generated.")
    logger.info("Final Report and Slides saved in reports/ directory.")
    logger.info("=================================================================")

if __name__ == '__main__':
    main()
