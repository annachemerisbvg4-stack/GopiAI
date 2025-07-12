import unittest
from gopiai.schemas import AgentState, Message, Memory, Conversation, Tool, ToolCall, ToolChoice

class TestSchemas(unittest.TestCase):

    def test_agent_state(self):
        self.assertEqual(AgentState.IDLE.value, "idle")
        self.assertEqual(AgentState.THINKING.value, "thinking")

    def test_message(self):
        msg = Message(content="Hello", role="user")
        self.assertEqual(msg.content, "Hello")
        self.assertEqual(msg.role, "user")

    def test_memory(self):
        mem = Memory(content="Test memory")
        self.assertEqual(mem.content, "Test memory")

    def test_tool_choice(self):
        tool_choice = ToolChoice(type="required", tool="my_tool")
        self.assertEqual(tool_choice.type, "required")
        self.assertEqual(tool_choice.tool, "my_tool")