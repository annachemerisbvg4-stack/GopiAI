"""
Custom File System Model с поддержкой иконок
===========================================

Кастомная модель файловой системы для отображения иконок файлов разных типов.
"""

import os
from typing import Optional, Any
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen
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
                cached_icon = self._icon_cache[file_path]
                if cached_icon is not None:
                    return cached_icon
                else:
                    # Если в кэше None, используем системную иконку
                    return super().data(index, role)
            
            # Получаем кастомную иконку для файла
            icon = self._get_file_icon(file_path)
            
            # Кэшируем иконку (включая None)
            self._icon_cache[file_path] = icon
            
            # Если иконка найдена, возвращаем её, иначе используем системную
            if icon is not None:
                return icon
            else:
                return super().data(index, role)
        
        # Для остальных ролей используем базовую реализацию
        return super().data(index, role)
    
    def _get_file_icon(self, file_path: str) -> Optional[QIcon]:
        """Получает кастомную иконку для файла"""
        try:
            # Определяем тип файла и иконку
            icon_name = FileTypeDetector.get_icon_for_file(file_path)
            
            # Сначала пробуем загрузить SVG иконку из assets/icons/lucide
            svg_icon = self._load_svg_icon(icon_name)
            if svg_icon and not svg_icon.isNull():
                return svg_icon
            
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
            
            # Если кастомная иконка недоступна, создаём детальную иконку
            return self._create_detailed_icon(file_path)
            
        except Exception as e:
            print(f"⚠️ Ошибка создания иконки для {file_path}: {e}")
            return None
    
    def _load_svg_icon(self, icon_name: str) -> Optional[QIcon]:
        """Загружает SVG иконку из директории assets/icons/lucide"""
        try:
            # Путь к SVG файлу
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            svg_path = os.path.join(base_dir, "assets", "icons", "lucide", f"{icon_name}.svg")
            
            if os.path.exists(svg_path):
                icon = QIcon(svg_path)
                if not icon.isNull():
                    return icon
                    
        except Exception as e:
            pass  # Просто игнорируем ошибки загрузки SVG
            
        return None
    
    def _create_detailed_icon(self, file_path: str) -> QIcon:
        """Создаёт детальную иконку для типа файла"""
        try:
            # Получаем тип файла
            file_type = FileTypeDetector.get_file_type(file_path)
            
            # Создаём иконку 16x16
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            if os.path.isdir(file_path):
                # Рисуем папку
                self._draw_folder_icon(painter)
            else:
                # Рисуем файл по типу
                self._draw_file_icon(painter, file_type)
            
            painter.end()
            
            return QIcon(pixmap)
            
        except Exception as e:
            print(f"⚠️ Ошибка создания детальной иконки: {e}")
            return QIcon()  # Пустая иконка
    
    def _draw_folder_icon(self, painter: QPainter):
        """Рисует иконку папки"""
        # Цвет папки
        folder_color = QColor(255, 193, 7)  # Жёлтый
        
        # Основная часть папки
        painter.fillRect(2, 6, 12, 8, folder_color)
        
        # Вкладка папки
        painter.fillRect(2, 4, 6, 3, folder_color.lighter(120))
        
        # Тень
        painter.setPen(QPen(folder_color.darker(150), 1))
        painter.drawRect(2, 6, 12, 8)
    
    def _draw_file_icon(self, painter: QPainter, file_type: str):
        """Рисует иконку файла по типу"""
        # Цвета для разных типов файлов
        type_colors = {
            'image': QColor(76, 175, 80),      # Зелёный
            'document': QColor(33, 150, 243),  # Синий
            'text': QColor(96, 125, 139),      # Серый
            'spreadsheet': QColor(76, 175, 80), # Зелёный
            'presentation': QColor(255, 152, 0), # Оранжевый
            'code': QColor(156, 39, 176),      # Фиолетовый
            'archive': QColor(121, 85, 72),    # Коричневый
            'audio': QColor(233, 30, 99),      # Розовый
            'video': QColor(244, 67, 54),      # Красный
            'executable': QColor(255, 87, 34), # Красно-оранжевый
            'system': QColor(158, 158, 158),   # Серый
            'config': QColor(255, 193, 7),     # Жёлтый
            'font': QColor(63, 81, 181),       # Индиго
            'database': QColor(139, 195, 74),  # Светло-зелёный
            'markdown': QColor(96, 125, 139),  # Серый
            'log': QColor(158, 158, 158),      # Серый
            'readme': QColor(3, 169, 244),     # Голубой
            'docker': QColor(33, 150, 243),    # Синий
            'git': QColor(255, 152, 0),        # Оранжевый
            'package': QColor(121, 85, 72),    # Коричневый
            'python-package': QColor(76, 175, 80), # Зелёный
            'makefile': QColor(255, 87, 34),   # Красно-оранжевый
            'hidden': QColor(158, 158, 158),   # Серый
            'file': QColor(96, 125, 139),      # Серый по умолчанию
        }
        
        # Выбираем цвет
        color = type_colors.get(file_type, QColor(96, 125, 139))
        
        # Основной документ
        painter.fillRect(3, 2, 9, 12, color)
        
        # Загнутый уголок
        painter.fillRect(12, 2, 2, 3, color.darker(150))
        painter.fillRect(10, 4, 2, 1, color.darker(150))
        
        # Рамка
        painter.setPen(QPen(color.darker(150), 1))
        painter.drawRect(3, 2, 9, 12)
        
        # Добавляем символ для типа файла
        self._draw_file_type_symbol(painter, file_type, color)
    
    def _draw_file_type_symbol(self, painter: QPainter, file_type: str, base_color: QColor):
        """Рисует символ типа файла"""
        painter.setPen(QPen(base_color.darker(200), 1))
        font = QFont()
        font.setPixelSize(8)
        painter.setFont(font)
        
        # Символы для разных типов
        symbols = {
            'image': '🖼',
            'document': 'DOC',
            'text': 'TXT',
            'spreadsheet': 'XLS',
            'presentation': 'PPT',
            'code': '</>', 
            'archive': 'ZIP',
            'audio': '♪',
            'video': '▶',
            'executable': 'EXE',
            'database': 'DB',
            'markdown': 'MD',
            'python-package': 'PY',
        }
        
        symbol = symbols.get(file_type, '')
        if symbol and len(symbol) <= 3:  # Только короткие символы
            painter.drawText(4, 10, symbol)
    
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
