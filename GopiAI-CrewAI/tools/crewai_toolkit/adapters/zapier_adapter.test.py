import unittest
from unittest.mock import patch, MagicMock
import os
from crewai.tools import BaseTool
from crewai_tools.zapier.zapier_actions import ZapierActionTool, ZapierActionsAdapter
from pydantic import BaseModel, Field

class TestZapierActions(unittest.TestCase):

    @patch("crewai_tools.zapier.zapier_actions.requests.request")
    def test_zapier_action_tool_run(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        tool = ZapierActionTool(name="Test", description="Test", action_id="123", api_key="test_key")
        result = tool._run(param1="value1")
        self.assertEqual(result, {"result": "success"})

    @patch("crewai_tools.zapier.zapier_actions.requests.request")
    def test_zapier_actions_adapter_get_zapier_actions(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        adapter = ZapierActionsAdapter(api_key="test_key")
        result = adapter.get_zapier_actions()
        self.assertEqual(result, {"results": []})

    @patch("crewai_tools.zapier.zapier_actions.requests.request")
    def test_zapier_actions_adapter_tools(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{
                "meta": {"action_label": "Test Action"},
                "description": "Test Description",
                "id": "123",
                "params": {"param1": {"description": "Param Description"}}
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        adapter = ZapierActionsAdapter(api_key="test_key")
        tools = adapter.tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "test_action")

    def test_zapier_actions_adapter_no_api_key(self):
        with self.assertRaises(ValueError):
            ZapierActionsAdapter()

    def test_zapier_actions_adapter_api_key_from_env(self):
        os.environ["ZAPIER_API_KEY"] = "env_key"
        adapter = ZapierActionsAdapter()
        self.assertEqual(adapter.api_key, "env_key")
        del os.environ["ZAPIER_API_KEY"]