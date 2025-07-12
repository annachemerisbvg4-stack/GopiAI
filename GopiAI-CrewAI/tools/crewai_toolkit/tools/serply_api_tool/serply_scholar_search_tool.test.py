import unittest
from unittest.mock import patch, MagicMock
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from typing import Any, Optional, Type
from urllib.parse import urlencode

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from unittest.mock import patch
from crewai_tools.serply_scholar_search.serply_scholar_search import (
    SerplyScholarSearchTool,
    SerplyScholarSearchToolSchema,
)


class TestSerplyScholarSearchTool(unittest.TestCase):
    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_search_query(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test Article",
                    "link": "http://test.com",
                    "description": "Test Description",
                    "cite": "Test Cite",
                    "author": {"authors": [{"name": "Test Author"}]},
                }
            ]
        }
        mock_request.return_value = mock_response
        tool = SerplyScholarSearchTool()
        result = tool._run(search_query="test query")
        self.assertIn("Test Article", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_query(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test Article",
                    "link": "http://test.com",
                    "description": "Test Description",
                    "cite": "Test Cite",
                    "author": {"authors": [{"name": "Test Author"}]},
                }
            ]
        }
        mock_request.return_value = mock_response
        tool = SerplyScholarSearchTool()
        result = tool._run(query="test query")
        self.assertIn("Test Article", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_no_articles(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"articles": []}
        mock_request.return_value = mock_response
        tool = SerplyScholarSearchTool()
        result = tool._run(search_query="test query")
        self.assertEqual("\nSearch results: \n", result)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_missing_key(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test Article",
                    "doc": {"link": "http://test.com"},
                    "description": "Test Description",
                    "cite": "Test Cite",
                    "author": {"authors": [{"name": "Test Author"}]},
                }
            ]
        }
        mock_request.return_value = mock_response
        tool = SerplyScholarSearchTool()
        result = tool._run(search_query="test query")
        self.assertIn("Test Article", result)

    def test_tool_schema(self):
        schema = SerplyScholarSearchToolSchema(search_query="test")
        self.assertEqual(schema.search_query, "test")