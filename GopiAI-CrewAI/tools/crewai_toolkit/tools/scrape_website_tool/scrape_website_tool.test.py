import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import ScrapeWebsiteTool, ScrapeWebsiteToolSchema
from pydantic import ValidationError

class TestScrapeWebsiteTool(unittest.TestCase):

    @patch('requests.get')
    def test_run_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        tool = ScrapeWebsiteTool(website_url="http://example.com")
        result = tool._run(website_url="http://example.com")
        self.assertEqual(result, " Test ")

    def test_validation_error(self):
        with self.assertRaises(ValidationError):
            ScrapeWebsiteToolSchema()

    def test_fixed_scrape_website_tool_schema(self):
         ScrapeWebsiteToolSchema(website_url="http://example.com")

    def test_tool_description_with_url(self):
        tool = ScrapeWebsiteTool(website_url="http://example.com")
        self.assertIn("http://example.com", tool.description)

    @patch('requests.get')
    def test_run_with_kwargs(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        tool = ScrapeWebsiteTool()
        result = tool._run(website_url="http://example.com")
        self.assertEqual(result, " Test ")