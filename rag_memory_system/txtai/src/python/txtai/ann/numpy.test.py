import unittest
import numpy as np
import tempfile
import os

from vectorhub.modules.indexer.numpy import NumPy

class TestNumPy(unittest.TestCase):
    def setUp(self):
        self.config = {"dimensions": 3, "quantize": 8}
        self.numpy_ann = NumPy(self.config)
        self.embeddings = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.queries = np.array([[1, 2, 3], [4, 5, 6]])

    def test_index_and_search(self):
        self.numpy_ann.index(self.embeddings)
        results = self.numpy_ann.search(self.queries, 2)
        self.assertEqual(len(results), 2)

    def test_append(self):
        self.numpy_ann.index(self.embeddings)
        new_embeddings = np.array([[10, 11, 12]])
        self.numpy_ann.append(new_embeddings)
        self.assertEqual(self.numpy_ann.backend.shape[0], 4)

    def test_delete(self):
        self.numpy_ann.index(self.embeddings)
        self.numpy_ann.delete([0, 2])
        self.assertEqual(np.count_nonzero(self.numpy_ann.backend), 3)

    def test_save_and_load(self):
        self.numpy_ann.index(self.embeddings)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "test_index.npy")
            self.numpy_ann.save(path)
            loaded_ann = NumPy(self.config)
            loaded_ann.load(path)
            np.testing.assert_array_equal(self.numpy_ann.backend, loaded_ann.backend)

    def test_hammingscore(self):
        self.numpy_ann.index(self.embeddings)
        scores = self.numpy_ann.hammingscore(self.queries)
        self.assertEqual(scores.shape, (2, 3))