import unittest
from unittest.mock import patch, MagicMock

from crewai.tools.firecrawl_search import FirecrawlSearchTool, FirecrawlSearchToolSchema


class TestFirecrawlSearchTool(unittest.TestCase):
    @patch("crewai.tools.firecrawl_search.FirecrawlApp")
    def test_firecrawl_search_tool_initialization(self, MockFirecrawlApp):
        tool = FirecrawlSearchTool(api_key="test_api_key")
        self.assertIsInstance(tool, FirecrawlSearchTool)
        MockFirecrawlApp.assert_called_once_with(api_key="test_api_key")

    @patch("crewai.tools.firecrawl_search.FirecrawlApp")
    def test_firecrawl_search_tool_run(self, MockFirecrawlApp):
        mock_firecrawl_instance = MockFirecrawlApp.return_value
        mock_firecrawl_instance.search.return_value = "search_results"
        tool = FirecrawlSearchTool(api_key="test_api_key")
        result = tool._run(query="test_query")
        self.assertEqual(result, "search_results")
        mock_firecrawl_instance.search.assert_called_once_with(
            query="test_query",
            limit=5,
            tbs=None,
            lang="en",
            country="us",
            location=None,
            timeout=60000,
        )

    @patch("crewai.tools.firecrawl_search.FirecrawlApp", side_effect=ImportError)
    @patch("crewai.tools.firecrawl_search.click.confirm", return_value=False)
    def test_firecrawl_search_tool_import_error(self, mock_confirm, MockFirecrawlApp):
        with self.assertRaises(ImportError):
            FirecrawlSearchTool(api_key="test_api_key")

    def test_firecrawl_search_tool_schema(self):
        schema = FirecrawlSearchToolSchema(query="test_query")
        self.assertEqual(schema.query, "test_query")

    def test_firecrawl_search_tool_no_api_key(self):
        tool = FirecrawlSearchTool()
        self.assertIsNone(tool.api_key)