import unittest
from unittest.mock import patch, MagicMock
from crewai.tools.scrapegraph_tool import ScrapegraphScrapeTool, ScrapegraphScrapeToolSchema, RateLimitError
from pydantic import ValidationError
import os

class TestScrapegraphScrapeTool(unittest.TestCase):

    def test_valid_url(self):
        data = {'website_url': 'https://www.example.com', 'user_prompt': 'test'}
        tool_schema = ScrapegraphScrapeToolSchema(**data)
        self.assertEqual(tool_schema.website_url, 'https://www.example.com')

    def test_invalid_url(self):
        with self.assertRaises(ValidationError):
            ScrapegraphScrapeToolSchema(website_url='invalid-url', user_prompt='test')

    @patch('crewai.tools.scrapegraph_tool.Client')
    @patch.dict(os.environ, {"SCRAPEGRAPH_API_KEY": "test_key"})
    def test_run_success(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.smartscraper.return_value = {"result": "Scraped content"}
        tool = ScrapegraphScrapeTool(api_key="test_key")
        result = tool._run(website_url="https://www.example.com", user_prompt="test prompt")
        self.assertEqual(result, {"result": "Scraped content"})
        mock_client_instance.close.assert_called_once()

    @patch('crewai.tools.scrapegraph_tool.Client')
    @patch.dict(os.environ, {"SCRAPEGRAPH_API_KEY": "test_key"})
    def test_run_rate_limit_error(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.smartscraper.side_effect = RateLimitError("Rate limit exceeded")
        tool = ScrapegraphScrapeTool(api_key="test_key")
        with self.assertRaises(RateLimitError):
            tool._run(website_url="https://www.example.com", user_prompt="test prompt")
        mock_client_instance.close.assert_called_once()

    def test_missing_api_key(self):
        with self.assertRaises(ValueError):
            ScrapegraphScrapeTool()