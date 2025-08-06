import unittest
from unittest.mock import MagicMock

from your_module import EmbeddingsTool, ToolFactory, FunctionTool  # Replace your_module


class TestTools(unittest.TestCase):

    def test_embeddings_tool_creation(self):
        tool = EmbeddingsTool(name="test", description="test", embeddings=MagicMock())
        self.assertIsInstance(tool, EmbeddingsTool)

    def test_function_tool_creation(self):
        tool = FunctionTool(name="test", description="test", function=MagicMock())
        self.assertIsInstance(tool, FunctionTool)

    def test_tool_factory_create_embeddings(self):
        factory = ToolFactory()
        tool = factory.create("embeddings", name="test", description="test", embeddings=MagicMock())
        self.assertIsInstance(tool, EmbeddingsTool)

    def test_tool_factory_create_function(self):
        factory = ToolFactory()
        tool = factory.create("function", name="test", description="test", function=MagicMock())
        self.assertIsInstance(tool, FunctionTool)

    def test_tool_factory_create_invalid(self):
        factory = ToolFactory()
        with self.assertRaises(ValueError):
            factory.create("invalid", name="test", description="test")