import unittest
from unittest.mock import patch, MagicMock
import os

from crewai import Agent, Crew, Task
# Assuming multion_tool is in the same directory or installed
from multion_tool import MultiOnTool  

class TestCrewAIWithMultiOn(unittest.TestCase):

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch('multion_tool.MultiOnTool.browse')
    def test_multion_tool_integration(self, mock_browse):
        mock_browse.return_value = "Mocked AI News Summary"

        multion_browse_tool = MultiOnTool(api_key="test_key")
        browser = Agent(role="Browser Agent", goal="control web browsers using natural language ", backstory="An expert browsing agent.", tools=[multion_browse_tool], verbose=True)
        browse_task = Task(description="Summarize the top 3 trending AI News headlines", expected_output="A summary of the top 3 trending AI News headlines", agent=browser)
        crew = Crew(agents=[browser], tasks=[browse_task])

        result = crew.kickoff()

        self.assertIn("Mocked AI News Summary", result)
        mock_browse.assert_called_once()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_agent_creation(self):
        multion_browse_tool = MultiOnTool(api_key="test_key")
        browser = Agent(role="Browser Agent", goal="control web browsers using natural language ", backstory="An expert browsing agent.", tools=[multion_browse_tool], verbose=True)
        self.assertIsInstance(browser, Agent)
        self.assertEqual(browser.role, "Browser Agent")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_task_creation(self):
        multion_browse_tool = MultiOnTool(api_key="test_key")
        browser = Agent(role="Browser Agent", goal="control web browsers using natural language ", backstory="An expert browsing agent.", tools=[multion_browse_tool], verbose=True)
        browse_task = Task(description="Summarize the top 3 trending AI News headlines", expected_output="A summary of the top 3 trending AI News headlines", agent=browser)
        self.assertIsInstance(browse_task, Task)
        self.assertEqual(browse_task.description, "Summarize the top 3 trending AI News headlines")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_crew_creation(self):
        multion_browse_tool = MultiOnTool(api_key="test_key")
        browser = Agent(role="Browser Agent", goal="control web browsers using natural language ", backstory="An expert browsing agent.", tools=[multion_browse_tool], verbose=True)
        browse_task = Task(description="Summarize the top 3 trending AI News headlines", expected_output="A summary of the top 3 trending AI News headlines", agent=browser)
        crew = Crew(agents=[browser], tasks=[browse_task])
        self.assertIsInstance(crew, Crew)
        self.assertEqual(len(crew.agents), 1)
        self.assertEqual(len(crew.tasks), 1)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch('multion_tool.MultiOnTool.browse')
    def test_kickoff_returns_string(self, mock_browse):
        mock_browse.return_value = "Mocked AI News Summary"

        multion_browse_tool = MultiOnTool(api_key="test_key")
        browser = Agent(role="Browser Agent", goal="control web browsers using natural language ", backstory="An expert browsing agent.", tools=[multion_browse_tool], verbose=True)
        browse_task = Task(description="Summarize the top 3 trending AI News headlines", expected_output="A summary of the top 3 trending AI News headlines", agent=browser)
        crew = Crew(agents=[browser], tasks=[browse_task])

        result = crew.kickoff()

        self.assertIsInstance(result, str)