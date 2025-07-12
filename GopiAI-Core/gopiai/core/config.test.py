import unittest
from unittest.mock import patch, mock_open
import json
from pathlib import Path
from gopiai_config import GopiAIConfig, ConfigManager, get_config, get_setting, set_setting

class TestConfigManager(unittest.TestCase):

    @patch("gopiai_config.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    def test_load_config_default(self, mock_file, mock_exists):
        mock_exists.return_value = False
        manager = ConfigManager()
        self.assertIsInstance(manager.config, GopiAIConfig)

    @patch("gopiai_config.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"debug_mode": true}')
    def test_load_config_from_file(self, mock_file, mock_exists):
        mock_exists.return_value = True
        manager = ConfigManager()
        self.assertTrue(manager.config.debug_mode)

    def test_get_setting(self):
        manager = ConfigManager()
        value = manager.get("ui.theme")
        self.assertEqual(value, "dark")

    def test_set_setting(self):
        manager = ConfigManager()
        manager.set("ui.theme", "light", save=False)
        self.assertEqual(manager.config.ui.theme, "light")

    @patch("gopiai_config.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    def test_global_functions(self, mock_file, mock_exists):
        mock_exists.return_value = False
        config = get_config()
        self.assertIsInstance(config, GopiAIConfig)
        set_setting("debug_mode", True, save=False)
        self.assertTrue(get_setting("debug_mode"))

if __name__ == '__main__':
    unittest.main()