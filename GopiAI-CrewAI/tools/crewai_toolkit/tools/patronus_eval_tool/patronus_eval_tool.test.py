import unittest
from unittest.mock import patch, MagicMock
import os
import json
from crewai.tools import PatronusEvalTool


class TestPatronusEvalTool(unittest.TestCase):
    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    @patch("requests.get")
    def test_init_run(self, mock_get):
        mock_evaluators_response = MagicMock()
        mock_evaluators_response.text = json.dumps({"evaluators": [{"id": "1", "name": "Judge", "description": "desc", "aliases": [], "deprecated": False}]})
        mock_criteria_response = MagicMock()
        mock_criteria_response.text = json.dumps({"evaluator_criteria": [{"evaluator_family": "Judge", "name": "crit", "description": "desc", "config": {}}]})
        mock_get.side_effect = [mock_evaluators_response, mock_criteria_response]

        tool = PatronusEvalTool()

        self.assertEqual(len(tool.evaluators), 1)
        self.assertEqual(len(tool.criteria), 1)

    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    def test_generate_description(self):
        tool = PatronusEvalTool()
        tool.criteria = [{"evaluator": "Judge", "name": "crit", "description": "desc"}]
        description = tool._generate_description()
        self.assertIn("Evaluators:", description)
        self.assertIn("Judge", description)

    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    @patch("requests.post")
    def test_run(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        tool = PatronusEvalTool()
        result = tool._run("input", "output", "context", [{"evaluator": "Judge", "criteria": "crit"}])

        self.assertEqual(result, {"result": "success"})

    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    @patch("requests.post")
    def test_run_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        tool = PatronusEvalTool()
        with self.assertRaises(Exception) as context:
            tool._run("input", "output", "context", [{"evaluator": "Judge", "criteria": "crit"}])

        self.assertTrue("Failed to evaluate model input and output" in str(context.exception))

    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    def test_env_vars(self):
        tool = PatronusEvalTool()
        self.assertEqual(len(tool.env_vars), 1)
        self.assertEqual(tool.env_vars[0].name, "PATRONUS_API_KEY")


if __name__ == "__main__":
    unittest.main()