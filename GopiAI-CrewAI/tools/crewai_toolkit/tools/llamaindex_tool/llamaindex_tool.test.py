import unittest
from unittest.mock import MagicMock, patch

from crewai.tools.llama_index_tool import LlamaIndexTool
from pydantic import BaseModel, Field


class TestLlamaIndexTool(unittest.TestCase):
    def test_from_tool_valid(self):
        mock_tool = MagicMock()
        mock_tool.metadata.name = "TestTool"
        mock_tool.metadata.description = "Test Description"

        class MockSchema(BaseModel):
            input: str = Field(..., description="Test input")

        mock_tool.metadata.fn_schema = MockSchema

        tool = LlamaIndexTool.from_tool(mock_tool)
        self.assertEqual(tool.name, "TestTool")
        self.assertEqual(tool.description, "Test Description")
        self.assertEqual(tool.args_schema, MockSchema)
        self.assertEqual(tool.llama_index_tool, mock_tool)

    def test_from_tool_invalid_type(self):
        with self.assertRaises(ValueError):
            LlamaIndexTool.from_tool("not_a_tool")

    def test_from_tool_no_schema(self):
        mock_tool = MagicMock()
        mock_tool.metadata.fn_schema = None
        with self.assertRaises(ValueError):
            LlamaIndexTool.from_tool(mock_tool)

    @patch("crewai.tools.llama_index_tool.QueryEngineTool")
    def test_from_query_engine(self, MockQueryEngineTool):
        mock_query_engine = MagicMock()
        tool = LlamaIndexTool.from_query_engine(mock_query_engine, name="TestQueryEngine", description="Test Description")
        self.assertEqual(tool.name, "TestQueryEngine")
        self.assertEqual(tool.description, "Test Description")

    def test_run(self):
        mock_tool = MagicMock()
        mock_tool.return_value.content = "Test Result"
        tool = LlamaIndexTool(name="TestTool", description="Test Description", args_schema=BaseModel, llama_index_tool=mock_tool, result_as_answer=True)
        result = tool._run(arg1="test")
        self.assertEqual(result, "Test Result")