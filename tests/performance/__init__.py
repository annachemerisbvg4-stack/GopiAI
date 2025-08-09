"""
Performance tests package for GopiAI system.

This package contains comprehensive performance tests covering:
- API endpoint benchmarks
- Memory system performance
- UI responsiveness testing
- System resource monitoring

Usage:
    # Run all performance tests
    python -m pytest tests/performance/
    
    # Run specific category
    python -m pytest tests/performance/test_api_benchmarks.py
    
    # Run performance suite
    python tests/performance/test_runner_performance.py
"""

__version__ = "1.0.0"
__author__ = "GopiAI Team"

# Import main classes for easy access
from .conftest import PerformanceMonitor, PerformanceMetrics, PerformanceAssertions
from .test_runner_performance import PerformanceTestRunner, run_performance_suite

__all__ = [
    'PerformanceMonitor',
    'PerformanceMetrics', 
    'PerformanceAssertions',
    'PerformanceTestRunner',
    'run_performance_suite'
]