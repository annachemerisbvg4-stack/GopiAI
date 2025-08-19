"""
Утилиты для загрузки Lucide SVG иконок и создания компактных кнопок-иконок.
- Без хардкода цветов: опираемся на системную палитру/тему Qt
- Аккуратные размеры: кнопка 28x28, иконка 18x18
- Fallback: мини-набор встроенных SVG и простые текстовые символы
"""
from __future__ import annotations
import os
import logging
from typing import Dict, Optional

from PySide6.QtCore import Qt, QByteArray, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtWidgets import QPushButton

try:
    from PySide6.QtSvg import QSvgRenderer  # предпочтительный рендер SVG
    _HAS_QTSVG = True
except Exception:
    QSvgRenderer = None  # type: ignore
    _HAS_QTSVG = False

logger = logging.getLogger(__name__)


def _icons_dir() -> str:
    """Абсолютный путь к каталогу Lucide SVG иконок."""
    # .../ui/utils -> .../ui
    ui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.abspath(os.path.join(ui_dir, 'assets', 'icons', 'lucide'))


def _lucide_svg_map() -> Dict[str, str]:
    """Мини-набор SVG иконок Lucide (outline) для fallback."""
    return {
        # paperclip
        "paperclip": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 115.66 5.66L9.88 17.56a2 2 0 11-2.83-2.83l8.49-8.49"/></svg>',
        # refresh-cw
        "refresh-cw": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.13-3.36L23 10"/><path d="M20.49 15a9 9 0 01-14.13 3.36L1 14"/></svg>',
        # eraser
        "eraser": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14l-7-7-8 8 5 5h6l4-4z"/><path d="M7 21h10"/></svg>',
        # minus-circle
        "minus-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/></svg>',
        # trash-2
        "trash-2": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>',
        # power
        "power": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v10"/><path d="M5.5 5.5a7 7 0 109.9 9.9"/></svg>',
        # power-off
        "power-off": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6a9 9 0 11-6 15"/><path d="M12 2v10"/></svg>',
        # key
        "key": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2"/><circle cx="7.5" cy="15.5" r="5.5"/><path d="M11 11l8-8"/><path d="M16 5l3 3"/></svg>',
        # image
        "image": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="M21 15l-5-5L5 21"/></svg>',
        # send
        "send": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>',
        # arrow-left
        "arrow-left": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
        # arrow-right
        "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
        # arrow-left-right
        "arrow-left-right": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3l-5 5 5 5"/><path d="M3 8h18"/><path d="M16 21l5-5-5-5"/></svg>',
        # corner-down-right
        "corner-down-right": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 10l5 5-5 5"/><path d="M4 4v7a4 4 0 004 4h12"/></svg>',
        # plus
        "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
        # check
        "check": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
        # x (close)
        "x": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
        # minus (minimize)
        "minus": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>',
        # maximize-2
        "maximize-2": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>',
        # square (restore)
        "square": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>',
    }


def _svg_to_icon(svg_text: str, size: int = 18) -> Optional[QIcon]:
    """Преобразует SVG-текст в QIcon. Возвращает None при отсутствии QtSvg."""
    if not _HAS_QTSVG or not svg_text:
        return None
    data = QByteArray(svg_text.encode("utf-8"))
    renderer = QSvgRenderer(data)
    if not renderer.isValid():
        return None
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)


def _load_icon_from_assets(icon_name: str, size: int = 18) -> Optional[QIcon]:
    """Пытается загрузить SVG из assets/lucide по имени (без .svg)."""
    if not _HAS_QTSVG:
        return None
    path = os.path.join(_icons_dir(), f"{icon_name}.svg")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            svg_text = f.read()
        return _svg_to_icon(svg_text, size=size)
    except Exception as e:
        logger.warning(f"Не удалось загрузить SVG иконку '{icon_name}': {e}")
        return None


def get_icon(icon_name: str, size: int = 18) -> Optional[QIcon]:
    """Возвращает QIcon из ассетов или fallback SVG. Если ничего не удалось — None."""
    icon = _load_icon_from_assets(icon_name, size=size)
    if icon is not None:
        return icon
    svg_map = _lucide_svg_map()
    return _svg_to_icon(svg_map.get(icon_name, ""), size=size)


def create_icon_button(icon_name: str, tooltip: str, *, btn_size: int = 28, icon_size: int = 18) -> QPushButton:
    """Создает компактную кнопку-иконку с тултипом без хардкода цветов.
    - Цвета и отступы берутся из темы/палитры Qt
    - Если иконка недоступна, использует текстовый символ
    """
    btn = QPushButton()
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setToolTip(tooltip)
    btn.setFixedSize(btn_size, btn_size)
    btn.setIconSize(QSize(icon_size, icon_size))

    icon = get_icon(icon_name, size=icon_size)
    if icon is not None:
        btn.setIcon(icon)
        btn.setText("")
    else:
        fallback_text = {
            "paperclip": "🧷",
            "refresh-cw": "↻",
            "eraser": "⌫",
            "minus-circle": "−",
            "trash-2": "🗑",
            "key": "🔑",
            "arrow-left": "←",
            "arrow-right": "→",
            "arrow-left-right": "↔",
            "corner-down-right": "➤",
            "plus": "+",
            "check": "✓",
            "x": "✕",
            "minus": "–",
            "maximize-2": "□",
            "square": "❐",
        }.get(icon_name, "•")
        btn.setText(fallback_text)

    # Без setStyleSheet: тема управляет цветами/фоном/ховером
    return btn
