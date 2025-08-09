"""
Core Utility Functions for GopiAI System

Provides common utility functions used across all GopiAI components.
"""

import os
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from pathlib import Path
import logging


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4()).replace('-', '')[:length]


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string using specified algorithm."""
    if algorithm == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def get_timestamp(include_timezone: bool = True) -> str:
    """Get current timestamp as ISO string."""
    if include_timezone:
        return datetime.now(timezone.utc).isoformat()
    else:
        return datetime.now().isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime object."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        # Fallback for different formats
        return datetime.fromisoformat(timestamp_str)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string with fallback."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except (TypeError, ValueError):
        return default


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def read_file_safe(file_path: Union[str, Path], default: str = "") -> str:
    """Safely read file content with fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError, UnicodeDecodeError):
        return default


def write_file_safe(file_path: Union[str, Path], content: str) -> bool:
    """Safely write content to file."""
    try:
        # Ensure parent directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except (IOError, UnicodeEncodeError):
        return False


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    try:
        return Path(file_path).stat().st_size
    except (FileNotFoundError, OSError):
        return 0


def is_file_readable(file_path: Union[str, Path]) -> bool:
    """Check if file is readable."""
    try:
        path_obj = Path(file_path)
        return path_obj.exists() and path_obj.is_file() and os.access(path_obj, os.R_OK)
    except (OSError, PermissionError):
        return False


def is_file_writable(file_path: Union[str, Path]) -> bool:
    """Check if file is writable."""
    try:
        path_obj = Path(file_path)
        if path_obj.exists():
            return os.access(path_obj, os.W_OK)
        else:
            # Check if parent directory is writable
            return os.access(path_obj.parent, os.W_OK)
    except (OSError, PermissionError):
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    return filename


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    if truncated_length <= 0:
        return suffix[:max_length]
    
    return text[:truncated_length] + suffix


def format_bytes(bytes_count: int) -> str:
    """Format bytes count to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
    """Merge two dictionaries."""
    if not deep:
        result = dict1.copy()
        result.update(dict2)
        return result
    
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """Unflatten dictionary with separator."""
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result


def get_env_var(var_name: str, default: Any = None, var_type: type = str) -> Any:
    """Get environment variable with type conversion."""
    value = os.environ.get(var_name, default)
    
    if value is None or value == default:
        return default
    
    try:
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        elif var_type == list:
            return value.split(',') if isinstance(value, str) else value
        else:
            return var_type(value)
    except (ValueError, TypeError):
        return default


def setup_logging(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        ensure_directory(Path(log_file).parent)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def retry_operation(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry operation with exponential backoff."""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (backoff ** attempt)
            time.sleep(wait_time)
    
    return None


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present in data."""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields


def clean_dict(d: Dict[str, Any], remove_none: bool = True, remove_empty: bool = False) -> Dict[str, Any]:
    """Clean dictionary by removing None or empty values."""
    cleaned = {}
    for key, value in d.items():
        if remove_none and value is None:
            continue
        if remove_empty and (value == "" or value == [] or value == {}):
            continue
        
        if isinstance(value, dict):
            cleaned_value = clean_dict(value, remove_none, remove_empty)
            if cleaned_value or not remove_empty:
                cleaned[key] = cleaned_value
        else:
            cleaned[key] = value
    
    return cleaned


def deep_get(d: Dict[str, Any], keys: str, default: Any = None, sep: str = '.') -> Any:
    """Get nested dictionary value using dot notation."""
    try:
        for key in keys.split(sep):
            d = d[key]
        return d
    except (KeyError, TypeError):
        return default


def deep_set(d: Dict[str, Any], keys: str, value: Any, sep: str = '.') -> None:
    """Set nested dictionary value using dot notation."""
    key_list = keys.split(sep)
    for key in key_list[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[key_list[-1]] = value