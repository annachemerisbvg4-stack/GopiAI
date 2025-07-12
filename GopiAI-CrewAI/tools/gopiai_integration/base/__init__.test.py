import unittest
from unittest.mock import MagicMock

from gopi_base_tools import GopiAIBaseTool

class TestGopiAIBaseTool(unittest.TestCase):

    def test_tool_creation(self):
        tool = GopiAIBaseTool()
        self.assertIsInstance(tool, GopiAIBaseTool)

    def test_tool_name_default(self):
        tool = GopiAIBaseTool()
        self.assertIsNone(tool.name)

    def test_tool_description_default(self):
        tool = GopiAIBaseTool()
        self.assertIsNone(tool.description)

    def test_tool_args_default(self):
        tool = GopiAIBaseTool()
        self.assertIsNone(tool.args)

    def test_tool_run_not_implemented(self):
        tool = GopiAIBaseTool()
        with self.assertRaises(NotImplementedError):
            tool.run("test")