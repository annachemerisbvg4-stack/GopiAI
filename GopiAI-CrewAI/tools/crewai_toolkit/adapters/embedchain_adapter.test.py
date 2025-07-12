import unittest
from unittest.mock import MagicMock

from crewai_tools.tools.rag.rag_tool import Adapter

from .rag_embedchain import EmbedchainAdapter


class TestEmbedchainAdapter(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.adapter = EmbedchainAdapter(embedchain_app=self.mock_app)

    def test_query_without_summarize(self):
        self.mock_app.query.return_value = ("answer", [("source1", {}), ("source2", {})])
        result = self.adapter.query("question")
        self.assertEqual(result, "source1\n\nsource2")

    def test_query_with_summarize(self):
        self.adapter.summarize = True
        self.mock_app.query.return_value = ("answer", [("source1", {}), ("source2", {})])
        result = self.adapter.query("question")
        self.assertEqual(result, "answer")

    def test_add(self):
        self.adapter.add("data")
        self.mock_app.add.assert_called_once_with("data")

    def test_add_with_kwargs(self):
        self.adapter.add("data", arg1="value1")
        self.mock_app.add.assert_called_once_with("data", arg1="value1")

    def test_inheritance(self):
        self.assertTrue(issubclass(EmbedchainAdapter, Adapter))