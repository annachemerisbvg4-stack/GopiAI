import unittest
import asyncio
from unittest.mock import patch
from gopiai.core.logging import get_logger

# Assuming gopiai.core.logging is available or can be mocked
class MockLogger:
    def info(self, message):
        pass
    def error(self, message):
        pass

class TestBrowserAdapter(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        from your_module import BrowserAdapter  # Replace your_module
        self.adapter = BrowserAdapter()

    async def test_initialize(self):
        result = await self.adapter.initialize()
        self.assertTrue(result)
        self.assertTrue(self.adapter.initialized)

    async def test_navigate(self):
        url = "https://www.example.com"
        result = await self.adapter.navigate(url)
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["url"], url)

    async def test_extract_content(self):
        result = await self.adapter.extract_content()
        self.assertTrue(result["success"])
        self.assertIn("content", result["data"])

    async def test_close(self):
        await self.adapter.initialize()
        result = await self.adapter.close()
        self.assertTrue(result["success"])
        self.assertFalse(self.adapter.initialized)

if __name__ == '__main__':
    unittest.main()