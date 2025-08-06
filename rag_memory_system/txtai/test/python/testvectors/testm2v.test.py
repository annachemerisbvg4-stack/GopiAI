"""
Model2Vec module tests
"""

import os
import unittest

import numpy as np

from txtai.vectors import VectorsFactory


class TestModel2Vec(unittest.TestCase):
    """
    Model2vec vectors tests
    """

    @classmethod
    def setUpClass(cls):
        """
        Create Model2Vec instance.
        """

        cls.model = VectorsFactory.create({"path": "minishlab/potion-base-8M"}, None)

    def testIndex(self):
        """
        Test indexing with Model2Vec vectors
        """

        ids, dimension, batches, stream = self.model.index([(0, "test", None)])

        self.assertEqual(len(ids), 1)
        self.assertEqual(dimension, 256)
        self.assertEqual(batches, 1)
        self.assertIsNotNone(os.path.exists(stream))

        # Test shape of serialized embeddings
        with open(stream, "rb") as queue:
            self.assertEqual(np.load(queue).shape, (1, 256))

    def testSearch(self):
        """
        Test searching with Model2Vec vectors
        """
        ids, dimension, batches, stream = self.model.index([(0, "test", None)])
        results = self.model.search("test", 1)
        self.assertEqual(len(results), 1)

    def testUpsert(self):
        """
        Test upserting with Model2Vec vectors
        """
        self.model.upsert([(1, "test2", None)])
        ids, dimension, batches, stream = self.model.index([(0, "test", None)])
        results = self.model.search("test2", 1)
        self.assertEqual(len(results), 1)

    def testDelete(self):
        """
        Test deleting with Model2Vec vectors
        """
        self.model.upsert([(1, "test2", None)])
        self.model.delete([1])
        ids, dimension, batches, stream = self.model.index([(0, "test", None)])
        results = self.model.search("test2", 1)
        self.assertEqual(len(results), 0)

    def testBatchDelete(self):
        """
        Test batch deleting with Model2Vec vectors
        """
        self.model.upsert([(1, "test2", None), (2, "test3", None)])
        self.model.delete([1, 2])
        ids, dimension, batches, stream = self.model.index([(0, "test", None)])
        results = self.model.search("test2", 1)
        self.assertEqual(len(results), 0)
        results = self.model.search("test3", 1)
        self.assertEqual(len(results), 0)