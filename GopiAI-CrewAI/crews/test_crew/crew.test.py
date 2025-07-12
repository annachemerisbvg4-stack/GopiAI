import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import yaml
from crewai import Agent, Task, Crew, Process
from io import StringIO

from your_module import TestCrew  # Replace your_module

class TestTestCrew(unittest.TestCase):

    @patch("your_module.TestCrew._load_yaml")
    def test_create_agents(self, mock_load_yaml):
        mock_load_yaml.return_value = {"agent1": {"role": "Role1", "goal": "Goal1", "backstory": "Backstory1"}}
        test_crew = TestCrew()
        agents = test_crew.create_agents()
        self.assertIsInstance(agents["agent1"], Agent)

    @patch("your_module.TestCrew._load_yaml")
    def test_create_tasks(self, mock_load_yaml):
        mock_load_yaml.return_value = {"task1": {"description": "Desc", "expected_output": "Output", "agent": "agent1"}}
        test_crew = TestCrew()
        agents = {"agent1": Agent(role="Role1", goal="Goal1", backstory="Backstory1")}
        tasks = test_crew.create_tasks(agents, {"topic": "Test"})
        self.assertIsInstance(tasks[0], Task)

    def test_create_crew(self):
        agents = {"agent1": Agent(role="Role1", goal="Goal1", backstory="Backstory1")}
        tasks = [Task(description="Desc", expected_output="Output", agent=agents["agent1"])]
        test_crew = TestCrew()
        crew = test_crew.create_crew(agents, tasks)
        self.assertIsInstance(crew, Crew)

    @patch("your_module.TestCrew._load_yaml")
    @patch("crewai.Crew.kickoff")
    def test_run(self, mock_kickoff, mock_load_yaml):
        mock_load_yaml.return_value = {}
        mock_kickoff.return_value = "Test Result"
        test_crew = TestCrew()
        result = test_crew.run("Test Topic")
        self.assertEqual(result, "Test Result")

    @patch("builtins.open", new_callable=mock_open, read_data="role: test")
    def test_load_yaml(self, mock_file):
        test_crew = TestCrew()
        test_crew.crew_dir = Path(".")
        result = test_crew._load_yaml("test.yaml")
        self.assertEqual(result, {'role': 'test'})

if __name__ == "__main__":
    unittest.main()