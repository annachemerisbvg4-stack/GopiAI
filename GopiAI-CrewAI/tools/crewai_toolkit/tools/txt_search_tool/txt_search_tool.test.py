import unittest
from unittest.mock import patch

from pydantic import ValidationError

from promptflow.tools.rag.rag_tool import RagTool
from promptflow.tools.txt_search.txt_search import (
    FixedTXTSearchToolSchema,
    TXTSearchTool,
    TXTSearchToolSchema,
)


class TestTXTSearchTool(unittest.TestCase):
    def test_txt_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            TXTSearchToolSchema(txt=None, search_query="test")
        TXTSearchToolSchema(txt="test.txt", search_query="test")

    def test_fixed_txt_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            FixedTXTSearchToolSchema(search_query=None)
        FixedTXTSearchToolSchema(search_query="test")

    @patch.object(RagTool, "_run")
    def test_txt_search_tool_run(self, mock_rag_tool_run):
        mock_rag_tool_run.return_value = "search result"
        tool = TXTSearchTool()
        result = tool._run(search_query="test", txt="test.txt")
        self.assertEqual(result, "search result")
        mock_rag_tool_run.assert_called_once_with(query="test")

    @patch.object(RagTool, "_run")
    def test_txt_search_tool_run_no_txt(self, mock_rag_tool_run):
        mock_rag_tool_run.return_value = "search result"
        tool = TXTSearchTool(txt="test.txt")
        result = tool._run(search_query="test")
        self.assertEqual(result, "search result")
        mock_rag_tool_run.assert_called_once_with(query="test")

    def test_txt_search_tool_init_with_txt(self):
        tool = TXTSearchTool(txt="test.txt")
        self.assertEqual(tool.args_schema, FixedTXTSearchToolSchema)
        self.assertTrue("test.txt" in tool.description)