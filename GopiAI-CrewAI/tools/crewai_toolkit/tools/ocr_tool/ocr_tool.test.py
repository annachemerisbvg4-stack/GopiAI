import unittest
from unittest.mock import patch, mock_open
from pydantic import ValidationError

from crewai.tools import OCRTool
from crewai import LLM
from crewai.tools.ocr_tool import OCRToolSchema

class TestOCRTool(unittest.TestCase):

    def test_ocr_tool_initialization_with_default_llm(self):
        tool = OCRTool()
        self.assertIsNotNone(tool._llm)
        self.assertEqual(tool._llm.model, "gpt-4o")

    def test_ocr_tool_initialization_with_provided_llm(self):
        mock_llm = LLM(model="test_model")
        tool = OCRTool(llm=mock_llm)
        self.assertEqual(tool._llm.model, "test_model")

    def test_ocr_tool_schema_validation(self):
        valid_data = {"image_path_url": "path/to/image.jpg"}
        schema = OCRToolSchema(**valid_data)
        self.assertEqual(schema.image_path_url, "path/to/image.jpg")

        with self.assertRaises(ValidationError):
            OCRToolSchema(image_path_url=None)

    @patch("crewai.tools.ocr_tool.OCRTool._encode_image")
    @patch("crewai.LLM.call")
    def test_ocr_tool_run_local_image(self, mock_llm_call, mock_encode_image):
        mock_encode_image.return_value = "base64_encoded_image"
        mock_llm_call.return_value = "Extracted text from image"
        tool = OCRTool()
        result = tool._run(image_path_url="path/to/image.jpg")
        self.assertEqual(result, "Extracted text from image")
        mock_encode_image.assert_called_once_with("path/to/image.jpg")
        mock_llm_call.assert_called_once()

    @patch("crewai.LLM.call")
    def test_ocr_tool_run_url_image(self, mock_llm_call):
        mock_llm_call.return_value = "Extracted text from image from URL"
        tool = OCRTool()
        result = tool._run(image_path_url="http://example.com/image.jpg")
        self.assertEqual(result, "Extracted text from image from URL")
        mock_llm_call.assert_called_once()