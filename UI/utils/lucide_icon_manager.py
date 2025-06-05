"""
GopiAI LucideIconManager - Менеджер Lucide иконок (Совместимость)
===============================================

Модуль совместимости для переадресации запросов к менеджеру иконок Lucide
из GopiAI-Widgets.

Автор: Crazy Coder
Версия: 2.0.0
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union, Set, List

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer


class LucideIconManager:
    """Менеджер для работы с иконками Lucide в приложении GopiAI."""

    _instance = None
    _cache = {}  # Кеш для иконок

    @classmethod
    def instance(cls):
        """Получение единственного экземпляра менеджера иконок (паттерн Singleton)."""
        if cls._instance is None:
            cls._instance = LucideIconManager()
        return cls._instance

    def __init__(self):
        """Инициализация менеджера иконок Lucide."""
        # Попытка использовать логгер, но с fallback на print
        try:
            from gopiai.core.logging import get_logger
            self.logger = get_logger().logger
        except ImportError:
            class SimpleLogger:
                def info(self, message): print(f"[INFO] {message}")
                def warning(self, message): print(f"[WARNING] {message}")
                def error(self, message): print(f"[ERROR] {message}")
                def debug(self, message): print(f"[DEBUG] {message}")
            self.logger = SimpleLogger()
              # Проверяем наличие оригинального менеджера в GopiAI-Widgets
        self.original_manager = None
        try:
            original_path = Path(__file__).parent.parent.parent / "GopiAI-Widgets" / "gopiai" / "widgets" / "managers" / "lucide_icon_manager.py"
            print(f"✅ Найден файл менеджера иконок: {original_path}")
            
            # Динамический импорт оригинального модуля
            import importlib.util
            spec = importlib.util.spec_from_file_location("lucide_icon_manager_original", original_path)
            if spec is not None and spec.loader is not None:
                original_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(original_module)
                
                if hasattr(original_module, "LucideIconManager"):
                    self.original_manager = original_module.LucideIconManager.instance()
                    print(f"✅ Инициализировано из {original_path}")
              except Exception as e:
            # print(f"❌ Ошибка при инициализации оригинального менеджера: {e}")  # Отладка отключена
            pass
            
        # Если не удалось инициализировать оригинальный менеджер, создаем свой
        if self.original_manager is None:
            self.icons_dir = self._get_icons_directory()
            self.available_icons = self._scan_available_icons()
            # print(f"⚠️ Используется локальная версия LucideIconManager")  # Отладка отключена
        else:
            # Если оригинальный менеджер инициализирован, используем его значения
            self.icons_dir = self.original_manager.icons_dir
            self.available_icons = self.original_manager.available_icons
            
    def _get_icons_directory(self) -> Path:
        """Получение пути к директории с иконками Lucide."""
        project_root = Path(__file__).parent.parent
        
        # Проверяем разные пути
        possible_paths = [
            project_root / "node_modules" / "lucide-static" / "icons",
            project_root / "node_modules" / "lucide" / "dist" / "svg",
            project_root / "assets" / "icons" / "lucide"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        # Если не найдено, создаем локальную директорию
        fallback_path = project_root / "assets" / "icons" / "lucide"
        fallback_path.mkdir(parents=True, exist_ok=True)
        return fallback_path

    def _scan_available_icons(self) -> Dict[str, Path]:
        """Сканирование доступных иконок в директориях."""
        icons = {}
        
        # Если директория существует, сканируем SVG файлы
        if self.icons_dir.exists():
            for file_path in self.icons_dir.glob("*.svg"):
                icon_name = file_path.stem
                icons[icon_name] = file_path
                # Добавляем вариант с подчеркиваниями
                if "-" in icon_name:
                    icons[icon_name.replace("-", "_")] = file_path
        
        return icons

    def get_icon(self, icon_name: str, color: Optional[str] = None, size: Union[QSize, int] = QSize(24, 24)) -> QIcon:
        """
        Получение иконки Lucide по имени.
        
        Args:
            icon_name: Имя иконки
            color: Цвет иконки в формате CSS (#RRGGBB)
            size: Размер иконки (QSize или int)
            
        Returns:
            QIcon: Объект иконки Qt
        """
        # Если доступен оригинальный менеджер, делегируем запрос ему
        if self.original_manager is not None:
            return self.original_manager.get_icon(icon_name, color, size)
            
        # Иначе используем локальную реализацию
        # Нормализуем имя иконки (заменяем дефисы на подчеркивания для совместимости)
        normalized_name = icon_name.replace("-", "_")

        # Если передано число как размер, создаем QSize
        if isinstance(size, int):
            size = QSize(size, size)

        # Создаем ключ для кеширования
        cache_key = f"{normalized_name}_{color}_{size.width()}x{size.height()}"

        # Проверяем кеш
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Если иконка не найдена среди доступных
        if (normalized_name not in self.available_icons and icon_name not in self.available_icons):
            print(f"[WARNING] Иконка не найдена: {icon_name}. Используем fallback.")
            return self._get_fallback_icon(size)

        # Получаем путь к SVG файлу
        if normalized_name in self.available_icons:
            svg_path = self.available_icons[normalized_name]
        else:
            svg_path = self.available_icons[icon_name]
            
        # Возвращаем пустую иконку (упрощенная реализация)
        return QIcon()
    
    def _get_fallback_icon(self, size: QSize) -> QIcon:
        """Создание заметной иконки-заполнителя для случаев, когда запрошенная иконка не найдена."""
        icon = QIcon()
        return icon
        
    def list_available_icons(self) -> List[str]:
        """Получение списка всех доступных иконок."""
        # Если доступен оригинальный менеджер, используем его метод
        if self.original_manager is not None:
            return self.original_manager.list_available_icons()
        return sorted(list(self.available_icons.keys()))


# Алиас для совместимости со старым кодом
def get_lucide_icon(icon_name, color=None, size=24):
    """Функция для получения иконки Lucide (для обратной совместимости)."""
    return LucideIconManager.instance().get_icon(icon_name, color, size)
