import unittest
from unittest.mock import patch, AsyncMock
import asyncio

from your_module import BrowserNavigateTool, BrowserExtractTool, ToolResult, Orchestrator  # Replace your_module

class TestBrowserTools(unittest.IsolatedAsyncioTestCase):

    @patch("your_module.HybridBrowserAgent")  # Replace your_module
    async def test_browser_navigate_tool(self, MockHybridBrowserAgent):
        mock_agent = AsyncMock()
        mock_agent.process.return_value = "Navigation Result"
        MockHybridBrowserAgent.return_value = mock_agent
        
        tool = BrowserNavigateTool()
        result = await tool.execute(url="https://www.example.com")
        
        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], "Navigation Result")

    @patch("your_module.HybridBrowserAgent")  # Replace your_module
    async def test_browser_extract_tool(self, MockHybridBrowserAgent):
        mock_agent = AsyncMock()
        mock_agent.process.return_value = "Extraction Result"
        MockHybridBrowserAgent.return_value = mock_agent
        
        tool = BrowserExtractTool()
        result = await tool.execute()
        
        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], "Extraction Result")

    async def test_base_tool_missing_param(self):
        async def mock_function(**kwargs):
            return ToolResult(success=True, message="Function executed")

        from your_module import BaseTool # Replace your_module
        tool = BaseTool(name="test_tool", description="Test tool", function=mock_function, required_params=["param1"])
        result = await tool.execute()
        self.assertFalse(result.success)
        self.assertIn("Отсутствует обязательный параметр", result.message)

    async def test_base_tool_exception(self):
        async def mock_function(**kwargs):
            raise ValueError("Test Error")
        from your_module import BaseTool # Replace your_module
        tool = BaseTool(name="test_tool", description="Test tool", function=mock_function)
        result = await tool.execute()
        self.assertFalse(result.success)
        self.assertIn("Ошибка при выполнении инструмента", result.message)

    async def test_orchestrator_create_agent(self):
        orchestrator = Orchestrator()
        agent = await orchestrator.create_hybrid_browser_agent("test_agent", "Test task")
        self.assertIn("test_agent", orchestrator.specialized_agents)

if __name__ == '__main__':
    unittest.main()