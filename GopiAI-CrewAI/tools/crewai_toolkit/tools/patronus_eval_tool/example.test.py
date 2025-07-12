import unittest
from unittest.mock import MagicMock, patch
import random

from crewai import Agent, Crew, Task
from patronus import Client, EvaluationResult
from patronus_local_evaluator_tool import PatronusLocalEvaluatorTool


class TestPatronusLocalEvaluatorTool(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock(spec=Client)
        self.patronus_eval_tool = PatronusLocalEvaluatorTool(
            patronus_client=self.mock_client,
            evaluator="random_evaluator",
            evaluated_model_gold_answer="example label",
        )
        self.coding_agent = Agent(
            role="Coding Agent",
            goal="Generate high quality code and verify that the output is code by using Patronus AI's evaluation tool.",
            backstory="You are an experienced coder who can generate high quality python code. You can follow complex instructions accurately and effectively.",
            tools=[self.patronus_eval_tool],
            verbose=True,
        )
        self.generate_code = Task(
            description="Create a simple program to generate the first N numbers in the Fibonacci sequence. Select the most appropriate evaluator and criteria for evaluating your output.",
            expected_output="Program that generates the first N numbers in the Fibonacci sequence.",
            agent=self.coding_agent,
        )
        self.crew = Crew(agents=[self.coding_agent], tasks=[self.generate_code])

    @patch("patronus_local_evaluator_tool.PatronusLocalEvaluatorTool.use")
    def test_patronus_local_evaluator_tool_use(self, mock_use):
        self.patronus_eval_tool.use("test input")
        mock_use.assert_called_once()

    def test_patronus_local_evaluator_tool_initialization(self):
        self.assertEqual(self.patronus_eval_tool.evaluator, "random_evaluator")
        self.assertEqual(self.patronus_eval_tool.evaluated_model_gold_answer, "example label")

    @patch("random.random")
    def test_random_evaluator(self, mock_random):
        mock_random.return_value = 0.6
        client = Client()

        @client.register_local_evaluator("random_evaluator")
        def random_evaluator(**kwargs):
            score = random.random()
            return EvaluationResult(
                score_raw=score,
                pass_=score >= 0.5,
                explanation="example explanation",  # Optional justification for LLM judges
            )

        result = random_evaluator()
        self.assertTrue(result.pass_)
        self.assertEqual(result.score_raw, 0.6)

    @patch("crewai.crew.Crew.kickoff")
    def test_crew_kickoff(self, mock_kickoff):
        self.crew.kickoff()
        mock_kickoff.assert_called_once()