import unittest
from unittest.mock import MagicMock

from fastapi import UploadFile
from fastapi.testclient import TestClient

from main import app  # Assuming your FastAPI app is in main.py


class TestUpload(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_upload_no_files(self):
        response = self.client.post("/upload")
        self.assertEqual(response.status_code, 422)

    def test_upload_single_file(self):
        file_content = b"test file content"
        file_mock = MagicMock(spec=UploadFile, filename="test.txt", file=MagicMock(read=MagicMock(return_value=file_content)))
        response = self.client.post("/upload", files={"files": ("test.txt", file_content)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_upload_multiple_files(self):
        file_content1 = b"test file content 1"
        file_content2 = b"test file content 2"
        files = [("files", ("test1.txt", file_content1)), ("files", ("test2.txt", file_content2))]
        response = self.client.post("/upload", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_upload_with_suffix(self):
        file_content = b"test file content"
        response = self.client.post("/upload", files={"files": ("test.txt", file_content)}, data={"suffix": ".test"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()[0].endswith(".test"))

    def test_upload_empty_file(self):
        file_content = b""
        response = self.client.post("/upload", files={"files": ("test.txt", file_content)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)