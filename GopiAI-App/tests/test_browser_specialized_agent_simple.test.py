import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from gopiai.app.agent.browser_specialized_agent import BrowserSpecializedAgent

class TestBrowserSpecializedAgent(unittest.IsolatedAsyncioTestCase):

    @patch('gopiai.app.agent.browser_specialized_agent.BrowserSpecializedAgent.process', new_callable=AsyncMock)
    async def test_process(self, mock_process):
        agent = BrowserSpecializedAgent(preferred_tool="auto")
        mock_process.return_value = "Test Result"
        result = await agent.process("Test Query")
        self.assertEqual(result, "Test Result")

    async def test_set_context(self):
        agent = BrowserSpecializedAgent(preferred_tool="auto")
        context = {"task": "Test Task", "relevant_files": {}}
        await agent.set_context(context)
        self.assertEqual(agent.context, context)

    def test_get_current_state(self):
        agent = BrowserSpecializedAgent(preferred_tool="auto")
        state = agent.get_current_state()
        self.assertIsInstance(state, dict)

    @patch('gopiai.app.agent.browser_specialized_agent.BrowserSpecializedAgent.cleanup', new_callable=AsyncMock)
    async def test_cleanup(self, mock_cleanup):
        agent = BrowserSpecializedAgent(preferred_tool="auto")
        await agent.cleanup()
        mock_cleanup.assert_called_once()

    def test_agent_creation(self):
        agent = BrowserSpecializedAgent(preferred_tool="auto")
        self.assertIsInstance(agent, BrowserSpecializedAgent)