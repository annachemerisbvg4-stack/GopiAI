import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from gopiai.app.agent.browser_specialized_agent import BrowserSpecializedAgent
from .test_utils import async_test

class TestTestWindow(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.window = TestWindow()

    def tearDown(self):
        self.window.close()
        del self.window
        del self.app

    @async_test
    async def test_init_agent_success(self):
        self.window.browser = MagicMock()
        await self.window._init_agent()
        self.assertIsInstance(self.window.agent, BrowserSpecializedAgent)
        self.assertEqual(self.window.result_output.toPlainText(), "Агент успешно инициализирован")

    @async_test
    async def test_init_agent_failure(self):
        self.window.browser = MagicMock(side_effect=Exception("Browser error"))
        await self.window._init_agent()
        self.assertIn("Ошибка при инициализации агента", self.window.result_output.toPlainText())

    @async_test
    async def test_process_query_empty(self):
        self.window.query_input.setText("")
        await self.window._process_query("")
        self.assertEqual(self.window.result_output.toPlainText(), "Запрос не может быть пустым")
    
    @async_test
    async def test_process_query_no_agent(self):
        self.window.agent = None
        await self.window._process_query("test query")
        self.assertEqual(self.window.result_output.toPlainText(), "Сначала инициализируйте агента")

    @async_test
    async def test_process_query_success(self):
        self.window.agent = MagicMock()
        self.window.agent.process.return_value = "Processed result"
        await self.window._process_query("test query")
        self.assertEqual(self.window.result_output.toPlainText(), "Processed result")