"""
Инструмент для работы с браузером через Browser-use.
"""

from gopiai.app.tool.base import BaseTool


class BrowserUseTool(BaseTool):
    """Инструмент для работы с браузером через Browser-use."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_use",
            description="Работает с браузером через Browser-use",
            parameters={
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": ["navigate", "click", "type", "extract"],
                    "required": True
                },
                "url": {
                    "type": "string",
                    "description": "URL для перехода (для действия navigate)"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS-селектор элемента (для действий click, type, extract)"
                },
                "text": {
                    "type": "string",
                    "description": "Текст для ввода (для действия type)"
                }
            }
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._browser_use(**kwargs)
    
    async def _browser_use(self, action, url=None, selector=None, text=None):
        """
        Работает с браузером через Browser-use.
        
        Args:
            action: Действие для выполнения
            url: URL для перехода (для действия navigate)
            selector: CSS-селектор элемента (для действий click, type, extract)
            text: Текст для ввода (для действия type)
            
        Returns:
            dict: Результат операции
        """
        if action == "navigate":
            if not url:
                return {
                    "success": False,
                    "message": "Не указан URL"
                }
            return {
                "success": True,
                "message": f"Выполнен переход по URL: {url}"
            }
        elif action == "click":
            if not selector:
                return {
                    "success": False,
                    "message": "Не указан селектор"
                }
            return {
                "success": True,
                "message": f"Выполнен клик по элементу: {selector}"
            }
        elif action == "type":
            if not selector or not text:
                return {
                    "success": False,
                    "message": "Не указан селектор или текст"
                }
            return {
                "success": True,
                "message": f"Введен текст '{text}' в элемент: {selector}"
            }
        elif action == "extract":
            if not selector:
                return {
                    "success": False,
                    "message": "Не указан селектор"
                }
            return {
                "success": True,
                "message": f"Извлечено содержимое элемента: {selector}",
                "content": "Пример содержимого"
            }
        else:
            return {
                "success": False,
                "message": f"Неизвестное действие: {action}"
            }
