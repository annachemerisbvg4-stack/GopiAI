# CrewAI Integration Tests

This directory contains comprehensive integration tests for the CrewAI API server, covering all REST endpoints, authentication, error handling, and external AI service integration.

## Test Structure

### Test Files

- **`test_api_endpoints.py`** - Tests all REST endpoints of the CrewAI server
- **`test_authentication.py`** - Tests authentication, authorization, and security
- **`test_error_handling.py`** - Tests error handling and recovery mechanisms
- **`test_external_ai_services.py`** - Tests integration with external AI services
- **`test_runner.py`** - Comprehensive test runner and coordinator

### Requirements Covered

- **Requirement 2.1**: API endpoint testing and integration
- **Requirement 2.2**: Service integration and authentication testing
- **Requirement 7.1**: API security testing

## Running Tests

### Prerequisites

1. **CrewAI Server**: The tests require the CrewAI server to be available
2. **Python Environment**: Tests should be run in the `crewai_env` environment
3. **Dependencies**: All test dependencies should be installed

### Quick Start

```bash
# Activate the CrewAI environment
call crewai_env\Scripts\activate.bat

# Run all integration tests
python tests/integration/test_runner.py

# Run specific test category
python tests/integration/test_runner.py --category api
python tests/integration/test_runner.py --category auth
python tests/integration/test_runner.py --category errors
python tests/integration/test_runner.py --category external
```

### Individual Test Files

```bash
# Run specific test file
pytest tests/integration/test_api_endpoints.py -v
pytest tests/integration/test_authentication.py -v
pytest tests/integration/test_error_handling.py -v
pytest tests/integration/test_external_ai_services.py -v
```

### Test Options

```bash
# Verbose output
python tests/integration/test_runner.py --verbose

# Quiet mode (errors only)
python tests/integration/test_runner.py --quiet

# Run with pytest directly
pytest tests/integration/ -v --tb=short
```

## Test Categories

### API Endpoints (`test_api_endpoints.py`)

Tests all REST endpoints of the CrewAI server:

- **Health Endpoint** (`/api/health`)
  - Basic health check functionality
  - Response headers and performance
  - Service status reporting

- **Process Endpoint** (`/api/process`)
  - Message processing requests
  - Request validation and error handling
  - Large message handling
  - Special character support

- **Task Endpoint** (`/api/task/<task_id>`)
  - Task status retrieval
  - Invalid task ID handling
  - Task lifecycle management

- **Debug Endpoint** (`/api/debug`)
  - System status information
  - Service readiness checks

- **Internal Endpoints** (`/internal/*`)
  - Model management
  - Provider state management
  - Configuration handling

- **Tools Endpoints** (`/api/tools`)
  - Tool listing and management
  - Tool state toggling
  - API key management

- **Settings Endpoints** (`/settings/*`)
  - Configuration retrieval
  - Settings updates
  - Terminal safety settings

### Authentication & Security (`test_authentication.py`)

Tests authentication, authorization, and security mechanisms:

- **API Key Validation**
  - Missing API key handling
  - Invalid API key handling
  - API key rotation
  - API key security (no exposure)

- **Access Control**
  - Internal endpoint access
  - Settings endpoint access
  - CORS header handling
  - Rate limiting behavior

- **Security Headers**
  - Security header presence
  - Sensitive header prevention
  - Content-Type validation

- **Session Management**
  - Request ID tracking
  - Concurrent session isolation
  - State management

- **Input Validation**
  - Malformed JSON handling
  - Content-Type validation
  - Unicode character handling

### Error Handling (`test_error_handling.py`)

Tests comprehensive error handling and recovery:

- **HTTP Error Handling**
  - 404 Not Found responses
  - 405 Method Not Allowed
  - 400 Bad Request handling
  - 413 Payload Too Large
  - Timeout handling
  - Connection error recovery

- **Service Error Handling**
  - AI service unavailable scenarios
  - RAG system unavailable handling
  - Database error handling
  - Concurrent request stress testing

