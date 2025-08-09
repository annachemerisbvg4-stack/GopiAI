# GopiAI UI Tests with pytest-qt

This directory contains comprehensive UI tests for the GopiAI desktop application using pytest-qt framework. These tests cover all major user interface components and user interaction scenarios.

## 📋 Test Coverage

### Core UI Components
- **Main Window** (`test_main_window_ui.py`)
  - Window initialization and properties
  - Menu bar functionality
  - Status bar operations
  - Central widget management
  - Keyboard shortcuts
  - Theme switching
  - File operations integration

- **Chat Widget** (`test_chat_widget.py`)
  - Chat initialization and state
  - Message display and history
  - User input handling
  - Integration with AI services
  - Performance with large histories

### User Interaction Scenarios
- **Message Sending** (`test_message_sending_ui.py`)
  - Simple text message sending
  - Empty message handling
  - Long message processing
  - Special characters and emojis
  - Error handling and timeouts
  - Rapid message sending
  - Streaming response handling

- **Model Switching** (`test_model_switching_ui.py`)
  - Model selector initialization
  - Model selection changes
  - Model data retrieval
  - Integration with chat functionality
  - Model availability checking
  - Configuration management
  - Performance testing

- **File Operations** (`test_file_operations_ui.py`)
  - File dialog operations
  - Drag and drop functionality
  - File import/export
  - File attachments in chat
  - Error handling for file operations
  - Progress indication
  - Bulk operations

- **Settings Management** (`test_settings_ui.py`)
  - Settings dialog functionality
  - Theme configuration
  - Font settings
  - API key management
  - Model configuration
  - Behavior settings
  - Settings persistence

## 🛠️ Test Infrastructure

### Fixtures and Mocks
All tests use comprehensive mock fixtures from `test_infrastructure/ui_fixtures.py`:

- `qtbot`: pytest-qt test bot for UI interactions
- `mock_main_window`: Mock main application window
- `mock_chat_widget`: Mock chat interface component
- `mock_model_selector`: Mock model selection widget
- `mock_settings_dialog`: Mock settings configuration dialog
- `mock_file_dialog`: Mock file operation dialogs
- `mock_theme_manager`: Mock theme management system
- `mock_notification_system`: Mock notification handling

### Test Data
Test data is provided through `ui_test_data` fixture containing:
- Sample conversation messages
- Sample conversation metadata
- Default settings configurations
- Mock file paths and content

## 🚀 Running UI Tests

### Run All UI Tests
```bash
# From GopiAI-UI directory
python -m pytest tests/ui/ -v

# Or using the test runner
python tests/ui/test_runner_ui.py
```

### Run Specific Test Categories
```bash
# Main window tests
python tests/ui/test_runner_ui.py --category main_window

# Message sending tests
python tests/ui/test_runner_ui.py --category message_sending

# Model switching tests
python tests/ui/test_runner_ui.py --category model_switching

# File operations tests
python tests/ui/test_runner_ui.py --category file_operations

# Settings tests
python tests/ui/test_runner_ui.py --category settings

# Integration tests
python tests/ui/test_runner_ui.py --category integration
```

### Run with Coverage
```bash
python tests/ui/test_runner_ui.py --coverage
```

### Run Specific Test Files
```bash
# Individual test files
python -m pytest tests/ui/test_main_window_ui.py -v
python -m pytest tests/ui/test_message_sending_ui.py -v
python -m pytest tests/ui/test_model_switching_ui.py -v
python -m pytest tests/ui/test_file_operations_ui.py -v
python -m pytest tests/ui/test_settings_ui.py -v
```

## 📊 Test Categories and Markers

### Pytest Markers
- `@pytest.mark.ui`: UI-specific tests requiring Qt environment
- `@pytest.mark.integration`: Integration tests spanning multiple components
- `@pytest.mark.slow`: Performance tests that may take longer to run

### Test Categories
- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interaction testing
- **User Scenario Tests**: Complete user workflow testing
- **Performance Tests**: UI responsiveness and speed testing
- **Error Handling Tests**: Error condition and recovery testing

## 🔧 Requirements

### Dependencies
```bash
# Core testing framework
pytest>=7.0.0
pytest-qt>=4.0.0

# UI framework
PySide6>=6.7.0

# Test infrastructure
pytest-mock>=3.10.0
pytest-cov>=4.0.0  # For coverage reporting
```

### Environment Setup
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Ensure GopiAI-UI is installed in development mode
pip install -e .
```

## 📝 Test Structure

### Test File Organization
```
tests/ui/
├── test_main_window_ui.py      # Main window functionality
├── test_chat_widget.py         # Chat interface components
├── test_message_sending_ui.py  # Message sending scenarios
├── test_model_switching_ui.py  # Model selection and switching
├── test_file_operations_ui.py  # File handling operations
├── test_settings_ui.py         # Settings and configuration
├── test_runner_ui.py           # Test execution coordinator
└── README.md                   # This documentation
```

### Test Class Organization
Each test file contains multiple test classes organized by functionality:

```python
class TestComponentInitialization:
    """Test component initialization and setup."""

class TestUserInteractions:
    """Test user interaction scenarios."""

class TestErrorHandling:
    """Test error conditions and recovery."""

class TestIntegration:
    """Test integration with other components."""

class TestPerformance:
    """Test performance characteristics."""
