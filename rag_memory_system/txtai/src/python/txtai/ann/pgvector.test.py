import unittest
from unittest.mock import MagicMock, patch

from annlite.index.pgvector import PGVector


class TestPGVector(unittest.TestCase):
    @unittest.skipIf(not PGVector, "PGVector dependencies not installed")
    def setUp(self):
        self.config = {"dimensions": 3, "url": "sqlite:///:memory:"}
        self.pgvector = PGVector(self.config)

    @patch("annlite.index.pgvector.Session")
    @patch("annlite.index.pgvector.create_engine")
    def test_connect(self, mock_create_engine, mock_session):
        self.pgvector.connect()
        self.assertTrue(self.pgvector.database)

    def test_prepare(self):
        data = [0.1, 0.2, 0.3]
        prepared_data = self.pgvector.prepare(data)
        self.assertEqual(prepared_data, data)

    @patch("annlite.index.pgvector.Session")
    @patch("annlite.index.pgvector.create_engine")
    def test_initialize(self, mock_create_engine, mock_session):
        self.pgvector.connect = MagicMock()
        self.pgvector.schema = MagicMock()
        self.pgvector.setting = MagicMock(return_value="vectors")
        self.pgvector.column = MagicMock(return_value=("column", "index"))
        self.pgvector.initialize()
        self.assertIsNotNone(self.pgvector.table)

    def test_score(self):
        score = 0.5
        calculated_score = self.pgvector.score(score)
        self.assertEqual(calculated_score, -0.5)

    def test_close(self):
        self.pgvector.database = MagicMock()
        self.pgvector.engine = MagicMock()
        self.pgvector.close()
        self.pgvector.database.close.assert_called_once()
        self.pgvector.engine.dispose.assert_called_once()