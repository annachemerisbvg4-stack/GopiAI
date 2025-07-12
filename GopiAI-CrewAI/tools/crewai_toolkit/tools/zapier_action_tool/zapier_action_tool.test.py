import unittest
from unittest.mock import patch, MagicMock
import os
from crewai_tools.adapters.zapier_adapter import ZapierActionsAdapter
from crewai_tools.tools.zapier import ZapierActionTools
from crewai.tools import BaseTool


class TestZapierActionTools(unittest.TestCase):

    @patch.dict(os.environ, {"ZAPIER_API_KEY": "test_api_key"})
    @patch("crewai_tools.adapters.zapier_adapter.ZapierActionsAdapter.tools")
    def test_zapier_action_tools_success_from_env(self, mock_tools):
        mock_tools.return_value = [BaseTool(name="Tool1"), BaseTool(name="Tool2")]
        tools = ZapierActionTools()
        self.assertEqual(len(tools), 2)

    @patch("crewai_tools.adapters.zapier_adapter.ZapierActionsAdapter.tools")
    def test_zapier_action_tools_success_from_param(self, mock_tools):
        mock_tools.return_value = [BaseTool(name="Tool1"), BaseTool(name="Tool2")]
        tools = ZapierActionTools(zapier_api_key="test_api_key")
        self.assertEqual(len(tools), 2)

    def test_zapier_action_tools_no_api_key(self):
        with self.assertRaises(ValueError) as context:
            ZapierActionTools()
        self.assertEqual(str(context.exception), "ZAPIER_API_KEY is not set")

    @patch.dict(os.environ, {"ZAPIER_API_KEY": "test_api_key"})
    @patch("crewai_tools.adapters.zapier_adapter.ZapierActionsAdapter.tools")
    def test_zapier_action_tools_with_action_list(self, mock_tools):
        mock_tools.return_value = [BaseTool(name="Tool1"), BaseTool(name="Tool2"), BaseTool(name="Tool3")]
        tools = ZapierActionTools(action_list=["Tool1", "Tool3"])
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0].name, "Tool1")
        self.assertEqual(tools[1].name, "Tool3")

    @patch.dict(os.environ, {"ZAPIER_API_KEY": "test_api_key"})
    @patch("crewai_tools.adapters.zapier_adapter.ZapierActionsAdapter.tools")
    def test_zapier_action_tools_empty_action_list(self, mock_tools):
        mock_tools.return_value = [BaseTool(name="Tool1"), BaseTool(name="Tool2")]
        tools = ZapierActionTools(action_list=[])
        self.assertEqual(len(tools), 0)