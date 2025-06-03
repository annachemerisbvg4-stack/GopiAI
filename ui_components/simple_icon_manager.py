"""
GopiAI Simple Icon Manager - Простой менеджер иконок
=================================================

Простой менеджер иконок для восстановления работы после очистки.

Автор: Crazy Coder  
Версия: 1.0.0
"""

import os
from pathlib import Path
from typing import Dict, Optional, Union, Any

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor


class SimpleIconManager:
    """Простой менеджер иконок для восстановления работы приложения"""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Синглтон экземпляр"""
        if cls._instance is None:
            cls._instance = SimpleIconManager()
        return cls._instance
    
    def __init__(self):
        """Инициализация менеджера иконок"""
        self.icon_cache = {}
        self.fallback_icons = {}
        self.lucide_manager = None
        
        # Пытаемся найти и загрузить LucideIconManager
        self._init_lucide_manager()
    
    def _init_lucide_manager(self):
        """Пытается найти и инициализировать Lucide менеджер"""
        # Список путей где может быть LucideIconManager
        paths = [
            Path(__file__).parent.parent / "GopiAI-Widgets" / "gopiai" / "widgets" / "managers" / "lucide_icon_manager.py",
            Path(__file__).parent.parent / "GopiAI-Widgets" / "gopiai" / "widgets" / "core" / "icon_adapter.py",
            Path(__file__).parent / "lucide_icon_manager.py",
        ]
        
        for path in paths:
            if path.exists():
                print(f"✅ Найден файл менеджера иконок: {path}")
                
                try:
                    # Если это файл в ui_components
                    if path.parent == Path(__file__).parent:
                        from . import lucide_icon_manager
                        if hasattr(lucide_icon_manager, "LucideIconManager"):
                            self.lucide_manager = lucide_icon_manager.LucideIconManager()
                            print("✅ Инициализировано из локального модуля")
                            break
                except ImportError as e:
                    print(f"⚠️ Ошибка импорта локального модуля: {e}")
                
                try:
                    # Если это файл в gopiai
                    if "gopiai" in str(path):
                        # Пробуем импортировать функцию из модуля
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("lucide_module", path)
                        lucide_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(lucide_module)
                        
                        if hasattr(lucide_module, "LucideIconManager"):
                            self.lucide_manager = lucide_module.LucideIconManager.instance()
                            print(f"✅ Инициализировано из {path}")
                            break
                        elif hasattr(lucide_module, "get_icon"):
                            # Это adapter
                            self.get_icon_func = lucide_module.get_icon
                            print(f"✅ Найдена функция get_icon в {path}")
                            break
                        elif hasattr(lucide_module, "get_lucide_icon"):
                            self.get_icon_func = lucide_module.get_lucide_icon
                            print(f"✅ Найдена функция get_lucide_icon в {path}")
                            break
                except Exception as e:
                    print(f"⚠️ Ошибка динамического импорта: {e}")
        
        if not self.lucide_manager and not hasattr(self, "get_icon_func"):
            print("⚠️ Не удалось инициализировать Lucide менеджер иконок")
    
    def get_icon(self, icon_name: str, color=None, size=24) -> QIcon:
        """
        Получение иконки по имени
        
        Args:
            icon_name: Имя иконки
            color: Цвет иконки (опционально)
            size: Размер иконки (QSize или int)
            
        Returns:
            QIcon: Иконка
        """
        # Нормализуем размер
        if isinstance(size, int):
            size = QSize(size, size)
            
        # Создаем ключ для кеша
        cache_key = f"{icon_name}_{color}_{size.width()}"
        
        # Проверяем кеш
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        icon = None
        
        # 1. Пытаемся получить иконку из Lucide менеджера
        if self.lucide_manager and hasattr(self.lucide_manager, "get_icon"):
            try:
                icon = self.lucide_manager.get_icon(icon_name, color, size)
            except Exception as e:
                print(f"⚠️ Ошибка получения иконки {icon_name} из Lucide: {e}")
                icon = None
        
        # 2. Пытаемся через функцию get_icon_func
        if icon is None and hasattr(self, "get_icon_func"):
            try:
                icon = self.get_icon_func(icon_name, color, size)
            except Exception as e:
                print(f"⚠️ Ошибка вызова get_icon_func для {icon_name}: {e}")
                icon = None
        
        # 3. Создаем простую иконку-заглушку
        if icon is None:
            # Создаем pixmap нужного размера
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)  # Прозрачный фон
            
            # Используем первую букву имени иконки
            painter = QPainter(pixmap)
            if icon_name:
                # Рисуем рамку
                painter.setPen(QColor(150, 150, 150))
                painter.drawRect(1, 1, size.width() - 2, size.height() - 2)
                
                # Рисуем первую букву
                if len(icon_name) > 0:
                    font = painter.font()
                    font.setPixelSize(size.width() // 2)
                    painter.setFont(font)
                    painter.drawText(
                        0, 0, size.width(), size.height(),
                        int(Qt.AlignCenter),
                        icon_name[0].upper()
                    )
            painter.end()
            
            # Создаем icon из pixmap
            icon = QIcon(pixmap)
        
        # Кешируем и возвращаем результат
        self.icon_cache[cache_key] = icon
        return icon


# Глобальная функция для использования в других модулях
def get_icon(icon_name, color=None, size=24):
    """Получить иконку из универсального менеджера"""
    return SimpleIconManager.instance().get_icon(icon_name, color, size)
