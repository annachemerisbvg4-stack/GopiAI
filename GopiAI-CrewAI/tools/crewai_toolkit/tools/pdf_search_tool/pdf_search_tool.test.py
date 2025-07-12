import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from embedchain.tools.pdf_search import PDFSearchTool, PDFSearchToolSchema, FixedPDFSearchToolSchema
from pydantic import ValidationError


class TestPDFSearchTool(unittest.TestCase):

    def test_pdf_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            PDFSearchToolSchema(query="test")
        PDFSearchToolSchema(query="test", pdf="test.pdf")

    def test_fixed_pdf_search_tool_schema(self):
        FixedPDFSearchToolSchema(query="test")

    @patch('embedchain.tools.rag.rag_tool.RagTool._run')
    def test_pdf_search_tool_run_with_pdf(self, mock_super_run):
        tool = PDFSearchTool()
        tool._run(query="test", pdf="test.pdf")
        mock_super_run.assert_called_once_with(query="test")

    @patch('embedchain.tools.rag.rag_tool.RagTool._run')
    def test_pdf_search_tool_run_without_pdf(self, mock_super_run):
        tool = PDFSearchTool(pdf="test.pdf")
        tool._run(query="test")
        mock_super_run.assert_called_once_with(query="test")

    @patch('embedchain.tools.rag.rag_tool.RagTool.add')
    def test_pdf_search_tool_add(self, mock_super_add):
        tool = PDFSearchTool()
        tool.add("test.pdf")
        mock_super_add.assert_called_once_with("test.pdf", data_type=DataType.PDF_FILE)