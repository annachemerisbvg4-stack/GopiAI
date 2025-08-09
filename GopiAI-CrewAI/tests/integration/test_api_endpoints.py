#!/usr/bin/env python3
"""
Integration Tests for CrewAI API Endpoints

Tests all REST endpoints of the CrewAI server to ensure proper functionality,
error handling, and integration with external services.

Requirements covered:
- 2.1: API endpoint testing
- 2.2: Service integration testing  
- 7.1: API security testing
"""

import pytest
import requests
import json
import time
import uuid
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock

try:
    from test_infrastructure.service_manager import ServiceManager
except ImportError:
    from .mock_service_manager import MockServiceManager as ServiceManager

try:
    from test_infrastructure.crewai_fixtures import (
        mock_openrouter_client,
        mock_state_manager,
        crewai_test_config
    )
except ImportError:
    # Mock fixtures if not available
    def mock_openrouter_client():
        return None
    def mock_state_manager():
        return None
    def crewai_test_config():
        return {}


class TestAPIEndpoints:
    """Test all CrewAI API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup_service(self):
        """Set up CrewAI server for testing."""
        self.base_url = "http://localhost:5051"
        self.service_manager = ServiceManager()
        
        # Start CrewAI server
        if not self.service_manager.start_service("crewai_server"):
            pytest.skip("CrewAI server failed to start")
        
        # Wait for server to be ready
        self._wait_for_server_ready()
        
        yield
        
        # Cleanup
        self.service_manager.stop_service("crewai_server")
    
    def _wait_for_server_ready(self, timeout: int = 30):
        """Wait for server to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(1)
        
        pytest.fail("Server did not become ready within timeout")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.RequestException as e:
            pytest.fail(f"Request failed: {e}")


