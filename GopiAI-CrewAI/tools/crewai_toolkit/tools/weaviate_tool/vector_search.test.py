import unittest
from unittest.mock import patch, MagicMock
import os
from pydantic import ValidationError

from crewai.tools.weaviate_tool import WeaviateVectorSearchTool, WeaviateToolSchema

class TestWeaviateVectorSearchTool(unittest.TestCase):

    @patch("crewai.tools.weaviate_tool.WEAVIATE_AVAILABLE", False)
    def test_tool_unavailable(self):
        with self.assertRaises(ImportError):
            WeaviateVectorSearchTool(weaviate_cluster_url="test", weaviate_api_key="test", collection_name="test")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("crewai.tools.weaviate_tool.WEAVIATE_AVAILABLE", True)
    @patch("crewai.tools.weaviate_tool.weaviate.connect_to_weaviate_cloud")
    def test_tool_run(self, mock_connect):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_response = MagicMock()

        mock_connect.return_value = mock_client
        mock_client.collections.get.return_value = mock_collection
        mock_collection.query.near_text.return_value = mock_response
        mock_response.objects = [MagicMock(properties={"test": "data"})]

        tool = WeaviateVectorSearchTool(weaviate_cluster_url="test", weaviate_api_key="test", collection_name="test")
        result = tool._run("test query")

        self.assertIn('"test": "data"', result)

    def test_tool_schema(self):
        data = {"query": "test query"}
        schema = WeaviateToolSchema(**data)
        self.assertEqual(schema.query, "test query")

    def test_tool_schema_validation_error(self):
        with self.assertRaises(ValidationError):
            WeaviateToolSchema()

    @patch.dict(os.environ, {}, clear=True)
    @patch("crewai.tools.weaviate_tool.WEAVIATE_AVAILABLE", True)
    def test_no_openai_api_key(self):
        with self.assertRaises(ValueError):
            WeaviateVectorSearchTool(weaviate_cluster_url="test", weaviate_api_key="test", collection_name="test")