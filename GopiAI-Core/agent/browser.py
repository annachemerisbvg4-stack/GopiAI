"""
Модуль браузерного агента.

Предоставляет базовую реализацию агента для работы с браузером.
"""

from gopiai.app.agent.toolcall import ToolCallAgent
from gopiai.app.prompt.browser import SYSTEM_PROMPT, NEXT_STEP_PROMPT


class BrowserAgent(ToolCallAgent):
    """
    Базовый агент для работы с браузером.
    
    Предоставляет основные возможности для навигации и взаимодействия с веб-страницами.
    """
    
    name: str = "browser_agent"
    description: str = "Агент для работы с браузером"
    
    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT
    
    max_observe: int = 10000
    max_steps: int = 20
