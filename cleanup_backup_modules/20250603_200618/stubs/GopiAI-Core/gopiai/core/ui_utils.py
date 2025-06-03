#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 📅 TODO_STUB_SEARCH: найти командой grep -r 'TODO_STUB' .

# 🚧 ВРЕМЕННАЯ ЗАГЛУШКА! НЕ УДАЛЯТЬ! 🚧
# TODO_STUB: Заменить на реальную реализацию после миграции циклических зависимостей
# CREATED: 31 мая 2025 г.
# PURPOSE: Разорвать циклическую зависимость GopiAI-Widgets <-> GopiAI-App

"""
🎯 UI утилиты для gopiai.core

Заглушки для замены gopiai.app.utils.ui_utils
"""

from typing import Optional, Any, Callable
from pathlib import Path

# 🚧 ЗАГЛУШКИ ДЛЯ ОСНОВНЫХ ФУНКЦИЙ UI_UTILS
def safe_get_icon(icon_name: str, fallback: str = "default") -> str:
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Безопасно получить иконку (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Реализовать через unified icon manager
    return f"icon:{icon_name}"

def apply_theme_to_widget(widget: Any, theme_name: Optional[str] = None):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Применить тему к виджету (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Интеграция с unified theme manager
    pass

def get_resource_path(resource_name: str) -> Path:
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Получить путь к ресурсу (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Unified resource management
    return Path("resources") / resource_name

def show_error_message(message: str, title: str = "Ошибка"):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Показать сообщение об ошибке (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Реальные диалоги ошибок
    print(f"❌ {title}: {message}")

def show_info_message(message: str, title: str = "Информация"):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Показать информационное сообщение (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Реальные информационные диалоги
    print(f"ℹ️ {title}: {message}")

def create_action(text: str, callback: Callable, icon: Optional[str] = None) -> Any:
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Создать действие (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Unified action system
    return None

def setup_widget_geometry(widget: Any, geometry_key: str):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Настроить геометрию виджета (заглушка)"""
    # 🚧 ЗАГЛУШКА! TODO_STUB: Integration with config system
    pass

# 🚧 ЗАГЛУШКИ ДЛЯ СОВМЕСТИМОСТИ
get_icon = safe_get_icon
apply_theme = apply_theme_to_widget
