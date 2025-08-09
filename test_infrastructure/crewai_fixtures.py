#!/usr/bin/env python3
"""
CrewAI-specific Test Fixtures

Provides specialized fixtures for testing GopiAI-CrewAI components.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import Dict, Any, List
import json
import tempfile
from pathlib import Path


@pytest.fixture
def mock_crewai_agent():
    """Mock CrewAI agent for testing."""
    mock_agent = MagicMock()
    
    # Configure agent properties
    mock_agent.role = "Test Agent"
    mock_agent.goal = "Test goal"
    mock_agent.backstory = "Test backstory"
    mock_agent.verbose = True
    mock_agent.allow_delegation = False
    
    # Mock agent execution
    mock_agent.execute_task.return_value = "Task completed successfully"
    
    return mock_agent


@pytest.fixture
def mock_crewai_task():
    """Mock CrewAI task for testing."""
    mock_task = MagicMock()
    
    # Configure task properties
    mock_task.description = "Test task description"
    mock_task.expected_output = "Expected test output"
    mock_task.agent = None
    
    return mock_task


@pytest.fixture
def mock_crewai_crew():
    """Mock CrewAI crew for testing."""
    mock_crew = MagicMock()
    
    # Configure crew properties
    mock_crew.agents = []
    mock_crew.tasks = []
    mock_crew.verbose = True
    
    # Mock crew execution
    mock_crew.kickoff.return_value = {
        "final_output": "Crew execution completed",
        "tasks_outputs": ["Task 1 output", "Task 2 output"]
    }
    
    return mock_crew


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    mock_provider = MagicMock()
    
    # Configure provider properties
    mock_provider.model_name = "test-model"
    mock_provider.temperature = 0.7
    mock_provider.max_tokens = 1000
    
    # Mock LLM calls
    mock_provider.call.return_value = "Mock LLM response"
    mock_provider.generate.return_value = ["Generated response 1", "Generated response 2"]
    
    return mock_provider


@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter client for testing."""
    mock_client = MagicMock()
    
    # Mock available models
    mock_client.get_models.return_value = {
        "data": [
            {"id": "openai/gpt-4", "name": "GPT-4"},
            {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet"},
            {"id": "google/gemini-pro", "name": "Gemini Pro"}
        ]
    }
    
    # Mock chat completion
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mock OpenRouter response"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    
    mock_client.chat.completions.create.return_value = mock_response
    mock_client.test_connection.return_value = True
    
    return mock_client


@pytest.fixture
def mock_api_server():
    """Mock API server for testing."""
    mock_server = MagicMock()
    
    # Mock server state
    mock_server.is_running = True
    mock_server.port = 5051
    mock_server.host = "localhost"
    
    # Mock server operations
    mock_server.start.return_value = True
    mock_server.stop.return_value = True
    mock_server.restart.return_value = True
    mock_server.health_check.return_value = {"status": "healthy"}
    
    return mock_server


@pytest.fixture
def mock_state_manager():
    """Mock state manager for testing."""
    mock_manager = MagicMock()
    
    # Default state
    default_state = {
        "current_provider": "openai",
        "current_model": "gpt-4",
        "usage_stats": {
            "requests": 0,
            "tokens": 0
        },
        "blacklisted_models": [],
        "rate_limits": {
            "requests_per_minute": 60,
            "tokens_per_minute": 40000
        }
    }
    
    mock_manager.get_state.return_value = default_state
    mock_manager.update_state.return_value = True
    mock_manager.save_state.return_value = True
    mock_manager.load_state.return_value = default_state
    mock_manager.reset_state.return_value = True
    
    return mock_manager


@pytest.fixture
def mock_command_processor():
    """Mock command processor for testing."""
    mock_processor = MagicMock()
    
    # Mock command processing
    mock_processor.process_command.return_value = {
        "status": "success",
        "result": "Command processed successfully",
        "tool_calls": []
    }
    
    mock_processor.validate_command.return_value = True
    mock_processor.extract_tools.return_value = []
    
    return mock_processor


@pytest.fixture
def mock_tool_executor():
    """Mock tool executor for testing."""
    mock_executor = MagicMock()
    
    # Mock tool execution
    mock_executor.execute.return_value = {
        "status": "success",
        "output": "Tool executed successfully",
        "error": None
    }
    
    mock_executor.is_available.return_value = True
    mock_executor.get_schema.return_value = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {}
    }
    
    return mock_executor


@pytest.fixture
def mock_memory_system():
    """Mock memory system for CrewAI."""
    mock_memory = MagicMock()
    
    # Mock memory operations
    mock_memory.add.return_value = True
    mock_memory.search.return_value = [
        {"content": "Previous conversation", "score": 0.9},
        {"content": "Related context", "score": 0.8}
    ]
    mock_memory.clear.return_value = True
    mock_memory.count.return_value = 10
    
    return mock_memory


@pytest.fixture
def crewai_test_config(temp_dir):
    """Create test configuration for CrewAI."""
    config = {
        "api": {
            "host": "localhost",
            "port": 5051,
            "timeout": 30
        },
        "models": {
            "default_provider": "openai",
            "default_model": "gpt-4",
            "fallback_models": ["gpt-3.5-turbo", "claude-3-haiku"]
        },
        "tools": {
            "enabled": ["browser_tools", "filesystem_tools"],
            "disabled": ["terminal_tools"],
            "safe_mode": True
        },
        "memory": {
            "enabled": True,
            "max_entries": 1000,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    }
    
    config_file = temp_dir / "crewai_test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_file


@pytest.fixture
def mock_env_file(temp_dir):
    """Create mock .env file for testing."""
    env_content = """
# Test environment variables
OPENAI_API_KEY=test-openai-key
ANTHROPIC_API_KEY=test-anthropic-key
GOOGLE_API_KEY=test-google-key
OPENROUTER_API_KEY=test-openrouter-key

# Server configuration
CREWAI_API_HOST=localhost
CREWAI_API_PORT=5051

# Feature flags
GOPIAI_TERMINAL_UNSAFE=0
GOPIAI_DEBUG=1
"""
    
    env_file = temp_dir / ".env"
    with open(env_file, 'w') as f:
        f.write(env_content.strip())
    
    return env_file


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing."""
    mock_limiter = MagicMock()
    
    # Mock rate limiting
    mock_limiter.can_proceed.return_value = True
    mock_limiter.record_request.return_value = None
    mock_limiter.get_remaining.return_value = {"requests": 59, "tokens": 39000}
    mock_limiter.reset.return_value = None
    mock_limiter.is_rate_limited.return_value = False
    
    return mock_limiter


@pytest.fixture
def mock_model_switcher():
    """Mock model switcher for testing."""
    mock_switcher = MagicMock()
    
    # Mock model switching
    mock_switcher.switch_to_model.return_value = True
    mock_switcher.get_current_model.return_value = "gpt-4"
    mock_switcher.get_available_models.return_value = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
    mock_switcher.is_model_available.return_value = True
    mock_switcher.get_model_info.return_value = {
        "name": "gpt-4",
        "provider": "openai",
        "context_length": 8192,
        "cost_per_token": 0.00003
    }
    
    return mock_switcher