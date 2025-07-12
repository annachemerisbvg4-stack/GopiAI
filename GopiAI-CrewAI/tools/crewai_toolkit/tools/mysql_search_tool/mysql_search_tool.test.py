import unittest
from unittest.mock import patch, MagicMock

from embedchain.loaders.mysql import MySQLLoader
from pydantic import ValidationError

from embedchain.tools.mysql_search import MySQLSearchTool, MySQLSearchToolSchema


class TestMySQLSearchTool(unittest.TestCase):

    def test_mysql_search_tool_schema_validation(self):
        with self.assertRaises(ValidationError):
            MySQLSearchToolSchema()

        MySQLSearchToolSchema(search_query="test query")

    @patch("embedchain.tools.rag.rag_tool.RagTool.__init__")
    @patch("embedchain.loaders.mysql.MySQLLoader")
    def test_mysql_search_tool_init(self, MockMySQLLoader, MockRagToolInit):
        db_uri = "mysql://user:password@host/database"
        tool = MySQLSearchTool(db_uri=db_uri, table_name="test_table")

        MockRagToolInit.assert_called_once()
        MockMySQLLoader.assert_called_once_with(config=dict(url=db_uri))
        self.assertEqual(tool.description, "A tool that can be used to semantic search a query the test_table database table's content.")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_add(self, mock_add):
        db_uri = "mysql://user:password@host/database"
        tool = MySQLSearchTool(db_uri=db_uri, table_name="test_table")
        tool.add("another_table")
        mock_add.assert_called_with("SELECT * FROM another_table;")

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_run(self, mock_super_run):
        db_uri = "mysql://user:password@host/database"
        tool = MySQLSearchTool(db_uri=db_uri, table_name="test_table")
        tool._run(search_query="test query")
        mock_super_run.assert_called_with(query="test query")