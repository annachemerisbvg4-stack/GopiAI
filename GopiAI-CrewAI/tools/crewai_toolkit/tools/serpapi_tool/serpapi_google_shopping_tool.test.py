import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from tools.serpapi_google_shopping import SerpApiGoogleShoppingTool, SerpApiGoogleShoppingToolSchema


class TestSerpApiGoogleShoppingTool(unittest.TestCase):

    def test_serpapi_google_shopping_tool_schema_validation(self):
        with self.assertRaises(ValidationError):
            SerpApiGoogleShoppingToolSchema()

        SerpApiGoogleShoppingToolSchema(search_query="test")

    def test_serpapi_google_shopping_tool_run(self):
        mock_client = MagicMock()
        mock_client.search.return_value = MagicMock(as_dict=MagicMock(return_value={"test": "test"}))
        tool = SerpApiGoogleShoppingTool(client=mock_client)
        result = tool._run(search_query="test")
        self.assertEqual(result, {"test": "test"})

    def test_serpapi_google_shopping_tool_run_with_location(self):
        mock_client = MagicMock()
        mock_client.search.return_value = MagicMock(as_dict=MagicMock(return_value={"test": "test"}))
        tool = SerpApiGoogleShoppingTool(client=mock_client)
        result = tool._run(search_query="test", location="New York")
        self.assertEqual(result, {"test": "test"})

    def test_serpapi_google_shopping_tool_run_http_error(self):
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("HTTPError")
        tool = SerpApiGoogleShoppingTool(client=mock_client)
        result = tool._run(search_query="test")
        self.assertTrue("An error occurred" in result)