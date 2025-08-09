# Performance Tests

This directory contains comprehensive performance tests for the GopiAI system, covering API benchmarks, memory system performance, UI responsiveness, and system resource monitoring.

## Overview

The performance test suite is designed to:
- Benchmark API endpoint response times and throughput
- Test memory system (txtai) indexing and search performance
- Verify UI responsiveness under various loads
- Monitor system resource usage (CPU, memory, disk I/O)
- Detect potential resource leaks and performance regressions

## Test Categories

### 1. API Performance Tests (`test_api_benchmarks.py`)

Tests the performance of CrewAI API server endpoints:

- **Health endpoint performance**: Response time and throughput
- **Models endpoint performance**: Model listing speed
- **Chat endpoint performance**: Message processing with different sizes
- **Concurrent user load**: Performance under multiple simultaneous users
- **Memory usage during requests**: Resource consumption monitoring
- **Sustained load testing**: Long-running performance validation

**Key Metrics:**
- Average response time (ms)
- Throughput (requests/second)
- Error rate (%)
- Memory usage (MB)
- CPU utilization (%)

### 2. Memory System Performance Tests (`test_memory_performance.py`)

Tests the txtai-based memory system performance:

- **Document indexing performance**: Speed of adding documents to index
- **Search performance**: Query response times and accuracy
- **Concurrent search performance**: Multiple simultaneous searches
- **Memory usage patterns**: Resource consumption during operations
- **Large dataset handling**: Performance with substantial document collections

**Key Metrics:**
- Documents indexed per second
- Search response time (ms)
- Memory usage during indexing (MB)
- Search accuracy vs performance tradeoffs
- Concurrent search throughput

### 3. UI Performance Tests (`test_ui_performance.py`)

Tests PySide6 UI application responsiveness:

- **Widget creation performance**: Time to create and display widgets
- **Text input responsiveness**: Typing and text processing speed
- **UI update frequency**: Refresh rates and update responsiveness
- **Chat widget performance**: Message handling and display speed
- **User interaction responsiveness**: Click and keyboard response times
- **Theme switching performance**: UI theme change speed

**Key Metrics:**
- Widget creation time (ms)
- Text input rate (characters/second)
- UI update frequency (updates/second)
- Interaction response time (ms)
- Memory usage during UI operations

### 4. System Monitoring Tests (`test_system_monitoring.py`)

Comprehensive system resource monitoring:

- **Baseline resource usage**: Normal system resource consumption
- **CPU usage under load**: Processor utilization patterns
- **Memory usage patterns**: RAM consumption and growth
- **Resource leak detection**: Memory, file handle, and thread leaks
- **Disk I/O monitoring**: File operation performance
- **Long-running stability**: Extended operation monitoring

**Key Metrics:**
- CPU utilization (%)
- Memory usage (MB) and growth patterns
- Disk I/O (MB read/write)
- Open file handles count
- Thread count
- Resource leak indicators

## Running Performance Tests

### Prerequisites

```bash
# Install required dependencies
pip install pytest pytest-qt psutil

# Ensure services are running (for API tests)
# Start CrewAI server on port 5051
# Start UI application (for UI tests)
```

### Running Individual Test Categories

```bash
# API performance tests
python -m pytest tests/performance/test_api_benchmarks.py -v

# Memory system performance tests
python -m pytest tests/performance/test_memory_performance.py -v

# UI performance tests (requires display)
python -m pytest tests/performance/test_ui_performance.py -v

# System monitoring tests
python -m pytest tests/performance/test_system_monitoring.py -v
```

### Running Complete Performance Suite

```bash
# Run all performance tests
python tests/performance/test_runner_performance.py

# Run specific categories
python tests/performance/test_runner_performance.py api,memory

# Run with custom pytest options
python -m pytest tests/performance/ -v --tb=short
```

### Running Benchmarks Directly

Each test module can be run directly for quick benchmarking:

```bash
# API benchmarks
python tests/performance/test_api_benchmarks.py

# Memory benchmarks
python tests/performance/test_memory_performance.py

# UI benchmarks (requires display)
python tests/performance/test_ui_performance.py

# System monitoring
python tests/performance/test_system_monitoring.py
```

## Configuration

Performance tests use configuration from `conftest.py`:

```python
benchmark_config = {
    'api_timeout': 30.0,
    'memory_threshold_mb': 500.0,
    'cpu_threshold_percent': 80.0,
    'response_time_threshold_ms': 5000.0,
    'ui_response_threshold_ms': 100.0,
    'search_response_threshold_ms': 1000.0,
    'concurrent_users': 5,
    'test_iterations': 10
}
```

### Customizing Thresholds

You can customize performance thresholds by modifying the `benchmark_config` fixture or setting environment variables:

