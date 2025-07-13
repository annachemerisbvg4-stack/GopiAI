import unittest
import numpy as np
from unittest.mock import patch

class TestHNSW(unittest.TestCase):

    @patch('hnsw.HNSWLIB', False)
    def test_init_hnswlib_not_available(self):
        from ann_benchmarks.algorithms.hnsw import HNSW
        config = {}
        with self.assertRaises(ImportError):
            HNSW(config)

    @patch('ann_benchmarks.algorithms.hnsw.HNSWLIB', True)
    def test_index(self):
        from ann_benchmarks.algorithms.hnsw import HNSW
        config = {"dimensions": 10, "metric": "ip"}
        hnsw = HNSW(config)
        embeddings = np.random.rand(100, 10).astype(np.float32)
        hnsw.index(embeddings)
        self.assertEqual(hnsw.config["offset"], 100)
        self.assertEqual(hnsw.config["deletes"], 0)

    @patch('ann_benchmarks.algorithms.hnsw.HNSWLIB', True)
    def test_append(self):
        from ann_benchmarks.algorithms.hnsw import HNSW
        config = {"dimensions": 10, "metric": "ip", "offset": 100}
        hnsw = HNSW(config)
        embeddings = np.random.rand(50, 10).astype(np.float32)
        hnsw.backend = unittest.mock.MagicMock()
        hnsw.append(embeddings)
        self.assertEqual(hnsw.config["offset"], 150)

    @patch('ann_benchmarks.algorithms.hnsw.HNSWLIB', True)
    def test_delete(self):
        from ann_benchmarks.algorithms.hnsw import HNSW
        config = {"dimensions": 10, "metric": "ip", "deletes": 0}
        hnsw = HNSW(config)
        hnsw.backend = unittest.mock.MagicMock()
        hnsw.delete([1, 2, 3])
        self.assertEqual(hnsw.config["deletes"], 3)

    @patch('ann_benchmarks.algorithms.hnsw.HNSWLIB', True)
    def test_search(self):
        from ann_benchmarks.algorithms.hnsw import HNSW
        config = {"dimensions": 10, "metric": "ip"}
        hnsw = HNSW(config)
        hnsw.backend = unittest.mock.MagicMock()
        hnsw.backend.knn_query.return_value = (np.array([[1, 2]]), np.array([[0.1, 0.2]]))
        queries = np.random.rand(10, 10).astype(np.float32)
        results = hnsw.search(queries, 2)
        self.assertEqual(len(results), 10)