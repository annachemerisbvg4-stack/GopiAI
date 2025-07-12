import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from crewai_tools.tools.rag.lance_db import LanceDBAdapter

class TestLanceDBAdapter(unittest.TestCase):

    @patch("crewai_tools.tools.rag.lance_db.lancedb_connect")
    @patch("crewai_tools.tools.rag.lance_db.OpenAIClient")
    def test_query(self, MockOpenAIClient, MockLanceDBConnect):
        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_db.open_table.return_value = mock_table
        MockLanceDBConnect.return_value = mock_db
        mock_embedding = MagicMock(return_value=[[0.1, 0.2, 0.3]])
        mock_openai_client = MagicMock()
        mock_openai_client.embeddings.create.return_value.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        MockOpenAIClient.return_value = mock_openai_client
        mock_table.search.return_value.limit.return_value.select.return_value.to_list.return_value = [{"text": "result1"}, {"text": "result2"}]

        adapter = LanceDBAdapter(uri="test_uri", table_name="test_table", embedding_function=mock_embedding, top_k=2)
        result = adapter.query("test_question")

        self.assertEqual(result, "result1\nresult2")

    @patch("crewai_tools.tools.rag.lance_db.lancedb_connect")
    def test_add(self, MockLanceDBConnect):
        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_db.open_table.return_value = mock_table
        MockLanceDBConnect.return_value = mock_db

        adapter = LanceDBAdapter(uri="test_uri", table_name="test_table")
        adapter.add(arg1="value1", arg2="value2")

        mock_table.add.assert_called_once_with(arg1="value1", arg2="value2")

    @patch("crewai_tools.tools.rag.lance_db.lancedb_connect")
    def test_model_post_init(self, MockLanceDBConnect):
        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_db.open_table.return_value = mock_table
        MockLanceDBConnect.return_value = mock_db

        adapter = LanceDBAdapter(uri="test_uri", table_name="test_table")

        MockLanceDBConnect.assert_called_once_with("test_uri")
        mock_db.open_table.assert_called_once_with("test_table")
        self.assertEqual(adapter._table, mock_table)

    def test_default_embedding_function(self):
        from crewai_tools.tools.rag.lance_db import _default_embedding_function
        embedding_function = _default_embedding_function()
        self.assertTrue(callable(embedding_function))

    def test_init_with_path(self):
        adapter = LanceDBAdapter(uri=Path("test_uri"), table_name="test_table")
        self.assertEqual(adapter.uri, Path("test_uri"))