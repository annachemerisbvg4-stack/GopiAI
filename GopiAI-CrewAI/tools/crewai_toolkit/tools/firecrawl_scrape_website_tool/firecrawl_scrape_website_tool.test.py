import unittest
from unittest.mock import patch, MagicMock

from crewai.tools.firecrawl_tool import FirecrawlScrapeWebsiteTool, FirecrawlScrapeWebsiteToolSchema

class TestFirecrawlScrapeWebsiteTool(unittest.TestCase):

    @patch("crewai.tools.firecrawl_tool.FirecrawlApp")
    def test_tool_initialization(self, MockFirecrawlApp):
        tool = FirecrawlScrapeWebsiteTool(api_key="test_api_key")
        self.assertIsInstance(tool, FirecrawlScrapeWebsiteTool)
        MockFirecrawlApp.assert_called_once_with(api_key="test_api_key")

    @patch("crewai.tools.firecrawl_tool.FirecrawlApp")
    def test_tool_run(self, MockFirecrawlApp):
        mock_firecrawl_instance = MockFirecrawlApp.return_value
        mock_firecrawl_instance.scrape_url.return_value = "Scraped content"
        tool = FirecrawlScrapeWebsiteTool(api_key="test_api_key")
        result = tool._run(url="http://example.com")
        self.assertEqual(result, "Scraped content")
        mock_firecrawl_instance.scrape_url.assert_called_once_with("http://example.com", **tool.config)

    def test_tool_schema(self):
        schema = FirecrawlScrapeWebsiteToolSchema(url="http://example.com")
        self.assertEqual(schema.url, "http://example.com")

    @patch("crewai.tools.firecrawl_tool.FirecrawlApp")
    def test_tool_default_config(self, MockFirecrawlApp):
        tool = FirecrawlScrapeWebsiteTool(api_key="test_api_key")
        self.assertEqual(tool.config["formats"], ["markdown"])
        self.assertTrue(tool.config["only_main_content"])
        self.assertEqual(tool.config["include_tags"], [])
        self.assertEqual(tool.config["exclude_tags"], [])
        self.assertEqual(tool.config["headers"], {})
        self.assertEqual(tool.config["wait_for"], 0)

    @patch("crewai.tools.firecrawl_tool.FirecrawlApp")
    def test_tool_custom_config(self, MockFirecrawlApp):
        custom_config = {"formats": ["html"], "only_main_content": False}
        tool = FirecrawlScrapeWebsiteTool(api_key="test_api_key", config=custom_config)
        self.assertEqual(tool.config["formats"], ["html"])
        self.assertFalse(tool.config["only_main_content"])