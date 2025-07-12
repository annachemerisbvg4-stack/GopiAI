import unittest
import gopiai

class TestGopiAI(unittest.TestCase):

    def test_version(self):
        self.assertEqual(gopiai.__version__, "0.1.0")

    def test_exports(self):
        expected_exports = [
            'get_logger', 'info', 'debug', 'warning', 'error', 'critical', 'logger',
            'get_config', 'get_config_manager', 'get_setting', 'set_setting', 'config'
        ]
        self.assertEqual(gopiai.__all__, expected_exports)

    def test_logging_import(self):
        self.assertTrue(hasattr(gopiai, 'get_logger'))

    def test_config_import(self):
        self.assertTrue(hasattr(gopiai, 'get_config'))

    def test_all_defined(self):
        for name in gopiai.__all__:
            self.assertTrue(hasattr(gopiai, name), f"'{name}' not found in gopiai module")