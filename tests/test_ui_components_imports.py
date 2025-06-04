import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для импортов
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


def test_ui_components_are_importable():
    # simply assert that classes are imported
    assert StandaloneMenuBar
    assert StandaloneTitlebar
    assert StandaloneTitlebarWithMenu
    assert CustomGrip
    assert FileExplorerWidget
    assert TabDocumentWidget
    assert ChatWidget
    assert TerminalWidget
