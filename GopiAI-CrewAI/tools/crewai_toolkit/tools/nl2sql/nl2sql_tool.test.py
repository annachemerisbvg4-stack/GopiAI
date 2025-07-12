import unittest
from unittest.mock import patch, MagicMock
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Type, Union

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from nl2sql_tool import NL2SQLTool, NL2SQLToolInput


class TestNL2SQLTool(unittest.TestCase):

    @patch('nl2sql_tool.create_engine')
    def test_execute_sql_success(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_session
        mock_result = MagicMock()
        mock_result.returns_rows = True
        mock_result.keys.return_value = ['col1', 'col2']
        mock_result.fetchall.return_value = [('val1', 'val2')]
        mock_session.execute.return_value = mock_result

        tool = NL2SQLTool(db_uri='sqlite:///:memory:')
        result = tool.execute_sql('SELECT * FROM test_table')

        self.assertEqual(result, [{'col1': 'val1', 'col2': 'val2'}])

    @patch('nl2sql_tool.create_engine')
    def test_execute_sql_no_rows(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_session
        mock_result = MagicMock()
        mock_result.returns_rows = False
        mock_session.execute.return_value = mock_result

        tool = NL2SQLTool(db_uri='sqlite:///:memory:')
        result = tool.execute_sql('CREATE TABLE test_table')

        self.assertEqual(result, 'Query CREATE TABLE test_table executed successfully')

    @patch('nl2sql_tool.create_engine')
    def test_execute_sql_error(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_session
        mock_session.execute.side_effect = Exception('Test Exception')

        tool = NL2SQLTool(db_uri='sqlite:///:memory:')
        with self.assertRaises(Exception) as context:
            tool.execute_sql('SELECT * FROM test_table')
        self.assertEqual(str(context.exception), 'Test Exception')

    @patch('nl2sql_tool.NL2SQLTool.execute_sql')
    def test_run_success(self, mock_execute_sql):
        mock_execute_sql.return_value = "Successful Query Result"
        tool = NL2SQLTool(db_uri='sqlite:///:memory:')
        result = tool._run("SELECT * FROM test_table")
        self.assertEqual(result, "Successful Query Result")

    @patch('nl2sql_tool.NL2SQLTool.execute_sql')
    def test_run_failure(self, mock_execute_sql):
        mock_execute_sql.side_effect = Exception("SQL Error")
        tool = NL2SQLTool(db_uri='sqlite:///:memory:', tables=[{'table_name': 'test_table'}], columns={'test_table_columns': ['col1', 'col2']})
        result = tool._run("SELECT * FROM test_table")
        self.assertIn("SQL Error", result)