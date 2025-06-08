from typing import List

from gopiai.app.agent.toolcall import ToolCallAgent
from gopiai.app.prompt.swe import SYSTEM_PROMPT
from gopiai.app.tool import Bash, StrReplaceEditor, Terminate, ToolCollection
from pydantic import Field


class SWEAgent(ToolCallAgent):
    """An agent that implements the SWEAgent paradigm for executing code and natural conversations."""

    name: str = "swe"
    description: str = (
        "an autonomous AI programmer that interacts directly with the computer to solve tasks."
    )

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = ""

    swe_tools: ToolCollection = ToolCollection(Bash(), StrReplaceEditor(), Terminate())
    special_tool_names: List[str] = Field(
        default_factory=lambda: [Terminate().terminate_name]
    )

    max_steps: int = 20
