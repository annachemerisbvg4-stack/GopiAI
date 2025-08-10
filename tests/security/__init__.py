#!/usr/bin/env python3
"""
Security tests package for GopiAI comprehensive testing system.

This package contains security tests covering all security requirements:
- 7.1: API protection against common attacks
- 7.2: Secret and API key management security
- 7.3: Authentication and session security
- 7.4: File system operation security

Test modules:
- test_api_security.py: API security tests for GopiAI-CrewAI
- test_ui_security.py: UI security tests for GopiAI-UI
- test_comprehensive_security.py: System-wide security tests
- test_runner_security.py: Security test runner and reporting
"""

__version__ = "1.0.0"
__author__ = "GopiAI Security Team"

# Import main test runner for convenience
from .test_runner_security import SecurityTestRunner

__all__ = ["SecurityTestRunner"]