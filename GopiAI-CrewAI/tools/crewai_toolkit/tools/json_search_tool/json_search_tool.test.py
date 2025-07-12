import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from embedchain.tools.search.json_search import JSONSearchTool, JSONSearchToolSchema, FixedJSONSearchToolSchema


class TestJSONSearchTool(unittest.TestCase):

    @patch('embedchain.tools.search.rag.rag_tool.RagTool.add')
    def test_json_search_tool_init_with_json_path(self, mock_add):
        tool = JSONSearchTool(json_path="test.json")
        self.assertEqual(tool.args_schema, FixedJSONSearchToolSchema)
        self.assertTrue("test.json" in tool.description)
        mock_add.assert_called_once_with("test.json", data_type=DataType.JSON)

    def test_json_search_tool_init_without_json_path(self):
        tool = JSONSearchTool()
        self.assertEqual(tool.args_schema, JSONSearchToolSchema)

    @patch('embedchain.tools.search.rag.rag_tool.RagTool._run')
    def test_json_search_tool_run_with_json_path(self, mock_super_run):
        tool = JSONSearchTool()
        tool._run(search_query="test query", json_path="test.json")
        mock_super_run.assert_called_once_with(query="test query")

    @patch('embedchain.tools.search.rag.rag_tool.RagTool._run')
    def test_json_search_tool_run_without_json_path(self, mock_super_run):
        tool = JSONSearchTool()
        tool._run(search_query="test query")
        mock_super_run.assert_called_once_with(query="test query")

    def test_json_search_tool_schema(self):
        schema = JSONSearchToolSchema(search_query="query", json_path="path")
        self.assertEqual(schema.search_query, "query")
        self.assertEqual(schema.json_path, "path")