"""
GopiAI Integration Tools for CrewAI
Set of specialized tools for integrating CrewAI with GopiAI
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
__description__ = 'Complete set of tools for integrating CrewAI with GopiAI platform'

# Information about tools
TOOLS_INFO = {
    'browser': {
        'class': 'GopiAIBrowserTool',
        'description': 'Search for information on the internet and work with web pages',
        'capabilities': ['search', 'fetch', 'extract', 'cache']
    },
    'filesystem': {
        'class': 'GopiAIFileSystemTool', 
        'description': 'Safe work with the file system',
        'capabilities': ['read', 'write', 'create', 'delete', 'find', 'list']
    },
    'ai_router': {
        'class': 'GopiAIRouterTool',
        'description': 'Rotation between LLM providers with automatic fallback',
        'capabilities': ['route', 'fallback', 'monitor', 'optimize']
    },
    'memory': {
        'class': 'GopiAIMemoryTool',
        'description': 'Long-term memory and RAG system',
        'capabilities': ['store', 'search', 'retrieve', 'categorize', 'summarize']
    },
    'communication': {
        'class': 'GopiAICommunicationTool',
        'description': 'Communication between agents and with UI',
        'capabilities': ['send', 'receive', 'broadcast', 'notify', 'monitor']
    }
}

def get_all_tools():
    """Returns all available GopiAI tools"""
    return [
        GopiAIBrowserTool(),
        GopiAIFileSystemTool(),
        GopiAIRouterTool(),
        GopiAIMemoryTool(),
        GopiAICommunicationTool()
    ]

def get_tool_by_name(tool_name: str):
    """Get tool by name"""
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
        raise ValueError(f"Unknown tool: {tool_name}")

print("GopiAI Integration Tools loaded successfully!")