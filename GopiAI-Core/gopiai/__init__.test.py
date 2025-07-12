import unittest
import GopiAI

class TestGopiAI(unittest.TestCase):

    def test_namespace_package_exists(self):
        self.assertTrue(hasattr(GopiAI, '__path__'))

    def test_namespace_package_is_list(self):
        self.assertIsInstance(GopiAI.__path__, list)

    def test_namespace_package_not_empty(self):
        self.assertGreater(len(GopiAI.__path__), 0)

    def test_namespace_package_type(self):
        self.assertIsInstance(GopiAI.__path__, list)

    def test_namespace_package_importable(self):
        try:
            import GopiAI
        except ImportError:
            self.fail("GopiAI could not be imported")

if __name__ == '__main__':
    unittest.main()