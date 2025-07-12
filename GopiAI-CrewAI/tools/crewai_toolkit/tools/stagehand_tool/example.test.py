import unittest
from unittest.mock import patch, MagicMock
import os

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from stagehand.schemas import AvailableModel

from crewai_tools import StagehandTool


class TestStagehandTool(unittest.TestCase):

    @patch("crewai_tools.stagehand.Stagehand")
    def test_stagehand_tool_initialization(self, MockStagehand):
        api_key = "test_api_key"
        project_id = "test_project_id"
        model_api_key = "test_model_api_key"

        with StagehandTool(
            api_key=api_key,
            project_id=project_id,
            model_api_key=model_api_key,
            model_name=AvailableModel.GPT_4O,
        ) as stagehand_tool:
            MockStagehand.assert_called_once_with(
                api_key=api_key,
                project_id=project_id,
                model_api_key=model_api_key,
                model_name=AvailableModel.GPT_4O,
            )

    @patch("crewai_tools.stagehand.Stagehand")
    def test_stagehand_tool_call(self, MockStagehand):
        api_key = "test_api_key"
        project_id = "test_project_id"
        model_api_key = "test_model_api_key"
        instruction = "Test instruction"

        mock_stagehand_instance = MockStagehand.return_value
        mock_stagehand_instance.act.return_value = "Test Result"

        with StagehandTool(
            api_key=api_key,
            project_id=project_id,
            model_api_key=model_api_key,
            model_name=AvailableModel.GPT_4O,
        ) as stagehand_tool:
            result = stagehand_tool.act(instruction=instruction)
            self.assertEqual(result, "Test Result")
            mock_stagehand_instance.act.assert_called_once_with(
                instruction=instruction, url=None, selector=None
            )

    @patch("crewai_tools.stagehand.Stagehand")
    def test_stagehand_tool_close(self, MockStagehand):
        api_key = "test_api_key"
        project_id = "test_project_id"
        model_api_key = "test_model_api_key"

        with StagehandTool(
            api_key=api_key,
            project_id=project_id,
            model_api_key=model_api_key,
            model_name=AvailableModel.GPT_4O,
        ) as stagehand_tool:
            pass

        mock_stagehand_instance = MockStagehand.return_value
        mock_stagehand_instance.close.assert_called_once()

    def test_available_model_enum(self):
        self.assertEqual(AvailableModel.GPT_4O, "gpt-4o")
        self.assertEqual(AvailableModel.GPT_4, "gpt-4")
        self.assertEqual(AvailableModel.GPT_3_5_TURBO, "gpt-3.5-turbo")