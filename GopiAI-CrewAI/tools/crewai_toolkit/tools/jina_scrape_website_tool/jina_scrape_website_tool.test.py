import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import requests

from crewai_tools import JinaScrapeWebsiteTool, JinaScrapeWebsiteToolInput


class TestJinaScrapeWebsiteTool(unittest.TestCase):
    @patch("requests.get")
    def test_run_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "Test content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = JinaScrapeWebsiteTool(website_url="http://example.com")
        result = tool._run()
        self.assertEqual(result, "Test content")

    def test_run_no_url(self):
        tool = JinaScrapeWebsiteTool()
        with self.assertRaises(ValueError):
            tool._run()

    @patch("requests.get")
    def test_run_with_api_key(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "Test content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = JinaScrapeWebsiteTool(website_url="http://example.com", api_key="test_key")
        tool._run()
        mock_get.assert_called_with(
            "https://r.jina.ai/http://example.com",
            headers={"Authorization": "Bearer test_key"},
            timeout=15,
        )

    @patch("requests.get")
    def test_run_with_custom_headers(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "Test content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        custom_headers = {"X-Custom-Header": "custom_value"}
        tool = JinaScrapeWebsiteTool(website_url="http://example.com", custom_headers=custom_headers)
        tool._run()
        mock_get.assert_called_with(
            "https://r.jina.ai/http://example.com",
            headers={"X-Custom-Header": "custom_value"},
            timeout=15,
        )