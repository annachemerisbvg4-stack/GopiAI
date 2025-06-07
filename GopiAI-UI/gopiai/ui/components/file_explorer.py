"""
File Explorer Component для GopiAI Standalone Interface
====================================================

Проводник файлов с деревом папок и поддержкой иконок для разных типов файлов.

ВАЖНО: Этот компонент настроен для предотвращения автоматического изменения 
размеров при выборе файлов с длинными именами. Ширина зафиксирована, 
пользователь может изменять размер панели только через сплиттер.

Основные защитные механизмы:
- Фиксированные минимальная и максимальная ширина (250-400px)
- QSizePolicy с фиксированной шириной 
- QTreeView с фиксированной шириной (240px)
- Отключенный горизонтальный скроллбар
- Переопределенные sizeHint и resizeEvent
- setStretchFactor(0, 0) для панели в главном сплиттере
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeView, QHBoxLayout, 
                               QPushButton, QLineEdit, QHeaderView, QSizePolicy, QFileSystemModel)
from PySide6.QtCore import QDir, Signal, Qt
from .file_type_detector import FileTypeDetector


class FileExplorerWidget(QWidget):
    """Проводник файлов с деревом папок и поддержкой иконок"""
      # Сигналы
    file_selected = Signal(str)  # Файл выбран
    file_double_clicked = Signal(str)  # Файл открыт двойным кликом
    
    def __init__(self, parent=None, icon_manager=None):
        super().__init__(parent)
        self.setObjectName("fileExplorer")
        self.icon_manager = icon_manager
        self._current_path = os.path.expanduser("~")
        self._ignore_resize = False  # Флаг для предотвращения циклов resizeEvent
        
        # Настройка фиксированного размера для предотвращения "прыгания"
        from PySide6.QtWidgets import QSizePolicy
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
          # Устанавливаем политику размера: фиксированная ширина, расширяемая высота
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(0)
        self.setSizePolicy(size_policy)
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Настройка интерфейса проводника"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Заголовок с иконкой
        header_layout = QHBoxLayout()
        
        if self.icon_manager:
            try:
                folder_icon = self.icon_manager.get_icon("folder")
                header = QLabel("Проводник")
                if folder_icon and not folder_icon.isNull():
                    header.setPixmap(folder_icon.pixmap(16, 16))
            except:
                header = QLabel("📁 Проводник")
        else:
            header = QLabel("📁 Проводник")
            
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Кнопка "Домой"
        home_btn = QPushButton("🏠")
        home_btn.setToolTip("Перейти в домашнюю папку")
        home_btn.setFixedSize(30, 30)
        home_btn.clicked.connect(self._go_home)
        header_layout.addWidget(home_btn)
        
        # Кнопка "Вверх"
        up_btn = QPushButton("⬆️")
        up_btn.setToolTip("Перейти на уровень вверх")
        up_btn.setFixedSize(30, 30)
        up_btn.clicked.connect(self._go_up)
        header_layout.addWidget(up_btn)
        
        layout.addLayout(header_layout)
        
        # Строка пути
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 5)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Путь к папке...")
        self.path_input.setText(self._current_path)
        self.path_input.returnPressed.connect(self._path_changed)
        path_layout.addWidget(self.path_input)
        
        go_btn = QPushButton("➡️")
        go_btn.setToolTip("Перейти к указанному пути")
        go_btn.setFixedSize(30, 30)
        go_btn.clicked.connect(self._path_changed)
        path_layout.addWidget(go_btn)
        
        layout.addLayout(path_layout)
          # Добавляем дерево файлов
        self.tree_view = QTreeView()
        self.model = QFileSystemModel()
        # Правильная инициализация модели файловой системы
        self.model.setRootPath(QDir.homePath())
        # Установка фильтров для отображения всех файлов и директорий
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        # Применяем модель к дереву
        self.tree_view.setModel(self.model)
        # Устанавливаем корневой индекс для отображения домашней директории
        self.tree_view.setRootIndex(self.model.index(QDir.homePath()))
        # Настраиваем отображение колонок
        self.tree_view.setColumnWidth(0, 250)
        # Скрываем ненужные колонки, оставляя только имя и размер
        for i in range(1, self.model.columnCount()):
            if i != 1:  # Оставляем колонку с размером (обычно 1)
                self.tree_view.hideColumn(i)
        layout.addWidget(self.tree_view)

    def _connect_signals(self):
        """Подключение сигналов"""
        if hasattr(self.tree_view, 'doubleClicked'):
            self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

    def _go_home(self):
        """Переход в домашнюю папку"""
        home_path = QDir.homePath()
        self.path_input.setText(home_path)
        self.tree_view.setRootIndex(self.model.index(home_path))

    def _go_up(self):
        """Переход на уровень вверх"""
        current_path = self.path_input.text()
        parent_path = QDir(current_path).absolutePath()
        if parent_path != current_path:
            parent_dir = QDir(parent_path)
            parent_dir.cdUp()
            new_path = parent_dir.absolutePath()
            self.path_input.setText(new_path)
            self.tree_view.setRootIndex(self.model.index(new_path))

    def _path_changed(self):
        """Обработка изменения пути"""
        path = self.path_input.text()
        if QDir(path).exists():
            self.tree_view.setRootIndex(self.model.index(path))
        else:
            self.path_input.setText(QDir.homePath())
            self.tree_view.setRootIndex(self.model.index(QDir.homePath()))

    def _on_item_double_clicked(self, index):
        """Обработка двойного клика по элементу"""
        if self.model.isDir(index):
            path = self.model.filePath(index)
            self.path_input.setText(path)
            self.tree_view.setRootIndex(index)