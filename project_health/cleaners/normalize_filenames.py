#!/usr/bin/env python
"""
Script to normalize filenames in the project by removing unusual characters.
This makes filenames more consistent and easier to work with across platforms.
"""

import os
import re
from pathlib import Path

def normalize_filename(filename):
    """
    Normalize a filename by removing unusual characters and emojis.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Normalized filename
    """
    # Remove emojis and other unusual characters
    # Keep only alphanumeric, dots, underscores, hyphens, and spaces
    clean_name = re.sub(r'[^\w\-\. ]', '', filename)
    
    # Replace spaces with underscores
    clean_name = clean_name.replace(' ', '_')
    
    # Ensure the filename is not empty
    if not clean_name:
        return filename
    
    return clean_name

def normalize_project_filenames(root_dir, preview_only=True):
    """
    Find and normalize filenames in the project.
    
    Args:
        root_dir (str): Path to the root directory
        preview_only (bool): If True, only preview changes without renaming
    """
    root_path = Path(root_dir)
    changes = []
    
    # First collect all files that need renaming
    for path in root_path.glob("**/*"):
        if not path.is_file():
            continue
        
        # Skip certain directories like venv
        if "venv" in str(path) or ".git" in str(path):
            continue
        
        filename = path.name
        normalized = normalize_filename(filename)
        
        if normalized != filename:
            changes.append((path, path.parent / normalized))
    
    # Preview or apply changes
    if changes:
        print(f"Found {len(changes)} files to rename:")
        for old_path, new_path in changes:
            if preview_only:
                print(f"Would rename: {old_path} -> {new_path}")
            else:
                try:
                    old_path.rename(new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Error renaming {old_path}: {e}")
    else:
        print("No files need renaming.")

if __name__ == "__main__":
    # Path to project root
    project_root = Path(__file__).parent.parent
    
    # First show a preview of what would be changed
    print("=== PREVIEW MODE ===")
    normalize_project_filenames(project_root, preview_only=True)
    
    # Ask for confirmation before making changes
    response = input("\nDo you want to apply these changes? (y/n): ")
    if response.lower() == 'y':
        print("\n=== APPLYING CHANGES ===")
        normalize_project_filenames(project_root, preview_only=False)
    else:
        print("Operation cancelled. No changes were made.")
