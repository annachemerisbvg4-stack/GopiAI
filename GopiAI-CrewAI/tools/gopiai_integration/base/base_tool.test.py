import unittest
from unittest.mock import patch
import os
import tempfile
import json
import logging

# Assuming GopiAIBaseTool is in gopiai_tool.py
from gopiai_tool import GopiAIBaseTool

class TestGopiAIBaseTool(unittest.TestCase):

    def setUp(self):
        class TestTool(GopiAIBaseTool):
            name = "test_tool"
            description = "Тестовый инструмент"

            def _run(self, action, value=""):
                if action == "echo":
                    return f"Echo: {value}"
                elif action == "error":
                    raise ValueError("Тестовая ошибка")
                else:
                    return f"Неизвестное действие: {action}"

            def _fallback(self, action, value="", error=None):
                return f"Fallback для {action}: {error}"
        self.TestTool = TestTool
        self.tool = TestTool()

    def test_successful_run(self):
        result = self.tool.run("echo", "test")
        self.assertEqual(result, "Echo: test")
        self.assertEqual(self.tool.get_metrics()['calls'], 1)
        self.assertEqual(self.tool.get_metrics()['errors'], 0)

    def test_error_handling_with_fallback(self):
        result = self.tool.run("error")
        self.assertTrue("Fallback" in result)
        self.assertEqual(self.tool.get_metrics()['calls'], 1)
        self.assertEqual(self.tool.get_metrics()['errors'], 1)

    def test_error_handling_no_fallback(self):
        class TestToolNoFallback(GopiAIBaseTool):
            name = "test_tool_no_fallback"
            description = "Тестовый инструмент без fallback"

            def _run(self, action, value=""):
                raise ValueError("Тестовая ошибка")
        tool = TestToolNoFallback()
        result = tool.run("any")
        self.assertTrue("Ошибка при выполнении инструмента" in result)

    @patch("subprocess.run")
    def test_run_node_script_success(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.stderr = ""

        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', encoding='utf-8', delete=False) as temp_output:
            json.dump({"result": "success"}, temp_output, ensure_ascii=False)
            temp_output_path = temp_output.name

        def side_effect(*args, **kwargs):
            return type('obj', (object,), {'returncode': 0, 'stdout': '', 'stderr': ''})()
        mock_subprocess_run.side_effect = side_effect
        result = self.tool.run_node_script("test.js", {"input": "test"})
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], {"result": "success"})

    def test_reset_metrics(self):
        self.tool.run("echo", "test")
        self.tool.run("error")
        self.tool.reset_metrics()
        metrics = self.tool.get_metrics()
        self.assertEqual(metrics['calls'], 0)
        self.assertEqual(metrics['errors'], 0)

if __name__ == '__main__':
    unittest.main()