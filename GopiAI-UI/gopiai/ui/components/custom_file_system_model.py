"""
Custom File System Model с поддержкой иконок
==========================================

Кастомная модель файловой системы для интеграции с системой иконок GopiAI.
"""

from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QIcon
from .file_type_detector import FileTypeDetector


class CustomFileSystemModel(QFileSystemModel):
    """Кастомная модель файловой системы с поддержкой иконок"""
    
    def __init__(self, icon_manager=None, parent=None):
        super().__init__(parent)
        self.icon_manager = icon_manager
        self.file_type_detector = FileTypeDetector()
        
        # Кеш иконок для улучшения производительности
        self._icon_cache = {}
        
        print(f"🎨 CustomFileSystemModel инициализирована с icon_manager: {type(icon_manager)}")
    
    def data(self, index: QModelIndex, role: int):
        """Переопределенный метод для предоставления иконок"""
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            # Получаем путь к файлу
            file_path = self.filePath(index)
            
            # Проверяем кеш
            if file_path in self._icon_cache:
                return self._icon_cache[file_path]
            
            # Определяем иконку на основе типа файла
            icon = self._get_icon_for_file(file_path)
            
            # Кешируем результат
            self._icon_cache[file_path] = icon
            
            return icon
        
        # Для всех остальных ролей используем родительскую реализацию
        return super().data(index, role)
    
    def _get_icon_for_file(self, file_path: str) -> QIcon:
        """Получает иконку для файла на основе его типа"""
        if not self.icon_manager:
            # Если нет менеджера иконок, возвращаем системную иконку
            return super().data(self.index(file_path), Qt.ItemDataRole.DecorationRole) or QIcon()
        
        try:
            # Определяем иконку через детектор типов файлов
            icon_name = self.file_type_detector.get_icon_for_file(file_path)
            
            # Получаем иконку от менеджера
            icon = self.icon_manager.get_icon(icon_name)
            
            if icon and not icon.isNull():
                return icon
            else:
                # Fallback к системной иконке
                return super().data(self.index(file_path), Qt.ItemDataRole.DecorationRole) or QIcon()
                
        except Exception as e:
            print(f"⚠️ Ошибка получения иконки для {file_path}: {e}")
            # Fallback к системной иконке
            return super().data(self.index(file_path), Qt.ItemDataRole.DecorationRole) or QIcon()
    
    def clear_icon_cache(self):
        """Очищает кеш иконок"""
        self._icon_cache.clear()
        print("🔄 Кеш иконок очищен")