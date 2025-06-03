#!/usr/bin/env python
"""
Script to analyze the project structure and generate a report.
Helps identify potential issues and opportunities for cleanup.
"""

import os
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

def get_file_size(file_path):
    """Get the size of a file in KB."""
    try:
        return os.path.getsize(file_path) / 1024
    except (FileNotFoundError, PermissionError):
        return 0

def get_file_age(file_path):
    """Get the age of a file in days."""
    try:
        mtime = os.path.getmtime(file_path)
        age_seconds = time.time() - mtime
        return age_seconds / (60 * 60 * 24)  # Convert to days
    except (FileNotFoundError, PermissionError):
        return 0

def analyze_project(root_dir):
    """
    Analyze the project structure and generate a report.
    
    Args:
        root_dir (str): Path to the root directory
    """
    root_path = Path(root_dir)
    
    # Stats to collect
    total_files = 0
    total_size_kb = 0
    file_extensions = Counter()
    large_files = []
    old_files = []
    empty_directories = []
    pycache_count = 0
    
    # Skip patterns
    skip_dirs = ["venv", ".git", ".idea", "__pycache__"]
    
    # Track directories and their files
    dir_contents = defaultdict(list)
    
    # Walk through the project
    for path in root_path.glob("**/*"):
        # Skip directories we don't want to analyze
        if any(skip_dir in str(path) for skip_dir in skip_dirs):
            if path.is_dir() and path.name == "__pycache__":
                pycache_count += 1
            continue
        
        # Track directory contents
        if path.is_dir():
            parent_dir = str(path)
            dir_contents[parent_dir] = []
        else:
            parent_dir = str(path.parent)
            dir_contents[parent_dir].append(path.name)
        
        # Analyze files
        if path.is_file():
            total_files += 1
            file_size = get_file_size(path)
            file_age = get_file_age(path)
            total_size_kb += file_size
            
            # Track file extension
            extension = path.suffix.lower()
            file_extensions[extension] += 1
            
            # Track large files (> 1MB)
            if file_size > 1024:
                large_files.append((str(path), file_size))
            
            # Track old files (> 90 days)
            if file_age > 90:
                old_files.append((str(path), file_age))
    
    # Find empty directories
    for dir_path, files in dir_contents.items():
        if not files and Path(dir_path).is_dir():
            empty_directories.append(dir_path)
    
    # Sort results
    large_files.sort(key=lambda x: x[1], reverse=True)
    old_files.sort(key=lambda x: x[1], reverse=True)
    
    # Generate report
    report = f"""
# Project Analysis Report

## Overview
- Total files: {total_files}
- Total size: {total_size_kb:.2f} KB ({total_size_kb/1024:.2f} MB)
- Python cache directories: {pycache_count}

## File Types
{'-' * 30}
"""
    
    for ext, count in file_extensions.most_common(10):
        report += f"- {ext or 'no extension'}: {count} files\n"
    
    if large_files:
        report += f"\n## Large Files (> 1MB)\n{'-' * 30}\n"
        for path, size in large_files[:10]:  # Show top 10
            report += f"- {path}: {size:.2f} KB ({size/1024:.2f} MB)\n"
    
    if old_files:
        report += f"\n## Old Files (> 90 days)\n{'-' * 30}\n"
        for path, age in old_files[:10]:  # Show top 10
            report += f"- {path}: {age:.1f} days old\n"
    
    if empty_directories:
        report += f"\n## Empty Directories\n{'-' * 30}\n"
        for dir_path in empty_directories[:10]:  # Show top 10
            report += f"- {dir_path}\n"
    
    report += f"\n## Recommendations\n{'-' * 30}\n"
    report += "1. Clean up Python cache directories\n"
    report += "2. Archive or remove old log files\n"
    report += "3. Consider removing empty directories\n"
    if any(x[1] > 10240 for x in large_files):  # Files > 10MB
        report += "4. Review large files (>10MB) to see if they can be reduced or stored elsewhere\n"
    
    return report

if __name__ == "__main__":
    # Path to project root
    project_root = Path(__file__).parent.parent
    
    # Analyze project
    report = analyze_project(project_root)
    
    # Print report
    print(report)
    
    # Save report to file
    report_path = project_root / "project_analysis.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"Report saved to {report_path}")
