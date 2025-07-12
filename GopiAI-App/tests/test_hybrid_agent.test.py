import unittest
from unittest.mock import patch, AsyncMock
import asyncio

# Assuming the code to be tested is in 'hybrid_agent.py'
from hybrid_agent import HybridBrowserAgent, SpecializedAgent

class TestHybridBrowserAgent(unittest.IsolatedAsyncioTestCase):

    async def test_specialized_agent_creation(self):
        agent = SpecializedAgent("test_agent")
        self.assertEqual(agent.name, "test_agent")
        self.assertEqual(agent.system_prompt, "Вы специализированный агент.")

    async def test_hybrid_agent_creation(self):
        agent = HybridBrowserAgent()
        self.assertEqual(agent.name, "hybrid_browser")
        self.assertTrue("браузерный агент" in agent.system_prompt)

    @patch('hybrid_agent.HybridBrowserAdapter.navigate', new_callable=AsyncMock)
    @patch('hybrid_agent.HybridBrowserAdapter.extract_content', new_callable=AsyncMock)
    async def test_hybrid_agent_process(self, mock_extract, mock_navigate):
        mock_navigate.return_value = {"success": True, "message": "Navigated"}
        mock_extract.return_value = {"success": True, "message": "Extracted", "data": {"content": "Test Content"}}
        agent = HybridBrowserAgent()
        result = await agent.process("Перейти на сайт example.com и извлечь содержимое страницы")
        self.assertTrue("Navigated" in result)
        self.assertTrue("Test Content" in result)

    @patch('hybrid_agent.HybridBrowserAdapter.close', new_callable=AsyncMock)
    async def test_hybrid_agent_cleanup(self, mock_close):
        agent = HybridBrowserAgent()
        await agent.cleanup()
        mock_close.assert_called_once()

    async def test_set_context(self):
        agent = SpecializedAgent("test_agent")
        context = {"task": "Test task"}
        await agent.set_context(context)
        self.assertEqual(agent.context, context)

if __name__ == '__main__':
    unittest.main()