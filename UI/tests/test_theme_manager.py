import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget

# Добавляем корень проекта в sys.path для импортов
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui_components.theme_manager import apply_simple_theme

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_apply_simple_theme():
    app = QApplication.instance() or QApplication([])
    widget = QWidget()
    widget.show()  # Should not raise
    assert apply_simple_theme(app) is True
