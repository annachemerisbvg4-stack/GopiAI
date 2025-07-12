import unittest
from unittest.mock import patch, MagicMock
from crewai.tools.scrapfly_scrape_website import ScrapflyScrapeWebsiteTool
from pydantic import ValidationError

class TestScrapflyScrapeWebsiteTool(unittest.TestCase):

    @patch("crewai.tools.scrapfly_scrape_website.ScrapflyClient")
    def test_tool_initialization(self, MockScrapflyClient):
        tool = ScrapflyScrapeWebsiteTool(api_key="test_api_key")
        MockScrapflyClient.assert_called_once_with(key="test_api_key")
        self.assertIsNotNone(tool.scrapfly)

    @patch("crewai.tools.scrapfly_scrape_website.ScrapflyClient")
    def test_tool_run_success(self, MockScrapflyClient):
        mock_scrapfly = MagicMock()
        MockScrapflyClient.return_value = mock_scrapfly
        mock_response = MagicMock()
        mock_response.scrape_result = {"content": "Test content"}
        mock_scrapfly.scrape.return_value = mock_response

        tool = ScrapflyScrapeWebsiteTool(api_key="test_api_key")
        tool.scrapfly = mock_scrapfly
        result = tool._run(url="http://example.com")
        self.assertEqual(result, "Test content")

    @patch("crewai.tools.scrapfly_scrape_website.ScrapflyClient")
    def test_tool_run_failure_no_ignore(self, MockScrapflyClient):
        mock_scrapfly = MagicMock()
        MockScrapflyClient.return_value = mock_scrapfly
        mock_scrapfly.scrape.side_effect = Exception("Scrape failed")

        tool = ScrapflyScrapeWebsiteTool(api_key="test_api_key")
        tool.scrapfly = mock_scrapfly
        with self.assertRaises(Exception) as context:
            tool._run(url="http://example.com")
        self.assertEqual(str(context.exception), "Scrape failed")

    @patch("crewai.tools.scrapfly_scrape_website.ScrapflyClient")
    def test_tool_run_failure_ignore(self, MockScrapflyClient):
        mock_scrapfly = MagicMock()
        MockScrapflyClient.return_value = mock_scrapfly
        mock_scrapfly.scrape.side_effect = Exception("Scrape failed")

        tool = ScrapflyScrapeWebsiteTool(api_key="test_api_key")
        tool.scrapfly = mock_scrapfly
        result = tool._run(url="http://example.com", ignore_scrape_failures=True)
        self.assertIsNone(result)

    def test_tool_schema_validation(self):
        from crewai.tools.scrapfly_scrape_website import ScrapflyScrapeWebsiteToolSchema
        with self.assertRaises(ValidationError):
            ScrapflyScrapeWebsiteToolSchema(url=123)