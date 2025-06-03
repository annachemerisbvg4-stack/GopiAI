"""
Инструмент для выполнения Python-кода.
"""

from gopiai.app.interfaces import ToolResult
from gopiai.app.tool.base import BaseTool


class PythonExecute(BaseTool):
    """Инструмент для выполнения Python-кода."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="python_execute",
            description="Выполняет Python-код",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python-код для выполнения"
                    }
                },
                "required": ["code"]
            }
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._execute(**kwargs)
    
    async def _execute(self, code):
        """
        Выполняет Python-код.
        
        Args:
            code: Python-код для выполнения
            
        Returns:
            dict: Результат выполнения кода
        """
        try:
            # Создаем локальное пространство имен
            local_vars = {}
            
            # Выполняем код
            exec(code, {}, local_vars)
            
            # Формируем результат
            output = str(local_vars.get("result", "Нет результата"))
            
            return ToolResult(
                message="Код успешно выполнен",
                data={"output": output}
            )
        except Exception as e:
            return ToolResult(
                message=f"Ошибка при выполнении кода: {str(e)}",
                data={"error": str(e)},
                success=False
            )
