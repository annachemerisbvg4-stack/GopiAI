#!/usr/bin/env python3
"""
Common Test Fixtures and Mocks for GopiAI Testing Infrastructure

Provides reusable fixtures and mocks for all GopiAI modules.
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass


@dataclass
class MockAIResponse:
    """Mock response from AI services."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = None


@dataclass
class MockConversation:
    """Mock conversation data."""
    id: str
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]


class AIServiceMocker:
    """Mock AI service responses for testing."""
    
    def __init__(self):
        self.responses = []
        self.call_count = 0
    
    def add_response(self, content: str, model: str = "test-model", 
                    provider: str = "test-provider"):
        """Add a mock response to the queue."""
        response = MockAIResponse(
            content=content,
            model=model,
            provider=provider,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )
        self.responses.append(response)
    
    def get_next_response(self) -> MockAIResponse:
        """Get the next mock response."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        
        # Default response if no more responses queued
        return MockAIResponse(
            content="Mock AI response",
            model="default-model",
            provider="default-provider",
            usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15}
        )


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key",
        "CREWAI_API_URL": "http://localhost:5051",
        "GOPIAI_ENV": "test"
    }
    
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def ai_service_mocker():
    """Provide AI service mocker for tests."""
    mocker = AIServiceMocker()
    
    # Add some default responses
    mocker.add_response("Hello, this is a test response!", "gpt-4", "openai")
    mocker.add_response("This is another test response.", "claude-3", "anthropic")
    
    return mocker


@pytest.fixture
def mock_crewai_server():
    """Mock CrewAI server responses."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        # Mock successful health check
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "healthy"}
        
        # Mock successful task submission
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "task_id": "test-task-123",
            "status": "submitted"
        }
        
        yield {
            "get": mock_get,
            "post": mock_post
        }


@pytest.fixture
def mock_txtai_memory():
    """Mock txtai memory system."""
    mock_index = MagicMock()
    
    # Mock search results
    mock_index.search.return_value = [
        {"id": "1", "text": "Test memory 1", "score": 0.9},
        {"id": "2", "text": "Test memory 2", "score": 0.8}
    ]
    
    # Mock index operations
    mock_index.index.return_value = None
    mock_index.upsert.return_value = None
    mock_index.delete.return_value = None
    
    with patch('txtai.Embeddings') as mock_embeddings:
        mock_embeddings.return_value = mock_index
        yield mock_index


@pytest.fixture
def sample_conversation():
    """Provide sample conversation data."""
    return MockConversation(
        id="test-conversation-123",
        messages=[
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
            {"role": "user", "content": "Can you help me with Python programming?"},
            {"role": "assistant", "content": "Of course! I'd be happy to help you with Python programming. What specific topic would you like to learn about?"}
        ],
        metadata={
            "created_at": "2025-01-01T00:00:00Z",
            "model": "gpt-4",
            "provider": "openai",
            "session_id": "test-session-456"
        }
    )


@pytest.fixture
def mock_ui_events():
    """Mock UI events for testing."""
    from unittest.mock import MagicMock
    
    # Mock Qt events
    mock_events = {
        "click": MagicMock(),
        "key_press": MagicMock(),
        "text_change": MagicMock(),
        "window_close": MagicMock()
    }
    
    return mock_events


@pytest.fixture
def test_config_file(temp_dir):
    """Create a test configuration file."""
    config = {
        "api": {
            "base_url": "http://localhost:5051",
            "timeout": 30
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
    
    config_file = temp_dir / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_file


@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system operations."""
    # Create some test files
    test_files = {
        "test.txt": "This is a test file",
        "config.json": '{"test": true}',
        "data.csv": "name,age\nJohn,30\nJane,25"
    }
    
    for filename, content in test_files.items():
        file_path = temp_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    return temp_dir


class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.data = {}
        self.connected = False
    
    def connect(self):
        """Mock database connection."""
        self.connected = True
        return True
    
    def disconnect(self):
        """Mock database disconnection."""
        self.connected = False
    
    def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Mock data insertion."""
        if table not in self.data:
            self.data[table] = []
        
        record_id = f"{table}_{len(self.data[table])}"
        record = {"id": record_id, **data}
        self.data[table].append(record)
        return record_id
    
    def select(self, table: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock data selection."""
        if table not in self.data:
            return []
        
        records = self.data[table]
        
        if filters:
            filtered_records = []
            for record in records:
                match = True
                for key, value in filters.items():
                    if key not in record or record[key] != value:
                        match = False
                        break
                if match:
                    filtered_records.append(record)
            return filtered_records
        
        return records
    
    def update(self, table: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Mock data update."""
        if table not in self.data:
            return False
        
        for record in self.data[table]:
            if record["id"] == record_id:
                record.update(data)
                return True
        
        return False
    
    def delete(self, table: str, record_id: str) -> bool:
        """Mock data deletion."""
        if table not in self.data:
            return False
        
        for i, record in enumerate(self.data[table]):
            if record["id"] == record_id:
                del self.data[table][i]
                return True
        
        return False


@pytest.fixture
def mock_database():
    """Provide mock database for tests."""
    db = MockDatabase()
    db.connect()
    
    # Add some test data
    db.insert("users", {"name": "Test User", "email": "test@example.com"})
    db.insert("conversations", {"user_id": "users_0", "title": "Test Chat"})
    
    yield db
    
    db.disconnect()


# Pytest configuration for common markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "ui: UI tests"
    )
    config.addinivalue_line(
        "markers", "api: API tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "requires_display: Tests requiring display"
    )
    config.addinivalue_line(
        "markers", "requires_server: Tests requiring server"
    )
    config.addinivalue_line(
        "markers", "xfail_known_issue: Known issues marked as expected failures"
    )