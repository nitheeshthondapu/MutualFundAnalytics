"""
Schedule ETL Script for Bluestock Mutual Fund Analytics.
This script sets up a scheduled task to run the ETL pipeline every weekday at 8 PM.
- On Windows: Uses Task Scheduler (schtasks.exe).
- On Linux/macOS: Uses crontab.
Usage:
  python scripts/schedule_etl.py
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def schedule_windows():
    """Schedules a Windows Task Scheduler job."""
    task_name = "BluestockMF_ETL"
    python_exe = sys.executable
    script_path = project_root / "scripts" / "etl_pipeline.py"
    
    # Absolute paths are required for Task Scheduler
    abs_script = script_path.resolve()
    abs_python = Path(python_exe).resolve()
    
    # Command to run: python.exe etl_pipeline.py
    # Execute starting at the project root directory
    command_to_run = f'cmd.exe /c "cd /d {project_root.resolve()} && \\"{abs_python}\\" \\"{abs_script}\\""'
    
    # schtasks command to create a weekly task on weekdays (Mon-Fri) at 20:00 (8 PM)
    # /sc weekly: weekly trigger
    # /d MON,TUE,WED,THU,FRI: weekdays
    # /st 20:00: start time 8:00 PM
    # /f: force overwrite if exists
    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", command_to_run,
        "/sc", "weekly",
        "/d", "MON,TUE,WED,THU,FRI",
        "/st", "20:00",
        "/f"
    ]
    
    print(f"Registering Windows Task: {task_name}...")
    print(f"Target Command: {command_to_run}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Success! Task Scheduler output:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Error: Failed to register Windows Task.")
        print("Error details:")
        print(e.stderr)
        print("\nNote: Please run the terminal as Administrator to grant permission for Task Scheduler scheduling.")
        return False

def schedule_unix():
    """Schedules a cron job on Unix-like operating systems."""
    python_exe = sys.executable
    script_path = (project_root / "scripts" / "etl_pipeline.py").resolve()
    
    # Cron expression: 0 20 * * 1-5 (8 PM, Mon-Fri)
    cron_command = f"0 20 * * 1-5 cd {project_root.resolve()} && {python_exe} {script_path} >> {project_root.resolve()}/etl_cron.log 2>&1"
    
    print("Setting up Unix Cron Job...")
    try:
        # Get existing crontab
        current_cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    except Exception:
        current_cron = ""
        
    # Check if task already scheduled
    if str(script_path) in current_cron:
        print("Cron job for etl_pipeline.py is already scheduled in crontab.")
        return True
        
    # Add new cron job
    new_cron = current_cron.rstrip() + "\n" + cron_command + "\n"
    
    # Write back to crontab
    try:
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=new_cron)
        if proc.returncode == 0:
            print("Success! Cron job scheduled successfully.")
            print(f"Added to crontab: {cron_command}")
            return True
        else:
            print("Failed to schedule cron job.")
            print(stderr)
            return False
    except Exception as e:
        print(f"Error scheduling cron job: {e}")
        return False

def main():
    print("=== Bluestock Mutual Fund ETL Scheduler ===")
    os_name = platform.system()
    if os_name == "Windows":
        schedule_windows()
    elif os_name in ["Linux", "Darwin"]:
        schedule_unix()
    else:
        print(f"Unsupported OS: {os_name}. Please configure manual scheduler.")

if __name__ == '__main__':
    main()
