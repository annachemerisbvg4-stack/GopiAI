import os
import sys
import types
import importlib
import pytest
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('GopiAI-Extensions'))
from gopiai_standalone_interface import FramelessGopiAIStandaloneWindow

class DummyMain:
    def __init__(self):
        self.dock_widgets = {}
        self.left = []
        self.right = []
        self.bottom = []

    def _add_to_left_panel(self, widget):
        self.left.append(widget)

    def _add_to_right_panel(self, widget):
        self.right.append(widget)

    def _add_to_bottom_panel(self, widget):
        self.bottom.append(widget)

DummyMain.add_dock_widget = FramelessGopiAIStandaloneWindow.add_dock_widget
DummyMain._toggle_ai_tools_extension = FramelessGopiAIStandaloneWindow._toggle_ai_tools_extension

@pytest.fixture
def app():
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def main(app):
    return DummyMain()

def setup_dummy_extension():
    # Создаем минимальный модуль gopiai.extensions с функцией _safely_import
    extensions_pkg = types.ModuleType('gopiai.extensions')
    def _safely_import(name):
        return importlib.import_module(name)
    extensions_pkg._safely_import = _safely_import
    sys.modules['gopiai.extensions'] = extensions_pkg

    module = types.ModuleType('gopiai.extensions.ai_tools_extension')
    def init_extension(win):
        widget = QWidget()
        widget.setObjectName('aiToolsWidget')
        win.add_dock_widget('ai_tools', widget, 'right')
    module.init_extension = init_extension
    sys.modules['gopiai.extensions.ai_tools_extension'] = module

def teardown_dummy_extension():
    sys.modules.pop('gopiai.extensions.ai_tools_extension', None)

def test_toggle_ai_tools_extension(main, monkeypatch):
    setup_dummy_extension()
    monkeypatch.setattr(QMessageBox, 'warning', lambda *a, **k: None)
    main._toggle_ai_tools_extension()
    assert 'ai_tools' in main.dock_widgets
    widget = main.dock_widgets['ai_tools']
    assert widget in main.right
    assert widget.isVisible()
    main._toggle_ai_tools_extension()
    assert not widget.isVisible()
    teardown_dummy_extension()
