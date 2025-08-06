import unittest

from vector_search import ANNFactory, Annoy, Faiss, HNSW, NumPy, PGVector, Torch


class TestANNImplementations(unittest.TestCase):
    def test_annoy_creation(self):
        annoy_index = ANNFactory.create("annoy", vector_size=128, metric="angular")
        self.assertIsInstance(annoy_index, Annoy)

    def test_faiss_creation(self):
        faiss_index = ANNFactory.create("faiss", vector_size=128, metric="ip")
        self.assertIsInstance(faiss_index, Faiss)

    def test_hnsw_creation(self):
        hnsw_index = ANNFactory.create("hnsw", vector_size=128, metric="cosine")
        self.assertIsInstance(hnsw_index, HNSW)

    def test_numpy_creation(self):
        numpy_index = ANNFactory.create("numpy", vector_size=128, metric="euclidean")
        self.assertIsInstance(numpy_index, NumPy)

    def test_pgvector_creation(self):
        pgvector_index = ANNFactory.create("pgvector", vector_size=128, metric="cosine")
        self.assertIsInstance(pgvector_index, PGVector)

    def test_torch_creation(self):
        torch_index = ANNFactory.create("torch", vector_size=128, metric="cosine")
        self.assertIsInstance(torch_index, Torch)


if __name__ == "__main__":
    unittest.main()