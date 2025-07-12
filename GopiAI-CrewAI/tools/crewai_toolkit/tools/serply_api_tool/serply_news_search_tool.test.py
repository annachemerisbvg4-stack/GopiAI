import unittest
from unittest.mock import patch, MagicMock
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Optional, Type
from urllib.parse import urlencode
import requests
from crewai_tools.serply_news_search.serply_news_search import (
    SerplyNewsSearchTool,
    SerplyNewsSearchToolSchema,
)


class TestSerplyNewsSearchTool(unittest.TestCase):
    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entries": [
                {
                    "title": "Test Title",
                    "link": "http://test.com",
                    "source": {"title": "Test Source"},
                    "published": "2023-01-01",
                }
            ]
        }
        mock_request.return_value = mock_response

        tool = SerplyNewsSearchTool()
        result = tool._run(search_query="test query")

        self.assertIn("Test Title", result)
        self.assertIn("http://test.com", result)
        self.assertIn("Test Source", result)
        self.assertIn("2023-01-01", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_no_entries(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "No results found"}
        mock_request.return_value = mock_response

        tool = SerplyNewsSearchTool()
        result = tool._run(search_query="test query")

        self.assertEqual(result, {"error": "No results found"})

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    def test_initialization(self):
        tool = SerplyNewsSearchTool(limit=5, proxy_location="CA")
        self.assertEqual(tool.limit, 5)
        self.assertEqual(tool.proxy_location, "CA")
        self.assertEqual(tool.headers["X-Proxy-Location"], "CA")

    def test_args_schema(self):
        self.assertEqual(
            SerplyNewsSearchTool.args_schema, SerplyNewsSearchToolSchema
        )

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_follow_redirect(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entries": [
                {
                    "title": "Test Title",
                    "link": "http://test.com",
                    "source": {"title": "Test Source"},
                    "published": "2023-01-01",
                }
            ]
        }
        mock_request.return_value = mock_response
        mock_redirect_response = MagicMock()
        mock_redirect_response.history = [MagicMock(headers={"Location": "http://final.com"})]
        mock_request.return_value = mock_redirect_response

        tool = SerplyNewsSearchTool()
        result = tool._run(search_query="test query")

        self.assertIn("http://final.com", result)