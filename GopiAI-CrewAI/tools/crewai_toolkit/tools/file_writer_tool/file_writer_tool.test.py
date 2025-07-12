import os
import unittest
from unittest.mock import patch, mock_open

from crewai.tools.file_writer import FileWriterTool, FileWriterToolInput, strtobool


class FileWriterToolTest(unittest.TestCase):
    def test_strtobool(self):
        self.assertTrue(strtobool("true"))
        self.assertFalse(strtobool("false"))
        with self.assertRaises(ValueError):
            strtobool("invalid")

    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_file_writer_tool_success(self, mock_file, mock_makedirs, mock_exists):
        tool = FileWriterTool()
        result = tool._run(filename="test.txt", content="test content", directory="./test_dir", overwrite=True)
        self.assertEqual(result, "Content successfully written to ./test_dir/test.txt")

    @patch("os.path.exists", return_value=True)
    def test_file_writer_tool_exists_no_overwrite(self, mock_exists):
        tool = FileWriterTool()
        result = tool._run(filename="test.txt", content="test content", directory="./test_dir", overwrite=False)
        self.assertIn("already exists", result)

    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    def test_file_writer_tool_no_directory(self, mock_makedirs, mock_exists):
        tool = FileWriterTool()
        with patch("builtins.open", new_callable=mock_open) as mock_file:
            result = tool._run(filename="test.txt", content="test content", overwrite=True)
            self.assertEqual(result, "Content successfully written to test.txt")

    def test_file_writer_tool_input_model(self):
        data = {"filename": "test.txt", "content": "test content", "directory": "./test_dir", "overwrite": "true"}
        input_model = FileWriterToolInput(**data)
        self.assertEqual(input_model.filename, "test.txt")
        self.assertEqual(input_model.content, "test content")
        self.assertEqual(input_model.directory, "./test_dir")
        self.assertEqual(input_model.overwrite, "true")