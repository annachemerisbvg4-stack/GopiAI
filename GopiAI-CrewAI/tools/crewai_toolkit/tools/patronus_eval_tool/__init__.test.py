import unittest
from unittest.mock import MagicMock

from patronus.llm_eval_tool.patronus_eval_tool import PatronusEvalTool
from patronus.llm_eval_tool.patronus_local_evaluator_tool import PatronusLocalEvaluatorTool
from patronus.llm_eval_tool.patronus_predefined_criteria_eval_tool import PatronusPredefinedCriteriaEvalTool


class TestPatronusEvalTools(unittest.TestCase):

    def test_patronus_eval_tool_initialization(self):
        tool = PatronusEvalTool(llm=MagicMock())
        self.assertIsInstance(tool, PatronusEvalTool)

    def test_patronus_local_evaluator_tool_initialization(self):
        tool = PatronusLocalEvaluatorTool(llm=MagicMock())
        self.assertIsInstance(tool, PatronusLocalEvaluatorTool)

    def test_patronus_predefined_criteria_eval_tool_initialization(self):
        tool = PatronusPredefinedCriteriaEvalTool(llm=MagicMock(), criteria="helpfulness")
        self.assertIsInstance(tool, PatronusPredefinedCriteriaEvalTool)

    def test_patronus_eval_tool_run(self):
        tool = PatronusEvalTool(llm=MagicMock())
        tool.llm.invoke = MagicMock(return_value="Good")
        result = tool._run("input", "output")
        self.assertEqual(result, "Good")

    def test_patronus_predefined_criteria_eval_tool_run(self):
        tool = PatronusPredefinedCriteriaEvalTool(llm=MagicMock(), criteria="helpfulness")
        tool.llm.invoke = MagicMock(return_value="Good")
        result = tool._run("input", "output")
        self.assertEqual(result, "Good")