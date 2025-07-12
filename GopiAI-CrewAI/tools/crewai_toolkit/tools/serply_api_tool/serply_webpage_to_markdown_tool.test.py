import unittest
from unittest.mock import patch, MagicMock
import os
from pydantic import ValidationError

from crewai_tools.tools.rag.serply_webpage_to_markdown import (
    SerplyWebpageToMarkdownTool,
    SerplyWebpageToMarkdownToolSchema,
)


class SerplyWebpageToMarkdownToolTest(unittest.TestCase):
    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = "Test markdown content"
        mock_request.return_value = mock_response

        tool = SerplyWebpageToMarkdownTool()
        result = tool._run(url="https://example.com")
        self.assertEqual(result, "Test markdown content")
        mock_request.assert_called_once()

    def test_schema_validation(self):
        try:
            SerplyWebpageToMarkdownToolSchema(url="https://example.com")
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")

    def test_schema_validation_missing_url(self):
        with self.assertRaises(ValidationError):
            SerplyWebpageToMarkdownToolSchema()

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    def test_proxy_location(self):
        tool = SerplyWebpageToMarkdownTool(proxy_location="CA")
        self.assertEqual(tool.proxy_location, "CA")
        self.assertEqual(tool.headers["X-Proxy-Location"], "CA")

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    def test_default_proxy_location(self):
        tool = SerplyWebpageToMarkdownTool()
        self.assertEqual(tool.proxy_location, "US")
        self.assertEqual(tool.headers["X-Proxy-Location"], "US")