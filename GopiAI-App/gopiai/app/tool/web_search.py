"""
Инструмент для поиска в интернете.
"""

from gopiai.app.tool.base import BaseTool


class WebSearch(BaseTool):
    """Инструмент для поиска в интернете."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="web_search",
            description="Выполняет поиск в интернете",
            function=self._search,
            parameters={
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос"
                },
                "search_engine": {
                    "type": "string",
                    "description": "Поисковая система",
                    "enum": ["google", "yandex", "bing"]
                }
            },
            required_params=["query"]
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._search(**kwargs)
    
    async def _search(self, query, search_engine="google"):
        """
        Выполняет поиск в интернете.
        
        Args:
            query: Поисковый запрос
            search_engine: Поисковая система
            
        Returns:
            dict: Результат поиска
        """
        # В минимальной версии просто возвращаем заглушку
        return {
            "success": True,
            "message": f"Выполнен поиск '{query}' в {search_engine}",
            "results": [
                {"title": "Результат 1", "url": "https://example.com/1", "snippet": "Пример результата 1"},
                {"title": "Результат 2", "url": "https://example.com/2", "snippet": "Пример результата 2"},
            ]
        }
