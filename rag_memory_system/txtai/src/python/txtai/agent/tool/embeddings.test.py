import unittest
from unittest.mock import MagicMock

from smolagents import Tool

from ...embeddings import Embeddings
from your_module import EmbeddingsTool  # Replace your_module


class TestEmbeddingsTool(unittest.TestCase):

    def test_init(self):
        config = {
            "name": "TestEmbeddings",
            "description": "Test description",
            "target": MagicMock(spec=Embeddings)
        }
        tool = EmbeddingsTool(config)
        self.assertEqual(tool.name, "TestEmbeddings")
        self.assertTrue("Test description" in tool.description)
        self.assertIsInstance(tool, Tool)

    def test_forward(self):
        mock_embeddings = MagicMock(spec=Embeddings)
        mock_embeddings.search.return_value = [{"id": 1, "text": "test", "score": 0.9}]
        config = {
            "name": "TestEmbeddings",
            "description": "Test description",
            "target": mock_embeddings
        }
        tool = EmbeddingsTool(config)
        result = tool.forward("test query")
        self.assertEqual(result, [{"id": 1, "text": "test", "score": 0.9}])
        mock_embeddings.search.assert_called_once_with("test query", 5)

    def test_load_with_target(self):
        mock_embeddings = MagicMock(spec=Embeddings)
        config = {
            "name": "TestEmbeddings",
            "description": "Test description",
            "target": mock_embeddings
        }
        tool = EmbeddingsTool(config)
        loaded_embeddings = tool.load(config)
        self.assertEqual(loaded_embeddings, mock_embeddings)

    def test_load_without_target(self):
        config = {
            "name": "TestEmbeddings",
            "description": "Test description",
            "path": "test_path"
        }
        tool = EmbeddingsTool(config)
        embeddings = tool.load(config)
        self.assertIsInstance(embeddings, Embeddings)
        # Assert that load was called with the correct arguments
        # self.assertEqual(embeddings.path, "test_path") # Assuming path is an attribute of Embeddings

if __name__ == '__main__':
    unittest.main()