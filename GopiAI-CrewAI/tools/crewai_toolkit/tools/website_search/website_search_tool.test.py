import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from embedchain.tools.web_page_search import (
    FixedWebsiteSearchToolSchema,
    WebsiteSearchTool,
    WebsiteSearchToolSchema,
)
from pydantic import ValidationError


class TestWebsiteSearchTool(unittest.TestCase):
    def test_website_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            WebsiteSearchToolSchema(search_query="test")
        WebsiteSearchToolSchema(search_query="test", website="https://example.com")

    def test_fixed_website_search_tool_schema(self):
        FixedWebsiteSearchToolSchema(search_query="test")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_website_search_tool_init_with_website(self, mock_add):
        tool = WebsiteSearchTool(website="https://example.com")
        self.assertEqual(tool.args_schema, FixedWebsiteSearchToolSchema)
        mock_add.assert_called_once_with("https://example.com", data_type=DataType.WEB_PAGE)

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_website_search_tool_run_with_website(self, mock_super_run, mock_add):
        tool = WebsiteSearchTool()
        tool._run(search_query="test query", website="https://example.com")
        mock_add.assert_called_once_with("https://example.com", data_type=DataType.WEB_PAGE)
        mock_super_run.assert_called_once_with(query="test query")

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_website_search_tool_run_without_website(self, mock_super_run):
        tool = WebsiteSearchTool()
        tool._run(search_query="test query")
        mock_super_run.assert_called_once_with(query="test query")