"""
File Explorer Component для GopiAI Standalone Interface
====================================================

Проводник файлов с деревом папок и поддержкой иконок для разных типов файлов.
"""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import QDir, Signal, Qt
from .icon_file_system_model import IconFileSystemModel
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
        
        # Дерево файлов с кастомной моделью
        self.tree_view = QTreeView()
        self.file_model = IconFileSystemModel(self.icon_manager, self)
        self.file_model.setRootPath("")
        self.tree_view.setModel(self.file_model)
        
        # Настройка отображения
        self.tree_view.setRootIndex(self.file_model.index(self._current_path))
        self.tree_view.hideColumn(1)  # Размер
        self.tree_view.hideColumn(2)  # Тип
        self.tree_view.hideColumn(3)  # Дата изменения
          # Настройка поведения
        self.tree_view.setAlternatingRowColors(False)  # Отключаем полосы для тестирования
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)  # Сортировка по имени
        
        layout.addWidget(self.tree_view)
        
        # Информационная панель
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Готов")
        self.info_label.setObjectName("statusLabel")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        # Счётчик файлов
        self.file_count_label = QLabel("")
        self.file_count_label.setObjectName("statusLabel")
        info_layout.addWidget(self.file_count_label)
        
        layout.addLayout(info_layout)
        
        # Обновляем счётчик файлов
        self._update_file_count()

    def _connect_signals(self):
        """Подключение сигналов"""
        # Выбор файла
        self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        # Двойной клик
        self.tree_view.doubleClicked.connect(self._on_double_click)
        
        # Изменение папки
        self.file_model.directoryLoaded.connect(self._update_file_count)

    def _on_selection_changed(self):
        """Обработка изменения выбора"""
        selected_file = self.get_selected_file()
        if selected_file:
            # Обновляем информацию
            file_type = FileTypeDetector.get_file_type(selected_file)
            file_name = os.path.basename(selected_file)
            
            if os.path.isdir(selected_file):
                self.info_label.setText(f"📁 Папка: {file_name}")
            else:
                self.info_label.setText(f"📄 {file_type.title()}: {file_name}")
            
            # Отправляем сигнал
            self.file_selected.emit(selected_file)
        else:
            self.info_label.setText("Готов")

    def _on_double_click(self, index):
        """Обработка двойного клика"""
        file_path = self.file_model.filePath(index)
        
        if os.path.isdir(file_path):
            # Если папка - переходим в неё
            self.set_root_path(file_path)
        else:
            # Если файл - отправляем сигнал открытия
            self.file_double_clicked.emit(file_path)

    def _go_home(self):
        """Переход в домашнюю папку"""
        home_path = os.path.expanduser("~")
        self.set_root_path(home_path)

    def _go_up(self):
        """Переход на уровень вверх"""
        parent_path = os.path.dirname(self._current_path)
        if parent_path != self._current_path:  # Проверяем, что можем подняться
            self.set_root_path(parent_path)

    def _path_changed(self):
        """Обработка изменения пути"""
        new_path = self.path_input.text().strip()
        if new_path and os.path.exists(new_path) and os.path.isdir(new_path):
            self.set_root_path(new_path)
        else:
            # Возвращаем старый путь
            self.path_input.setText(self._current_path)
            self.info_label.setText("⚠️ Неверный путь")

    def _update_file_count(self):
        """Обновление счётчика файлов"""
        try:
            if os.path.exists(self._current_path):
                items = os.listdir(self._current_path)
                folders = sum(1 for item in items if os.path.isdir(os.path.join(self._current_path, item)))
                files = len(items) - folders
                self.file_count_label.setText(f"📁 {folders} | 📄 {files}")
            else:
                self.file_count_label.setText("")
        except Exception as e:
            print(f"⚠️ Ошибка подсчёта файлов: {e}")
            self.file_count_label.setText("")

    def set_root_path(self, path: str):
        """Установка корневого пути для проводника"""
        if os.path.exists(path) and os.path.isdir(path):
            self._current_path = os.path.abspath(path)
            self.tree_view.setRootIndex(self.file_model.index(self._current_path))
            self.path_input.setText(self._current_path)
            self.info_label.setText(f"📁 {os.path.basename(self._current_path)}")
            self._update_file_count()
        else:
            print(f"⚠️ Путь не существует: {path}")
            self.info_label.setText("⚠️ Путь не найден")

    def get_selected_file(self) -> str:
        """Получение выбранного файла"""
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            return self.file_model.filePath(indexes[0])
        return ""

    def set_icon_manager(self, icon_manager):
        """Установка менеджера иконок"""
        self.icon_manager = icon_manager
        if self.file_model:
            self.file_model.set_icon_manager(icon_manager)
        
        # Обновляем заголовок
        self._update_header_icon()

    def _update_header_icon(self):
        """Обновление иконки в заголовке"""
        if self.icon_manager:
            try:
                folder_icon = self.icon_manager.get_icon("folder")
                if folder_icon and not folder_icon.isNull():
                    # Найдём заголовок и обновим его иконку
                    header = self.findChild(QLabel, "panelHeader") 
                    if header:
                        header.setPixmap(folder_icon.pixmap(16, 16))
                        header.setText("Проводник")
            except Exception as e:
                print(f"⚠️ Ошибка обновления иконки заголовка: {e}")

    def refresh(self):
        """Обновление содержимого проводника"""
        if self.file_model:
            self.file_model.clear_icon_cache()
        self._update_file_count()
        self.info_label.setText("🔄 Обновлено")
