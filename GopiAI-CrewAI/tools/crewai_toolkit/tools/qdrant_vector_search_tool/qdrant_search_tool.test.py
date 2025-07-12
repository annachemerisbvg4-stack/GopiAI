import unittest
from unittest.mock import patch, MagicMock
import json
import os

from crewai.tools.qdrant_vector_search import (
    QdrantVectorSearchTool,
    QdrantToolSchema,
    QDRANT_AVAILABLE,
)


class TestQdrantVectorSearchTool(unittest.TestCase):
    @unittest.skipUnless(
        QDRANT_AVAILABLE, "Qdrant client not available, skipping tests."
    )
    @patch("crewai.tools.qdrant_vector_search.QdrantClient")
    def test_qdrant_tool_initialization(self, MockQdrantClient):
        tool = QdrantVectorSearchTool(
            qdrant_url="http://localhost:6333", collection_name="test_collection"
        )
        self.assertIsInstance(tool, QdrantVectorSearchTool)
        MockQdrantClient.assert_called_once_with(url="http://localhost:6333", api_key=None)

    @unittest.skipUnless(
        QDRANT_AVAILABLE, "Qdrant client not available, skipping tests."
    )
    @patch("crewai.tools.qdrant_vector_search.QdrantClient")
    def test_qdrant_tool_initialization_with_api_key(self, MockQdrantClient):
        tool = QdrantVectorSearchTool(
            qdrant_url="http://localhost:6333",
            collection_name="test_collection",
            qdrant_api_key="test_api_key",
        )
        self.assertIsInstance(tool, QdrantVectorSearchTool)
        MockQdrantClient.assert_called_once_with(
            url="http://localhost:6333", api_key="test_api_key"
        )

    @unittest.skipUnless(
        QDRANT_AVAILABLE, "Qdrant client not available, skipping tests."
    )
    @patch("crewai.tools.qdrant_vector_search.QdrantClient")
    def test_qdrant_tool_run(self, MockQdrantClient):
        mock_client = MockQdrantClient.return_value
        mock_client.query_points.return_value = [
            (
                1.0,
                [
                    MagicMock(
                        payload={"metadata": {"key": "value"}, "text": "test context"},
                        score=0.8,
                    )
                ],
            )
        ]
        tool = QdrantVectorSearchTool(
            qdrant_url="http://localhost:6333", collection_name="test_collection"
        )
        with patch.object(tool, "_vectorize_query", return_value=[0.1, 0.2, 0.3]):
            result = tool._run(query="test query")
        self.assertIsInstance(result, str)
        result_dict = json.loads(result)
        self.assertEqual(len(result_dict), 1)
        self.assertEqual(result_dict[0]["metadata"], {"key": "value"})
        self.assertEqual(result_dict[0]["context"], "test context")
        self.assertEqual(result_dict[0]["distance"], 0.8)

    @unittest.skipUnless(
        QDRANT_AVAILABLE, "Qdrant client not available, skipping tests."
    )
    @patch("crewai.tools.qdrant_vector_search.QdrantClient")
    def test_qdrant_tool_run_with_filter(self, MockQdrantClient):
        mock_client = MockQdrantClient.return_value
        mock_client.query_points.return_value = [
            (
                1.0,
                [
                    MagicMock(
                        payload={"metadata": {"key": "value"}, "text": "test context"},
                        score=0.8,
                    )
                ],
            )
        ]
        tool = QdrantVectorSearchTool(
            qdrant_url="http://localhost:6333", collection_name="test_collection"
        )
        with patch.object(tool, "_vectorize_query", return_value=[0.1, 0.2, 0.3]):
            result = tool._run(query="test query", filter_by="key", filter_value="value")
        self.assertIsInstance(result, str)
        result_dict = json.loads(result)
        self.assertEqual(len(result_dict), 1)
        self.assertEqual(result_dict[0]["metadata"], {"key": "value"})
        self.assertEqual(result_dict[0]["context"], "test context")
        self.assertEqual(result_dict[0]["distance"], 0.8)

    @unittest.skipUnless(
        QDRANT_AVAILABLE, "Qdrant client not available, skipping tests."
    )
    def test_qdrant_tool_schema(self):
        schema = QdrantToolSchema(query="test query")
        self.assertEqual(schema.query, "test query")