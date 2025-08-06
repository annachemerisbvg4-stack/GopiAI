import unittest
from unittest.mock import MagicMock

from agent.agent import Agent
from agent.factory import ProcessFactory


class TestAgent(unittest.TestCase):

    def test_agent_creation(self):
        ProcessFactory.create = MagicMock()
        agent = Agent(max_iterations=5)
        self.assertTrue(hasattr(agent, 'process'))
        self.assertTrue(hasattr(agent, 'tools'))
        ProcessFactory.create.assert_called_once_with({'max_steps': 5})

    def test_agent_call(self):
        mock_process = MagicMock()
        ProcessFactory.create = MagicMock(return_value=mock_process)
        agent = Agent()
        agent.process = mock_process
        agent("test instruction")
        mock_process.model.parameters.assert_called_once_with(8192)
        mock_process.run.assert_called_once_with("test instruction", stream=False)

    def test_agent_call_with_stream(self):
        mock_process = MagicMock()
        ProcessFactory.create = MagicMock(return_value=mock_process)
        agent = Agent()
        agent.process = mock_process
        agent("test instruction", stream=True)
        mock_process.model.parameters.assert_called_once_with(8192)
        mock_process.run.assert_called_once_with("test instruction", stream=True)

    def test_agent_call_with_kwargs(self):
        mock_process = MagicMock()
        ProcessFactory.create = MagicMock(return_value=mock_process)
        agent = Agent()
        agent.process = mock_process
        agent("test instruction", test_kwarg="test_value")
        mock_process.model.parameters.assert_called_once_with(8192)
        mock_process.run.assert_called_once_with("test instruction", stream=False, test_kwarg="test_value")

    def test_agent_tools_access(self):
        mock_process = MagicMock()
        mock_process.tools = {"tool1": "value1"}
        ProcessFactory.create = MagicMock(return_value=mock_process)
        agent = Agent()
        self.assertEqual(agent.tools, {"tool1": "value1"})