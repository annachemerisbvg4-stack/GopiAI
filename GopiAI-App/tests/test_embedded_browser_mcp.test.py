import unittest
from unittest.mock import patch, AsyncMock
from PySide6.QtWidgets import QApplication
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from main import TestWindow  # Replace 'your_module' with the actual module name

class TestTestWindow(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.app = QApplication.instance() if QApplication.instance() else QApplication([])
        self.window = TestWindow()

    @patch("main.setup_browsermcp", new_callable=AsyncMock)
    async def test_setup_browsermcp_success(self, mock_setup_browsermcp):
        mock_setup_browsermcp.return_value = True
        await self.window._setup_browsermcp()
        self.assertEqual(self.window.result_label.text(), "BrowserMCP успешно настроен")

    @patch("main.inject_browsermcp", new_callable=AsyncMock)
    async def test_inject_browsermcp_success(self, mock_inject_browsermcp):
        mock_inject_browsermcp.return_value = True
        await self.window._inject_browsermcp()
        self.assertEqual(self.window.result_label.text(), "BrowserMCP успешно внедрен")

    async def test_navigate_to_google_no_adapter(self):
        await self.window._navigate_to_google()
        self.assertEqual(self.window.result_label.text(), "Сначала внедрите BrowserMCP")

    @patch("gopiai.app.utils.browser_adapters.HybridBrowserAdapter.navigate", new_callable=AsyncMock)
    async def test_navigate_to_google_success(self, mock_navigate):
        self.window.adapter = AsyncMock()
        mock_navigate.return_value = {"success": True}
        await self.window._navigate_to_google()
        self.assertEqual(self.window.result_label.text(), "Успешно выполнен переход на Google")

    async def test_extract_content_no_adapter(self):
        await self.window._extract_content()
        self.assertEqual(self.window.result_label.text(), "Сначала внедрите BrowserMCP")

if __name__ == '__main__':
    unittest.main()