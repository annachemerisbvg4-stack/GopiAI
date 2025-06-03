"""
Core Widgets - Main UI components for GopiAI

This module contains the primary widget components including:
- Basic widgets (cards, labels, text editors)
- Main application widgets (central widget, project explorer)
- Utility widgets (docks, output, settings)
- Visualization widgets (flow diagrams, analysis)
"""

from .card_widget import CardWidget
from .simple_label import SimpleLabel  
from .text_editor import TextEditorWidget
from .central_widget import setup_central_widget
from .code_analysis_widget import CodeAnalysisWidget
from .debug_ui import UIDiagnostics, UI_DiagnosticsDialog, run_ui_diagnostics
from .docks import create_docks
from .dock_title_bar import DockTitleBar
# from .flow_visualization import FlowVisualizationDialog  # TODO: Fix gopiai.app dependencies
# from .flow_visualizer import FlowVisualizer  # TODO: Fix gopiai.app dependencies
from .icon_adapter import IconAdapter
from .output_widget import OutputWidget
from .plan_view_widget import PlanViewWidget
from .project_explorer import ProjectExplorer
from .settings_widget import SettingsWidget

__all__ = [
    'CardWidget', 'SimpleLabel', 'TextEditorWidget', 'setup_central_widget',
    'CodeAnalysisWidget', 'UIDiagnostics', 'UI_DiagnosticsDialog', 'run_ui_diagnostics',
    'create_docks', 'DockTitleBar', 
    'IconAdapter', 'OutputWidget', 'PlanViewWidget', 'ProjectExplorer', 'SettingsWidget'
]