```bash
export PERF_MEMORY_THRESHOLD_MB=1000
export PERF_CPU_THRESHOLD_PERCENT=90
export PERF_RESPONSE_TIME_THRESHOLD_MS=10000
```

## Test Markers

Performance tests use pytest markers for organization:

- `@pytest.mark.slow`: Long-running tests (>30 seconds)
- `@pytest.mark.skipif`: Conditional test execution
- `@pytest.mark.parametrize`: Multiple test scenarios

### Running Specific Test Types

```bash
# Skip slow tests
python -m pytest tests/performance/ -m "not slow"

# Run only slow tests
python -m pytest tests/performance/ -m "slow"

# Run with custom markers
python -m pytest tests/performance/ -m "api or memory"
```

## Performance Monitoring

### Real-time Monitoring

The `PerformanceMonitor` class provides real-time system monitoring:

```python
from tests.performance.conftest import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring(interval=0.1)

# Your code here

metrics = monitor.stop_monitoring()
```

### Resource Leak Detection

The `ResourceLeakDetector` helps identify memory and resource leaks:

```python
from tests.performance.test_system_monitoring import ResourceLeakDetector

detector = ResourceLeakDetector()
detector.set_baseline()

# Your operations here

leak_info = detector.check_for_leaks(threshold_mb=50.0)
```

## Performance Reports

### Automated Reports

The test runner generates comprehensive performance reports:

```json
{
  "summary": {
    "total_tests": 25,
    "passed": 23,
    "failed": 2,
    "success_rate": 92.0,
    "total_duration_ms": 45000,
    "avg_test_duration_ms": 1800
  },
  "categories": {
    "api": {"success_rate": 100.0, "avg_duration_ms": 2500},
    "memory": {"success_rate": 90.0, "avg_duration_ms": 3200},
    "ui": {"success_rate": 85.0, "avg_duration_ms": 1200},
    "system": {"success_rate": 95.0, "avg_duration_ms": 1500}
  },
  "performance_insights": [
    "MEMORY tests are slow (avg: 3200ms)",
    "UI has 2 failing performance tests"
  ],
  "recommendations": [
    "Optimize memory performance test execution time",
    "Address failing UI performance tests"
  ]
}
```

### Custom Reporting

You can generate custom performance reports:

```python
from tests.performance.test_runner_performance import PerformanceTestRunner

runner = PerformanceTestRunner()
report = runner.run_all_performance_tests(['api', 'memory'])
runner.save_report(report, 'custom_performance_report.json')
```

## Troubleshooting

### Common Issues

1. **API tests failing**: Ensure CrewAI server is running on port 5051
2. **UI tests skipped**: PySide6 not available or no display
3. **Memory tests slow**: Large document sets or limited system resources
4. **System monitoring errors**: Insufficient permissions for process monitoring

### Performance Optimization

1. **Reduce test iterations** for faster execution during development
2. **Use test markers** to run only relevant test categories
3. **Adjust thresholds** based on your system capabilities
4. **Run tests on dedicated hardware** for consistent results

### Debugging Performance Issues

```bash
# Run with verbose output
python -m pytest tests/performance/ -v -s

# Run with profiling
python -m pytest tests/performance/ --profile

# Run single test with debugging
python -m pytest tests/performance/test_api_benchmarks.py::TestAPIPerformance::test_health_endpoint_performance -v -s
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Performance Tests
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-qt psutil
      - name: Run performance tests
        run: |
          python tests/performance/test_runner_performance.py api,memory,system
      - name: Upload performance report
        uses: actions/upload-artifact@v2
        with:
          name: performance-report
          path: performance_report_*.json
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Performance Tests') {
            steps {
                sh 'python tests/performance/test_runner_performance.py'
                archiveArtifacts artifacts: 'performance_report_*.json'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'performance_report_*.json',
                    reportName: 'Performance Report'
                ])
            }
        }
    }
}
```

## Best Practices

1. **Consistent Environment**: Run tests on consistent hardware/environment
2. **Baseline Measurements**: Establish performance baselines for comparison
3. **Regular Monitoring**: Run performance tests regularly to catch regressions
4. **Threshold Management**: Adjust thresholds based on system capabilities
5. **Resource Cleanup**: Ensure proper cleanup to avoid test interference
6. **Documentation**: Document performance requirements and expectations

## Contributing

When adding new performance tests:

1. Follow the existing test structure and naming conventions
2. Include appropriate performance assertions and thresholds
3. Add comprehensive docstrings and comments
4. Update this README with new test descriptions
5. Ensure tests are deterministic and reliable
6. Include both positive and negative test scenarios

## Support

For issues with performance tests:

1. Check the troubleshooting section above
2. Review test logs and error messages
3. Verify system requirements and dependencies
4. Check for known issues in the project documentation
5. Create an issue with detailed reproduction steps