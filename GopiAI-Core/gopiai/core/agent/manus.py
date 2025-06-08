from gopiai.app.agent.browser import BrowserAgent
from gopiai.app.config import WORKSPACE_ROOT
from gopiai.app.prompt.browser import NEXT_STEP_PROMPT as BROWSER_NEXT_STEP_PROMPT
from gopiai.app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from gopiai.app.tool import Terminate
from gopiai.app.tool.browser_use_tool import BrowserUseTool
from gopiai.app.tool.python_execute import PythonExecute
from gopiai.app.tool.str_replace_editor import StrReplaceEditor
from gopiai.app.tool.web_search import WebSearch

# from gopiai.app.tool.tavily_tool import TavilyTool  # Remove TavilyTool import


class Manus(BrowserAgent):
    """
    A versatile general-purpose agent that uses planning to solve various tasks.

    This agent extends BrowserAgent with a comprehensive set of tools and capabilities,
    including Python execution, web browsing, file operations, and information retrieval
    to handle a wide range of user requests.
    """

    name: str = "Manus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=WORKSPACE_ROOT)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20    # Мы не переопределяем tools_collection здесь, так как оно наследуется
    # Вместо этого мы добавим инструменты через метод add_tool в __init__

    def __init__(self, **kwargs):
        """Инициализирует агента Manus с нужными инструментами."""
        super().__init__(**kwargs)
        
        # Добавляем необходимые инструменты
        self.add_tool(PythonExecute())
        self.add_tool(WebSearch())
        self.add_tool(BrowserUseTool())
        self.add_tool(StrReplaceEditor())
        self.add_tool(Terminate())

    async def think(self) -> bool:
        """Process current state and decide next actions with appropriate context."""
        # Store original prompt
        original_prompt = self.next_step_prompt

        # Only check recent messages (last 3) for browser activity
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            "browser_use" in msg.content.lower()
            for msg in recent_messages
            if hasattr(msg, "content") and isinstance(msg.content, str)
        )

        if browser_in_use:
            # Override with browser-specific prompt temporarily to get browser context
            self.next_step_prompt = BROWSER_NEXT_STEP_PROMPT

        # Call parent's think method
        result = await super().think()

        # Restore original prompt
        self.next_step_prompt = original_prompt

        return result
