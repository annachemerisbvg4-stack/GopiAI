import unittest
from unittest.mock import patch, MagicMock

from embedchain.loaders.postgres import PostgresLoader
from pydantic import ValidationError

from embedchain.tools.pg_search import PGSearchTool, PGSearchToolSchema


class TestPGSearchTool(unittest.TestCase):

    def test_pg_search_tool_schema(self):
        with self.assertRaises(ValidationError):
            PGSearchToolSchema(search_query=None)
        PGSearchToolSchema(search_query="test query")

    @patch("embedchain.tools.rag.rag_tool.RagTool.__init__")
    @patch("embedchain.loaders.postgres.PostgresLoader")
    def test_pg_search_tool_init(self, MockPostgresLoader, MockRagToolInit):
        db_uri = "postgresql://user:password@host:port/database"
        tool = PGSearchTool(table_name="test_table", db_uri=db_uri)

        MockRagToolInit.assert_called_once_with(data_type="postgres", loader=MockPostgresLoader.return_value)
        MockPostgresLoader.assert_called_once_with(config=dict(url=db_uri))
        self.assertEqual(tool.description, "A tool that can be used to semantic search a query the test_table database table's content.")

    @patch("embedchain.tools.rag.rag_tool.RagTool.add")
    def test_pg_search_tool_add(self, MockRagToolAdd):
        db_uri = "postgresql://user:password@host:port/database"
        tool = PGSearchTool(table_name="test_table", db_uri=db_uri)
        tool.add("another_table")
        MockRagToolAdd.assert_called_with("SELECT * FROM another_table;")

    @patch("embedchain.tools.rag.rag_tool.RagTool._run")
    def test_pg_search_tool_run(self, MockRagToolRun):
        db_uri = "postgresql://user:password@host:port/database"
        tool = PGSearchTool(table_name="test_table", db_uri=db_uri)
        tool._run(search_query="test query")
        MockRagToolRun.assert_called_with(query="test query")