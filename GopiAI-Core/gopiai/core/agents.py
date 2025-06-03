"""
🎯 Агенты для всех модулей GopiAI
Унифицированный доступ к агентам
"""

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
