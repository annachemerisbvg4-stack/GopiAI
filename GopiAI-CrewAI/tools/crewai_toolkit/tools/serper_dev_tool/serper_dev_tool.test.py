import unittest
from unittest.mock import patch, mock_open
import os
import json
from crewai.tools.serper_dev_search import SerperDevTool, SerperDevToolSchema
from pydantic import ValidationError

class TestSerperDevTool(unittest.TestCase):

    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('requests.post')
    def test_run_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"organic": [{"title": "Test", "link": "http://test.com"}], "searchParameters": {}}
        tool = SerperDevTool()
        result = tool._run(search_query="test query")
        self.assertIn("organic", result)

    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    def test_validation_error(self):
        with self.assertRaises(ValidationError):
            SerperDevToolSchema(search_query=None)

    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('requests.post')
    def test_api_request_exception(self, mock_post):
        mock_post.side_effect = Exception("API Error")
        tool = SerperDevTool()
        with self.assertRaises(Exception) as context:
            tool._run(search_query="test query")
        self.assertEqual(str(context.exception), "API Error")

    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('requests.post')
    def test_empty_response(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}
        tool = SerperDevTool()
        with self.assertRaises(ValueError) as context:
            tool._run(search_query="test query")
        self.assertEqual(str(context.exception), "Empty response from Serper API")

    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('requests.post')
    @patch('crewai.tools.serper_dev_search._save_results_to_file')
    def test_save_file_option(self, mock_save, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"organic": [{"title": "Test", "link": "http://test.com"}], "searchParameters": {}}
        tool = SerperDevTool()
        tool._run(search_query="test query", save_file=True)
        self.assertTrue(mock_save.called)