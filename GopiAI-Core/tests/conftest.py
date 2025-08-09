#!/usr/bin/env python3
"""
Pytest configuration and fixtures for GopiAI-Core tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system with test files."""
    # Create some test files
    test_files = {
        "test.txt": "This is a test file",
        "config.json": '{"test": true, "value": 42}',
        "empty.txt": "",
        "unicode.txt": "Unicode content: 🚀 测试 العربية"
    }
    
    for filename, content in test_files.items():
        file_path = temp_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return temp_dir


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ],
        "conversation": {
            "id": "conv-123",
            "title": "Test Conversation",
            "created_at": "2025-01-01T00:00:00Z"
        },
        "config": {
            "api": {
                "base_url": "http://localhost:5051",
                "timeout": 30,
                "max_retries": 3
            },
            "ui": {
                "theme": "dark",
                "font_size": 12
            },
            "memory": {
                "max_entries": 1000,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }
    }


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "TEST_STRING": "test_value",
        "TEST_INT": "42",
        "TEST_BOOL": "true",
        "TEST_LIST": "item1,item2,item3",
        "TEST_FLOAT": "3.14"
    }
    
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_logger():
    """Provide a mock logger for tests."""
    logger = MagicMock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions and classes"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests that may take significant time"
    )
    config.addinivalue_line(
        "markers", "xfail_known_issue: Known issues marked as expected failures"
    )


# Custom pytest collection hook to ensure proper test discovery
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ['integration', 'slow', 'xfail_known_issue'] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() 
               for keyword in ['large', 'performance', 'stress', 'load']):
            item.add_marker(pytest.mark.slow)


# Fixture for mocking external dependencies
@pytest.fixture
def mock_external_deps():
    """Mock external dependencies that might not be available during testing."""
    mocks = {}
    
    # Mock any external libraries that might not be installed
    try:
        import requests
        mocks['requests'] = requests
    except ImportError:
        mocks['requests'] = MagicMock()
    
    try:
        import numpy
        mocks['numpy'] = numpy
    except ImportError:
        mocks['numpy'] = MagicMock()
    
    return mocks