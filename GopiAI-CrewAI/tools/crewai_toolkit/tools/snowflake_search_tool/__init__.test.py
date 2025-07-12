import unittest
from unittest.mock import patch
from pydantic import ValidationError

from snowflake.connector import connect

from ..snowflake_search_tool import (
    SnowflakeConfig,
    SnowflakeSearchTool,
    SnowflakeSearchToolInput,
)

class TestSnowflakeSearchTool(unittest.TestCase):

    def test_snowflake_config_validation(self):
        with self.assertRaises(ValidationError):
            SnowflakeConfig(account="")

    @patch("snowflake.connector.connect")
    def test_snowflake_search_tool_run(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
        tool = SnowflakeSearchTool(config=SnowflakeConfig(account="test_account", user="test_user", password="test_password", database="test_db", schema="test_schema", warehouse="test_warehouse"))
        result = tool.run(SnowflakeSearchToolInput(query="SELECT * FROM table"))
        self.assertEqual(result, "result1\nresult2")

    @patch("snowflake.connector.connect")
    def test_snowflake_search_tool_run_empty_result(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = []
        tool = SnowflakeSearchTool(config=SnowflakeConfig(account="test_account", user="test_user", password="test_password", database="test_db", schema="test_schema", warehouse="test_warehouse"))
        result = tool.run(SnowflakeSearchToolInput(query="SELECT * FROM table"))
        self.assertEqual(result, "No results found.")

    def test_snowflake_search_tool_input_validation(self):
        with self.assertRaises(ValidationError):
            SnowflakeSearchToolInput(query="")