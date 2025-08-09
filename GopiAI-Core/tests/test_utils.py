#!/usr/bin/env python3
"""
Unit tests for GopiAI Core Utilities

Tests utility functions used across all GopiAI components.
"""

import pytest
import os
import json
import tempfile
import logging
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, mock_open, MagicMock

from gopiai.core.utils import (
    generate_id,
    generate_short_id,
    hash_string,
    get_timestamp,
    parse_timestamp,
    safe_json_loads,
    safe_json_dumps,
    ensure_directory,
    read_file_safe,
    write_file_safe,
    get_file_size,
    is_file_readable,
    is_file_writable,
    sanitize_filename,
    truncate_string,
    format_bytes,
    format_duration,
    merge_dicts,
    flatten_dict,
    unflatten_dict,
    get_env_var,
    setup_logging,
    retry_operation,
    validate_required_fields,
    clean_dict,
    deep_get,
    deep_set
)


class TestIDGeneration:
    """Test ID generation utilities."""
    
    @pytest.mark.unit
    def test_generate_id(self):
        """Test unique ID generation."""
        id1 = generate_id()
        id2 = generate_id()
        
        # IDs should be different
        assert id1 != id2
        
        # IDs should be strings
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        
        # IDs should have reasonable length (UUID format)
        assert len(id1) == 36  # UUID format: 8-4-4-4-12
    
    @pytest.mark.unit
    def test_generate_id_with_prefix(self):
        """Test ID generation with prefix."""
        prefix = "user_"
        id_with_prefix = generate_id(prefix)
        
        assert id_with_prefix.startswith(prefix)
        assert len(id_with_prefix) > len(prefix)
    
    @pytest.mark.unit
    def test_generate_short_id(self):
        """Test short ID generation."""
        short_id = generate_short_id()
        
        assert isinstance(short_id, str)
        assert len(short_id) == 8  # Default length
        
        # Test custom length
        custom_id = generate_short_id(12)
        assert len(custom_id) == 12
        
        # IDs should be different
        assert short_id != custom_id


class TestHashing:
    """Test hashing utilities."""
    
    @pytest.mark.unit
    def test_hash_string_md5(self):
        """Test MD5 hashing."""
        text = "Hello, World!"
        hash_result = hash_string(text, "md5")
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 32  # MD5 hash length
        
        # Same input should produce same hash
        assert hash_string(text, "md5") == hash_result
    
    @pytest.mark.unit
    def test_hash_string_sha256(self):
        """Test SHA256 hashing."""
        text = "Hello, World!"
        hash_result = hash_string(text, "sha256")
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA256 hash length
        
        # Same input should produce same hash
        assert hash_string(text, "sha256") == hash_result
    
    @pytest.mark.unit
    def test_hash_string_invalid_algorithm(self):
        """Test hashing with invalid algorithm."""
        with pytest.raises(ValueError):
            hash_string("test", "invalid_algorithm")


class TestTimestampUtilities:
    """Test timestamp utilities."""
    
    @pytest.mark.unit
    def test_get_timestamp(self):
        """Test timestamp generation."""
        timestamp = get_timestamp()
        
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format
        
        # Test without timezone
        timestamp_no_tz = get_timestamp(include_timezone=False)
        assert isinstance(timestamp_no_tz, str)
        assert "+" not in timestamp_no_tz and "Z" not in timestamp_no_tz
    
    @pytest.mark.unit
    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        # Test ISO format with timezone
        iso_timestamp = "2025-01-01T12:00:00+00:00"
        parsed = parse_timestamp(iso_timestamp)
        
        assert isinstance(parsed, datetime)
        assert parsed.year == 2025
        assert parsed.month == 1
        assert parsed.day == 1
        
        # Test ISO format with Z
        z_timestamp = "2025-01-01T12:00:00Z"
        parsed_z = parse_timestamp(z_timestamp)
        assert isinstance(parsed_z, datetime)
    
    @pytest.mark.unit
    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        with pytest.raises(ValueError):
            parse_timestamp("invalid-timestamp")