class TestHealthEndpoint(TestAPIEndpoints):
    """Test /api/health endpoint."""
    
    def test_health_check_success(self):
        """Test successful health check."""
        response = self._make_request("GET", "/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["online", "limited_mode"]
        assert "rag_status" in data
        assert "indexed_documents" in data
        assert isinstance(data["indexed_documents"], int)
    
    def test_health_check_headers(self):
        """Test health check response headers."""
        response = self._make_request("GET", "/api/health")
        
        assert response.status_code == 200
        assert "Content-Type" in response.headers
        assert "application/json" in response.headers["Content-Type"]
        
        # Check for request ID header
        assert "X-Request-ID" in response.headers
    
    def test_health_check_performance(self):
        """Test health check response time."""
        start_time = time.time()
        response = self._make_request("GET", "/api/health")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Health check should be fast (under 1 second)
        response_time = end_time - start_time
        assert response_time < 1.0, f"Health check too slow: {response_time}s"


class TestProcessEndpoint(TestAPIEndpoints):
    """Test /api/process endpoint."""
    
    def test_process_request_success(self):
        """Test successful message processing."""
        payload = {
            "message": "Hello, this is a test message",
            "metadata": {
                "user_id": "test_user",
                "session_id": "test_session"
            }
        }
        
        response = self._make_request("POST", "/api/process", json=payload)
        
        assert response.status_code == 202
        data = response.json()
        
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "pending"
        assert "message" in data
        assert "created_at" in data
        assert "request_id" in data
        
        # Validate task_id format (should be UUID)
        task_id = data["task_id"]
        uuid.UUID(task_id)  # Will raise ValueError if invalid
    
    def test_process_request_missing_message(self):
        """Test process request with missing message field."""
        payload = {
            "metadata": {
                "user_id": "test_user"
            }
        }
        
        response = self._make_request("POST", "/api/process", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "message" in data["error"].lower()
    
    def test_process_request_invalid_json(self):
        """Test process request with invalid JSON."""
        response = self._make_request(
            "POST", 
            "/api/process",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "json" in data["error"].lower()
    
    def test_process_request_empty_payload(self):
        """Test process request with empty payload."""
        response = self._make_request("POST", "/api/process", json={})
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_process_request_large_message(self):
        """Test process request with large message."""
        # Create a large message (1MB)
        large_message = "A" * (1024 * 1024)
        payload = {
            "message": large_message,
            "metadata": {}
        }
        
        response = self._make_request("POST", "/api/process", json=payload)
        
        # Should either accept or reject gracefully
        assert response.status_code in [202, 413, 400]
        
        if response.status_code == 202:
            data = response.json()
            assert "task_id" in data
    
    def test_process_request_special_characters(self):
        """Test process request with special characters."""
        payload = {
            "message": "Test with special chars: 🚀 ñáéíóú 中文 русский",
            "metadata": {
                "test": "special_chars"
            }
        }
        
        response = self._make_request("POST", "/api/process", json=payload)
        
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data


class TestTaskEndpoint(TestAPIEndpoints):
    """Test /api/task/<task_id> endpoint."""
    
    def test_get_task_status_success(self):
        """Test getting task status for existing task."""
        # First create a task
        payload = {
            "message": "Test message for task status",
            "metadata": {}
        }
        
        create_response = self._make_request("POST", "/api/process", json=payload)
        assert create_response.status_code == 202
        
        task_id = create_response.json()["task_id"]
        
        # Now get task status
        response = self._make_request("GET", f"/api/task/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "task_id" in data
        assert data["task_id"] == task_id
        assert "status" in data
        assert data["status"] in ["pending", "processing", "completed", "failed"]
        assert "message" in data
        assert "created_at" in data
    
    def test_get_task_status_not_found(self):
        """Test getting task status for non-existent task."""
        fake_task_id = str(uuid.uuid4())
        
        response = self._make_request("GET", f"/api/task/{fake_task_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()
    
    def test_get_task_status_invalid_uuid(self):
        """Test getting task status with invalid UUID."""
        invalid_task_id = "not-a-valid-uuid"
        
        response = self._make_request("GET", f"/api/task/{invalid_task_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestDebugEndpoint(TestAPIEndpoints):
    """Test /api/debug endpoint."""
    
    def test_debug_status(self):
        """Test debug status endpoint."""
        response = self._make_request("GET", "/api/debug")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "server_ready" in data
        assert isinstance(data["server_ready"], bool)
        assert "smart_delegator_ready" in data
        assert isinstance(data["smart_delegator_ready"], bool)
        assert "rag_system_ready" in data
        assert isinstance(data["rag_system_ready"], bool)
        assert "active_tasks" in data
        assert isinstance(data["active_tasks"], int)
        assert "task_ids" in data
        assert isinstance(data["task_ids"], list)


class TestInternalEndpoints(TestAPIEndpoints):
    """Test internal API endpoints."""
    
    def test_get_models_by_provider(self):
        """Test getting models by provider."""
        response = self._make_request("GET", "/internal/models?provider=openai")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Each model should have required fields
        for model in data:
            assert "provider" in model
            assert model["provider"] == "openai"
    
    def test_get_models_missing_provider(self):
        """Test getting models without provider parameter."""
        response = self._make_request("GET", "/internal/models")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "provider" in data["error"].lower()
    
    def test_update_provider_model_state(self):
        """Test updating provider/model state."""
        payload = {
            "provider": "openai",
            "model_id": "gpt-4"
        }
        
        response = self._make_request("POST", "/internal/state", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "success"
        assert "provider" in data
        assert data["provider"] == "openai"
        assert "model_id" in data
        assert data["model_id"] == "gpt-4"
    
    def test_update_state_missing_fields(self):
        """Test updating state with missing required fields."""
        payload = {
            "provider": "openai"
            # Missing model_id
        }
        
        response = self._make_request("POST", "/internal/state", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_get_current_state(self):
        """Test getting current provider/model state."""
        response = self._make_request("GET", "/internal/state")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain state information
        assert isinstance(data, dict)


class TestToolsEndpoints(TestAPIEndpoints):
    """Test tools management endpoints."""
    
    def test_get_tools(self):
        """Test getting tools list."""
        response = self._make_request("GET", "/api/tools")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        # Should contain tool categories
        for category, tools in data.items():
            assert isinstance(tools, list)
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "enabled" in tool
                assert "has_custom_key" in tool
                assert "available" in tool
    
    def test_toggle_tool(self):
        """Test toggling tool state."""
        payload = {
            "tool_name": "test_tool",
            "enabled": True
        }
        
        response = self._make_request("POST", "/api/tools/toggle", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "tool_name" in data
        assert data["tool_name"] == "test_tool"
        assert "enabled" in data
        assert data["enabled"] is True
    
    def test_toggle_tool_missing_name(self):
        """Test toggling tool without tool name."""
        payload = {
            "enabled": True
        }
        
        response = self._make_request("POST", "/api/tools/toggle", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_set_tool_key(self):
        """Test setting tool API key."""
        payload = {
            "tool_name": "test_tool",
            "api_key": "test-api-key-123"
        }
        
        response = self._make_request("POST", "/api/tools/set_key", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "tool_name" in data
        assert data["tool_name"] == "test_tool"
        assert "has_key" in data
        assert data["has_key"] is True
    
    def test_set_tool_key_empty(self):
        """Test setting empty tool API key (should remove key)."""
        payload = {
            "tool_name": "test_tool",
            "api_key": ""
        }
        
        response = self._make_request("POST", "/api/tools/set_key", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "has_key" in data
        assert data["has_key"] is False


class TestAgentsEndpoint(TestAPIEndpoints):
    """Test agents management endpoint."""
    
    def test_get_agents(self):
        """Test getting agents list."""
        response = self._make_request("GET", "/api/agents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "agents" in data
        assert isinstance(data["agents"], list)
        
        for agent in data["agents"]:
            assert "id" in agent
            assert "name" in agent
            assert "description" in agent
            assert "type" in agent
            assert agent["type"] in ["agent", "flow"]


class TestSettingsEndpoints(TestAPIEndpoints):
    """Test settings management endpoints."""
    
    def test_get_effective_config(self):
        """Test getting effective configuration."""
        # First make a process request to populate config
        payload = {"message": "test", "metadata": {}}
        self._make_request("POST", "/api/process", json=payload)
        
        response = self._make_request("GET", "/settings/effective")
        
        # Should either return config or 404 if not captured yet
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
    
    def test_get_terminal_unsafe_status(self):
        """Test getting terminal unsafe status."""
        response = self._make_request("GET", "/settings/terminal_unsafe")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "enabled" in data
        assert isinstance(data["enabled"], bool)
        assert "source" in data
        assert "settings_path" in data
    
    def test_set_terminal_unsafe_status(self):
        """Test setting terminal unsafe status."""
        payload = {
            "enabled": True
        }
        
        response = self._make_request("POST", "/settings/terminal_unsafe", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "enabled" in data
        assert "source" in data
        assert "written" in data
        assert data["written"] is True


class TestErrorHandling(TestAPIEndpoints):
    """Test API error handling."""
    
    def test_404_for_unknown_endpoint(self):
        """Test 404 response for unknown endpoints."""
        response = self._make_request("GET", "/api/unknown-endpoint")
        
        assert response.status_code == 404
    
    def test_405_for_wrong_method(self):
        """Test 405 response for wrong HTTP method."""
        response = self._make_request("POST", "/api/health")
        
        assert response.status_code == 405
    
    def test_request_timeout_handling(self):
        """Test request timeout handling."""
        # This test would require a way to simulate slow responses
        # For now, just verify the server responds within reasonable time
        start_time = time.time()
        response = self._make_request("GET", "/api/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 10  # Should respond within 10 seconds


class TestConcurrentRequests(TestAPIEndpoints):
    """Test concurrent request handling."""
    
    def test_concurrent_health_checks(self):
        """Test multiple concurrent health check requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_health_request():
            try:
                response = self._make_request("GET", "/api/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # Start 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_health_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # At least 8 out of 10 should succeed
        assert success_count >= 8
    
    def test_concurrent_process_requests(self):
        """Test multiple concurrent process requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_process_request(message_id):
            try:
                payload = {
                    "message": f"Concurrent test message {message_id}",
                    "metadata": {"test_id": message_id}
                }
                response = self._make_request("POST", "/api/process", json=payload)
                results.put((message_id, response.status_code))
            except Exception as e:
                results.put((message_id, f"Error: {e}"))
        
        # Start 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_process_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60)
        
        # Check results
        success_count = 0
        while not results.empty():
            message_id, result = results.get()
            if result == 202:
                success_count += 1
        
        # All should succeed
        assert success_count == 5


class TestSecurityAspects(TestAPIEndpoints):
    """Test security aspects of the API."""
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts."""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in malicious_payloads:
            response = self._make_request(
                "POST", 
                "/api/process",
                json={"message": payload, "metadata": {}}
            )
            
            # Should either process normally or reject gracefully
            assert response.status_code in [202, 400]
            
            # Should not return database errors
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get("error", "").lower()
                assert "sql" not in error_msg
                assert "database" not in error_msg
    
    def test_xss_protection(self):
        """Test protection against XSS attempts."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            response = self._make_request(
                "POST",
                "/api/process", 
                json={"message": payload, "metadata": {}}
            )
            
            # Should process normally (API should sanitize/escape)
            assert response.status_code == 202
    
    def test_request_size_limits(self):
        """Test request size limits."""
        # Try to send a very large request
        large_payload = {
            "message": "A" * (10 * 1024 * 1024),  # 10MB
            "metadata": {}
        }
        
        response = self._make_request("POST", "/api/process", json=large_payload)
        
        # Should either accept or reject with appropriate status
        assert response.status_code in [202, 413, 400]
    
    def test_header_injection_protection(self):
        """Test protection against header injection."""
        malicious_headers = {
            "X-Injected-Header": "malicious\r\nX-Another-Header: injected",
            "User-Agent": "test\r\nX-Injected: header"
        }
        
        response = self._make_request(
            "GET", 
            "/api/health",
            headers=malicious_headers
        )
        
        # Should process normally
        assert response.status_code == 200
        
        # Check that injected headers are not reflected
        response_headers = dict(response.headers)
        assert "X-Injected-Header" not in response_headers
        assert "X-Another-Header" not in response_headers
        assert "X-Injected" not in response_headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])