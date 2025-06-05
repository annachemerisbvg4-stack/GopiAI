#!/usr/bin/env python
"""
Script to clean up __pycache__ directories in the project.
This helps reduce clutter and potential issues with stale cache files.
"""

import os
import shutil
from pathlib import Path

def cleanup_pycache(root_dir):
    """
    Recursively find and remove all __pycache__ directories.
    
    Args:
        root_dir (str): Path to the root directory to clean
    """
    root_path = Path(root_dir)
    removed_count = 0
    
    # Find all __pycache__ directories
    for pycache_dir in root_path.glob("**/__pycache__"):
        if pycache_dir.is_dir():
            # Remove the directory and all its contents
            shutil.rmtree(str(pycache_dir))
            removed_count += 1
            print(f"Removed: {pycache_dir}")
    
    # Find all .pyc files that might be outside __pycache__ directories
    for pyc_file in root_path.glob("**/*.pyc"):
        if pyc_file.is_file():
            pyc_file.unlink()
            removed_count += 1
            print(f"Removed: {pyc_file}")
    
    print(f"Cache cleanup complete. Removed {removed_count} cache directories and files.")

if __name__ == "__main__":
    # Path to project root
    project_root = Path(__file__).parent.parent
    
    # Clean up Python cache
    cleanup_pycache(project_root)