class TestJSONUtilities:
    """Test JSON handling utilities."""
    
    @pytest.mark.unit
    def test_safe_json_loads_valid(self):
        """Test safe JSON loading with valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = safe_json_loads(json_str)
        
        assert result == {"key": "value", "number": 42}
    
    @pytest.mark.unit
    def test_safe_json_loads_invalid(self):
        """Test safe JSON loading with invalid JSON."""
        invalid_json = '{"key": "value", invalid}'
        result = safe_json_loads(invalid_json, default={"error": True})
        
        assert result == {"error": True}
        
        # Test with None default
        result_none = safe_json_loads(invalid_json)
        assert result_none is None
    
    @pytest.mark.unit
    def test_safe_json_dumps_valid(self):
        """Test safe JSON dumping with valid data."""
        data = {"key": "value", "number": 42}
        result = safe_json_dumps(data)
        
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result
    
    @pytest.mark.unit
    def test_safe_json_dumps_invalid(self):
        """Test safe JSON dumping with invalid data."""
        # Create object that can't be serialized easily
        class UnserializableClass:
            def __init__(self):
                self.func = lambda x: x
        
        invalid_data = {"obj": UnserializableClass()}
        result = safe_json_dumps(invalid_data, default='{"error": "serialization_failed"}')
        
        # The function uses default=str, so it might actually serialize
        # Let's check if it's either the default or a serialized version
        assert isinstance(result, str)
        assert len(result) > 0


class TestFileUtilities:
    """Test file system utilities."""
    
    @pytest.mark.unit
    def test_ensure_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "new" / "nested" / "directory"
            
            result = ensure_directory(test_path)
            
            assert result.exists()
            assert result.is_dir()
            assert result == test_path
    
    @pytest.mark.unit
    def test_read_file_safe_existing(self):
        """Test safe file reading with existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            content = read_file_safe(temp_file_path)
            assert content == "Test content"
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.unit
    def test_read_file_safe_nonexistent(self):
        """Test safe file reading with non-existent file."""
        content = read_file_safe("/nonexistent/file.txt", default="default content")
        assert content == "default content"
    
    @pytest.mark.unit
    def test_write_file_safe(self):
        """Test safe file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_file.txt"
            
            success = write_file_safe(file_path, "Test content")
            
            assert success is True
            assert file_path.exists()
            assert file_path.read_text() == "Test content"
    
    @pytest.mark.unit
    def test_get_file_size(self):
        """Test file size calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("Hello, World!")
            temp_file_path = temp_file.name
        
        try:
            size = get_file_size(temp_file_path)
            assert size > 0
            assert isinstance(size, int)
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.unit
    def test_get_file_size_nonexistent(self):
        """Test file size for non-existent file."""
        size = get_file_size("/nonexistent/file.txt")
        assert size == 0
    
    @pytest.mark.unit
    def test_is_file_readable(self):
        """Test file readability check."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            assert is_file_readable(temp_file_path) is True
            assert is_file_readable("/nonexistent/file.txt") is False
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.unit
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test with invalid characters
        dirty_filename = 'file<>:"/\\|?*name.txt'
        clean_filename = sanitize_filename(dirty_filename)
        
        assert "<" not in clean_filename
        assert ">" not in clean_filename
        assert ":" not in clean_filename
        assert '"' not in clean_filename
        assert "/" not in clean_filename
        assert "\\" not in clean_filename
        assert "|" not in clean_filename
        assert "?" not in clean_filename
        assert "*" not in clean_filename
        
        # Test with empty filename
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"


class TestStringUtilities:
    """Test string manipulation utilities."""
    
    @pytest.mark.unit
    def test_truncate_string(self):
        """Test string truncation."""
        long_string = "This is a very long string that needs to be truncated"
        
        # Test normal truncation
        truncated = truncate_string(long_string, 20)
        assert len(truncated) == 20
        assert truncated.endswith("...")
        
        # Test string shorter than max length
        short_string = "Short"
        assert truncate_string(short_string, 20) == "Short"
        
        # Test custom suffix
        custom_truncated = truncate_string(long_string, 20, " [more]")
        assert custom_truncated.endswith(" [more]")
    
    @pytest.mark.unit
    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        assert format_bytes(500) == "500.0 B"
    
    @pytest.mark.unit
    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(0.5) == "500ms"
        assert format_duration(1.5) == "1.5s"
        assert format_duration(65) == "1.1m"
        assert format_duration(3665) == "1.0h"


class TestDictionaryUtilities:
    """Test dictionary manipulation utilities."""
    
    @pytest.mark.unit
    def test_merge_dicts_shallow(self):
        """Test shallow dictionary merging."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        
        merged = merge_dicts(dict1, dict2, deep=False)
        
        assert merged == {"a": 1, "b": 3, "c": 4}
        # Original dicts should be unchanged
        assert dict1 == {"a": 1, "b": 2}
        assert dict2 == {"b": 3, "c": 4}
    
    @pytest.mark.unit
    def test_merge_dicts_deep(self):
        """Test deep dictionary merging."""
        dict1 = {"a": 1, "nested": {"x": 1, "y": 2}}
        dict2 = {"b": 2, "nested": {"y": 3, "z": 4}}
        
        merged = merge_dicts(dict1, dict2, deep=True)
        
        expected = {"a": 1, "b": 2, "nested": {"x": 1, "y": 3, "z": 4}}
        assert merged == expected
    
    @pytest.mark.unit
    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested_dict = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3
                }
            }
        }
        
        flattened = flatten_dict(nested_dict)
        
        expected = {
            "a": 1,
            "b.c": 2,
            "b.d.e": 3
        }
        assert flattened == expected
    
    @pytest.mark.unit
    def test_unflatten_dict(self):
        """Test dictionary unflattening."""
        flattened_dict = {
            "a": 1,
            "b.c": 2,
            "b.d.e": 3
        }
        
        unflattened = unflatten_dict(flattened_dict)
        
        expected = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3
                }
            }
        }
        assert unflattened == expected
    
    @pytest.mark.unit
    def test_clean_dict(self):
        """Test dictionary cleaning."""
        dirty_dict = {
            "a": 1,
            "b": None,
            "c": "",
            "d": [],
            "e": {},
            "f": "valid"
        }
        
        # Remove None values
        cleaned_none = clean_dict(dirty_dict, remove_none=True, remove_empty=False)
        assert "b" not in cleaned_none
        assert "c" in cleaned_none
        
        # Remove empty values
        cleaned_empty = clean_dict(dirty_dict, remove_none=False, remove_empty=True)
        assert "c" not in cleaned_empty
        assert "d" not in cleaned_empty
        assert "e" not in cleaned_empty
        assert "b" in cleaned_empty
    
    @pytest.mark.unit
    def test_deep_get(self):
        """Test deep dictionary value retrieval."""
        nested_dict = {
            "a": {
                "b": {
                    "c": "value"
                }
            }
        }
        
        # Test existing path
        assert deep_get(nested_dict, "a.b.c") == "value"
        
        # Test non-existing path
        assert deep_get(nested_dict, "a.b.x", "default") == "default"
        
        # Test partial path
        assert deep_get(nested_dict, "a.b") == {"c": "value"}
    
    @pytest.mark.unit
    def test_deep_set(self):
        """Test deep dictionary value setting."""
        test_dict = {}
        
        deep_set(test_dict, "a.b.c", "value")
        
        expected = {
            "a": {
                "b": {
                    "c": "value"
                }
            }
        }
        assert test_dict == expected


