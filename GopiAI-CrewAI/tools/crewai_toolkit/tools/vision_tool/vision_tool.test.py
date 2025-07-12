import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
from pydantic import ValidationError

from crewai.tools import VisionTool
from crewai import LLM


class TestVisionTool(unittest.TestCase):
    def test_image_prompt_schema_valid_url(self):
        from crewai.tools import ImagePromptSchema

        schema = ImagePromptSchema(image_path_url="http://example.com/image.jpg")
        self.assertEqual(schema.image_path_url, "http://example.com/image.jpg")

    def test_image_prompt_schema_invalid_file(self):
        from crewai.tools import ImagePromptSchema

        with self.assertRaises(ValidationError):
            ImagePromptSchema(image_path_url="invalid_file.jpg")

    def test_image_prompt_schema_invalid_extension(self):
        from crewai.tools import ImagePromptSchema

        with self.assertRaises(ValidationError):
            with patch("pathlib.Path.exists", return_value=True):
                ImagePromptSchema(image_path_url="image.txt")

    @patch("crewai.LLM.call")
    def test_vision_tool_run_with_url(self, mock_call):
        mock_call.return_value = "Image description"
        tool = VisionTool()
        result = tool._run(image_path_url="http://example.com/image.jpg")
        self.assertEqual(result, "Image description")

    @patch("base64.b64encode")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake image data")
    @patch("crewai.LLM.call")
    def test_vision_tool_run_with_file(self, mock_call, mock_file, mock_b64encode):
        mock_call.return_value = "Image description"
        mock_b64encode.return_value = b"base64_encoded_image"
        tool = VisionTool()
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", return_value=".jpg"):
                result = tool._run(image_path_url="image.jpg")
        self.assertEqual(result, "Image description")