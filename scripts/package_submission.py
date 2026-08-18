"""
Package Submission Script for Bluestock Mutual Fund Analytics.
This script creates a clean zip file of the capstone project on the Desktop
excluding Git metadata, __pycache__ folders, and virtual environment folders.
The root folder inside the zip is named 'bluestock_mf_capstone' as required.
"""

import os
import zipfile
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    desktop = project_root.parent
    zip_path = desktop / "bluestock_mf_capstone.zip"
    
    print(f"Creating clean submission zip at: {zip_path}")
    
    exclude_dirs = {'__pycache__', '.venv', '.idea', '.vscode', '.agents', '.gemini', '.ipynb_checkpoints'}
    exclude_extensions = {'.pyc', '.pyo', '.db-journal'}
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in exclude_extensions:
                    continue
                    
                # Relative path from project root
                rel_path = file_path.relative_to(project_root)
                # Map the root folder name to 'bluestock_mf_capstone'
                archive_name = Path("bluestock_mf_capstone") / rel_path
                
                zipf.write(str(file_path), str(archive_name))
                
    print("Clean submission zip bluestock_mf_capstone.zip created successfully on Desktop!")

if __name__ == '__main__':
    main()
