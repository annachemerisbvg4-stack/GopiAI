#!/usr/bin/env python
"""
Script to clean up log files in the logs directory.
Keeps the most recent logs and archives or removes older ones.
"""

import os
import shutil
import datetime
from pathlib import Path

def cleanup_logs(logs_dir, max_recent_logs=10, archive=True):
    """
    Clean up log files by keeping only the most recent ones.
    
    Args:
        logs_dir (str): Path to the logs directory
        max_recent_logs (int): Maximum number of recent logs to keep
        archive (bool): Whether to archive old logs instead of deleting them
    """
    # Ensure logs directory exists
    logs_path = Path(logs_dir)
    if not logs_path.exists() or not logs_path.is_dir():
        print(f"Logs directory {logs_dir} does not exist or is not a directory")
        return
    
    # Create archives directory if needed
    if archive:
        archive_path = logs_path / "archived"
        archive_path.mkdir(exist_ok=True)
    
    # Get all log files and sort by modification time (newest first)
    log_files = list(logs_path.glob("*.log"))
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Keep the most recent logs, archive or delete the rest
    if len(log_files) > max_recent_logs:
        for log_file in log_files[max_recent_logs:]:
            if archive:
                # Move to archive folder
                shutil.move(str(log_file), str(archive_path / log_file.name))
                print(f"Archived {log_file.name}")
            else:
                # Delete the log file
                log_file.unlink()
                print(f"Deleted {log_file.name}")
    
    print(f"Log cleanup complete. Kept {min(max_recent_logs, len(log_files))} most recent logs.")

if __name__ == "__main__":
    # Path to logs directory relative to project root
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    
    # Clean up logs, keeping 10 most recent and archiving the rest
    cleanup_logs(logs_dir, max_recent_logs=10, archive=True)
