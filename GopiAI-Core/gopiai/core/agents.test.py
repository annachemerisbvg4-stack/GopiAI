import unittest
from unittest.mock import patch

class BaseAgent:
    """Базовый класс агента"""
    
    def __init__(self):
        self.name = "BaseAgent"
    
    def execute(self, command: str):
        """Выполнить команду"""
        print(f"[{self.name}] Executing: {command}")

# Временные заглушки
def get_coding_agent():
    """Получить агента кодирования"""
    return BaseAgent()

def get_browser_agent():
    """Получить браузерного агента"""
    return BaseAgent()

class TestBaseAgent(unittest.TestCase):

    def test_base_agent_creation(self):
        agent = BaseAgent()
        self.assertEqual(agent.name, "BaseAgent")

    @patch('__main__.BaseAgent.execute')
    def test_base_agent_execute(self, mock_execute):
        agent = BaseAgent()
        agent.execute("test_command")
        mock_execute.assert_called_with("test_command")

    def test_get_coding_agent(self):
        agent = get_coding_agent()
        self.assertIsInstance(agent, BaseAgent)

    def test_get_browser_agent(self):
        agent = get_browser_agent()
        self.assertIsInstance(agent, BaseAgent)

    @patch('sys.stdout')
    def test_base_agent_execute_print(self, mock_stdout):
        agent = BaseAgent()
        agent.execute("test_command")
        mock_stdout.assert_called()

if __name__ == '__main__':
    unittest.main()