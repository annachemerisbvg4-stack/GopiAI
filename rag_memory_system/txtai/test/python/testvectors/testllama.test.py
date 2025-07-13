import os
import unittest
import numpy as np
from txtai.vectors import VectorsFactory


class TestLlamaCpp(unittest.TestCase):
    """
    llama.cpp vectors tests
    """

    @classmethod
    def setUpClass(cls):
        """
        Create LlamaCpp instance.
        """

        cls.model = VectorsFactory.create({"path": "nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q2_K.gguf"}, None)

    def testIndex(self):
        """
        Test indexing with LlamaCpp vectors
        """

        ids, dimension, batches, stream = self.model.index([(0, "test", None)])

        self.assertEqual(len(ids), 1)
        self.assertEqual(dimension, 768)
        self.assertEqual(batches, 1)
        self.assertIsNotNone(os.path.exists(stream))

        # Test shape of serialized embeddings
        with open(stream, "rb") as queue:
            self.assertEqual(np.load(queue).shape, (1, 768))

    def test_encode(self):
        """Test encoding a single string."""
        embedding = self.model.encode("test")
        self.assertEqual(len(embedding), 768)

    def test_batch_encode(self):
        """Test encoding a batch of strings."""
        texts = ["test1", "test2", "test3"]
        embeddings = self.model.encode(texts)
        self.assertEqual(len(embeddings), 3)
        for embedding in embeddings:
            self.assertEqual(len(embedding), 768)

    def test_similarity(self):
        """Test similarity calculation."""
        embedding1 = self.model.encode("test1")
        embedding2 = self.model.encode("test2")
        similarity = self.model.similarity(embedding1, embedding2)
        self.assertIsInstance(similarity, float)

    def test_batch_similarity(self):
        """Test batch similarity calculation."""
        embedding = self.model.encode("test")
        embeddings = self.model.encode(["test1", "test2"])
        similarities = self.model.similarity(embedding, embeddings)
        self.assertEqual(len(similarities), 2)
        for similarity in similarities:
            self.assertIsInstance(similarity, float)