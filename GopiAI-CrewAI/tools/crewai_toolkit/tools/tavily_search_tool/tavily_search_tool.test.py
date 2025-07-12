import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import BaseTool
from tavily import TavilyClient, AsyncTavilyClient
from typing import Any
import os
import json

from crewai.tools.tavily_search import TavilySearchTool, TavilySearchToolSchema

class TavilySearchToolTest(unittest.TestCase):

    @patch("crewai.tools.tavily_search.TAVILY_AVAILABLE", False)
    @patch("crewai.tools.tavily_search.click.confirm", return_value=False)
    def test_init_no_tavily_no_install(self, mock_confirm):
        with self.assertRaises(ImportError):
            TavilySearchTool()

    @patch("crewai.tools.tavily_search.TavilyClient")
    def test_run_success(self, MockTavilyClient):
        mock_client = MagicMock()
        MockTavilyClient.return_value = mock_client
        mock_client.search.return_value = {"results": [{"content": "This is a test."}]}
        tool = TavilySearchTool(api_key="test_key")
        result = tool._run(query="test query")
        self.assertIsInstance(result, str)

    @patch("crewai.tools.tavily_search.AsyncTavilyClient")
    async def test_arun_success(self, MockAsyncTavilyClient):
        mock_client = MagicMock()
        MockAsyncTavilyClient.return_value = mock_client
        mock_client.search.return_value = {"results": [{"content": "This is a test."}]}
        tool = TavilySearchTool(api_key="test_key")
        result = await tool._arun(query="test query")
        self.assertIsInstance(result, str)

    @patch("crewai.tools.tavily_search.TavilyClient")
    def test_run_content_truncation(self, MockTavilyClient):
        mock_client = MagicMock()
        MockTavilyClient.return_value = mock_client
        long_content = "This is a very long string " * 200
        mock_client.search.return_value = {"results": [{"content": long_content}]}
        tool = TavilySearchTool(api_key="test_key", max_content_length_per_result=100)
        result = tool._run(query="test query")
        result_dict = json.loads(result)
        self.assertTrue(len(result_dict["results"][0]["content"]) <= 103)
