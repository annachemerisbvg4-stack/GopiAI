import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from gopiai.app.agent.toolcall import ToolCallAgent, TOOL_CALL_REQUIRED
from gopiai.app.schema import AgentState, Message, ToolCall, Function
from gopiai.app.tool import Terminate


class TestToolCallAgent(unittest.IsolatedAsyncioTestCase):

    async def test_think_token_limit_exceeded(self):
        agent = ToolCallAgent()
        agent.llm = AsyncMock()
        agent.llm.ask_tool.side_effect = Exception(TokenLimitExceeded("Test error"))
        with self.assertRaises(Exception):
            await agent.think()
        self.assertEqual(agent.state, AgentState.FINISHED)

    async def test_act_no_tool_calls_required(self):
        agent = ToolCallAgent()
        agent.tool_choices = "required"
        agent.tool_calls = []
        with self.assertRaisesRegex(ValueError, TOOL_CALL_REQUIRED):
            await agent.act()

    async def test_execute_tool_invalid_command(self):
        agent = ToolCallAgent()
        command = ToolCall(id="1", function=Function(name="invalid", arguments="{}"))
        result = await agent.execute_tool(command)
        self.assertIn("Error: Unknown tool", result)

    async def test_handle_special_tool_terminate(self):
        agent = ToolCallAgent()
        agent.state = AgentState.RUNNING
        await agent._handle_special_tool(name="terminate", result="done")
        self.assertEqual(agent.state, AgentState.FINISHED)

    async def test_run_with_dict_input(self):
        agent = ToolCallAgent()
        agent.step = AsyncMock(return_value="Step result")
        agent.max_steps = 2
        agent.state = AgentState.RUNNING
        result = await agent.run({"task": "Test task", "context": {"key": "value"}})
        self.assertEqual(result, "Step result")
        self.assertEqual(agent.current_step, 1)