- **Data Validation Errors**
  - Invalid JSON structure handling
  - Unicode validation errors
  - Field length validation
  - Nested data validation

- **Security Error Handling**
  - Injection attack prevention
  - Header injection prevention
  - DoS protection testing

- **Recovery Mechanisms**
  - Graceful degradation
  - Error logging and tracking
  - Circuit breaker behavior
  - Memory leak prevention

### External AI Services (`test_external_ai_services.py`)

Tests integration with external AI services:

- **OpenAI Integration**
  - Model availability testing
  - Authentication handling
  - Rate limiting handling
  - Error response handling

- **Anthropic Integration**
  - Claude model availability
  - Authentication handling
  - Content filtering testing

- **Google AI Integration**
  - Gemini model availability
  - Authentication handling
  - Multimodal support testing

- **OpenRouter Integration**
  - Model availability testing
  - Authentication handling

- **Provider Switching**
  - Provider state management
  - Model switching within providers
  - Invalid provider handling
  - Concurrent switching requests

- **Service Resilience**
  - Network timeout handling
  - Service unavailable fallback
  - Partial service degradation
  - API key rotation handling
  - Error propagation and logging

## Test Configuration

### Environment Variables

The tests respect the following environment variables:

- `OPENAI_API_KEY` - OpenAI API key for testing
- `ANTHROPIC_API_KEY` - Anthropic API key for testing
- `GOOGLE_API_KEY` - Google AI API key for testing
- `OPENROUTER_API_KEY` - OpenRouter API key for testing

### Test Data

Tests use mock data and avoid making actual API calls to external services when possible. Real API calls are only made when necessary for integration testing.

### Service Management

Tests automatically:
- Start the CrewAI server before testing
- Wait for server readiness
- Stop the server after testing
- Handle service failures gracefully

## Test Results

### Output Locations

- **Console Output**: Real-time test progress and results
- **Log Files**: Detailed logs in `~/.gopiai/logs/integration_tests.log`
- **JUnit XML**: Test results in `~/.gopiai/logs/junit_*.xml` format

### Success Criteria

Tests are considered successful when:
- All API endpoints respond correctly
- Authentication and security measures work properly
- Error handling is robust and informative
- External service integration is resilient
- No security vulnerabilities are detected

### Performance Benchmarks

- Health check responses: < 1 second
- API endpoint responses: < 30 seconds
- Concurrent request handling: 80%+ success rate
- Error recovery: Graceful degradation maintained

## Troubleshooting

### Common Issues

1. **Server Start Failure**
   - Check if port 5051 is available
   - Verify CrewAI environment is activated
   - Check for missing dependencies

2. **Test Timeouts**
   - Increase timeout values in test configuration
   - Check network connectivity
   - Verify server performance

3. **Authentication Failures**
   - Verify API keys are set correctly
   - Check environment variable names
   - Ensure keys have proper permissions

4. **External Service Errors**
   - Check API key validity
   - Verify service availability
   - Review rate limiting settings

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python tests/integration/test_runner.py --verbose
```

### Manual Testing

For manual testing of specific endpoints:

```bash
# Health check
curl http://localhost:5051/api/health

# Process request
curl -X POST http://localhost:5051/api/process \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "metadata": {}}'
```

## Contributing

When adding new integration tests:

1. Follow the existing test structure and naming conventions
2. Include proper error handling and cleanup
3. Add tests to the appropriate category
4. Update this README with new test descriptions
5. Ensure tests are independent and can run in any order

## Requirements Traceability

| Requirement | Test File | Test Classes |
|-------------|-----------|--------------|
| 2.1 - API endpoint testing | `test_api_endpoints.py` | All test classes |
| 2.2 - Service integration | `test_authentication.py`, `test_external_ai_services.py` | Authentication, External services |
| 7.1 - API security | `test_authentication.py`, `test_error_handling.py` | Security, Error handling |