import unittest
from unittest.mock import MagicMock

from crewai_tools.rag_tool import Adapter, RagTool


class TestRagTool(unittest.TestCase):
    def test_rag_tool_initialization_with_default_adapter(self):
        tool = RagTool()
        self.assertIsNotNone(tool.adapter)

    def test_rag_tool_initialization_with_custom_adapter(self):
        mock_adapter = MagicMock(spec=Adapter)
        tool = RagTool(adapter=mock_adapter)
        self.assertEqual(tool.adapter, mock_adapter)

    def test_rag_tool_add_calls_adapter_add(self):
        mock_adapter = MagicMock(spec=Adapter)
        tool = RagTool(adapter=mock_adapter)
        tool.add("test")
        mock_adapter.add.assert_called_once_with("test")

    def test_rag_tool_run_calls_adapter_query(self):
        mock_adapter = MagicMock(spec=Adapter)
        mock_adapter.query.return_value = "test_answer"
        tool = RagTool(adapter=mock_adapter)
        result = tool._run("test_question")
        self.assertEqual(result, "Relevant Content:\ntest_answer")
        mock_adapter.query.assert_called_once_with("test_question")

    def test_rag_tool_initialization_with_config(self):
        config = {"test": "value"}
        tool = RagTool(config=config)
        self.assertIsNotNone(tool.adapter)