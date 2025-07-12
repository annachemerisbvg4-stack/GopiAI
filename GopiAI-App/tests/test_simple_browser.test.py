import sys
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

from your_module import TestWindow  # Replace your_module

class TestTestWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)

    def setUp(self):
        self.window = TestWindow()

    def test_window_title(self):
        self.assertEqual(self.window.windowTitle(), "Тестирование встроенного браузера")

    def test_browser_initial_url(self):
        self.assertEqual(self.window.browser.url().toString(), "https://www.example.com")

    @patch('your_module.TestWindow.handle_js_result') # Replace your_module
    def test_execute_js(self, mock_handle_js_result):
        self.window.execute_js()
        self.assertTrue(mock_handle_js_result.called)

    def test_navigate_to_google(self):
        self.window.navigate_to_google()
        self.assertEqual(self.window.browser.url().toString(), "https://www.google.com/")