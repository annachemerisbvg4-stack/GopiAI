# GopiAI-CrewAI Unit Tests

This directory contains comprehensive unit tests for the GopiAI-CrewAI module, covering all major components and functionality.

## Test Coverage

### 1. API Server Tests (`test_api_server.py`)
- **21 tests** covering all API endpoints and server functionality
- Health check endpoints (healthy and limited mode)
- Request processing (valid JSON, missing fields, invalid JSON)
- Task status management (existing and non-existent tasks)
- Debug status endpoint
- Model provider management
- State management (get/update current state)
- Tools management (get tools, toggle tools, set API keys)
- Agents management
- Error handling and recovery
- Task cleanup mechanisms
- Concurrent request handling

### 2. Model Switching Tests (`test_model_switching.py`)
- **16 tests** covering LLM rotation and model selection
- Available models retrieval (with/without API keys)
- Next available model selection (success and rate-limited scenarios)
- Usage tracking and registration
- Rate limiting mechanisms
- Blacklist functionality for overused models
- Provider switching between Gemini and OpenRouter
- API key validation (including edge cases)
- Model selection by intelligence score
- Legacy compatibility functions
- State persistence
- Usage statistics
- Complete model switching workflow

### 3. Command Processing Tests (`test_command_processing.py`)
- **16 tests** covering command extraction, validation, and execution
- Valid single and array command processing
- Invalid JSON handling
- Missing required fields handling
- Empty and malformed command handling
- Free text filtering (prevents accidental command execution)
- Tool execution (success, failure, unavailable scenarios)
- Tool schema validation
- Concurrent command execution
- Command validation edge cases
- Parameter validation for different data types
- Error recovery during command processing
- Complete command processing pipeline

### 4. State Manager Tests (`test_state_manager.py`)
- **16 tests** covering state persistence and management
- Loading state from existing, non-existent, corrupted, and empty files
- Saving state to new and existing files
- Directory creation for state files
- Permission error handling
- State file path management
- Legacy state migration from old file locations
- State validation and handling of extra fields
- Concurrent state access
- Unicode/encoding handling
- Complete state lifecycle management
- Mock-based state manager testing

## Test Infrastructure

### Fixtures and Mocks (`conftest.py`)
- Comprehensive fixture setup for all test scenarios
- Mock objects for external dependencies (AI services, databases, etc.)
- Test environment configuration
- Shared test data and utilities
- Automatic cleanup after tests

### Test Runner (`test_runner.py`)
- Automated test discovery and execution
- Comprehensive reporting and summary generation
- Coverage report generation
- Dependency checking
- Category-based test execution
- Pattern-based test filtering

## Running Tests

### Run All Unit Tests
```bash
python -m pytest tests/unit/ -v --tb=short --ignore=tests/unit/test_runner.py
```

### Run Specific Test Files
```bash
python -m pytest tests/unit/test_api_server.py -v
python -m pytest tests/unit/test_model_switching.py -v
python -m pytest tests/unit/test_command_processing.py -v
python -m pytest tests/unit/test_state_manager.py -v
```

### Run Tests by Category
```bash
python -m pytest tests/unit/ -m unit -v
python -m pytest tests/unit/ -m integration -v
python -m pytest tests/unit/ -m api -v
```

### Generate Coverage Report
```bash
python -m pytest tests/unit/ --cov=gopiai --cov-report=html --cov-report=term-missing
```

## Test Results

- **Total Tests**: 69
- **Passed**: 69 (100%)
- **Failed**: 0
- **Success Rate**: 100%

All tests are passing and provide comprehensive coverage of:
- API server endpoints and functionality
- Model switching and LLM rotation
- Command processing and tool execution
- State management and persistence

## Test Categories

Tests are organized using pytest markers:
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API endpoint tests
- `@pytest.mark.slow`: Slow running tests

## Requirements Covered

This implementation satisfies the following requirements from the comprehensive testing system specification:

- **Requirement 1.1**: Модульные тесты для всех основных классов и функций
- **Requirement 1.2**: Точная информация о сломанных функциях/классах
- **Requirement 2.1**: Проверка взаимодействия между компонентами

The tests provide comprehensive coverage of the GopiAI-CrewAI module's core functionality, ensuring reliability and maintainability of the codebase.