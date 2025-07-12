import unittest
from unittest.mock import patch, MagicMock
from crewai.tools.stagehand_tool import StagehandTool, StagehandToolSchema, StagehandResult
from pydantic import ValidationError

class TestStagehandTool(unittest.TestCase):

    def test_stagehand_tool_schema_validation(self):
        with self.assertRaises(ValidationError):
            StagehandToolSchema(instruction=None)

    @patch("crewai.tools.stagehand_tool._HAS_STAGEHAND", True)
    def test_stagehand_tool_initialization(self):
        tool = StagehandTool(api_key="test", project_id="test", model_api_key="test", _testing=True)
        self.assertIsNotNone(tool)

    @patch("crewai.tools.stagehand_tool._HAS_STAGEHAND", True)
    async def test_stagehand_tool_act_command(self):
        tool = StagehandTool(api_key="test", project_id="test", model_api_key="test", _testing=True)
        result = await tool._async_run(instruction="Click button", command_type="act")
        self.assertTrue(result.success)

    @patch("crewai.tools.stagehand_tool._HAS_STAGEHAND", True)
    async def test_stagehand_tool_navigate_command(self):
        tool = StagehandTool(api_key="test", project_id="test", model_api_key="test", _testing=True)
        result = await tool._async_run(instruction="Go to example", url="https://example.com", command_type="navigate")
        self.assertTrue(result.success)

    @patch("crewai.tools.stagehand_tool._HAS_STAGEHAND", True)
    def test_stagehand_tool_close(self):
        tool = StagehandTool(api_key="test", project_id="test", model_api_key="test", _testing=True)
        tool.close()
        self.assertIsNone(tool._stagehand)
        self.assertIsNone(tool._page)