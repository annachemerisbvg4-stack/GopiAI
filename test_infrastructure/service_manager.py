#!/usr/bin/env python3
"""
Service Management System for GopiAI Testing Infrastructure

Manages the lifecycle of services required for testing, including:
- CrewAI API server
- UI application (for E2E tests)
- Memory system (txtai)
- Test data isolation
"""

import os
import sys
import time
import json
import signal
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import requests
import psutil


class ServiceStatus(Enum):
    """Service status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceConfig:
    """Configuration for a service."""
    name: str
    command: List[str]
    working_directory: str
    environment_vars: Dict[str, str]
    health_check_url: Optional[str] = None
    health_check_timeout: int = 30
    startup_timeout: int = 60
    port: Optional[int] = None
    log_file: Optional[str] = None


@dataclass
class ServiceInfo:
    """Information about a running service."""
    name: str
    status: ServiceStatus
    pid: Optional[int] = None
    port: Optional[int] = None
    process: Optional[subprocess.Popen] = None
    start_time: Optional[float] = None
    log_file: Optional[str] = None


class ServiceManager:
    """Manages services required for testing."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.services: Dict[str, ServiceInfo] = {}
        self.logger = self._setup_logging()
        self.test_mode = True
        self._shutdown_handlers_registered = False
        
        # Service configurations
        self.service_configs = self._create_service_configs()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the service manager."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _create_service_configs(self) -> Dict[str, ServiceConfig]:
        """Create service configurations."""
        configs = {}
        
        # CrewAI API Server
        crewai_env_path = self.root_path / "GopiAI-CrewAI"
        crewai_python = self._get_environment_python("crewai_env")
        
        if crewai_python and crewai_env_path.exists():
            configs["crewai_server"] = ServiceConfig(
                name="crewai_server",
                command=[str(crewai_python), "crewai_api_server.py"],
                working_directory=str(crewai_env_path),
                environment_vars={
                    "GOPIAI_ENV": "test",
                    "CREWAI_TEST_MODE": "true",
                    "FLASK_ENV": "testing"
                },
                health_check_url="http://localhost:5051/health",
                port=5051,
                log_file="test_crewai_server.log"
            )
        
        # UI Application (for E2E tests)
        ui_env_path = self.root_path / "GopiAI-UI"
        ui_python = self._get_environment_python("gopiai_env")
        
        if ui_python and ui_env_path.exists():
            configs["ui_app"] = ServiceConfig(
                name="ui_app",
                command=[str(ui_python), "-m", "gopiai.ui.main", "--test-mode"],
                working_directory=str(ui_env_path),
                environment_vars={
                    "GOPIAI_ENV": "test",
                    "QT_QPA_PLATFORM": "offscreen",  # For headless testing
                    "DISPLAY": ":99"  # Virtual display
                },
                startup_timeout=30,
                log_file="test_ui_app.log"
            )
        
        # Memory System (txtai) - if needed separately
        txtai_env_path = self.root_path / "rag_memory_system"
        txtai_python = self._get_environment_python("txtai_env")
        
        if txtai_python and txtai_env_path.exists():
            configs["memory_system"] = ServiceConfig(
                name="memory_system",
                command=[str(txtai_python), "memory_server.py"],
                working_directory=str(txtai_env_path),
                environment_vars={
                    "GOPIAI_ENV": "test",
                    "TXTAI_TEST_MODE": "true"
                },
                health_check_url="http://localhost:8000/health",
                port=8000,
                log_file="test_memory_system.log"
            )
        
        return configs
    
    def _get_environment_python(self, env_name: str) -> Optional[Path]:
        """Get Python executable for a specific environment."""
        env_path = self.root_path / env_name
        
        # Windows
        python_exe = env_path / "Scripts" / "python.exe"
        if python_exe.exists():
            return python_exe
        
        # Unix
        python_exe = env_path / "bin" / "python"
        if python_exe.exists():
            return python_exe
        
        return None
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.service_configs:
            self.logger.error(f"Service {service_name} not configured")
            return False
        
        if service_name in self.services:
            current_status = self.services[service_name].status
            if current_status == ServiceStatus.RUNNING:
                self.logger.info(f"Service {service_name} is already running")
                return True
            elif current_status == ServiceStatus.STARTING:
                self.logger.info(f"Service {service_name} is already starting")
                return self._wait_for_service_start(service_name)
        
        config = self.service_configs[service_name]
        self.logger.info(f"Starting service: {service_name}")
        
        # Create service info
        service_info = ServiceInfo(
            name=service_name,
            status=ServiceStatus.STARTING,
            port=config.port,
            start_time=time.time()
        )
        self.services[service_name] = service_info
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(config.environment_vars)
            
            # Prepare log file
            if config.log_file:
                log_path = Path(config.working_directory) / config.log_file
                service_info.log_file = str(log_path)
                log_file = open(log_path, 'w')
            else:
                log_file = subprocess.PIPE
            
            # Start the process
            process = subprocess.Popen(
                config.command,
                cwd=config.working_directory,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            service_info.process = process
            service_info.pid = process.pid
            
            # Wait for service to start
            if self._wait_for_service_start(service_name):
                service_info.status = ServiceStatus.RUNNING
                self.logger.info(f"Service {service_name} started successfully (PID: {process.pid})")
                
                # Register shutdown handlers
                if not self._shutdown_handlers_registered:
                    self._register_shutdown_handlers()
                
                return True
            else:
                service_info.status = ServiceStatus.ERROR
                self.logger.error(f"Service {service_name} failed to start")
                self._cleanup_failed_service(service_name)
                return False
                
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            self.logger.error(f"Failed to start service {service_name}: {e}")
            return False
    
    def _wait_for_service_start(self, service_name: str) -> bool:
        """Wait for a service to start and become healthy."""
        config = self.service_configs[service_name]
        service_info = self.services[service_name]
        
        start_time = time.time()
        timeout = config.startup_timeout
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if service_info.process and service_info.process.poll() is not None:
                self.logger.error(f"Service {service_name} process terminated unexpectedly")
                return False
            
            # Check health endpoint if available
            if config.health_check_url:
                try:
                    response = requests.get(
                        config.health_check_url,
                        timeout=config.health_check_timeout
                    )
                    if response.status_code == 200:
                        return True
                except requests.RequestException:
                    pass
            else:
                # For services without health check, just wait a bit
                if time.time() - start_time > 5:  # Give it 5 seconds
                    return True
            
            time.sleep(1)
        
        return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            self.logger.warning(f"Service {service_name} is not running")
            return True
        
        service_info = self.services[service_name]
        if service_info.status == ServiceStatus.STOPPED:
            return True
        
        self.logger.info(f"Stopping service: {service_name}")
        service_info.status = ServiceStatus.STOPPING
        
        try:
            if service_info.process:
                # Try graceful shutdown first
                service_info.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    service_info.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.logger.warning(f"Force killing service {service_name}")
                    service_info.process.kill()
                    service_info.process.wait()
                
                service_info.status = ServiceStatus.STOPPED
                service_info.process = None
                service_info.pid = None
                
                self.logger.info(f"Service {service_name} stopped successfully")
                return True
            
        except Exception as e:
            self.logger.error(f"Error stopping service {service_name}: {e}")
            service_info.status = ServiceStatus.ERROR
            return False
        
        return True
    
    def _cleanup_failed_service(self, service_name: str):
        """Clean up a failed service."""
        if service_name in self.services:
            service_info = self.services[service_name]
            if service_info.process:
                try:
                    service_info.process.kill()
                    service_info.process.wait()
                except:
                    pass
            del self.services[service_name]
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get the status of a service."""
        if service_name not in self.services:
            return ServiceStatus.STOPPED
        
        service_info = self.services[service_name]
        
        # Check if process is still running
        if service_info.process and service_info.process.poll() is not None:
            service_info.status = ServiceStatus.STOPPED
            service_info.process = None
            service_info.pid = None
        
        return service_info.status
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy."""
        if service_name not in self.service_configs:
            return False
        
        config = self.service_configs[service_name]
        
        # Check if service is running
        if self.get_service_status(service_name) != ServiceStatus.RUNNING:
            return False
        
        # Check health endpoint if available
        if config.health_check_url:
            try:
                response = requests.get(
                    config.health_check_url,
                    timeout=config.health_check_timeout
                )
                return response.status_code == 200
            except requests.RequestException:
                return False
        
        # If no health check URL, assume healthy if running
        return True
    
    def start_all_services(self) -> bool:
        """Start all configured services."""
        self.logger.info("Starting all services...")
        
        success = True
        for service_name in self.service_configs:
            if not self.start_service(service_name):
                success = False
        
        if success:
            self.logger.info("All services started successfully")
        else:
            self.logger.error("Some services failed to start")
        
        return success
    
    def stop_all_services(self) -> bool:
        """Stop all running services."""
        self.logger.info("Stopping all services...")
        
        success = True
        for service_name in list(self.services.keys()):
            if not self.stop_service(service_name):
                success = False
        
        if success:
            self.logger.info("All services stopped successfully")
        else:
            self.logger.error("Some services failed to stop cleanly")
        
        return success
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service."""
        self.logger.info(f"Restarting service: {service_name}")
        
        if not self.stop_service(service_name):
            return False
        
        # Wait a moment before restarting
        time.sleep(2)
        
        return self.start_service(service_name)
    
    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """Get detailed information about a service."""
        return self.services.get(service_name)
    
    def list_services(self) -> Dict[str, ServiceInfo]:
        """List all services and their status."""
        return self.services.copy()
    
    def setup_test_isolation(self):
        """Set up test data isolation."""
        self.logger.info("Setting up test data isolation...")
        
        # Create test-specific directories
        test_dirs = [
            "test_conversations",
            "test_memory",
            "test_logs",
            "test_cache"
        ]
        
        for dir_name in test_dirs:
            test_dir = self.root_path / dir_name
            test_dir.mkdir(exist_ok=True)
        
        # Set environment variables for test isolation
        os.environ["GOPIAI_CONVERSATIONS_DIR"] = str(self.root_path / "test_conversations")
        os.environ["GOPIAI_MEMORY_DIR"] = str(self.root_path / "test_memory")
        os.environ["GOPIAI_LOGS_DIR"] = str(self.root_path / "test_logs")
        os.environ["GOPIAI_CACHE_DIR"] = str(self.root_path / "test_cache")
        
        self.logger.info("Test data isolation configured")
    
    def cleanup_test_data(self):
        """Clean up test data after tests complete."""
        self.logger.info("Cleaning up test data...")
        
        import shutil
        
        test_dirs = [
            "test_conversations",
            "test_memory", 
            "test_logs",
            "test_cache"
        ]
        
        for dir_name in test_dirs:
            test_dir = self.root_path / dir_name
            if test_dir.exists():
                try:
                    shutil.rmtree(test_dir)
                    self.logger.debug(f"Removed test directory: {test_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove test directory {test_dir}: {e}")
        
        self.logger.info("Test data cleanup completed")
    
    def _register_shutdown_handlers(self):
        """Register handlers to clean up services on shutdown."""
        def cleanup_handler(signum, frame):
            self.logger.info("Received shutdown signal, cleaning up services...")
            self.stop_all_services()
            self.cleanup_test_data()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
        
        self._shutdown_handlers_registered = True
    
    def __enter__(self):
        """Context manager entry."""
        self.setup_test_isolation()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_all_services()
        self.cleanup_test_data()


# Convenience functions for common operations
def start_crewai_server() -> bool:
    """Start only the CrewAI server."""
    manager = ServiceManager()
    return manager.start_service("crewai_server")


def stop_crewai_server() -> bool:
    """Stop the CrewAI server."""
    manager = ServiceManager()
    return manager.stop_service("crewai_server")


def check_crewai_health() -> bool:
    """Check if CrewAI server is healthy."""
    manager = ServiceManager()
    return manager.check_service_health("crewai_server")


# Test utilities
class TestServiceManager:
    """Simplified service manager for testing."""
    
    def __init__(self):
        self.manager = ServiceManager()
    
    def __enter__(self):
        self.manager.setup_test_isolation()
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.stop_all_services()
        self.manager.cleanup_test_data()


if __name__ == "__main__":
    # Command-line interface for service management
    import argparse
    
    parser = argparse.ArgumentParser(description="GopiAI Service Manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "health"])
    parser.add_argument("--service", help="Specific service name")
    parser.add_argument("--all", action="store_true", help="Apply to all services")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.action == "start":
        if args.all:
            success = manager.start_all_services()
        elif args.service:
            success = manager.start_service(args.service)
        else:
            print("Specify --service or --all")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.action == "stop":
        if args.all:
            success = manager.stop_all_services()
        elif args.service:
            success = manager.stop_service(args.service)
        else:
            print("Specify --service or --all")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.action == "restart":
        if args.service:
            success = manager.restart_service(args.service)
        else:
            print("Specify --service for restart")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        services = manager.list_services()
        if not services:
            print("No services running")
        else:
            for name, info in services.items():
                print(f"{name}: {info.status.value} (PID: {info.pid})")
    
    elif args.action == "health":
        if args.service:
            healthy = manager.check_service_health(args.service)
            print(f"{args.service}: {'healthy' if healthy else 'unhealthy'}")
            sys.exit(0 if healthy else 1)
        else:
            all_healthy = True
            for service_name in manager.service_configs:
                healthy = manager.check_service_health(service_name)
                print(f"{service_name}: {'healthy' if healthy else 'unhealthy'}")
                if not healthy:
                    all_healthy = False
            sys.exit(0 if all_healthy else 1)