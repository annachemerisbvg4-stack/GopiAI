import unittest
from unittest.mock import patch
import asyncio
from your_module import BrowserAdapter, BrowserMCPAdapter, BrowserUseAdapter, HybridBrowserAdapter  # Replace your_module

class TestBrowserAdapters(unittest.IsolatedAsyncioTestCase):

    async def test_browser_adapter_navigate(self):
        adapter = BrowserAdapter()
        result = await adapter.navigate("https://www.example.com")
        self.assertTrue(result["success"])

    @patch('your_module.BrowserMCPAdapter._is_mcp_installed', return_value=True)
    @patch('your_module.BrowserMCPAdapter._is_mcp_server_running', return_value=False)
    @patch('your_module.BrowserMCPAdapter._start_mcp_server', return_value=True)
    async def test_browser_mcp_adapter_initialize(self, mock_start, mock_running, mock_installed):
        adapter = BrowserMCPAdapter()
        result = await adapter.initialize()
        self.assertTrue(result)

    @patch('your_module.BrowserUseAdapter.initialize', return_value=True)
    async def test_hybrid_browser_adapter_initialize_browser_use(self, mock_browser_use):
        adapter = HybridBrowserAdapter(preferred_tool="browser_use")
        result = await adapter.initialize()
        self.assertTrue(result)

    @patch('your_module.BrowserMCPAdapter.initialize', return_value=True)
    async def test_hybrid_browser_adapter_navigate(self, mock_mcp):
        adapter = HybridBrowserAdapter(preferred_tool="mcp")
        await adapter.initialize()
        result = await adapter.navigate("https://www.example.com")
        self.assertTrue(result["success"])

    async def test_browser_adapter_close(self):
        adapter = BrowserAdapter()
        result = await adapter.close()
        self.assertTrue(result["success"])