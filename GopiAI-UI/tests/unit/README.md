# GopiAI-UI Unit Tests

This directory contains comprehensive unit tests for the GopiAI-UI module, covering all major UI components, widgets, and functionality.

## Test Structure

### Test Files

- **`test_main_window.py`** - Tests for main application window functionality
- **`test_theme_manager.py`** - Tests for theme management and switching
- **`test_settings_dialog.py`** - Tests for settings dialog and configuration
- **`test_model_selector.py`** - Tests for AI model selection widget
- **`test_user_input_handling.py`** - Tests for user input processing and validation
- **`test_notification_system.py`** - Tests for notification display and management
- **`test_runner.py`** - Comprehensive test runner with reporting
- **`conftest.py`** - Shared fixtures and test configuration

### Test Categories

Tests are organized using pytest markers:

- **`@pytest.mark.ui`** - UI tests requiring Qt widgets
- **`@pytest.mark.integration`** - Integration tests between components
- **`@pytest.mark.slow`** - Performance and slow-running tests
- **`@pytest.mark.requires_display`** - Tests requiring a display
- **`@pytest.mark.requires_qt`** - Tests requiring PySide6/Qt

## Running Tests

### Run All Unit Tests
```bash
cd GopiAI-UI
python -m pytest tests/unit/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/unit/test_main_window.py -v
```

### Run Tests by Category
```bash
# UI tests only
python -m pytest tests/unit/ -m ui -v

# Integration tests only
python -m pytest tests/unit/ -m integration -v

# Exclude slow tests
python -m pytest tests/unit/ -m "not slow" -v
```

### Run with Coverage
```bash
python -m pytest tests/unit/ --cov=gopiai.ui --cov-report=html --cov-report=term-missing -v
```

### Using the Test Runner
```bash
# Run all tests
python tests/unit/test_runner.py --all

# Run specific test file
python tests/unit/test_runner.py --test test_main_window.py

# Run by category
python tests/unit/test_runner.py --category ui

# Run with coverage
python tests/unit/test_runner.py --coverage
```

## Test Infrastructure

### Fixtures

The tests use a comprehensive fixture system from `test_infrastructure/ui_fixtures.py`:

- **`qtbot`** - pytest-qt bot for UI testing
- **`mock_main_window`** - Mock main application window
- **`mock_chat_widget`** - Mock chat interface widget
- **`mock_model_selector`** - Mock AI model selector
- **`mock_settings_dialog`** - Mock settings dialog
- **`mock_theme_manager`** - Mock theme management system
- **`mock_notification_system`** - Mock notification system
- **`ui_test_data`** - Sample test data for UI components

### Mocking Strategy

Tests use extensive mocking to:
- Isolate units under test
- Avoid dependencies on external services
- Enable testing without full Qt environment
- Provide predictable test data

### Test Data

Sample test data includes:
- Mock conversations and messages
- Theme configurations
- Settings and preferences
- Model configurations
- Notification examples

## Test Coverage

The unit tests aim to cover:

### Main Window (`test_main_window.py`)
- Window initialization and layout
- Integration with child widgets
- Menu and status bar functionality
- Window state management
- Error handling

### Theme Manager (`test_theme_manager.py`)
- Theme loading and switching
- Theme persistence
- Color scheme management
- Integration with UI components
- Error handling for missing themes

### Settings Dialog (`test_settings_dialog.py`)
- Dialog initialization and display
- Settings validation and persistence
- Tab navigation and categories
- Import/export functionality
- Integration with other components

### Model Selector (`test_model_selector.py`)
- Model listing and selection
- Provider switching
- API key management
- Model validation
- Integration with AI services

### User Input Handling (`test_user_input_handling.py`)
- Text input processing
- Keyboard shortcuts
- Drag and drop operations
- Input validation and sanitization
- Mouse interactions

### Notification System (`test_notification_system.py`)
- Notification display and queuing
- System tray integration
- Notification settings and preferences
- Error handling
- Integration with other components

## Requirements Coverage

These tests fulfill the following requirements from the comprehensive testing system specification:

- **Requirement 1.1** - Unit tests for all major classes and functions
- **Requirement 3.1** - UI tests with pytest-qt for PySide6 components
- **Requirement 3.2** - Tests for user interactions and widget functionality

## Dependencies

### Required Packages
- `pytest` - Test framework
- `pytest-qt` - Qt testing support
- `pytest-cov` - Coverage reporting
- `PySide6` - Qt framework (optional for mocked tests)

### Test Infrastructure
- `test_infrastructure/ui_fixtures.py` - UI-specific fixtures
- `test_infrastructure/fixtures.py` - General test fixtures

## Configuration

### pytest.ini
The tests use configuration from `GopiAI-UI/pytest.ini`:
- Test discovery patterns
- Coverage settings
- Marker definitions
- Qt API configuration

### Environment Variables
Tests respect these environment variables:
- `GOPIAI_TEST_MODE=true` - Enable test mode
- `GOPIAI_DEBUG=true` - Enable debug logging
- `DISPLAY` - Required for display-dependent tests

## Best Practices

### Writing New Tests
1. Use descriptive test names that explain what is being tested
2. Follow the Arrange-Act-Assert pattern
3. Use appropriate fixtures to set up test data
4. Mock external dependencies
5. Add appropriate pytest markers
6. Include both positive and negative test cases

### Test Organization
1. Group related tests in classes
2. Use descriptive class and method names
3. Add docstrings explaining test purpose
4. Separate unit tests from integration tests
5. Use markers to categorize tests

### Error Handling
1. Test both success and failure scenarios
2. Verify error messages and types
3. Test graceful degradation
4. Include edge cases and boundary conditions

## Troubleshooting

### Common Issues

**Qt Application Errors**
- Ensure QApplication is properly initialized
- Use `qtbot` fixture for Qt widget tests
- Check for proper widget cleanup

**Import Errors**
- Verify test infrastructure is in Python path
- Check that all required packages are installed
- Ensure GopiAI modules are properly installed

**Display Issues**
- Use `@pytest.mark.requires_display` for tests needing display
- Tests will be skipped in headless environments
- Use mocks for display-independent testing

**Fixture Issues**
- Check fixture imports in conftest.py
- Verify fixture scope and lifetime
- Use appropriate fixture combinations

### Debug Mode
Enable debug logging:
```bash
GOPIAI_DEBUG=true python -m pytest tests/unit/ -v -s
```

### Verbose Output
Get detailed test output:
```bash
python -m pytest tests/unit/ -v --tb=long
```

## Contributing

When adding new UI components:
1. Create corresponding unit tests
2. Add appropriate fixtures if needed
3. Update this README if necessary
4. Ensure tests pass in CI environment
5. Maintain test coverage above 70%

## Integration

These unit tests integrate with:
- **GopiAI-Core tests** - Shared interfaces and exceptions
- **GopiAI-CrewAI tests** - API integration testing
- **Integration tests** - Cross-component testing
- **E2E tests** - Full application testing

The test infrastructure is designed to support the complete testing pyramid for the GopiAI project.