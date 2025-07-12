import unittest
from unittest.mock import MagicMock

class TestTools(unittest.TestCase):

    def test_aimindtool(self):
        from .ai_mind_tool.ai_mind_tool import AIMindTool
        tool = AIMindTool()
        self.assertIsInstance(tool, AIMindTool)

    def test_brave_search_tool(self):
        from .brave_search_tool.brave_search_tool import BraveSearchTool
        tool = BraveSearchTool()
        self.assertIsInstance(tool, BraveSearchTool)

    def test_code_interpreter_tool(self):
        from .code_interpreter_tool.code_interpreter_tool import CodeInterpreterTool
        tool = CodeInterpreterTool()
        self.assertIsInstance(tool, CodeInterpreterTool)

    def test_dalle_tool(self):
        from .dalle_tool.dalle_tool import DallETool
        tool = DallETool()
        self.assertIsInstance(tool, DallETool)

    def test_file_read_tool(self):
        from .file_read_tool.file_read_tool import FileReadTool
        tool = FileReadTool()
        self.assertIsInstance(tool, FileReadTool)