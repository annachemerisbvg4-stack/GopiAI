import unittest
from unittest.mock import patch

from . import *

class TestGopiAIIntegrationTools(unittest.TestCase):

    def test_all_tools_returned(self):
        tools = get_all_tools()
        self.assertEqual(len(tools), 6)

    def test_get_tool_by_name_success(self):
        tool = get_tool_by_name('browser')
        self.assertIsInstance(tool, GopiAIBrowserTool)

    def test_get_tool_by_name_failure(self):
        with self.assertRaises(ValueError):
            get_tool_by_name('invalid_tool')

    def test_tools_info_structure(self):
        self.assertIn('browser', TOOLS_INFO)
        self.assertIn('class', TOOLS_INFO['browser'])
        self.assertIn('description', TOOLS_INFO['browser'])
        self.assertIn('capabilities', TOOLS_INFO['browser'])

    def test_version_and_author(self):
        self.assertEqual(__version__, '1.0.0')
        self.assertEqual(__author__, 'GopiAI Team')