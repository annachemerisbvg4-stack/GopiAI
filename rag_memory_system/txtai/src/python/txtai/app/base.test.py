import unittest
from unittest.mock import patch, mock_open

from txtai.app import Application, ReadOnlyError


class TestApplication(unittest.TestCase):
    def test_read_yaml_from_file(self):
        yaml_content = "key: value"
        with patch("os.path.exists", return_value=True), patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Application.read("config.yaml")
            self.assertEqual(config, {"key": "value"})

    def test_read_yaml_from_string(self):
        yaml_content = "key: value"
        config = Application.read(yaml_content)
        self.assertEqual(config, {"key": "value"})

    def test_read_yaml_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Application.read("nonexistent_file.yaml")

    def test_add_read_only_error(self):
        config = {"writable": False}
        app = Application(config, loaddata=False)
        app.config = config
        with self.assertRaises(ReadOnlyError):
            app.add([{"id": 1, "data": "test"}])

    def test_index_read_only_error(self):
        config = {"writable": False}
        app = Application(config, loaddata=False)
        app.config = config
        app.documents = True
        with self.assertRaises(ReadOnlyError):
            app.index()