"""
Модуль планирующего агента.

Предоставляет реализацию агента, который использует планирование для решения задач.
"""

from gopiai.app.agent.toolcall import ToolCallAgent
from gopiai.app.prompt.planning import SYSTEM_PROMPT, NEXT_STEP_PROMPT


class PlanningAgent(ToolCallAgent):
    """
    Агент, использующий планирование для решения задач.
    
    Этот агент сначала создает план действий, а затем выполняет его шаг за шагом.
    """
    
    name: str = "planning_agent"
    description: str = "Агент, использующий планирование для решения задач"
    
    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT
    
    max_observe: int = 10000
    max_steps: int = 20
