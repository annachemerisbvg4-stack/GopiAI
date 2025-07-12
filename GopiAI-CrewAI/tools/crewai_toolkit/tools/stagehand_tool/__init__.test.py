import unittest
from unittest.mock import MagicMock

from stagehand.stagehand_tool import StagehandTool


class TestStagehandTool(unittest.TestCase):

    def test_init(self):
        tool = StagehandTool()
        self.assertIsInstance(tool, StagehandTool)

    def test_run_success(self):
        tool = StagehandTool()
        tool.run = MagicMock(return_value=0)
        result = tool.run()
        self.assertEqual(result, 0)

    def test_run_failure(self):
        tool = StagehandTool()
        tool.run = MagicMock(return_value=1)
        result = tool.run()
        self.assertEqual(result, 1)

    def test_help(self):
        tool = StagehandTool()
        tool.help = MagicMock()
        tool.help()
        tool.help.assert_called_once()

    def test_version(self):
        tool = StagehandTool()
        tool.version = MagicMock()
        tool.version()
        tool.version.assert_called_once()