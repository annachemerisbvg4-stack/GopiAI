import unittest
from unittest.mock import patch

from embedchain.models.data_type import DataType
from pydantic import ValidationError

from embedchain.tools.xml_search import (
    FixedXMLSearchToolSchema,
    XMLSearchTool,
    XMLSearchToolSchema,
)


class TestXMLSearchTool(unittest.TestCase):
    def test_xml_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            XMLSearchToolSchema(search_query="test")

        XMLSearchToolSchema(search_query="test", xml="path/to/xml")

    def test_fixed_xml_search_tool_schema(self):
        FixedXMLSearchToolSchema(search_query="test")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_xml_search_tool_init_with_xml(self, mock_add):
        xml_path = "path/to/xml"
        tool = XMLSearchTool(xml=xml_path)
        mock_add.assert_called_once_with(xml_path)
        self.assertEqual(tool.args_schema, FixedXMLSearchToolSchema)
        self.assertIn(xml_path, tool.description)

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_xml_search_tool_run_with_xml(self, mock_super_run, mock_add):
        xml_path = "path/to/xml"
        search_query = "test query"
        tool = XMLSearchTool()
        tool._run(search_query=search_query, xml=xml_path)
        mock_add.assert_called_once_with(xml_path)
        mock_super_run.assert_called_once_with(query=search_query)

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_xml_search_tool_run_without_xml(self, mock_super_run):
        search_query = "test query"
        tool = XMLSearchTool()
        tool._run(search_query=search_query)
        mock_super_run.assert_called_once_with(query=search_query)