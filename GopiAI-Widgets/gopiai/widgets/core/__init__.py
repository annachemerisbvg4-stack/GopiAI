"""
Core Widgets - Main UI components for GopiAI

This module contains the primary widget components including:
- Basic widgets (cards, labels, text editors)
- Main application widgets (central widget, file explorer)
- Utility widgets (output, settings)
- Visualization widgets (flow diagrams, analysis)
"""

from .card_widget import CardWidget
from .simple_label import SimpleLabel  
from .text_editor import TextEditorWidget
from .central_widget import setup_central_widget
from .code_analysis_widget import CodeAnalysisWidget
from .output_widget import OutputWidget
from .plan_view_widget import PlanViewWidget

# Импорты из других папок GopiAI-UI
try:
    from gopiai.ui.components.file_explorer import FileExplorerWidget
    from gopiai.ui.components.icon_file_system_model import IconFileSystemModel
    from gopiai.ui.dialogs.settings_dialog import GopiAISettingsDialog
    
    __all__ = [
        'CardWidget', 'SimpleLabel', 'TextEditorWidget', 'setup_central_widget',
        'CodeAnalysisWidget', 'OutputWidget', 'PlanViewWidget',
        'FileExplorerWidget', 'IconFileSystemModel', 'GopiAISettingsDialog'
    ]
except ImportError:
    # Если модули GopiAI-UI недоступны, используем только локальные
    __all__ = [
        'CardWidget', 'SimpleLabel', 'TextEditorWidget', 'setup_central_widget',
        'CodeAnalysisWidget', 'OutputWidget', 'PlanViewWidget'
    ]