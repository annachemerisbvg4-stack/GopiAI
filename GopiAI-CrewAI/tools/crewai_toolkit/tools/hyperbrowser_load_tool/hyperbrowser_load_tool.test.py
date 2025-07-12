import unittest
from unittest.mock import patch, MagicMock
import os

from crewai.tools.hyperbrowser_load import HyperbrowserLoadTool, HyperbrowserLoadToolSchema
from pydantic import ValidationError

class TestHyperbrowserLoadTool(unittest.TestCase):

    @patch.dict(os.environ, {"HYPERBROWSER_API_KEY": "test_api_key"})
    @patch("crewai.tools.hyperbrowser_load.Hyperbrowser")
    def test_tool_initialization(self, MockHyperbrowser):
        tool = HyperbrowserLoadTool()
        self.assertIsInstance(tool, HyperbrowserLoadTool)
        self.assertEqual(tool.api_key, "test_api_key")
        MockHyperbrowser.assert_called_once_with(api_key="test_api_key")

    def test_tool_initialization_no_api_key(self):
        with self.assertRaises(ValueError):
            HyperbrowserLoadTool(api_key=None)

    @patch.dict(os.environ, {"HYPERBROWSER_API_KEY": "test_api_key"})
    @patch("crewai.tools.hyperbrowser_load.Hyperbrowser")
    def test_run_scrape(self, MockHyperbrowser):
        mock_hyperbrowser_instance = MockHyperbrowser.return_value
        mock_hyperbrowser_instance.scrape.start_and_wait.return_value.data.markdown = "test_markdown"
        tool = HyperbrowserLoadTool()
        result = tool._run(url="http://example.com", operation="scrape")
        self.assertEqual(result, "test_markdown")

    @patch.dict(os.environ, {"HYPERBROWSER_API_KEY": "test_api_key"})
    @patch("crewai.tools.hyperbrowser_load.Hyperbrowser")
    def test_run_crawl(self, MockHyperbrowser):
        mock_hyperbrowser_instance = MockHyperbrowser.return_value
        mock_hyperbrowser_instance.crawl.start_and_wait.return_value.data = [MagicMock(url="http://example.com", markdown="test_markdown")]
        tool = HyperbrowserLoadTool()
        result = tool._run(url="http://example.com", operation="crawl")
        self.assertIn("test_markdown", result)