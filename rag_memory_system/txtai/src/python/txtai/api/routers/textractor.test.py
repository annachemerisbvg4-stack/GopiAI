import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from your_module import router  # Replace your_module

app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestTextractorAPI(unittest.TestCase):

    @patch("your_module.application.get")  # Replace your_module
    def test_textract_success(self, mock_application_get):
        mock_application_get.return_value.pipeline.return_value = "extracted text"
        response = client.get("/textract?file=test.pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "extracted text")

    @patch("your_module.application.get")  # Replace your_module
    def test_batchtextract_success(self, mock_application_get):
        mock_application_get.return_value.pipeline.return_value = ["text1", "text2"]
        response = client.post("/batchtextract", json=["file1.pdf", "file2.pdf"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["text1", "text2"])

    def test_batchtextract_validation_error(self):
        response = client.post("/batchtextract", json=123)
        self.assertEqual(response.status_code, 422)

    @patch("your_module.application.get")  # Replace your_module
    def test_textract_pipeline_exception(self, mock_application_get):
        mock_application_get.return_value.pipeline.side_effect = Exception("Pipeline error")
        response = client.get("/textract?file=test.pdf")
        self.assertEqual(response.status_code, 500)

    @patch("your_module.application.get")  # Replace your_module
    def test_batchtextract_pipeline_exception(self, mock_application_get):
        mock_application_get.return_value.pipeline.side_effect = Exception("Pipeline error")
        response = client.post("/batchtextract", json=["file1.pdf", "file2.pdf"])
        self.assertEqual(response.status_code, 500)