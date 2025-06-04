"""
Custom File System Model с поддержкой иконок
===========================================

Кастомная модель файловой системы для отображения иконок файлов разных типов.
"""

import os
from typing import Optional, Any
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFileSystemModel
from .file_type_detector import FileTypeDetector


class IconFileSystemModel(QFileSystemModel):
    """Модель файловой системы с поддержкой кастомных иконок"""
    
    def __init__(self, icon_manager=None, parent=None):
        super().__init__(parent)
        self.icon_manager = icon_manager
        self._icon_cache = {}  # Кэш для иконок
        
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Переопределяем получение данных для добавления кастомных иконок"""
        
        if role == Qt.ItemDataRole.DecorationRole:
            # Получаем путь к файлу
            file_path = self.filePath(index)
            
            # Проверяем кэш
            if file_path in self._icon_cache:
                return self._icon_cache[file_path]
            
            # Получаем иконку для файла
            icon = self._get_file_icon(file_path)
            
            # Кэшируем иконку
            if icon is not None:
                self._icon_cache[file_path] = icon
            
            return icon
        
        # Для остальных ролей используем базовую реализацию
        return super().data(index, role)
    
    def _get_file_icon(self, file_path: str) -> Optional[QIcon]:
        """Получает иконку для файла"""
        try:
            # Определяем тип файла и иконку
            icon_name = FileTypeDetector.get_icon_for_file(file_path)
            
            # Если есть менеджер иконок, используем его
            if self.icon_manager:
                try:
                    # Пробуем получить иконку из менеджера
                    if hasattr(self.icon_manager, 'get_icon'):
                        icon = self.icon_manager.get_icon(icon_name)
                        if icon and not icon.isNull():
                            return icon
                    elif hasattr(self.icon_manager, 'create_icon'):
                        pixmap = self.icon_manager.create_icon(icon_name, size=16)
                        if pixmap and not pixmap.isNull():
                            return QIcon(pixmap)
                except Exception as e:
                    print(f"⚠️ Ошибка получения иконки {icon_name}: {e}")
            
            # Fallback: возвращаем None для использования системных иконок
            return None
            
        except Exception as e:
            print(f"⚠️ Ошибка создания иконки для {file_path}: {e}")
            return None
    
    def set_icon_manager(self, icon_manager):
        """Устанавливает менеджер иконок"""
        self.icon_manager = icon_manager
        # Очищаем кэш при смене менеджера
        self._icon_cache.clear()
        # Обновляем модель
        self.layoutChanged.emit()
    
    def clear_icon_cache(self):
        """Очищает кэш иконок"""
        self._icon_cache.clear()
        self.layoutChanged.emit()
