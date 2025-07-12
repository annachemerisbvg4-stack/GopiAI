import asyncio
import unittest
from unittest.mock import patch, MagicMock

from crewai.tools.snowflake_search import (
    SnowflakeSearchTool,
    SnowflakeConfig,
    SnowflakeSearchToolInput,
)


class TestSnowflakeSearchTool(unittest.IsolatedAsyncioTestCase):
    @patch("crewai.tools.snowflake_search.SNOWFLAKE_AVAILABLE", True)
    @patch("crewai.tools.snowflake_search.snowflake.connector.connect")
    async def test_run_query(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.description = [("col1",), ("col2",)]
        mock_cursor.fetchall.return_value = [("val1", "val2")]
        mock_connect.return_value.cursor.return_value = mock_cursor

        config = SnowflakeConfig(account="test", user="test", password="test")
        tool = SnowflakeSearchTool(config=config)
        result = await tool._run(query="SELECT * FROM test")
        self.assertEqual(result, [{"col1": "val1", "col2": "val2"}])

    @patch("crewai.tools.snowflake_search.SNOWFLAKE_AVAILABLE", True)
    @patch("crewai.tools.snowflake_search.snowflake.connector.connect")
    async def test_run_query_with_database_schema_override(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.description = [("col1",), ("col2",)]
        mock_cursor.fetchall.return_value = [("val1", "val2")]
        mock_connect.return_value.cursor.return_value = mock_cursor

        config = SnowflakeConfig(account="test", user="test", password="test")
        tool = SnowflakeSearchTool(config=config)
        await tool._run(
            query="SELECT * FROM test", database="override_db", snowflake_schema="override_schema"
        )
        self.assertEqual(mock_cursor.call_count, 1)

    @patch("crewai.tools.snowflake_search.SNOWFLAKE_AVAILABLE", True)
    @patch("crewai.tools.snowflake_search.snowflake.connector.connect")
    async def test_run_query_empty_result(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_connect.return_value.cursor.return_value = mock_cursor

        config = SnowflakeConfig(account="test", user="test", password="test")
        tool = SnowflakeSearchTool(config=config)
        result = await tool._run(query="SELECT * FROM test")
        self.assertEqual(result, [])

    @patch("crewai.tools.snowflake_search.SNOWFLAKE_AVAILABLE", True)
    @patch("crewai.tools.snowflake_search.snowflake.connector.connect")
    async def test_execute_query_retries(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_connect.return_value.cursor.return_value = mock_cursor

        config = SnowflakeConfig(account="test", user="test", password="test")
        tool = SnowflakeSearchTool(config=config, max_retries=2, retry_delay=0.01)
        with self.assertRaises(Exception):
            await tool._execute_query(query="SELECT * FROM test")

    def test_snowflake_config_validation(self):
        with self.assertRaises(ValueError):
            SnowflakeConfig(account="test", user="test")