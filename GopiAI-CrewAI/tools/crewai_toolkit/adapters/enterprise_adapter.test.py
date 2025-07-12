import unittest
from unittest.mock import patch, MagicMock
from crewai_tools_enterprise_action_kit import EnterpriseActionTool, EnterpriseActionKitToolAdapter
import json

class TestEnterpriseActionTool(unittest.TestCase):

    @patch('requests.post')
    def test_run_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        tool = EnterpriseActionTool(
            name="TestAction",
            description="Test Description",
            enterprise_action_token="test_token",
            action_name="test_action",
            action_schema={},
        )
        result = tool._run(input_text="test input")
        self.assertEqual(result, '{\n  "result": "success"\n}')

    @patch('requests.post')
    def test_run_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.json.return_value = {"error": {"message": "test error"}}
        mock_post.return_value = mock_response

        tool = EnterpriseActionTool(
            name="TestAction",
            description="Test Description",
            enterprise_action_token="test_token",
            action_name="test_action",
            action_schema={},
        )
        result = tool._run(input_text="test input")
        self.assertEqual(result, "API request failed: test error")

class TestEnterpriseActionKitToolAdapter(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_actions_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "actions": {
                "category1": [
                    {"function": {"name": "action1", "description": "desc1", "parameters": {"properties": {}, "required": []}}},
                    {"function": {"name": "action2", "description": "desc2", "parameters": {"properties": {}, "required": []}}}
                ]
            }
        }
        mock_get.return_value = mock_response

        adapter = EnterpriseActionKitToolAdapter(enterprise_action_token="test_token")
        adapter._fetch_actions()
        self.assertIn("action1", adapter._actions_schema)
        self.assertIn("action2", adapter._actions_schema)

    @patch('requests.get')
    def test_fetch_actions_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Test Exception")
        mock_get.return_value = mock_response

        adapter = EnterpriseActionKitToolAdapter(enterprise_action_token="test_token")
        adapter._fetch_actions()
        self.assertEqual(adapter._actions_schema, {})

    @patch('requests.get')
    def test_tools(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "actions": {
                "category1": [
                    {"function": {"name": "action1", "description": "desc1", "parameters": {"properties": {}, "required": []}}},
                ]
            }
        }
        mock_get.return_value = mock_response
        adapter = EnterpriseActionKitToolAdapter(enterprise_action_token="test_token")
        tools = adapter.tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "action1")