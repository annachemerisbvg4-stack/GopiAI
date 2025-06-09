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
from .core.flow_visualization import FlowVisualizationDialog
from .core.output_widget import OutputWidget
from .core.plan_view_widget import PlanViewWidget

# Попытка импорта компонентов из GopiAI-UI
try:
    from gopiai.ui.components.file_explorer import FileExplorerWidget
    from gopiai.ui.dialogs.settings_dialog import GopiAISettingsDialog
    HAS_UI_COMPONENTS = True
except ImportError:
    HAS_UI_COMPONENTS = False

from .core.widgets import *

# Dialogs - временно отключены проблемные импорты
# from .dialogs.emoji_dialog import EmojiDialog
# from .dialogs.reasoning_agent_dialog import ReasoningAgentDialog

# Editors - только существующие файлы  
from .editors.syntax_highlighter import PythonHighlighter

# Processors
from .processors.action_predictor import ActionPredictor
from .processors.browser_processor import AsyncPagePreProcessor

# Components (reusable UI elements)
from . import components

__all__ = [
    # Core widgets
    'CardWidget', 'SimpleLabel', 'TextEditorWidget', 'setup_central_widget', 
    'CodeAnalysisWidget', 'UIDiagnostics', 'UI_DiagnosticsDialog', 'run_ui_diagnostics',
    'FlowVisualizationDialog', 'OutputWidget', 'PlanViewWidget',
]

# Добавляем компоненты UI, если они доступны
if HAS_UI_COMPONENTS:
    __all__.extend(['FileExplorerWidget', 'GopiAISettingsDialog'])