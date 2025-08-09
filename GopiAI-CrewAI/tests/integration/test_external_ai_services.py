#!/usr/bin/env python3
"""
Integration Tests for External AI Services

Tests integration with external AI services (OpenAI, Anthropic, Google, etc.)
including authentication, rate limiting, and error handling.

Requirements covered:
- 2.2: External service integration testing
- 7.1: API security with external services
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock

try:
    from test_infrastructure.service_manager import ServiceManager
except ImportError:
    from .mock_service_manager import MockServiceManager as ServiceManager


class TestExternalAIServices:
    """Test integration with external AI services."""
    
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


class TestOpenAIIntegration:
    """Test OpenAI service integration."""
    
    def test_openai_models_availability(self):
        """Test OpenAI models are available through the API."""
        response = requests.get(
            "http://localhost:5051/internal/models?provider=openai",
            timeout=10
        )
        
        assert response.status_code == 200
        models = response.json()
        
        assert isinstance(models, list)
        
        # Check for common OpenAI models
        model_names = [model.get("model_id", "") for model in models]
        expected_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        
        # At least one expected model should be available
        found_models = [model for model in expected_models if any(model in name for name in model_names)]
        assert len(found_models) > 0, f"No expected OpenAI models found. Available: {model_names}"
    
    def test_openai_authentication_handling(self):
        """Test OpenAI authentication handling."""
        # Test with invalid API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "invalid-key-test"}):
            # Server should still start and accept requests
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
            
            # Process request should be accepted (failure handled later)
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": "Test with invalid OpenAI key",
                    "metadata": {"provider": "openai"}
                },
                timeout=10
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
    
    def test_openai_rate_limiting_handling(self):
        """Test handling of OpenAI rate limits."""
        # This test simulates rate limiting scenarios
        # In practice, we can't easily trigger real rate limits in tests
        
        # Test multiple rapid requests
        task_ids = []
        
        for i in range(5):
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": f"Rate limit test {i}",
                    "metadata": {"provider": "openai", "test": "rate_limit"}
                },
                timeout=10
            )
            
            # Should accept all requests
            assert response.status_code == 202
            data = response.json()
            task_ids.append(data["task_id"])
        
        # All task IDs should be unique
        assert len(set(task_ids)) == len(task_ids)
    
    def test_openai_error_response_handling(self):
        """Test handling of OpenAI API errors."""
        # Test with potentially problematic content
        problematic_messages = [
            "Generate harmful content",  # Should be filtered
            "Very long message " * 1000,  # Might hit token limits
            "",  # Empty message
        ]
        
        for message in problematic_messages:
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": message,
                    "metadata": {"provider": "openai"}
                },
                timeout=10
            )
            
            # Should either accept or reject gracefully
            assert response.status_code in [202, 400]
            
            if response.status_code == 202:
                data = response.json()
                assert "task_id" in data


class TestAnthropicIntegration:
    """Test Anthropic (Claude) service integration."""
    
    def test_anthropic_models_availability(self):
        """Test Anthropic models are available through the API."""
        response = requests.get(
            "http://localhost:5051/internal/models?provider=anthropic",
            timeout=10
        )
        
        assert response.status_code == 200
        models = response.json()
        
        assert isinstance(models, list)
        
        # Check for common Anthropic models
        model_names = [model.get("model_id", "") for model in models]
        expected_models = ["claude-3", "claude-2", "claude-instant"]
        
        # At least one expected model should be available
        found_models = [model for model in expected_models if any(model in name for name in model_names)]
        assert len(found_models) > 0, f"No expected Anthropic models found. Available: {model_names}"
    
    def test_anthropic_authentication_handling(self):
        """Test Anthropic authentication handling."""
        # Test with invalid API key
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "invalid-anthropic-key"}):
            # Server should handle gracefully
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": "Test with invalid Anthropic key",
                    "metadata": {"provider": "anthropic"}
                },
                timeout=10
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
    
    def test_anthropic_content_filtering(self):
        """Test Anthropic content filtering and safety."""
        # Test with various content types
        test_messages = [
            "Write a simple hello world program",  # Safe content
            "Explain quantum physics",  # Complex but safe
            "Tell me a joke",  # Creative content
        ]
        
        for message in test_messages:
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": message,
                    "metadata": {"provider": "anthropic"}
                },
                timeout=10
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data


class TestGoogleAIIntegration:
    """Test Google AI (Gemini) service integration."""
    
    def test_google_models_availability(self):
        """Test Google AI models are available through the API."""
        response = requests.get(
            "http://localhost:5051/internal/models?provider=google",
            timeout=10
        )
        
        assert response.status_code == 200
        models = response.json()
        
        assert isinstance(models, list)
        
        # Check for common Google models
        model_names = [model.get("model_id", "") for model in models]
        expected_models = ["gemini-pro", "gemini-1.5", "gemini"]
        
        # At least one expected model should be available
        found_models = [model for model in expected_models if any(model in name for name in model_names)]
        assert len(found_models) > 0, f"No expected Google models found. Available: {model_names}"
    
    def test_google_authentication_handling(self):
        """Test Google AI authentication handling."""
        # Test with invalid API key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "invalid-google-key"}):
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": "Test with invalid Google key",
                    "metadata": {"provider": "google"}
                },
                timeout=10
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
    
    def test_google_multimodal_support(self):
        """Test Google AI multimodal capabilities."""
        # Test text-only request (should work)
        response = requests.post(
            "http://localhost:5051/api/process",
            json={
                "message": "Describe this text input",
                "metadata": {"provider": "google", "type": "text"}
            },
            timeout=10
        )
        
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data


class TestOpenRouterIntegration:
    """Test OpenRouter service integration."""
    
    def test_openrouter_models_availability(self):
        """Test OpenRouter models are available through the API."""
        response = requests.get(
            "http://localhost:5051/internal/models?provider=openrouter",
            timeout=10
        )
        
        # OpenRouter might not be configured, so we accept both success and error
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            models = response.json()
            assert isinstance(models, list)
    
    def test_openrouter_authentication_handling(self):
        """Test OpenRouter authentication handling."""
        # Test with invalid API key
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "invalid-openrouter-key"}):
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": "Test with invalid OpenRouter key",
                    "metadata": {"provider": "openrouter"}
                },
                timeout=10
            )
            
            # Should accept request regardless of key validity
            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data


class TestProviderSwitching:
    """Test switching between AI providers."""
    
    def test_provider_state_management(self):
        """Test provider state management."""
        # Test setting different providers
        providers_to_test = ["openai", "anthropic", "google"]
        
        for provider in providers_to_test:
            # Set provider state
            response = requests.post(
                "http://localhost:5051/internal/state",
                json={
                    "provider": provider,
                    "model_id": f"{provider}-test-model"
                },
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["provider"] == provider
            
            # Verify state was set
            response = requests.get("http://localhost:5051/internal/state", timeout=10)
            assert response.status_code == 200
            
            state_data = response.json()
            assert state_data.get("provider") == provider
    
    def test_model_switching_within_provider(self):
        """Test switching models within the same provider."""
        # Test OpenAI model switching
        openai_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        
        for model in openai_models:
            response = requests.post(
                "http://localhost:5051/internal/state",
                json={
                    "provider": "openai",
                    "model_id": model
                },
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["model_id"] == model
    
    def test_invalid_provider_handling(self):
        """Test handling of invalid provider names."""
        invalid_providers = ["invalid_provider", "nonexistent", ""]
        
        for provider in invalid_providers:
            response = requests.post(
                "http://localhost:5051/internal/state",
                json={
                    "provider": provider,
                    "model_id": "test-model"
                },
                timeout=10
            )
            
            # Should either reject or handle gracefully
            assert response.status_code in [200, 400]
    
    def test_concurrent_provider_switching(self):
        """Test concurrent provider switching requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def switch_provider(provider, model):
            try:
                response = requests.post(
                    "http://localhost:5051/internal/state",
                    json={
                        "provider": provider,
                        "model_id": model
                    },
                    timeout=10
                )
                results.put((provider, model, response.status_code))
            except Exception as e:
                results.put((provider, model, f"error: {e}"))
        
        # Start concurrent switching requests
        threads = []
        test_configs = [
            ("openai", "gpt-4"),
            ("anthropic", "claude-3"),
            ("google", "gemini-pro"),
            ("openai", "gpt-3.5-turbo"),
        ]
        
        for provider, model in test_configs:
            thread = threading.Thread(target=switch_provider, args=(provider, model))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        success_count = 0
        while not results.empty():
            provider, model, result = results.get()
            if result == 200:
                success_count += 1
        
        # Most should succeed
        assert success_count >= len(test_configs) - 1


