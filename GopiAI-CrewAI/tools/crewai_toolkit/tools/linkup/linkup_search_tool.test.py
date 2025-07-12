import unittest
from unittest.mock import patch, MagicMock

from crewai.tools import BaseTool

try:
    from linkup import LinkupClient

    LINKUP_AVAILABLE = True
except ImportError:
    LINKUP_AVAILABLE = False
    LinkupClient = MagicMock  # type placeholder when package is not available

from pydantic import PrivateAttr

from crewai.tools.linkup_search import LinkupSearchTool


class TestLinkupSearchTool(unittest.TestCase):
    @patch("crewai.tools.linkup_search.LinkupClient")
    def test_initialization(self, MockLinkupClient):
        api_key = "test_api_key"
        tool = LinkupSearchTool(api_key=api_key)
        MockLinkupClient.assert_called_once_with(api_key=api_key)
        self.assertIsInstance(tool, LinkupSearchTool)

    @patch("crewai.tools.linkup_search.LinkupClient")
    def test_run_success(self, MockLinkupClient):
        api_key = "test_api_key"
        tool = LinkupSearchTool(api_key=api_key)
        mock_client = MockLinkupClient.return_value
        mock_response = MagicMock()
        mock_response.results = [
            MagicMock(name="Test Result", url="http://test.com", content="Test Content")
        ]
        mock_client.search.return_value = mock_response
        result = tool._run(query="test_query")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 1)

    @patch("crewai.tools.linkup_search.LinkupClient")
    def test_run_failure(self, MockLinkupClient):
        api_key = "test_api_key"
        tool = LinkupSearchTool(api_key=api_key)
        mock_client = MockLinkupClient.return_value
        mock_client.search.side_effect = Exception("Test Error")
        result = tool._run(query="test_query")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Test Error")

    @patch("crewai.tools.linkup_search.LinkupClient")
    def test_package_dependencies(self, MockLinkupClient):
        api_key = "test_api_key"
        tool = LinkupSearchTool(api_key=api_key)
        self.assertEqual(tool.package_dependencies, ["linkup-sdk"])