import unittest
from unittest.mock import MagicMock, patch

from crewai.tools import MultiOnTool


class MultiOnToolTests(unittest.TestCase):
    @patch("crewai.tools.multion.MultiOnTool.multion")
    def test_run_success(self, mock_multion):
        mock_multion.browse.return_value = MagicMock(
            message="Test Message", status="Test Status", session_id="Test Session ID"
        )
        tool = MultiOnTool(api_key="test_api_key")
        result = tool._run("Test Command")
        self.assertEqual(result, "Test Message\n\n STATUS: Test Status")
        self.assertEqual(tool.session_id, "Test Session ID")

    @patch("crewai.tools.multion.MultiOnTool.multion")
    def test_run_with_args_kwargs(self, mock_multion):
        mock_multion.browse.return_value = MagicMock(
            message="Test Message", status="Test Status", session_id="Test Session ID"
        )
        tool = MultiOnTool(api_key="test_api_key")
        tool._run("Test Command", "arg1", kwarg1="value1")
        mock_multion.browse.assert_called_with(
            cmd="Test Command",
            session_id=None,
            local=False,
            max_steps=3,
            arg1="arg1",
            kwarg1="value1",
        )

    @patch("crewai.tools.multion.MultiOnTool.multion")
    def test_init(self, mock_multion):
        tool = MultiOnTool(api_key="test_api_key", local=True, max_steps=5)
        self.assertTrue(tool.local)
        self.assertEqual(tool.max_steps, 5)
        mock_multion.assert_called_with(api_key="test_api_key")

    @patch("crewai.tools.multion.MultiOnTool.multion")
    def test_init_defaults(self, mock_multion):
        tool = MultiOnTool(api_key="test_api_key")
        self.assertFalse(tool.local)
        self.assertEqual(tool.max_steps, 3)
        mock_multion.assert_called_with(api_key="test_api_key")