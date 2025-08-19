"""
Заглушки для отсутствующего модуля gopiai_integration.
Это позволяет приложению запускаться без старого бэкенда CrewAI.
"""
import logging

logger = logging.getLogger(__name__)

def _log_stub_call(func_name, *args, **kwargs):
    logger.warning(f"[STUB] Вызвана функция-заглушка: {func_name} с args: {args}, kwargs: {kwargs}. Эта функциональность отключена.")

# --- Заглушки для main.py ---
def set_terminal_widget(widget):
    _log_stub_call('set_terminal_widget', widget)
    pass

# --- Заглушки для crewai_client.py ---
class EmotionalState:
    NEUTRAL = "neutral"

class EmotionalClassifier:
    def __init__(self, *args, **kwargs):
        _log_stub_call('EmotionalClassifier.__init__', *args, **kwargs)
    def analyze_emotional_state(self, *args, **kwargs):
        _log_stub_call('EmotionalClassifier.analyze_emotional_state', *args, **kwargs)
        return {'primary_emotion': EmotionalState.NEUTRAL, 'confidence': 0.0, 'intensity': 0.0}

class AIRouterLLM:
    def __init__(self, *args, **kwargs):
        _log_stub_call('AIRouterLLM.__init__', *args, **kwargs)

class ModelConfigManager:
    pass

def get_model_config_manager():
    _log_stub_call('get_model_config_manager')
    return ModelConfigManager()

class ToolsInstructionManager:
    def get_tools_summary(self):
        _log_stub_call('ToolsInstructionManager.get_tools_summary')
        return {}
    def get_tool_detailed_instructions(self, tool_name):
        _log_stub_call('ToolsInstructionManager.get_tool_detailed_instructions', tool_name)
        return ""

def get_tools_instruction_manager():
    _log_stub_call('get_tools_instruction_manager')
    return ToolsInstructionManager()

# --- Заглушки для openrouter_model_widget.py ---
class OpenRouterClient:
    def __init__(self, *args, **kwargs):
        _log_stub_call('OpenRouterClient.__init__', *args, **kwargs)
    def get_models(self, *args, **kwargs):
        _log_stub_call('OpenRouterClient.get_models', *args, **kwargs)
        return []

def get_openrouter_client():
    _log_stub_call('get_openrouter_client')
    return OpenRouterClient()

# --- Заглушки для unified_model_widget.py ---
class ModelProvider:
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
