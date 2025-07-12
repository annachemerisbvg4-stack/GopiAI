import unittest
from unittest.mock import patch, MagicMock
import os
import json
from typing import List, Dict

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests

from your_module import PatronusPredefinedCriteriaEvalTool, FixedBaseToolSchema  # Replace your_module


class TestPatronusPredefinedCriteriaEvalTool(unittest.TestCase):
    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    @patch("requests.post")
    def test_run_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        evaluators = [{"evaluator": "test_evaluator", "criteria": "test_criteria"}]
        tool = PatronusPredefinedCriteriaEvalTool(evaluators=evaluators)
        kwargs = {
            "evaluated_model_input": {"description": "test_input"},
            "evaluated_model_output": {"description": "test_output"},
            "evaluated_model_retrieved_context": {"description": "test_context"},
            "evaluated_model_gold_answer": {"description": "test_answer"},
        }
        result = tool._run(**kwargs)
        self.assertEqual(result, {"result": "success"})

    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    @patch("requests.post")
    def test_run_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        evaluators = [{"evaluator": "test_evaluator", "criteria": "test_criteria"}]
        tool = PatronusPredefinedCriteriaEvalTool(evaluators=evaluators)
        kwargs = {
            "evaluated_model_input": {"description": "test_input"},
            "evaluated_model_output": {"description": "test_output"},
            "evaluated_model_retrieved_context": {"description": "test_context"},
            "evaluated_model_gold_answer": {"description": "test_answer"},
        }

        with self.assertRaises(Exception) as context:
            tool._run(**kwargs)

        self.assertTrue("Failed to evaluate model input and output" in str(context.exception))

    def test_init_with_evaluators(self):
        evaluators = [{"evaluator": "test_evaluator", "criteria": "test_criteria"}]
        tool = PatronusPredefinedCriteriaEvalTool(evaluators=evaluators)
        self.assertEqual(tool.evaluators, evaluators)
        self.assertTrue("evaluators=[[{'evaluator': 'test_evaluator', 'criteria': 'test_criteria'}]" in tool.description)

    def test_init_without_evaluators(self):
        tool = PatronusPredefinedCriteriaEvalTool()
        self.assertEqual(tool.evaluators, [])

    @patch.dict(os.environ, {"PATRONUS_API_KEY": "test_api_key"})
    @patch("requests.post")
    def test_run_with_string_inputs(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        evaluators = [{"evaluator": "test_evaluator", "criteria": "test_criteria"}]
        tool = PatronusPredefinedCriteriaEvalTool(evaluators=evaluators)
        kwargs = {
            "evaluated_model_input": "test_input",
            "evaluated_model_output": "test_output",
            "evaluated_model_retrieved_context": "test_context",
            "evaluated_model_gold_answer": "test_answer",
        }
        tool._run(**kwargs)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        data = json.loads(call_args.kwargs['data'])
        self.assertEqual(data['evaluated_model_input'], "test_input")
        self.assertEqual(data['evaluated_model_output'], "test_output")
        self.assertEqual(data['evaluated_model_retrieved_context'], "test_context")
        self.assertEqual(data['evaluated_model_gold_answer'], "test_answer")