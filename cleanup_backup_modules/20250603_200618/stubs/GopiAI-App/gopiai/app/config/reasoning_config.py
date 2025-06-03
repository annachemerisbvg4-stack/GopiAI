"""
Заглушка для gopiai.app.config.reasoning_config.
STUB: Используется временно для избежания циклических зависимостей.
"""

from enum import Enum

# STUB: Заглушка для ReasoningStrategy
class ReasoningStrategy(Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    EXPERT = "expert"

__all__ = ['ReasoningStrategy']
