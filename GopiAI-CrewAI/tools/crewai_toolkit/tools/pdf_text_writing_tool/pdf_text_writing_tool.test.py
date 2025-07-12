import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
from pydantic import ValidationError

from crewai_tools.tools.rag.pdf_text_writing import PDFTextWritingTool, PDFTextWritingToolSchema


class TestPDFTextWritingTool(unittest.TestCase):
    def setUp(self):
        self.tool = PDFTextWritingTool()
        self.pdf_path = "test.pdf"
        Path(self.pdf_path).write_bytes(b"dummy pdf content")

    def tearDown(self):
        try:
            Path("modified_output.pdf").unlink()
        except FileNotFoundError:
            pass
        try:
            Path(self.pdf_path).unlink()
        except FileNotFoundError:
            pass

    def test_pdf_text_writing_tool_schema(self):
        valid_data = {
            "pdf_path": "test.pdf",
            "text": "Test text",
            "position": (100, 200),
        }
        schema = PDFTextWritingToolSchema(**valid_data)
        self.assertEqual(schema.pdf_path, "test.pdf")
        self.assertEqual(schema.text, "Test text")
        self.assertEqual(schema.position, (100, 200))

        with self.assertRaises(ValidationError):
            PDFTextWritingToolSchema(text="Test text", position=(100, 200))

    @patch("crewai_tools.tools.rag.pdf_text_writing.PdfReader")
    @patch("crewai_tools.tools.rag.pdf_text_writing.PdfWriter")
    def test_run_success(self, MockPdfWriter, MockPdfReader):
        mock_reader = MockPdfReader.return_value
        mock_reader.pages = [object()]
        mock_writer = MockPdfWriter.return_value
        mock_writer.write.return_value = None

        result = self.tool.run(
            pdf_path=self.pdf_path, text="Test text", position=(100, 200), font_size=12, font_color="0 0 0 rg"
        )
        self.assertEqual(result, "Text added to modified_output.pdf successfully.")

    def test_run_page_number_out_of_range(self):
        result = self.tool.run(
            pdf_path=self.pdf_path, text="Test text", position=(100, 200), font_size=12, font_color="0 0 0 rg", page_number=10
        )
        self.assertEqual(result, "Page number out of range.")

    def test_run_font_file_not_exists(self):
        result = self.tool.run(
            pdf_path=self.pdf_path, text="Test text", position=(100, 200), font_size=12, font_color="0 0 0 rg", font_file="non_existent_font.ttf"
        )
        self.assertEqual(result, "Font file does not exist.")