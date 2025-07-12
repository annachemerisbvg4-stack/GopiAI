import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Any
from bs4 import BeautifulSoup

from tools.scrape_element_from_website import (
    ScrapeElementFromWebsiteTool,
    ScrapeElementFromWebsiteToolSchema,
    FixedScrapeElementFromWebsiteToolSchema,
)


class TestScrapeElementFromWebsiteTool(unittest.TestCase):
    @patch("requests.get")
    def test_run_with_kwargs(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = "<html><body><div id='test'>Test Content</div></body></html>"
        mock_get.return_value = mock_response
        tool = ScrapeElementFromWebsiteTool()
        result = tool._run(website_url="http://example.com", css_element="#test")
        self.assertEqual(result, "Test Content")

    @patch("requests.get")
    def test_run_with_instance_attributes(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = "<html><body><div id='test'>Test Content</div></body></html>"
        mock_get.return_value = mock_response
        tool = ScrapeElementFromWebsiteTool(
            website_url="http://example.com", css_element="#test"
        )
        result = tool._run()
        self.assertEqual(result, "Test Content")

    @patch("requests.get")
    def test_run_with_multiple_elements(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = "<html><body><div class='test'>Test1</div><div class='test'>Test2</div></body></html>"
        mock_get.return_value = mock_response
        tool = ScrapeElementFromWebsiteTool()
        result = tool._run(website_url="http://example.com", css_element=".test")
        self.assertEqual(result, "Test1\nTest2")

    def test_tool_description_generation(self):
        tool = ScrapeElementFromWebsiteTool(website_url="http://example.com", css_element="#test")
        self.assertIn("http://example.com", tool.description)
        self.assertEqual(tool.args_schema, FixedScrapeElementFromWebsiteToolSchema)

    @patch("requests.get")
    def test_run_with_cookies(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = "<html><body><div id='test'>Test Content</div></body></html>"
        mock_get.return_value = mock_response
        tool = ScrapeElementFromWebsiteTool(
            website_url="http://example.com",
            css_element="#test",
            cookies={"name": "test_cookie", "value": "TEST_COOKIE_VALUE"},
        )
        with patch.dict("os.environ", {"TEST_COOKIE_VALUE": "cookie_value"}):
            tool._run()
            mock_get.assert_called_with(
                "http://example.com",
                headers=tool.headers,
                cookies={"test_cookie": "cookie_value"},
            )