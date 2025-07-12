import unittest
from unittest.mock import patch, mock_open
import os
from crewai.tools import BaseTool
from crewai_tools.serply_web_search.serply_web_search import SerplyWebSearchTool, SerplyWebSearchToolSchema
from pydantic import ValidationError


class TestSerplyWebSearchTool(unittest.TestCase):
    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_serply_web_search_tool_run(self, mock_request):
        mock_response = unittest.mock.MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Test Title", "link": "Test Link", "description": "Test Description"}
            ]
        }
        mock_request.return_value = mock_response
        tool = SerplyWebSearchTool()
        result = tool._run(search_query="test query")
        self.assertIn("Test Title", result)
        self.assertIn("Test Link", result)
        self.assertIn("Test Description", result)

    def test_serply_web_search_tool_schema(self):
        schema = SerplyWebSearchToolSchema(search_query="test query")
        self.assertEqual(schema.search_query, "test query")

    def test_serply_web_search_tool_missing_api_key(self):
        with self.assertRaises(KeyError):
            SerplyWebSearchTool()

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    def test_serply_web_search_tool_init_params(self):
        tool = SerplyWebSearchTool(hl="fr", limit=5, device_type="mobile", proxy_location="CA")
        self.assertEqual(tool.hl, "us")
        self.assertEqual(tool.limit, 5)
        self.assertEqual(tool.device_type, "mobile")
        self.assertEqual(tool.proxy_location, "CA")
        self.assertEqual(tool.query_payload["gl"], "CA")
        self.assertEqual(tool.query_payload["hl"], "fr")
        self.assertEqual(tool.query_payload["num"], 5)

    @patch.dict(os.environ, {"SERPLY_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_serply_web_search_tool_no_results(self, mock_request):
        mock_response = unittest.mock.MagicMock()
        mock_response.json.return_value = {"no": "results"}
        mock_request.return_value = mock_response
        tool = SerplyWebSearchTool()
        result = tool._run(search_query="test query")
        self.assertEqual(result, {"no": "results"})