import unittest
import os
import json
from unittest.mock import patch, mock_open
from datetime import datetime
from pydantic import ValidationError

from crewai.tools.base_tool import BaseTool
from your_module import GopiAICommunicationTool, CommunicationInput  # Replace your_module

class TestGopiAICommunicationTool(unittest.TestCase):

    def setUp(self):
        self.tool = GopiAICommunicationTool(
            messages_path="./test_communication",
            message_queue_file="./test_communication/message_queue.json",
            agent_status_file="./test_communication/agent_status.json",
            ui_notifications_file="./test_communication/ui_notifications.json"
        )
        os.makedirs("./test_communication", exist_ok=True)
        self.tool.init_files()

    def tearDown(self):
        import shutil
        shutil.rmtree("./test_communication")

    def test_send_message(self):
        result = self.tool._run("send", recipient="test_agent", message="Test message", message_type="info", priority=3)
        self.assertIn("Сообщение отправлено", result)

    def test_receive_messages(self):
        self.tool._run("send", recipient="test_agent", message="Test message", message_type="info", priority=3)
        result = self.tool._run("receive", agent_id="test_agent")
        self.assertIn("Новые сообщения", result)

    def test_notify_ui(self):
        result = self.tool._run("notify", message="Test notification", message_type="info", priority=3)
        self.assertIn("Уведомление отправлено", result)

    def test_list_active_agents(self):
        self.tool._update_agent_status("test_agent", "active")
        result = self.tool._run("list_agents")
        self.assertIn("Активные агенты", result)

    def test_communication_input_validation(self):
        with self.assertRaises(ValidationError):
            CommunicationInput(action="invalid_action", recipient="test", message="test")

if __name__ == '__main__':
    unittest.main()