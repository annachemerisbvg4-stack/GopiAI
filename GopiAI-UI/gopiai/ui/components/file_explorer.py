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
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QHBoxLayout, QPushButton, QLineEdit, QHeaderView
from PySide6.QtCore import QDir, Signal, Qt, QSize
from PySide6.QtWidgets import QFileSystemModel
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
        
        # Дерево файлов
        self.tree_view = QTreeView(self)
        self.tree_view.setObjectName("fileTreeView")
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setItemsExpandable(True)
        self.tree_view.setExpandsOnDoubleClick(True)
        
        # Отключаем горизонтальный скроллбар
        self.tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(self.tree_view)
          # Установка модели файловой системы
        self.model = QFileSystemModel()
        if self.icon_manager:
            self.model.iconProvider = self.icon_manager
        self.model.setRootPath(QDir.rootPath())
        self.tree_view.setModel(self.model)
        
        # Установка корневого индекса
        self.tree_view.setRootIndex(self.model.index(self._current_path))
        
        # Настройка размеров колонок
        header = self.tree_view.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.setColumnWidth(0, 200)  # Имя файла
        for column in range(1, self.model.columnCount()):
            header.hideSection(column)  # Скрываем все колонки, кроме имени файла
        
        # Сигналы изменения модели
        self.model.modelReset.connect(self._on_model_reset)
        self.model.directoryLoaded.connect(self._on_directory_loaded)
        
    def _connect_signals(self):
        """Подключение сигналов проводника"""
        if hasattr(self, 'tree_view'):
            # Сигналы дерева файлов
            self.tree_view.clicked.connect(self._handle_click)
            self.tree_view.doubleClicked.connect(self._handle_double_click)

    def _go_home(self):
        """Переход в домашнюю директорию"""
        home_path = os.path.expanduser("~")
        self._current_path = home_path
        self.path_input.setText(home_path)
        if hasattr(self, 'tree_view'):
            self.tree_view.setRootIndex(self.model.index(home_path))

    def _go_up(self):
        """Переход на уровень вверх"""
        current = self._current_path
        parent = os.path.dirname(current)
        if parent != current:  # Проверка, что мы не в корне
            self._current_path = parent
            self.path_input.setText(parent)
            if hasattr(self, 'tree_view'):
                self.tree_view.setRootIndex(self.model.index(parent))

    def _path_changed(self):
        """Обработка изменения пути"""
        new_path = self.path_input.text()
        if os.path.exists(new_path):
            self._current_path = new_path
            if hasattr(self, 'tree_view'):
                self.tree_view.setRootIndex(self.model.index(new_path))
        else:
            # Возвращаем старый путь при ошибке
            self.path_input.setText(self._current_path)

    def _handle_click(self, index):
        """Обработка клика по элементу"""
        if hasattr(self, 'model'):
            path = self.model.filePath(index)
            if os.path.isfile(path):
                self.file_selected.emit(path)

    def _handle_double_click(self, index):
        """Обработка двойного клика по элементу"""
        if hasattr(self, 'model'):
            path = self.model.filePath(index)
            if os.path.isfile(path):
                self.file_double_clicked.emit(path)
            elif os.path.isdir(path):
                self._current_path = path
                self.path_input.setText(path)

    def _on_model_reset(self):
        """Обработка сброса модели"""
        if hasattr(self, 'tree_view'):
            self.tree_view.setRootIndex(self.model.index(self._current_path))

    def _on_directory_loaded(self, path):
        """Обработка загрузки директории"""
        if path == self._current_path and hasattr(self, 'tree_view'):
            # Обновляем вид после загрузки директории
            self.tree_view.setRootIndex(self.model.index(path))
            # При необходимости раскрываем первый уровень
            self.tree_view.expandToDepth(0)
            
    def sizeHint(self):
        """Предпочтительный размер виджета"""
        return QSize(300, 600)  # Ширина: 300px, Высота: 600px
        
    def resizeEvent(self, event):
        """Обработка изменения размера виджета"""
        if not self._ignore_resize:
            try:
                super().resizeEvent(event)
                # Ограничиваем ширину tree_view
                if hasattr(self, 'tree_view'):
                    self.tree_view.setFixedWidth(self.width() - 10)  # Отступ 5px с каждой стороны
            except Exception as e:
                print(f"Ошибка при изменении размера: {e}")
        event.accept()