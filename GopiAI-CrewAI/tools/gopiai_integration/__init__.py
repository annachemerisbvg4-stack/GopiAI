"""
🚀 GopiAI Integration Tools для CrewAI
Набор специализированных инструментов для интеграции CrewAI с GopiAI
"""

from .browser_tools import GopiAIBrowserTool
from .filesystem_tools import GopiAIFileSystemTool
from .ai_router_tools import GopiAIRouterTool
from .memory_tools import GopiAIMemoryTool
from .communication_tools import GopiAICommunicationTool

__all__ = [
    'GopiAIBrowserTool',
    'GopiAIFileSystemTool', 
    'GopiAIRouterTool',
    'GopiAIMemoryTool',
    'GopiAICommunicationTool'
]

__version__ = '1.0.0'
__author__ = 'GopiAI Team'
__description__ = 'Полный набор инструментов для интеграции CrewAI с GopiAI платформой'

# Информация об инструментах
TOOLS_INFO = {
    'browser': {
        'class': 'GopiAIBrowserTool',
        'description': 'Поиск информации в интернете и работа с веб-страницами',
        'capabilities': ['search', 'fetch', 'extract', 'cache']
    },
    'filesystem': {
        'class': 'GopiAIFileSystemTool', 
        'description': 'Безопасная работа с файловой системой',
        'capabilities': ['read', 'write', 'create', 'delete', 'find', 'list']
    },
    'ai_router': {
        'class': 'GopiAIRouterTool',
        'description': 'Ротация между LLM провайдерами с автоматическим fallback',
        'capabilities': ['route', 'fallback', 'monitor', 'optimize']
    },
    'memory': {
        'class': 'GopiAIMemoryTool',
        'description': 'Долговременная память и RAG система',
        'capabilities': ['store', 'search', 'retrieve', 'categorize', 'summarize']
    },
    'communication': {
        'class': 'GopiAICommunicationTool',
        'description': 'Коммуникация между агентами и с UI',
        'capabilities': ['send', 'receive', 'broadcast', 'notify', 'monitor']
    }
}

def get_all_tools():
    """Возвращает все доступные GopiAI инструменты"""
    return [
        GopiAIBrowserTool(),
        GopiAIFileSystemTool(),
        GopiAIRouterTool(),
        GopiAIMemoryTool(),
        GopiAICommunicationTool()
    ]

def get_tool_by_name(tool_name: str):
    """Получить инструмент по имени"""
    tools_map = {
        'browser': GopiAIBrowserTool,
        'filesystem': GopiAIFileSystemTool,
        'ai_router': GopiAIRouterTool,
        'memory': GopiAIMemoryTool,
        'communication': GopiAICommunicationTool
    }
    
    if tool_name in tools_map:
        return tools_map[tool_name]()
    else:
        raise ValueError(f"Неизвестный инструмент: {tool_name}")

print("GopiAI Integration Tools loaded successfully!")