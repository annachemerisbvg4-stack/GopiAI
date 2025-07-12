import unittest
from unittest.mock import patch, MagicMock

from crewai.tools.spider_tool import SpiderTool, SpiderToolSchema, SpiderToolConfig
from pydantic import ValidationError

class SpiderToolTest(unittest.TestCase):

    def test_spider_tool_schema_validation(self):
        with self.assertRaises(ValidationError):
            SpiderToolSchema(website_url=None)
        SpiderToolSchema(website_url="https://example.com")

    @patch("crewai.tools.spider_tool.Spider")
    def test_spider_tool_run_scrape(self, MockSpider):
        mock_spider_instance = MockSpider.return_value
        mock_spider_instance.scrape_url.return_value = "Scraped content"
        tool = SpiderTool(api_key="test_key", log_failures=False)
        result = tool._run(website_url="https://example.com", mode="scrape")
        self.assertEqual(result, "Scraped content")

    @patch("crewai.tools.spider_tool.Spider")
    def test_spider_tool_run_crawl(self, MockSpider):
        mock_spider_instance = MockSpider.return_value
        mock_spider_instance.crawl_url.return_value = "Crawled content"
        tool = SpiderTool(api_key="test_key", log_failures=False)
        result = tool._run(website_url="https://example.com", mode="crawl")
        self.assertEqual(result, "Crawled content")

    def test_validate_url(self):
        tool = SpiderTool()
        self.assertTrue(tool._validate_url("https://example.com"))
        self.assertFalse(tool._validate_url("invalid-url"))
        self.assertFalse(tool._validate_url("ftp://example.com"))