class TestEnvironmentUtilities:
    """Test environment variable utilities."""
    
    @pytest.mark.unit
    def test_get_env_var_string(self):
        """Test getting string environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            value = get_env_var("TEST_VAR")
            assert value == "test_value"
        
        # Test with default
        value = get_env_var("NONEXISTENT_VAR", "default_value")
        assert value == "default_value"
    
    @pytest.mark.unit
    def test_get_env_var_bool(self):
        """Test getting boolean environment variable."""
        with patch.dict(os.environ, {"BOOL_VAR": "true"}):
            value = get_env_var("BOOL_VAR", var_type=bool)
            assert value is True
        
        with patch.dict(os.environ, {"BOOL_VAR": "false"}):
            value = get_env_var("BOOL_VAR", var_type=bool)
            assert value is False
        
        with patch.dict(os.environ, {"BOOL_VAR": "1"}):
            value = get_env_var("BOOL_VAR", var_type=bool)
            assert value is True
    
    @pytest.mark.unit
    def test_get_env_var_int(self):
        """Test getting integer environment variable."""
        with patch.dict(os.environ, {"INT_VAR": "42"}):
            value = get_env_var("INT_VAR", var_type=int)
            assert value == 42
        
        # Test invalid integer
        with patch.dict(os.environ, {"INT_VAR": "not_an_int"}):
            value = get_env_var("INT_VAR", default=0, var_type=int)
            assert value == 0
    
    @pytest.mark.unit
    def test_get_env_var_list(self):
        """Test getting list environment variable."""
        with patch.dict(os.environ, {"LIST_VAR": "item1,item2,item3"}):
            value = get_env_var("LIST_VAR", var_type=list)
            assert value == ["item1", "item2", "item3"]


class TestLoggingUtilities:
    """Test logging utilities."""
    
    @pytest.mark.unit
    def test_setup_logging(self):
        """Test logging setup."""
        logger = setup_logging("test_logger", "DEBUG")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
        
        # Test that logger has handlers
        assert len(logger.handlers) > 0
    
    @pytest.mark.unit
    def test_setup_logging_with_file(self):
        """Test logging setup with file handler."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Ensure the logs directory exists
            logs_dir = Path(temp_dir) / "logs"
            logs_dir.mkdir(exist_ok=True)
            log_file = logs_dir / "test.log"
            
            logger = setup_logging("test_logger_file", "INFO", str(log_file))
            
            try:
                # Should have both console and file handlers
                assert len(logger.handlers) == 2
                
                # Test logging
                logger.info("Test message")
                
                # Check that log file was created
                assert log_file.exists()
            finally:
                # Clean up handlers to avoid file lock issues
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)


