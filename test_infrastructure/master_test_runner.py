#!/usr/bin/env python3
"""
Master Test Runner for GopiAI Testing Infrastructure

This module provides a unified interface for running tests across all GopiAI modules
with proper environment management and service coordination.
"""

import os
import sys
import subprocess
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import argparse

from test_discovery import TestDiscovery, TestCategory, TestEnvironment
from problem_discovery import ProblemDiscovery

# Try to import service manager, but handle gracefully if not available
try:
    from service_manager import ServiceManager
    SERVICE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ServiceManager not available: {e}")
    SERVICE_MANAGER_AVAILABLE = False
    
    class MockServiceManager:
        """Mock service manager for when the real one is not available."""
        def start_crewai_server(self): return True
        def start_ui_application(self): return True
        def start_memory_system(self): return True
        def stop_all_services(self): return True
        def start_all_services(self): return True
        def check_service_health(self, service): return True
    
    ServiceManager = MockServiceManager


class TestResult(Enum):
    """Test execution results."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestExecution:
    """Represents a test execution result."""
    module: str
    category: str
    environment: str
    command: str
    result: TestResult
    duration: float
    output: str
    error_output: str
    exit_code: int


class MasterTestRunner:
    """Master test runner for all GopiAI modules."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.logger = logging.getLogger(__name__)
        if SERVICE_MANAGER_AVAILABLE:
            self.service_manager = ServiceManager()
        else:
            self.service_manager = MockServiceManager()
            self.logger.warning("Using mock service manager - services will not be started")
        self.test_discovery = TestDiscovery(root_path)
        self.problem_discovery = ProblemDiscovery(root_path)
        
        # Test execution results
        self.executions: List[TestExecution] = []
        
        # Environment configurations
        self.env_configs = {
            TestEnvironment.CREWAI_ENV: {
                "venv_path": self.root_path / "GopiAI-CrewAI" / "crewai_env",
                "python_path": self.root_path / "GopiAI-CrewAI" / "crewai_env" / "Scripts" / "python.exe",
                "activate_script": self.root_path / "GopiAI-CrewAI" / "crewai_env" / "Scripts" / "activate.bat",
            },
            TestEnvironment.GOPIAI_ENV: {
                "venv_path": self.root_path / "gopiai_env",
                "python_path": self.root_path / "gopiai_env" / "Scripts" / "python.exe",
                "activate_script": self.root_path / "gopiai_env" / "Scripts" / "activate.bat",
            },
            TestEnvironment.TXTAI_ENV: {
                "venv_path": self.root_path / "txtai_env",
                "python_path": self.root_path / "txtai_env" / "Scripts" / "python.exe",
                "activate_script": self.root_path / "txtai_env" / "Scripts" / "activate.bat",
            }
        }

    def run_all_tests(self, 
                     categories: Optional[List[TestCategory]] = None,
                     environments: Optional[List[TestEnvironment]] = None,
                     parallel: bool = False,
                     generate_reports: bool = True) -> Dict:
        """Run all tests with specified filters."""
        self.logger.info("Starting master test runner")
        
        # Discover tests
        test_modules = self.test_discovery.discover_all_tests()
        self.logger.info(f"Discovered {len(test_modules)} test modules")
        
        # Filter tests if specified
        if categories:
            test_modules = [m for m in test_modules if m.category in categories]
        if environments:
            test_modules = [m for m in test_modules if m.environment in environments]
        
        self.logger.info(f"Running {len(test_modules)} test modules after filtering")
        
        # Group tests by environment for efficient execution
        env_groups = {}
        for module in test_modules:
            if module.environment not in env_groups:
                env_groups[module.environment] = []
            env_groups[module.environment].append(module)
        
        # Execute tests by environment
        for environment, modules in env_groups.items():
            self.logger.info(f"Running tests in environment: {environment.value}")
            self._run_environment_tests(environment, modules, parallel)
        
        # Generate reports if requested
        if generate_reports:
            self._generate_execution_report()
            self._generate_problem_report()
        
        return self._create_summary()

    def run_unit_tests(self, modules: Optional[List[str]] = None) -> Dict:
        """Run unit tests for specified modules."""
        return self.run_all_tests(
            categories=[TestCategory.UNIT],
            environments=None
        )

    def run_integration_tests(self, services: Optional[List[str]] = None) -> Dict:
        """Run integration tests with optional service filtering."""
        # Start required services
        if services is None or "crewai_server" in services:
            self.service_manager.start_crewai_server()
        
        try:
            return self.run_all_tests(
                categories=[TestCategory.INTEGRATION],
                environments=None
            )
        finally:
            # Clean up services
            self.service_manager.stop_all_services()

    def run_ui_tests(self, components: Optional[List[str]] = None) -> Dict:
        """Run UI tests with optional component filtering."""
        return self.run_all_tests(
            categories=[TestCategory.UI],
            environments=[TestEnvironment.GOPIAI_ENV]
        )

    def run_e2e_tests(self, scenarios: Optional[List[str]] = None) -> Dict:
        """Run end-to-end tests with optional scenario filtering."""
        # Start all required services
        self.service_manager.start_all_services()
        
        try:
            return self.run_all_tests(
                categories=[TestCategory.E2E],
                environments=None
            )
        finally:
            # Clean up services
            self.service_manager.stop_all_services()

    def run_performance_tests(self) -> Dict:
        """Run performance tests."""
        return self.run_all_tests(
            categories=[TestCategory.PERFORMANCE],
            environments=None
        )

    def run_security_tests(self) -> Dict:
        """Run security tests."""
        return self.run_all_tests(
            categories=[TestCategory.SECURITY],
            environments=None
        )

    def _run_environment_tests(self, 
                              environment: TestEnvironment, 
                              modules: List, 
                              parallel: bool = False):
        """Run tests in a specific environment."""
        env_config = self.env_configs[environment]
        
        # Check if environment exists
        if not env_config["venv_path"].exists():
            self.logger.error(f"Environment {environment.value} not found at {env_config['venv_path']}")
            return
        
        # Group modules by GopiAI module for efficient execution
        module_groups = {}
        for test_module in modules:
            gopiai_module = test_module.module_name
            if gopiai_module not in module_groups:
                module_groups[gopiai_module] = []
            module_groups[gopiai_module].append(test_module)
        
        # Execute tests for each GopiAI module
        for gopiai_module, test_modules in module_groups.items():
            self._run_module_tests(gopiai_module, test_modules, environment)

    def _run_module_tests(self, 
                         gopiai_module: str, 
                         test_modules: List, 
                         environment: TestEnvironment):
        """Run tests for a specific GopiAI module."""
        self.logger.info(f"Running tests for {gopiai_module} in {environment.value}")
        
        env_config = self.env_configs[environment]
        module_path = self.root_path / gopiai_module
        
        if not module_path.exists():
            self.logger.error(f"Module path {module_path} does not exist")
            return
        
        # Build pytest command
        python_exe = env_config["python_path"]
        
        # Group test modules by category for organized execution
        category_groups = {}
        for test_module in test_modules:
            category = test_module.category
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(test_module)
        
        # Execute tests by category
        for category, modules in category_groups.items():
            test_files = [module.file_path for module in modules]
            self._execute_pytest_command(
                gopiai_module, 
                category.value, 
                environment.value,
                python_exe, 
                module_path, 
                test_files
            )

    def _execute_pytest_command(self, 
                               module: str, 
                               category: str, 
                               environment: str,
                               python_exe: Path, 
                               module_path: Path, 
                               test_files: List[str]):
        """Execute a pytest command and record results."""
        # Build command
        cmd = [
            str(python_exe),
            "-m", "pytest",
            "-v",
            "--tb=short",
            "--color=yes",
            f"--junitxml=test_results_{module}_{category}.xml"
        ]
        
        # Add HTML report if pytest-html is available
        try:
            import pytest_html
            cmd.extend([f"--html=test_report_{module}_{category}.html", "--self-contained-html"])
        except ImportError:
            self.logger.debug("pytest-html not available, skipping HTML report generation")
        
        # Add test files (convert to forward slashes for cross-platform compatibility)
        for test_file in test_files:
            test_path = str(self.root_path / test_file).replace('\\', '/')
            cmd.append(test_path)
        
        self.logger.info(f"Executing: {' '.join(cmd)}")
        
        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=module_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Determine result status
            if result.returncode == 0:
                status = TestResult.PASSED
            elif result.returncode == 5:  # No tests collected
                status = TestResult.SKIPPED
            else:
                status = TestResult.FAILED
            
            # Record execution
            execution = TestExecution(
                module=module,
                category=category,
                environment=environment,
                command=' '.join(cmd),
                result=status,
                duration=duration,
                output=result.stdout,
                error_output=result.stderr,
                exit_code=result.returncode
            )
            
            self.executions.append(execution)
            
            self.logger.info(f"Test execution completed: {status.value} in {duration:.2f}s")
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            execution = TestExecution(
                module=module,
                category=category,
                environment=environment,
                command=' '.join(cmd),
                result=TestResult.ERROR,
                duration=duration,
                output="",
                error_output="Test execution timed out",
                exit_code=-1
            )
            
            self.executions.append(execution)
            self.logger.error(f"Test execution timed out after {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            execution = TestExecution(
                module=module,
                category=category,
                environment=environment,
                command=' '.join(cmd),
                result=TestResult.ERROR,
                duration=duration,
                output="",
                error_output=str(e),
                exit_code=-1
            )
            
            self.executions.append(execution)
            self.logger.error(f"Test execution failed: {e}")

    def _generate_execution_report(self):
        """Generate a comprehensive test execution report."""
        report = {
            "summary": {
                "total_executions": len(self.executions),
                "total_duration": sum(e.duration for e in self.executions),
                "by_result": {},
                "by_module": {},
                "by_category": {},
                "by_environment": {}
            },
            "executions": []
        }
        
        # Convert executions to serializable format
        for execution in self.executions:
            exec_dict = asdict(execution)
            exec_dict["result"] = execution.result.value
            report["executions"].append(exec_dict)
        
        # Calculate summary statistics
        for execution in self.executions:
            # By result
            result = execution.result.value
            report["summary"]["by_result"][result] = report["summary"]["by_result"].get(result, 0) + 1
            
            # By module
            module = execution.module
            report["summary"]["by_module"][module] = report["summary"]["by_module"].get(module, 0) + 1
            
            # By category
            category = execution.category
            report["summary"]["by_category"][category] = report["summary"]["by_category"].get(category, 0) + 1
            
            # By environment
            environment = execution.environment
            report["summary"]["by_environment"][environment] = report["summary"]["by_environment"].get(environment, 0) + 1
        
        # Write report
        report_file = "test_execution_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Test execution report written to {report_file}")

    def _generate_problem_report(self):
        """Generate a problem discovery report."""
        problems = self.problem_discovery.discover_all_problems()
        self.problem_discovery.generate_report("test_problems_report.json")
        self.problem_discovery.generate_pytest_markers("test_known_issues.py")

    def _create_summary(self) -> Dict:
        """Create a summary of test execution results."""
        summary = {
            "total_executions": len(self.executions),
            "passed": len([e for e in self.executions if e.result == TestResult.PASSED]),
            "failed": len([e for e in self.executions if e.result == TestResult.FAILED]),
            "skipped": len([e for e in self.executions if e.result == TestResult.SKIPPED]),
            "errors": len([e for e in self.executions if e.result == TestResult.ERROR]),
            "total_duration": sum(e.duration for e in self.executions),
            "success_rate": 0.0
        }
        
        if summary["total_executions"] > 0:
            summary["success_rate"] = summary["passed"] / summary["total_executions"] * 100
        
        return summary


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="GopiAI Master Test Runner")
    parser.add_argument("--category", choices=["unit", "integration", "ui", "e2e", "performance", "security"],
                       help="Run tests of specific category")
    parser.add_argument("--environment", choices=["crewai_env", "gopiai_env", "txtai_env"],
                       help="Run tests in specific environment")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--no-reports", action="store_true", help="Skip report generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create runner
    runner = MasterTestRunner()
    
    # Determine what to run
    categories = None
    if args.category:
        categories = [TestCategory(args.category)]
    
    environments = None
    if args.environment:
        environments = [TestEnvironment(args.environment)]
    
    # Run tests
    summary = runner.run_all_tests(
        categories=categories,
        environments=environments,
        parallel=args.parallel,
        generate_reports=not args.no_reports
    )
    
    # Print summary
    print("\n" + "="*50)
    print("TEST EXECUTION SUMMARY")
    print("="*50)
    print(f"Total executions: {summary['total_executions']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    print(f"Total duration: {summary['total_duration']:.2f}s")
    print("="*50)
    
    # Exit with appropriate code
    if summary['failed'] > 0 or summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()