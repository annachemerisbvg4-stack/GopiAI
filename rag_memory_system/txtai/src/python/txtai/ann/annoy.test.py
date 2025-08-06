import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from vectorai.ann.annoy_ import Annoy

class AnnoyTest(unittest.TestCase):
    @patch("vectorai.ann.annoy_.ANNOY", False)
    def test_init_no_annoy(self):
        with self.assertRaises(ImportError):
            Annoy({"dimensions": 10, "metric": "angular"})

    @patch("vectorai.ann.annoy_.ANNOY", True)
    @patch("vectorai.ann.annoy_.AnnoyIndex")
    def test_load(self, MockAnnoyIndex):
        annoy_instance = Annoy({"dimensions": 10, "metric": "angular"})
        annoy_instance.load("test_path")
        MockAnnoyIndex.return_value.load.assert_called_with("test_path")

    @patch("vectorai.ann.annoy_.ANNOY", True)
    @patch("vectorai.ann.annoy_.AnnoyIndex")
    def test_index(self, MockAnnoyIndex):
        annoy_instance = Annoy({"dimensions": 10, "metric": "angular"})
        embeddings = np.random.rand(5, 10)
        annoy_instance.index(embeddings)
        MockAnnoyIndex.return_value.build.assert_called()

    @patch("vectorai.ann.annoy_.ANNOY", True)
    @patch("vectorai.ann.annoy_.AnnoyIndex")
    def test_search(self, MockAnnoyIndex):
        annoy_instance = Annoy({"dimensions": 10, "metric": "angular"})
        annoy_instance.backend = MagicMock()
        annoy_instance.backend.get_nns_by_vector.return_value = ([1, 2], [0.1, 0.2])
        queries = np.random.rand(2, 10)
        results = annoy_instance.search(queries, 2)
        self.assertEqual(len(results), 2)

    @patch("vectorai.ann.annoy_.ANNOY", True)
    @patch("vectorai.ann.annoy_.AnnoyIndex")
    def test_count(self, MockAnnoyIndex):
        annoy_instance = Annoy({"dimensions": 10, "metric": "angular"})
        annoy_instance.backend = MagicMock()
        annoy_instance.backend.get_n_items.return_value = 5
        count = annoy_instance.count()
        self.assertEqual(count, 5)