"""
GopiAI Widgets - Comprehensive UI Component Library

This package contains all UI components organized by functionality:
- core: Main widget components
- dialogs: Dialog windows and popup interfaces
- editors: Code editors and syntax highlighting
- managers: Icon, theme, and resource managers
- processors: Action prediction and processing components
- components: Reusable UI components
- i18n: Internationalization and localization
- resources: Static resources (icons, stylesheets, etc.)
"""

# Core widgets
from .core.card_widget import CardWidget
from .core.simple_label import SimpleLabel
from .core.text_editor import TextEditorWidget
from .core.central_widget import setup_central_widget
from .core.code_analysis_widget import CodeAnalysisWidget
from .core.debug_ui import UIDiagnostics, UI_DiagnosticsDialog, run_ui_diagnostics
from .core.docks import create_docks
from .core.dock_title_bar import DockTitleBar
from .core.flow_visualization import FlowVisualizationDialog
from .core.flow_visualizer import FlowVisualizer
from .core.icon_adapter import IconAdapter
from .core.output_widget import OutputWidget
from .core.plan_view_widget import PlanViewWidget
from .core.project_explorer import ProjectExplorer
from .core.settings_widget import SettingsWidget
from .core.widgets import *

# Dialogs
from .dialogs.chat_search_dialog import ChatSearchDialog
# Временно отключены для исправления импортов
# from .dialogs.coding_agent_dialog import CodingAgentDialog
# from .dialogs.emoji_dialog import EmojiDialog
# from .dialogs.reasoning_agent_dialog import ReasoningAgentDialog

# Editors
from .editors.code_editor import CodeEditor
from .editors.syntax_highlighter import PythonHighlighter

# Managers
from .managers.lucide_icon_manager import LucideIconManager
from .managers.theme_manager import ThemeManager

# Processors
from .processors.action_predictor import ActionPredictor
from .processors.browser_processor import AsyncPagePreProcessor

# Components (reusable UI elements)
from . import components

__all__ = [
    # Core widgets
    'CardWidget', 'SimpleLabel', 'TextEditorWidget', 'setup_central_widget', 
    'CodeAnalysisWidget', 'UIDiagnostics', 'UI_DiagnosticsDialog', 'run_ui_diagnostics', 'create_docks', 'DockTitleBar',
    'FlowVisualizationDialog', 'FlowVisualizer', 'IconAdapter', 'OutputWidget',
    'PlanViewWidget', 'ProjectExplorer', 'SettingsWidget',
    
    # Dialogs
    'ChatSearchDialog',
    # Временно отключены: 'CodingAgentDialog', 'EmojiDialog', 'ReasoningAgentDialog',
    
    # Editors
    'CodeEditor', 'PythonHighlighter',
    
    # Managers
    'LucideIconManager', 'ThemeManager',
    
    # Processors
    'ActionPredictor', 'AsyncPagePreProcessor',
]