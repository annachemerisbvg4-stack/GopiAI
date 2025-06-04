import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMenuBar
from PySide6.QtGui import QAction, QIcon, QPixmap

# Добавляем корень проекта в sys.path для импортов
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui_components.icon_system import AutoIconMapper, AutoIconSystem

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
app = QApplication.instance() or QApplication([])


class DummyIconManager:
    def __init__(self):
        self.requested = []

    def get_icon(self, name, color=None, size=None):
        self.requested.append(name)
        pixmap = QPixmap(1, 1)
        pixmap.fill()
        return QIcon(pixmap)


def test_auto_icon_mapper_basic():
    mapper = AutoIconMapper()
    assert mapper.get_icon_name("open_action") == "folder-open"
    assert mapper.get_icon_name("custom") == "custom"
    # cache should contain the keys now
    assert "open_action" in mapper.name_cache


def test_apply_icons_to_menu():
    dummy = DummyIconManager()
    system = AutoIconSystem(provided_icon_manager=dummy)
    menu = QMenuBar()
    act1 = QAction("Open", menu)
    act1.setObjectName("open_action")
    menu.addAction(act1)
    act2 = QAction("Save", menu)
    act2.setObjectName("save_action")
    menu.addAction(act2)

    count = system.apply_icons_to_menu(menu)
    assert count == 2
    assert set(dummy.requested) == {"folder-open", "save"}
