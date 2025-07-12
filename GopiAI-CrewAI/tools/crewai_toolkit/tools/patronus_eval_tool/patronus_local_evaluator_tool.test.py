import unittest
from unittest.mock import MagicMock, patch

from crewai.tools.patronus_local_evaluator import (
    PatronusLocalEvaluatorTool,
    FixedLocalEvaluatorToolSchema,
)


class TestPatronusLocalEvaluatorTool(unittest.TestCase):
    def test_tool_initialization(self):
        mock_client = MagicMock()
        tool = PatronusLocalEvaluatorTool(
            patronus_client=mock_client,
            evaluator="test_evaluator",
            evaluated_model_gold_answer="test_answer",
        )
        self.assertEqual(tool.client, mock_client)
        self.assertEqual(tool.evaluator, "test_evaluator")
        self.assertEqual(tool.evaluated_model_gold_answer, "test_answer")

    @patch("crewai.tools.patronus_local_evaluator.PYPATRONUS_AVAILABLE", True)
    def test_initialize_patronus_available(self):
        mock_client = MagicMock()
        tool = PatronusLocalEvaluatorTool(
            evaluator="test_evaluator",
            evaluated_model_gold_answer="test_answer",
        )
        tool._initialize_patronus(mock_client)
        self.assertEqual(tool.client, mock_client)

    @patch("crewai.tools.patronus_local_evaluator.PYPATRONUS_AVAILABLE", False)
    @patch("crewai.tools.patronus_local_evaluator.click.confirm", return_value=False)
    def test_initialize_patronus_not_available_no_install(self, mock_confirm):
        with self.assertRaises(ImportError):
            PatronusLocalEvaluatorTool(
                evaluator="test_evaluator",
                evaluated_model_gold_answer="test_answer",
            )

    @patch("crewai.tools.patronus_local_evaluator.PYPATRONUS_AVAILABLE", True)
    def test_run(self):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.pass_ = True
        mock_result.explanation = "Test explanation"
        mock_client.evaluate.return_value = mock_result

        tool = PatronusLocalEvaluatorTool(
            patronus_client=mock_client,
            evaluator="test_evaluator",
            evaluated_model_gold_answer="test_answer",
        )
        result = tool._run(
            evaluated_model_input="test_input",
            evaluated_model_output="test_output",
            evaluated_model_retrieved_context="test_context",
        )
        self.assertEqual(
            result, "Evaluation result: True, Explanation: Test explanation"
        )

    def test_args_schema(self):
        self.assertEqual(
            PatronusLocalEvaluatorTool.args_schema, FixedLocalEvaluatorToolSchema
        )