```

## 🎯 Test Scenarios Covered

### Main Window Tests
- ✅ Window initialization and properties
- ✅ Menu bar and toolbar functionality
- ✅ Status bar updates
- ✅ Central widget management
- ✅ Keyboard shortcuts
- ✅ Theme switching
- ✅ File operations integration
- ✅ Settings dialog integration
- ✅ Notification system integration

### Chat Widget Tests
- ✅ Chat initialization and state management
- ✅ Message display and formatting
- ✅ Message history management
- ✅ User input handling
- ✅ Integration with AI services
- ✅ Error handling and recovery
- ✅ Performance with large histories

### Message Sending Tests
- ✅ Simple text message sending
- ✅ Empty message validation
- ✅ Long message handling
- ✅ Special characters and emoji support
- ✅ Multiple model support
- ✅ Error handling and timeouts
- ✅ Rapid message sending
- ✅ Streaming response handling
- ✅ Message history updates

### Model Switching Tests
- ✅ Model selector initialization
- ✅ Model selection changes
- ✅ Model data and configuration
- ✅ Integration with chat functionality
- ✅ Model availability checking
- ✅ Custom model addition
- ✅ Performance optimization
- ✅ Keyboard shortcuts

### File Operations Tests
- ✅ File dialog operations (open/save/directory)
- ✅ Drag and drop functionality
- ✅ File import/export operations
- ✅ File attachments in chat
- ✅ Multiple file handling
- ✅ Error handling (not found, permissions, size)
- ✅ Progress indication
- ✅ Bulk operations

### Settings Tests
- ✅ Settings dialog functionality
- ✅ Theme configuration and preview
- ✅ Font selection and sizing
- ✅ API key management and validation
- ✅ Model configuration
- ✅ Behavior and privacy settings
- ✅ Settings persistence (save/load/reset)
- ✅ Import/export functionality

## 🔍 Debugging UI Tests

### Common Issues and Solutions

1. **Qt Application Not Found**
   ```python
   # Ensure QApplication is properly initialized in fixtures
   app = QApplication.instance()
   if app is None:
       app = QApplication(sys.argv)
   ```

2. **Widget Not Visible**
   ```python
   # Add widget to qtbot and show
   qtbot.addWidget(widget)
   widget.show()
   qtbot.waitForWindowShown(widget)
   ```

3. **Mock Assertions Failing**
   ```python
   # Ensure mocks are properly configured
   mock_widget.method.return_value = expected_value
   mock_widget.method.assert_called_once_with(expected_args)
   ```

### Debug Mode
```bash
# Run tests with debug output
python -m pytest tests/ui/ -v -s --tb=long

# Run with Qt debug information
python -m pytest tests/ui/ -v --qt-log-level=DEBUG
```

## 📈 Performance Considerations

### Test Execution Speed
- Mock-based tests run quickly (< 1s per test)
- Integration tests may take longer (2-5s per test)
- Performance tests include timing assertions

### Memory Usage
- Tests use mocks to minimize memory footprint
- Large message history tests verify memory efficiency
- Cleanup ensures no memory leaks between tests

## 🤝 Contributing

### Adding New UI Tests

1. **Create Test File**
   ```python
   # tests/ui/test_new_component_ui.py
   import pytest
   from ui_fixtures import qtbot, mock_component
   
   class TestNewComponent:
       def test_component_functionality(self, qtbot, mock_component):
           # Test implementation
           pass
   ```

2. **Update Test Runner**
   ```python
   # Add new category to test_runner_ui.py
   def _run_new_component_tests(self):
       test_file = Path(__file__).parent / "test_new_component_ui.py"
       return self._run_pytest_file(test_file, "new_component")
   ```

3. **Update Documentation**
   - Add test description to this README
   - Document any new fixtures or test data
   - Update coverage information

### Best Practices

1. **Use Descriptive Test Names**
   ```python
   def test_send_message_with_special_characters_succeeds(self):
       # Clear what the test does and expected outcome
   ```

2. **Mock External Dependencies**
   ```python
   # Mock AI services, file systems, network calls
   @patch('gopiai.ui.components.ai_service')
   def test_with_mocked_service(self, mock_service):
       pass
   ```

3. **Test Both Success and Failure Cases**
   ```python
   def test_file_upload_success(self):
       # Test successful upload
       
   def test_file_upload_failure_handling(self):
       # Test error handling
   ```

4. **Use Appropriate Assertions**
   ```python
   # UI-specific assertions
   assert widget.isVisible()
   assert widget.text() == "Expected Text"
   mock_method.assert_called_once_with(expected_args)
   ```

## 📚 Additional Resources

- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [PySide6 Testing Guide](https://doc.qt.io/qtforpython/tutorials/index.html)
- [GopiAI UI Architecture](../../README.md)
- [Test Infrastructure Documentation](../../../test_infrastructure/README.md)

## 🏆 Test Results

Test results are automatically saved to:
- `ui_test_results.json`: Detailed JSON results
- `test_results_*.xml`: JUnit XML format for CI/CD
- `ui_coverage_html/`: HTML coverage reports (when using --coverage)

Example test execution output:
```
🎯 GopiAI UI Test Results Summary
================================================================================
Total Tests: 156
✅ Passed: 148
❌ Failed: 2
⏭️ Skipped: 6
⏱️ Duration: 45.2s
📊 Success Rate: 94.9%
================================================================================
```