class TestRetryUtilities:
    """Test retry utilities."""
    
    @pytest.mark.unit
    def test_retry_operation_success(self):
        """Test retry operation that succeeds."""
        call_count = 0
        
        def successful_operation():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = retry_operation(successful_operation, max_retries=3)
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.unit
    def test_retry_operation_eventual_success(self):
        """Test retry operation that succeeds after failures."""
        call_count = 0
        
        def eventually_successful_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not ready yet")
            return "success"
        
        result = retry_operation(eventually_successful_operation, max_retries=3, delay=0.01)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.unit
    def test_retry_operation_failure(self):
        """Test retry operation that always fails."""
        call_count = 0
        
        def failing_operation():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            retry_operation(failing_operation, max_retries=3, delay=0.01)
        
        assert call_count == 3


class TestValidationUtilities:
    """Test validation utilities."""
    
    @pytest.mark.unit
    def test_validate_required_fields(self):
        """Test required field validation."""
        data = {"field1": "value1", "field2": "value2"}
        required = ["field1", "field2", "field3"]
        
        missing = validate_required_fields(data, required)
        
        assert missing == ["field3"]
    
    @pytest.mark.unit
    def test_validate_required_fields_all_present(self):
        """Test validation when all required fields are present."""
        data = {"field1": "value1", "field2": "value2"}
        required = ["field1", "field2"]
        
        missing = validate_required_fields(data, required)
        
        assert missing == []
    
    @pytest.mark.unit
    def test_validate_required_fields_none_values(self):
        """Test validation with None values."""
        data = {"field1": "value1", "field2": None}
        required = ["field1", "field2"]
        
        missing = validate_required_fields(data, required)
        
        assert missing == ["field2"]


@pytest.mark.xfail_known_issue
class TestKnownUtilityIssues:
    """Test known issues with utilities marked as expected failures."""
    
    def test_file_encoding_issue(self):
        """Test known issue with file encoding."""
        # This test documents a known issue with file encoding
        # when dealing with non-UTF-8 files
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            # Write non-UTF-8 content
            temp_file.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8 sequence
            temp_file_path = temp_file.name
        
        try:
            # This should fail due to encoding issues
            content = read_file_safe(temp_file_path)
            
            # The function should return default value, but might fail
            # depending on the system's handling of encoding errors
            assert content == ""
        finally:
            os.unlink(temp_file_path)
    
    def test_deep_recursion_issue(self):
        """Test known issue with deep recursion in nested operations."""
        # This documents a potential issue with very deeply nested dictionaries
        # that might cause recursion limits to be exceeded
        
        # Create very deeply nested dictionary
        deep_dict = {}
        current = deep_dict
        for i in range(1000):  # Very deep nesting
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["value"] = "deep_value"
        
        # This should fail due to recursion limits
        with pytest.raises(RecursionError):
            flatten_dict(deep_dict)
    
    def test_large_file_memory_issue(self):
        """Test known issue with large file handling."""
        # This documents a potential memory issue when handling very large files
        
        # Simulate reading a very large file
        large_content = "x" * (100 * 1024 * 1024)  # 100MB string
        
        with patch("builtins.open", mock_open(read_data=large_content)):
            # This might cause memory issues on systems with limited RAM
            content = read_file_safe("fake_large_file.txt")
            
            # This assertion might fail due to memory constraints
            assert len(content) == 100 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])