import importlib.util
import os
import sys
import shutil
from pathlib import Path

import pytest

# Добавляем корень проекта в sys.path для импортов
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_imports():
    from ui_components import (
        StandaloneMenuBar,
        StandaloneTitlebar,
        StandaloneTitlebarWithMenu,
        CustomGrip,
        FileExplorerWidget,
        TabDocumentWidget,
        ChatWidget,
        TerminalWidget,
    )
    assert StandaloneMenuBar and StandaloneTitlebar and StandaloneTitlebarWithMenu
    assert CustomGrip and FileExplorerWidget and TabDocumentWidget
    assert ChatWidget and TerminalWidget


def test_module_structure():
    modules = [
        "ui_components/__init__.py",
        "ui_components/menu_bar.py",
        "ui_components/titlebar.py",
        "ui_components/file_explorer.py",
        "ui_components/tab_widget.py",
        "ui_components/chat_widget.py",
        "ui_components/terminal_widget.py",
    ]
    for path in modules:
        assert Path(path).exists(), f"missing {path}"


def test_fallback_mode(tmp_path):
    ui_components_path = Path("ui_components")
    backup = tmp_path / "ui_components_backup"
    shutil.move(ui_components_path, backup)
    try:
        spec = importlib.util.spec_from_file_location(
            "gopiai_standalone_interface_modular",
            "gopiai_standalone_interface_modular.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert True
    finally:
        shutil.move(str(backup), ui_components_path)

