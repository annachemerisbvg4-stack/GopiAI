import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import FirecrawlCrawlWebsiteTool
from pydantic import ValidationError

class TestFirecrawlCrawlWebsiteTool(unittest.TestCase):

    @patch("crewai.tools.firecrawl_website.FirecrawlApp")
    def test_tool_initialization(self, MockFirecrawlApp):
        tool = FirecrawlCrawlWebsiteTool(api_key="test_key")
        self.assertIsInstance(tool, FirecrawlCrawlWebsiteTool)
        MockFirecrawlApp.assert_called_once_with(api_key="test_key")

    def test_tool_schema_validation(self):
        with self.assertRaises(ValidationError):
            FirecrawlCrawlWebsiteToolSchema(url=123)

    @patch("crewai.tools.firecrawl_website.FirecrawlApp")
    def test_run_method(self, MockFirecrawlApp):
        mock_firecrawl_instance = MockFirecrawlApp.return_value
        mock_firecrawl_instance.crawl_url.return_value = "Crawl Result"
        tool = FirecrawlCrawlWebsiteTool(api_key="test_key")
        result = tool._run("https://example.com")
        self.assertEqual(result, "Crawl Result")
        mock_firecrawl_instance.crawl_url.assert_called_once_with("https://example.com", **tool.config)

    @patch("crewai.tools.firecrawl_website.FirecrawlApp", side_effect=ImportError)
    @patch("click.confirm", return_value=False)
    def test_import_error_no_install(self, mock_confirm, MockFirecrawlApp):
        with self.assertRaises(ImportError):
            FirecrawlCrawlWebsiteTool(api_key="test_key")

    @patch("crewai.tools.firecrawl_website.FirecrawlApp", side_effect=ImportError)
    @patch("click.confirm", return_value=True)
    @patch("subprocess.run")
    def test_import_error_with_install(self, mock_subprocess_run, mock_confirm, MockFirecrawlApp):
        mock_subprocess_run.return_value.returncode = 0
        with self.assertRaises(ImportError):
            FirecrawlCrawlWebsiteTool(api_key="test_key")