# Security Tests

This directory contains comprehensive security tests for the GopiAI system, covering all security requirements (7.1, 7.2, 7.3, 7.4).

## Test Structure

### API Security Tests (`test_api_security.py`)
- **SQL Injection Protection**: Tests protection against SQL injection attacks
- **XSS Protection**: Tests protection against Cross-Site Scripting attacks
- **CSRF Protection**: Tests protection against Cross-Site Request Forgery
- **Input Validation**: Tests comprehensive input validation and sanitization
- **Rate Limiting**: Tests API rate limiting protection

### UI Security Tests (`test_ui_security.py`)
- **Input Sanitization**: Tests UI input validation and sanitization
- **Secret Management**: Tests masking of sensitive data in UI
- **Session Security**: Tests UI session management and timeout handling
- **File System Security**: Tests secure file operations in UI

### Comprehensive Security Tests (`test_comprehensive_security.py`)
- **System-wide Security**: Tests security across all modules
- **Communication Security**: Tests inter-module communication security
- **Data Protection**: Tests data encryption and PII handling
- **Security Monitoring**: Tests security event logging and intrusion detection

## Requirements Coverage

### Requirement 7.1: API Protection
- ✅ SQL injection protection tests
- ✅ XSS protection tests
- ✅ CSRF protection tests
- ✅ Input validation and sanitization tests
- ✅ Rate limiting tests

### Requirement 7.2: Secret Management
- ✅ API key protection in logs
- ✅ API key protection in responses
- ✅ Environment variable security
- ✅ Secret masking in debug output
- ✅ UI password field masking
- ✅ API key display masking

### Requirement 7.3: Authentication Security
- ✅ Session token validation
- ✅ Session hijacking protection
- ✅ Authentication bypass protection
- ✅ Session timeout handling
- ✅ Auto-logout on inactivity
- ✅ Secure credential storage

### Requirement 7.4: File System Security
- ✅ Directory traversal protection
- ✅ File access permissions
- ✅ File upload security
- ✅ Temporary file security
- ✅ File dialog path validation
- ✅ File type validation
- ✅ Drag and drop security

## Running Security Tests

### Run All Security Tests
```bash
pytest tests/security/ -v
```

### Run Specific Security Test Categories
```bash
# API security tests
pytest tests/security/test_api_security.py -v

# UI security tests
pytest tests/security/test_ui_security.py -v

# Comprehensive security tests
pytest tests/security/test_comprehensive_security.py -v
```

### Run Tests by Security Requirement
```bash
# Tests for API protection (Requirement 7.1)
pytest tests/security/ -k "injection or xss or csrf or validation" -v

# Tests for secret management (Requirement 7.2)
pytest tests/security/ -k "secret or api_key or password" -v

# Tests for authentication (Requirement 7.3)
pytest tests/security/ -k "auth or session or token" -v

# Tests for file system security (Requirement 7.4)
pytest tests/security/ -k "file or path or upload" -v
```

### Run Tests with Security Markers
```bash
# Run all security tests
pytest -m security -v

# Run tests that require a running server
pytest -m "security and requires_server" -v

# Run slow security tests
pytest -m "security and slow_security" -v
```

## Test Configuration

### Environment Variables
The security tests use the following environment variables:
- `TESTING=true`: Indicates test mode
- `DEBUG=false`: Disables debug mode for security tests
- `OPENAI_API_KEY`: Mock API key for testing (automatically set)
- `ANTHROPIC_API_KEY`: Mock API key for testing (automatically set)

### Mock Services
Security tests use mock services to avoid dependencies on external systems:
- **Mock API Server**: Simulates the CrewAI API server
- **Mock Secure Storage**: Simulates encrypted credential storage
- **Mock File System**: Simulates file system operations
- **Mock Logger**: Captures security event logs

### Test Data
Common test data is provided through fixtures:
- **Malicious Inputs**: XSS, SQL injection, path traversal attempts
- **Safe Inputs**: Normal user input for comparison
- **API Keys**: Mock API keys for testing secret handling
- **Sensitive Patterns**: Regex patterns for detecting sensitive data

## Security Test Best Practices

### 1. Test Isolation
- Each test is isolated and doesn't affect others
- Mock services prevent external dependencies
- Temporary files are cleaned up automatically

### 2. Comprehensive Coverage
- Tests cover both positive and negative scenarios
- Edge cases and boundary conditions are tested
- All security requirements are mapped to specific tests

### 3. Realistic Attack Scenarios
- Tests simulate real-world attack patterns
- Multiple attack vectors are tested for each vulnerability
- Tests include both automated and manual attack scenarios

### 4. Performance Considerations
- Security tests are designed to run quickly
- Heavy operations use mocks and stubs
- Parallel execution is supported where safe

## Known Issues and Limitations

### Current Limitations
- Some tests use mock implementations instead of real security libraries
- Windows-specific file permission tests are limited
- Network-based attacks require manual testing with real services

### Future Improvements
- Integration with real security scanning tools
- Automated penetration testing
- Performance impact analysis of security measures
- Integration with CI/CD security pipelines

## Security Test Maintenance

### Adding New Security Tests
1. Identify the security requirement being tested
2. Create test cases for both positive and negative scenarios
3. Use appropriate fixtures and mocks
4. Add proper markers and documentation
5. Update this README with new test information

### Updating Existing Tests
1. Ensure backward compatibility
2. Update test data and scenarios as needed
3. Maintain comprehensive coverage
4. Update documentation and comments

### Security Test Review Process
1. All security tests should be reviewed by security-aware developers
2. Test scenarios should be validated against current threat models
3. Regular updates should be made based on new security vulnerabilities
4. Performance impact of security tests should be monitored

## Integration with CI/CD

Security tests are designed to integrate with continuous integration pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Security Tests
  run: |
    pytest tests/security/ -v --tb=short
    pytest -m security --cov=gopiai --cov-report=xml
```

## Reporting Security Issues

If security tests reveal actual vulnerabilities:
1. Do not commit the failing test until the vulnerability is fixed
2. Report the issue through appropriate security channels
3. Create a secure test case that will pass once the issue is resolved
4. Document the fix and update related tests

## References

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Qt Security Guidelines](https://doc.qt.io/qt-6/security.html)