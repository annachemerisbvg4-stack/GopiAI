import unittest
import os
import shutil
import tempfile
from crewai.tools import FileCompressorTool


class FileCompressorToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = FileCompressorTool()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")
        self.test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(self.test_dir)
        with open(os.path.join(self.test_dir, "test_file2.txt"), "w") as f:
            f.write("test content 2")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_compress_zip_file(self):
        output_path = os.path.join(self.temp_dir, "test_file.zip")
        result = self.tool._run(input_path=self.test_file, output_path=output_path, overwrite=True, format="zip")
        self.assertIn("Successfully compressed", result)
        self.assertTrue(os.path.exists(output_path))

    def test_compress_zip_directory(self):
        output_path = os.path.join(self.temp_dir, "test_dir.zip")
        result = self.tool._run(input_path=self.test_dir, output_path=output_path, overwrite=True, format="zip")
        self.assertIn("Successfully compressed", result)
        self.assertTrue(os.path.exists(output_path))

    def test_compress_tar_gz(self):
        output_path = os.path.join(self.temp_dir, "test_dir.tar.gz")
        result = self.tool._run(input_path=self.test_dir, output_path=output_path, overwrite=True, format="tar.gz")
        self.assertIn("Successfully compressed", result)
        self.assertTrue(os.path.exists(output_path))

    def test_invalid_input_path(self):
        result = self.tool._run(input_path="non_existent_file.txt", output_path="output.zip", overwrite=True, format="zip")
        self.assertIn("Input path", result)

    def test_invalid_format(self):
        result = self.tool._run(input_path=self.test_file, output_path="output.invalid", overwrite=True, format="invalid")
        self.assertIn("Compression format", result)
