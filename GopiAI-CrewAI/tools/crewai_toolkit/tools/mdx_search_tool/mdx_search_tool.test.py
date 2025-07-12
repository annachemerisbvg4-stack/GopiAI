import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from embedchain.tools.mdx_search import (
    FixedMDXSearchToolSchema,
    MDXSearchTool,
    MDXSearchToolSchema,
)
from pydantic import ValidationError


class TestMDXSearchTool(unittest.TestCase):
    def test_mdx_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            MDXSearchToolSchema(search_query="test")
        MDXSearchToolSchema(search_query="test", mdx="test.mdx")

    def test_fixed_mdx_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            FixedMDXSearchToolSchema()
        FixedMDXSearchToolSchema(search_query="test")

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_mdx_search_tool_run(self, mock_super_run):
        mock_super_run.return_value = "test_result"
        tool = MDXSearchTool()
        result = tool._run(search_query="test_query", mdx="test.mdx")
        self.assertEqual(result, "test_result")
        mock_super_run.assert_called_once_with(query="test_query")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_mdx_search_tool_add(self, mock_super_add):
        tool = MDXSearchTool()
        tool.add("test.mdx")
        mock_super_add.assert_called_once_with("test.mdx", data_type=DataType.MDX)

    def test_mdx_search_tool_init_with_mdx(self):
        tool = MDXSearchTool(mdx="test.mdx")
        self.assertEqual(tool.args_schema, FixedMDXSearchToolSchema)
        self.assertTrue("test.mdx" in tool.description)