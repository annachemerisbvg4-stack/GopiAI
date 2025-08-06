import unittest
import numpy as np
import os
import shutil

from txtai.ann import Faiss

class TestFaiss(unittest.TestCase):
    def setUp(self):
        self.test_dir = "testfaiss"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_index_and_search(self):
        embeddings = np.random.rand(100, 128).astype(np.float32)
        config = {}
        faiss_ann = Faiss(config)
        faiss_ann.index(embeddings)
        results = faiss_ann.search(np.random.rand(5, 128).astype(np.float32), 10)
        self.assertEqual(len(results), 5)

    def test_save_and_load(self):
        embeddings = np.random.rand(100, 128).astype(np.float32)
        config = {}
        faiss_ann = Faiss(config)
        faiss_ann.index(embeddings)
        path = os.path.join(self.test_dir, "test.faiss")
        faiss_ann.save(path)
        loaded_faiss_ann = Faiss(config)
        loaded_faiss_ann.load(path)
        self.assertEqual(faiss_ann.count(), loaded_faiss_ann.count())

    def test_append(self):
        embeddings1 = np.random.rand(50, 128).astype(np.float32)
        embeddings2 = np.random.rand(50, 128).astype(np.float32)
        config = {}
        faiss_ann = Faiss(config)
        faiss_ann.index(embeddings1)
        faiss_ann.append(embeddings2)
        self.assertEqual(faiss_ann.count(), 100)

    def test_delete(self):
        embeddings = np.random.rand(100, 128).astype(np.float32)
        config = {}
        faiss_ann = Faiss(config)
        faiss_ann.index(embeddings)
        faiss_ann.delete([0, 1, 2])
        self.assertEqual(faiss_ann.count(), 97)

    def test_binary_index(self):
        embeddings = np.random.rand(100, 16).astype(np.float32)
        config = {"quantize": 8}
        faiss_ann = Faiss(config)
        faiss_ann.index(embeddings)
        results = faiss_ann.search(np.random.rand(5, 16).astype(np.float32), 10)
        self.assertEqual(len(results), 5)