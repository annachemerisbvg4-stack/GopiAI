"""
File Explorer Component для GopiAI Standalone Interface
====================================================

Проводник файлов с деревом папок.
"""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QFileSystemModel


class FileExplorerWidget(QWidget):
    """Проводник файлов с деревом папок"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fileExplorer")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса проводника"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Заголовок
        header = QLabel("📁 Проводник")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Дерево файлов
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.tree_view.setModel(self.file_model)
        
        # Настройка отображения
        self.tree_view.setRootIndex(self.file_model.index(os.path.expanduser("~")))
        self.tree_view.hideColumn(1)  # Размер
        self.tree_view.hideColumn(2)  # Тип
        self.tree_view.hideColumn(3)  # Дата изменения
        
        layout.addWidget(self.tree_view)

    def set_root_path(self, path: str):
        """Установка корневого пути для проводника"""
        if os.path.exists(path):
            self.tree_view.setRootIndex(self.file_model.index(path))
        else:
            print(f"⚠️ Путь не существует: {path}")

    def get_selected_file(self) -> str:
        """Получение выбранного файла"""
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            return self.file_model.filePath(indexes[0])
        return ""
