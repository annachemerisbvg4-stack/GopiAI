import unittest
from unittest.mock import patch, MagicMock
import logging
from typing import List, Optional, Any, Mapping, ClassVar
from pydantic import Field
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult, Generation
from llm_rotation_config import (
    select_llm_model_safe, 
    rate_limit_monitor, 
    get_api_key_for_provider, 
    LLM_MODELS_CONFIG,
    get_active_models,
    get_models_by_intelligence,
    get_next_available_model
)
from crewai import LLM # Assuming this is litellm's LLM
from ai_router import AIRouterLLM
class TestAIRouterLLM(unittest.TestCase):
    @patch('ai_router.select_llm_model_safe')
    @patch('ai_router.get_api_key_for_provider')
    @patch('crewai.LLM.call')
    def test_generate_success(self, mock_llm_call, mock_get_api_key, mock_select_model):
        mock_select_model.return_value = "test_model"
        mock_get_api_key.return_value = "test_api_key"
        mock_llm_call.return_value = "Test response"
        llm = AIRouterLLM()
        result = llm._generate(["test prompt"])
        self.assertEqual(result.generations[0][0].text, "Test response")
    @patch('ai_router.select_llm_model_safe')
    def test_generate_no_available_models(self, mock_select_model):
        mock_select_model.return_value = None
        llm = AIRouterLLM()
        result = llm._generate(["test prompt"])
        self.assertIn("Все LLM модели временно недоступны", result.generations[0][0].text)
    @patch('ai_router.select_llm_model_safe')
    @patch('ai_router.get_api_key_for_provider')
    def test_generate_api_error(self, mock_get_api_key, mock_select_model):
        mock_select_model.return_value = "test_model"
        mock_get_api_key.return_value = "test_api_key"
        llm = AIRouterLLM()
        with self.assertRaises(ValueError):
            llm._try_model_request("test prompt", "test_model")
    def test_is_quota_error(self):
        llm = AIRouterLLM()
        self.assertTrue(llm._is_quota_error("Quota exceeded"))
        self.assertFalse(llm._is_quota_error("Some other error"))
    def test_get_system_status(self):
        llm = AIRouterLLM()
        status = llm.get_system_status()
        self.assertIsInstance(status, dict)
if __name__ == '__main__':
    unittest.main()