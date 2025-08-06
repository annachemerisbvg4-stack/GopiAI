import os
import unittest

import numpy as np

from txtai.vectors import External, VectorsFactory


class TestExternal(unittest.TestCase):
    """
    External vectors tests
    """

    @classmethod
    def setUpClass(cls):
        """
        Create External vectors instance.
        """

        cls.model = VectorsFactory.create({"method": "external"}, None)

    def testIndex(self):
        """
        Test indexing with external vectors
        """

        # Generate dummy data
        data = np.random.rand(1000, 768).astype(np.float32)

        # Generate enough volume to test batching
        documents = [(x, data[x], None) for x in range(1000)]

        ids, dimension, batches, stream = self.model.index(documents)

        self.assertEqual(len(ids), 1000)
        self.assertEqual(dimension, 768)
        self.assertEqual(batches, 2)
        self.assertIsNotNone(os.path.exists(stream))

        # Test shape of serialized embeddings
        with open(stream, "rb") as queue:
            self.assertEqual(np.load(queue).shape, (500, 768))

    def testMethod(self):
        """
        Test method is derived when transform function passed
        """

        model = VectorsFactory.create({"transform": lambda x: x}, None)
        self.assertTrue(isinstance(model, External))

    def test_no_method_or_transform(self):
        """Test that External is not created if no method or transform is provided."""
        model = VectorsFactory.create({}, None)
        self.assertNotIsInstance(model, External)

    def test_empty_documents(self):
        """Test indexing with empty documents."""
        documents = []
        ids, dimension, batches, stream = self.model.index(documents)
        self.assertEqual(len(ids), 0)
        self.assertEqual(dimension, None)
        self.assertEqual(batches, 0)
        self.assertIsNone(stream)

    def test_small_batch(self):
        """Test indexing with a small number of documents."""
        data = np.random.rand(5, 768).astype(np.float32)
        documents = [(x, data[x], None) for x in range(5)]
        ids, dimension, batches, stream = self.model.index(documents)
        self.assertEqual(len(ids), 5)
        self.assertEqual(dimension, 768)
        self.assertEqual(batches, 1)
        self.assertIsNotNone(os.path.exists(stream))