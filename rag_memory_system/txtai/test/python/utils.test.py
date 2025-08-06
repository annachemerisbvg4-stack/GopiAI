import unittest
import os
from unittest.mock import patch

class Utils:
    """
    Utility constants and methods
    """

    PATH = "/tmp/txtai"

class TestUtils(unittest.TestCase):

    def test_path_exists(self):
        self.assertEqual(Utils.PATH, "/tmp/txtai")

    def test_path_is_string(self):
        self.assertIsInstance(Utils.PATH, str)

    @patch.dict(os.environ, {"TEST_PATH": "/tmp/test"})
    def test_path_override(self):
        self.assertEqual(Utils.PATH, "/tmp/txtai")

    def test_path_not_none(self):
        self.assertIsNotNone(Utils.PATH)

    def test_path_not_empty(self):
        self.assertTrue(len(Utils.PATH) > 0)