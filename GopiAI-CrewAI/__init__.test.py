import unittest
from unittest.mock import patch

# Assuming the code to be tested is in a file named 'gopiai_crewai.py'
# and contains the version and author information.
import gopiai_crewai

class TestGopiAICrewAI(unittest.TestCase):

    def test_version(self):
        self.assertEqual(gopiai_crewai.__version__, "0.1.0")

    def test_author(self):
        self.assertEqual(gopiai_crewai.__author__, "GopiAI Team")

    def test_version_type(self):
        self.assertIsInstance(gopiai_crewai.__version__, str)

    def test_author_type(self):
        self.assertIsInstance(gopiai_crewai.__author__, str)

    def test_version_not_empty(self):
        self.assertTrue(len(gopiai_crewai.__version__) > 0)