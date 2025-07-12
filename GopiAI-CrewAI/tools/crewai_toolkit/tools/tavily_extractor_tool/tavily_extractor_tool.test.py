import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import BaseTool
from crewai.tools.tavily_extractor import TavilyExtractorTool, TavilyExtractorToolSchema
from pydantic import ValidationError
import os
import json

class TavilyExtractorToolTest(unittest.TestCase):

    @patch("crewai.tools.tavily_extractor.TAVILY_AVAILABLE", False)
    @patch("crewai.tools.tavily_extractor.click.confirm", return_value=False)
    def test_init_no_tavily_no_install(self, mock_confirm):
        with self.assertRaises(ImportError):
            TavilyExtractorTool()

    @patch("crewai.tools.tavily_extractor.TAVILY_AVAILABLE", True)
    def test_init_success(self):
        tool = TavilyExtractorTool(api_key="test_api_key")
        self.assertIsNotNone(tool.client)
        self.assertIsNotNone(tool.async_client)

    @patch("crewai.tools.tavily_extractor.TAVILY_AVAILABLE", True)
    def test_run_success(self):
        tool = TavilyExtractorTool(api_key="test_api_key")
        tool.client = MagicMock()
        tool.client.extract.return_value = {"content": "test content"}
        result = tool._run(urls="http://example.com")
        self.assertEqual(json.loads(result), {"content": "test content"})

    @patch("crewai.tools.tavily_extractor.TAVILY_AVAILABLE", True)
    async def test_arun_success(self):
        tool = TavilyExtractorTool(api_key="test_api_key")
        tool.async_client = MagicMock()
        tool.async_client.extract.return_value = {"content": "test content"}
        result = await tool._arun(urls="http://example.com")
        self.assertEqual(json.loads(result), {"content": "test content"})

    def test_validation_error(self):
        with self.assertRaises(ValidationError):
            TavilyExtractorToolSchema(urls=None)