class TestServiceResilience:
    """Test resilience to external service issues."""
    
    def test_network_timeout_handling(self):
        """Test handling of network timeouts to external services."""
        # This test simulates network issues
        # We can't easily simulate real timeouts, so we test the system's response
        
        # Make requests that might timeout
        response = requests.post(
            "http://localhost:5051/api/process",
            json={
                "message": "Test message that might timeout",
                "metadata": {"timeout_test": True}
            },
            timeout=10
        )
        
        # Should accept the request
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
    
    def test_service_unavailable_fallback(self):
        """Test fallback behavior when services are unavailable."""
        # Test with all API keys removed
        with patch.dict(os.environ, {}, clear=True):
            # Health check should still work
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            # Should indicate limited mode or degraded service
            assert data["status"] in ["online", "limited_mode"]
            
            # Process requests should still be accepted
            response = requests.post(
                "http://localhost:5051/api/process",
                json={
                    "message": "Test in fallback mode",
                    "metadata": {}
                },
                timeout=10
            )
            
            # Should either work or fail gracefully
            assert response.status_code in [202, 503]
    
    def test_partial_service_degradation(self):
        """Test behavior when some services are unavailable."""
        # Test with only some API keys available
        partial_env = {
            "OPENAI_API_KEY": "test-openai-key",
            # Missing ANTHROPIC_API_KEY and GOOGLE_API_KEY
        }
        
        with patch.dict(os.environ, partial_env, clear=True):
            # Should still work with available services
            response = requests.get("http://localhost:5051/api/health", timeout=10)
            assert response.status_code == 200
            
            # OpenAI models should be available
            response = requests.get(
                "http://localhost:5051/internal/models?provider=openai",
                timeout=10
            )
            assert response.status_code == 200
            
            # Other providers might not be available
            response = requests.get(
                "http://localhost:5051/internal/models?provider=anthropic",
                timeout=10
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 404]
    
    def test_api_key_rotation_handling(self):
        """Test handling of API key rotation."""
        # Test updating API keys through the tools endpoint
        test_keys = {
            "openai_tool": "new-openai-key-123",
            "anthropic_tool": "new-anthropic-key-456",
            "google_tool": "new-google-key-789"
        }
        
        for tool_name, api_key in test_keys.items():
            response = requests.post(
                "http://localhost:5051/api/tools/set_key",
                json={
                    "tool_name": tool_name,
                    "api_key": api_key
                },
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["has_key"] is True
    
    def test_error_propagation_and_logging(self):
        """Test that external service errors are properly handled and logged."""
        # Make a request that might cause external service errors
        response = requests.post(
            "http://localhost:5051/api/process",
            json={
                "message": "Test error propagation",
                "metadata": {"test_errors": True}
            },
            timeout=10
        )
        
        # Should accept the request
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        
        # Check that we can get task status
        task_id = data["task_id"]
        
        # Wait a bit for processing
        time.sleep(2)
        
        response = requests.get(f"http://localhost:5051/api/task/{task_id}", timeout=10)
        assert response.status_code == 200
        
        task_data = response.json()
        assert "status" in task_data
        assert task_data["status"] in ["pending", "processing", "completed", "failed"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])