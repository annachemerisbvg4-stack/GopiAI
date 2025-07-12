import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from langchain_community.tools.google_serper.tool import (
    SerpApiGoogleSearchTool,
    SerpApiGoogleSearchToolSchema,
)


class TestSerpApiGoogleSearchTool(unittest.TestCase):
    def test_serpapi_google_search_tool_schema_validation(self):
        with self.assertRaises(ValidationError):
            SerpApiGoogleSearchToolSchema()

        SerpApiGoogleSearchToolSchema(search_query="test")

    def test_serpapi_google_search_tool_run_success(self):
        mock_client = MagicMock()
        mock_client.search.return_value = MagicMock(
            as_dict=MagicMock(return_value={"test": "test"})
        )
        tool = SerpApiGoogleSearchTool(client=mock_client)
        result = tool._run(search_query="test")
        self.assertEqual(result, {"test": "test"})

    def test_serpapi_google_search_tool_run_http_error(self):
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("HTTPError")
        tool = SerpApiGoogleSearchTool(client=mock_client)
        result = tool._run(search_query="test")
        self.assertIn("An error occurred", result)

    def test_serpapi_google_search_tool_omit_fields(self):
        mock_client = MagicMock()
        mock_client.search.return_value = MagicMock(
            as_dict=MagicMock(
                return_value={
                    "search_metadata": "test",
                    "search_parameters": "test",
                    "serpapi_test": "test",
                    "test_token": "test",
                    "displayed_link": "test",
                    "pagination": "test",
                    "test": "test",
                }
            )
        )
        tool = SerpApiGoogleSearchTool(client=mock_client)
        result = tool._run(search_query="test")
        self.assertEqual(result, {"test": "test"})