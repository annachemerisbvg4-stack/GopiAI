"""AI Tools for GopiAI.

This package provides various tools that the AI can use to assist the user,
including UI interaction, file operations, and more.
"""

from typing import Dict, Type, Any, Optional, TYPE_CHECKING
import importlib
import inspect
import json

# Lazy imports to avoid circular dependencies
if TYPE_CHECKING:
    from .ui_assistant import UIAssistantTool

# Dictionary of available tools (initialized on first use)
_TOOLS: Dict[str, Any] = {}

def _get_tools() -> Dict[str, Any]:
    """Lazily initialize and return the tools dictionary."""
    if not _TOOLS:
        from .ui_assistant import get_ui_assistant
        _TOOLS['ui_assistant'] = get_ui_assistant()
    return _TOOLS

def get_tool(tool_name: str) -> Any:
    """
    Get a tool by name.
    
    Args:
        tool_name: The name of the tool to get.
        
    Returns:
        The tool instance, or None if not found.
    """
    return _get_tools().get(tool_name)

def get_available_tools() -> Dict[str, Any]:
    """
    Get a dictionary of all available tools.
    
    Returns:
        A dictionary mapping tool names to tool instances.
    """
    return _get_tools().copy()

def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the JSON schema for a tool's parameters.
    
    Args:
        tool_name: The name of the tool.
        
    Returns:
        A dictionary containing the tool's schema, or None if the tool doesn't exist.
    """
    tool = get_tool(tool_name)
    if not tool:
        return None
    
    # Get the tool's methods that don't start with underscore
    methods = [
        (name, method) 
        for name, method in inspect.getmembers(tool, inspect.ismethod) 
        if not name.startswith('_')
    ]
    
    schema = {
        'name': tool_name,
        'description': tool.__doc__ or 'No description available.',
        'methods': {}
    }
    
    for method_name, method in methods:
        # Skip private methods
        if method_name.startswith('_'):
            continue
            
        # Get method signature
        sig = inspect.signature(method)
        params = {}
        
        # Skip 'self' parameter
        parameters = list(sig.parameters.values())[1:]  # Skip 'self'
        
        for param in parameters:
            param_info = {
                'type': param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'Any',
                'required': param.default == inspect.Parameter.empty,
            }
            
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
                
            params[param.name] = param_info
            
        schema['methods'][method_name] = {
            'description': method.__doc__ or 'No description available.',
            'parameters': params,
            'return_type': sig.return_annotation.__name__ if sig.return_annotation != inspect.Signature.empty else 'None'
        }
    
    return schema

# Export commonly used tools
def get_ui_assistant_tool() -> 'UIAssistantTool':
    """Get the UI Assistant tool instance."""
    from .ui_assistant import get_ui_assistant
    return get_ui_assistant()
