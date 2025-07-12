import unittest
from unittest.mock import MagicMock

from crewai_tools.tools.rag.rag_tool import Adapter
from .pdf_embedchain_adapter import PDFEmbedchainAdapter


class TestPDFEmbedchainAdapter(unittest.TestCase):
    def test_query_with_src(self):
        mock_app = MagicMock()
        mock_app.config.id = "test_app_id"
        mock_app.query.return_value = ("test_result", [("source1",), ("source2",)])
        adapter = PDFEmbedchainAdapter(embedchain_app=mock_app, src="test_src")
        result = adapter.query("test_question")
        self.assertEqual(result, "source1\n\nsource2")
        mock_app.query.assert_called_once()

    def test_query_without_src(self):
        mock_app = MagicMock()
        mock_app.config.id = "test_app_id"
        mock_app.query.return_value = ("test_result", [("source1",), ("source2",)])
        adapter = PDFEmbedchainAdapter(embedchain_app=mock_app)
        result = adapter.query("test_question")
        self.assertEqual(result, "source1\n\nsource2")
        mock_app.query.assert_called_once()

    def test_query_summarize(self):
        mock_app = MagicMock()
        mock_app.config.id = "test_app_id"
        mock_app.query.return_value = ("test_result", [("source1",), ("source2",)])
        adapter = PDFEmbedchainAdapter(embedchain_app=mock_app, summarize=True)
        result = adapter.query("test_question")
        self.assertEqual(result, "test_result")
        mock_app.query.assert_called_once()

    def test_add_with_args(self):
        mock_app = MagicMock()
        adapter = PDFEmbedchainAdapter(embedchain_app=mock_app)
        adapter.add("test_src", "arg1", "arg2")
        self.assertEqual(adapter.src, "test_src")
        mock_app.add.assert_called_once_with("test_src", "arg1", "arg2")

    def test_add_without_args(self):
        mock_app = MagicMock()
        adapter = PDFEmbedchainAdapter(embedchain_app=mock_app)
        adapter.add()
        self.assertIsNone(adapter.src)
        mock_app.add.assert_called_once_with()