import os
import sys

from PySide6.QtCore import QDir, QFileInfo, QMimeData, QModelIndex, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QCursor, QDrag, QIcon, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileIconProvider,
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QTreeView,
    QVBoxLayout,
    QWidget,
)
from gopiai.core.logging import get_logger
logger = get_logger().logger  # Added import for standard logger
# from gopiai.core.logging import get_logger
logger = get_logger().logger  # Commented out until app module is available

logger = get_logger().logger  # Use standard logger for now

from ..i18n.translator import tr
# Удаляем get_icon, IconManager импортируем только для проверки типа, если нужно
from .icon_adapter import IconAdapter


class FileIconProvider(QFileIconProvider):
    """Провайдер иконок для файловой системы с поддержкой специальных типов файлов."""

    def __init__(self, icon_manager: IconAdapter):  # Принимаем icon_manager
        super().__init__()
        self.icon_manager = icon_manager

        # Словарь соответствия расширений и имен иконок
        self.extension_icon_map = {
            # Текстовые/код
            "py": "python_file",
            "js": "js_file",
            "ts": "file-code",
            "jsx": "file-code",
            "tsx": "file-code",
            "html": "html_file",
            "htm": "html_file",
            "css": "css_file",
            "scss": "css_file",
            "sass": "css_file",
            "less": "css_file",
            "json": "json",
            "xml": "file-code",
            "yml": "file-code",
            "yaml": "file-code",
            "md": "markdown",
            "txt": "text_file",
            "csv": "spreadsheet",
            "log": "text_file",
            "sql": "database",
            "sh": "terminal",
            "bat": "terminal",
            "ps1": "terminal",
            "c": "file-code",
            "cpp": "file-code",
            "h": "file-code",
            "hpp": "file-code",
            "java": "file-code",
            "php": "file-code",
            "rb": "file-code",
            "go": "file-code",
            "rs": "file-code",
            "swift": "file-code",
            "kt": "file-code",
            # Изображения
            "jpg": "image_file",
            "jpeg": "image_file",
            "png": "image_file",
            "gif": "image_file",
            "bmp": "image_file",
            "svg": "image_file",
            "ico": "image_file",
            "webp": "image_file",
            # Документы
            "doc": "document",
            "docx": "document",
            "xls": "spreadsheet",
            "xlsx": "spreadsheet",
            "ppt": "file-text",
            "pptx": "file-text",
            "pdf": "pdf",
            # Архивы
            "zip": "archive",
            "rar": "archive",
            "7z": "archive",
            "tar": "archive",
            "gz": "archive",
            "tgz": "archive",
            # Другие
            "mp3": "music",
            "wav": "music",
            "ogg": "music",
            "mp4": "video",
            "avi": "video",
            "mov": "video",
            "mkv": "video",
            "exe": "package",
            "msi": "package",
            "dll": "package",
            "so": "package",
            # Конфигурация и настройки
            "ini": "settings",
            "cfg": "settings",
            "conf": "settings",
            "gitignore": "git",
            "gitattributes": "git",
            "env": "settings",
        }

    def icon(self, fileInfo):
        """Возвращает иконку для файла."""
        # Если это QFileInfo объект, получаем информацию о файле
        if isinstance(fileInfo, QFileInfo):
            if fileInfo.isDir():
                # Для директорий используем стандартную иконку папки
                if fileInfo.fileName() == "." or fileInfo.fileName() == "..":
                    return super().icon(fileInfo)
                return self.icon_manager.get_icon("folder")

            # Получаем расширение файла
            suffix = fileInfo.suffix().lower()

            # Проверяем специальные файлы по имени (без расширения или с особым названием)
            filename = fileInfo.fileName().lower()

            # Специальная обработка git-файлов
            if filename == ".gitignore" or filename == ".gitattributes":
                return self.icon_manager.get_icon("git")

            if filename in ["makefile", "dockerfile"]:
                return self.icon_manager.get_icon("file-code")
            if filename == "readme.md":
                return self.icon_manager.get_icon("markdown")
            if filename.startswith("license"):
                return self.icon_manager.get_icon("file-text")

            # Проверяем расширение по словарю маппинга
            if suffix in self.extension_icon_map:
                return self.icon_manager.get_icon(self.extension_icon_map[suffix])

            # Для всех других типов файлов используем стандартную иконку файла
            return self.icon_manager.get_icon("file")

        # Для всех других типов используем стандартную иконку
        return super().icon(fileInfo)


class ProjectExplorer(QWidget):
    """Виджет проводника проекта с расширенной функциональностью."""

    # Сигналы
    file_double_clicked = Signal(str)  # Путь к файлу при двойном клике

    def __init__(
        self, icon_manager: IconAdapter, parent=None
    ):  # Принимаем icon_manager
        super().__init__(parent)
        self.icon_manager = icon_manager  # Сохраняем экземпляр
        self.setAcceptDrops(True)  # Разрешаем drop для drag & drop

        # Создаем layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Создаем header с выбором директории
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(2, 2, 2, 2)

        # Добавляем выпадающий список с путями
        self.path_combo = QComboBox()
        self.path_combo.setEditable(False)
        self.path_combo.currentIndexChanged.connect(self._on_path_changed)

        # Кнопка обновления
        self.refresh_label = QLabel()
        self.refresh_label.setPixmap(
            self.icon_manager.get_icon("refresh").pixmap(16, 16)
        )
        self.refresh_label.setToolTip(tr("project.refresh", "Обновить"))
        self.refresh_label.mousePressEvent = self._on_refresh_label_clicked
        self.refresh_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.header_layout.addWidget(self.path_combo, 1)  # 1 = stretch factor
        self.header_layout.addWidget(self.refresh_label)

        self.main_layout.addLayout(self.header_layout)

        # Создаем модель файловой системы
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.rootPath())
        self.fs_model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)

        # Устанавливаем провайдер иконок
        self.fs_model.setIconProvider(
            FileIconProvider(self.icon_manager)
        )  # Передаем icon_manager

        # Создаем дерево файлов
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setHeaderHidden(True)

        # Скрываем ненужные колонки, оставляем только имя
        for i in range(1, self.fs_model.columnCount()):
            self.tree_view.hideColumn(i)

        # Двойной клик на элементе
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)

        # Добавляем контекстное меню
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        # Настройка drag & drop
        self.tree_view.setDragEnabled(True)
        self.tree_view.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

        # Добавляем дерево в layout
        self.main_layout.addWidget(self.tree_view)

        # Инициализация с текущей директорией
        self._initialize_paths()

    def _initialize_paths(self):
        """Инициализирует список путей."""
        # Очищаем список
        self.path_combo.clear()

        # Получаем текущую директорию
        current_dir = os.getcwd()

        # Добавляем основные пути
        self.path_combo.addItem(
            self.icon_manager.get_icon("folder"), "Текущая директория", current_dir
        )
        self.path_combo.addItem(
            self.icon_manager.get_icon("home_folder"),
            "Домашняя директория",
            QDir.homePath(),
        )

        # Добавляем корневые диски (для Windows)
        if sys.platform == "win32":
            for drive in QDir.drives():
                drive_path = drive.absolutePath()
                self.path_combo.addItem(
                    self.icon_manager.get_icon("drive"), drive_path, drive_path
                )

        # Устанавливаем текущую директорию
        self._set_current_path(current_dir)

    def _set_current_path(self, path):
        """Устанавливает текущий путь в дереве."""
        # Устанавливаем корневой индекс
        root_index = self.fs_model.setRootPath(path)
        self.tree_view.setRootIndex(root_index)

        # Обновляем комбо-бокс, если путь не в списке
        found = False
        for i in range(self.path_combo.count()):
            if self.path_combo.itemData(i) == path:
                self.path_combo.setCurrentIndex(i)
                found = True
                break

        if not found and os.path.exists(path):
            self.path_combo.addItem(
                self.icon_manager.get_icon("folder"), os.path.basename(path), path
            )
            self.path_combo.setCurrentIndex(self.path_combo.count() - 1)

    def _on_path_changed(self, index):
        """Обработчик изменения выбранного пути."""
        if index >= 0:
            path = self.path_combo.itemData(index)
            if path and os.path.exists(path):
                self._set_current_path(path)

    def _refresh_tree(self):
        """Обновляет дерево файлов."""
        try:
            # Проверяем наличие необходимых атрибутов
            if not hasattr(self, "fs_model") or not hasattr(self, "tree_view"):
                logger.error(
                    "Не могу обновить дерево файлов: отсутствуют необходимые атрибуты"
                )
                return

            # Сохраняем текущий путь
            current_path = self.fs_model.rootPath()
            logger.info(f"Обновление дерева файлов, текущий путь: {current_path}")

            # Переустанавливаем путь для обновления
            root_index = self.fs_model.setRootPath(current_path)
            self.tree_view.setRootIndex(root_index)
            logger.info("Дерево файлов успешно обновлено")
        except Exception as e:
            logger.error(f"Ошибка при обновлении дерева файлов: {str(e)}")
            import traceback

            logger.debug(traceback.format_exc())

    def _on_item_double_clicked(self, index):
        """Обработчик двойного клика на элементе дерева."""
        # Получаем путь к файлу
        file_path = self.fs_model.filePath(index)

        # Если это директория, открываем её
        if os.path.isdir(file_path):
            self._set_current_path(file_path)
        else:
            # Если это файл, эмитируем сигнал
            self.file_double_clicked.emit(file_path)

    def _show_context_menu(self, position):
        """Показывает контекстное меню."""
        # Получаем индекс под курсором
        index = self.tree_view.indexAt(position)

        if not index.isValid():
            return

        # Получаем путь к файлу/директории
        file_path = self.fs_model.filePath(index)
        is_dir = os.path.isdir(file_path)

        # Создаем меню
        menu = QMenu()

        # Инициализируем переменные действий
        open_action = None
        new_file_action = None
        new_dir_action = None

        # Добавляем действия в зависимости от типа
        if is_dir:
            # Действия для директории
            open_action = menu.addAction(
                self.icon_manager.get_icon("folder_open"), tr("menu.open", "Открыть")
            )
            menu.addSeparator()
            new_file_action = menu.addAction(
                self.icon_manager.get_icon("file"), tr("menu.new_file", "Новый файл")
            )  # Используем file
            new_dir_action = menu.addAction(
                self.icon_manager.get_icon("folder"),
                tr("menu.new_folder", "Новая папка"),
            )  # Используем folder
        else:
            # Действия для файла
            open_action = menu.addAction(
                self.icon_manager.get_icon("file"), tr("menu.open", "Открыть")
            )  # Используем file

        menu.addSeparator()
        rename_action = menu.addAction(
            self.icon_manager.get_icon("edit"), tr("menu.rename", "Переименовать")
        )  # Используем edit
        delete_action = menu.addAction(
            self.icon_manager.get_icon("close"), tr("menu.delete", "Удалить")
        )  # Используем close

        # Выполняем меню
        action = menu.exec(self.tree_view.viewport().mapToGlobal(position))

        # Обрабатываем действия
        if action == open_action:
            self._on_item_double_clicked(index)
        elif is_dir and action == new_file_action:
            self._create_new_file(file_path)
        elif is_dir and action == new_dir_action:
            self._create_new_directory(file_path)
        elif action == rename_action:
            self._rename_item(file_path)
        elif action == delete_action:
            self._delete_item(file_path)

    def _create_new_file(self, parent_dir):
        """Создает новый файл в указанной директории."""
        file_name, ok = QInputDialog.getText(
            self,
            tr("dialog.new_file.title", "Новый файл"),
            tr("dialog.new_file.prompt", "Введите имя файла:"),
        )

        if ok and file_name:
            file_path = os.path.join(parent_dir, file_name)

            # Проверяем, существует ли файл
            if os.path.exists(file_path):
                QMessageBox.warning(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr(
                        "dialog.error.file_exists",
                        "Файл с таким именем уже существует.",
                    ),
                )
                return

            try:
                # Создаем пустой файл
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")

                # Обновляем дерево
                self._refresh_tree()

                # Эмитируем сигнал для открытия файла
                self.file_double_clicked.emit(file_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr(
                        "dialog.error.create_file", f"Не удалось создать файл: {str(e)}"
                    ),
                )

    def _create_new_directory(self, parent_dir):
        """Создает новую директорию в указанной директории."""
        dir_name, ok = QInputDialog.getText(
            self,
            tr("dialog.new_folder.title", "Новая папка"),
            tr("dialog.new_folder.prompt", "Введите имя папки:"),
        )

        if ok and dir_name:
            dir_path = os.path.join(parent_dir, dir_name)

            # Проверяем, существует ли директория
            if os.path.exists(dir_path):
                QMessageBox.warning(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr(
                        "dialog.error.dir_exists",
                        "Папка с таким именем уже существует.",
                    ),
                )
                return

            try:
                # Создаем директорию
                os.makedirs(dir_path)

                # Обновляем дерево
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr(
                        "dialog.error.create_dir", f"Не удалось создать папку: {str(e)}"
                    ),
                )

    def _rename_item(self, path):
        """Переименовывает файл или директорию."""
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(
            self,
            tr("dialog.rename.title", "Переименовать"),
            tr("dialog.rename.prompt", "Введите новое имя:"),
            text=old_name,
        )

        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)

            # Проверяем, существует ли файл/директория с таким именем
            if os.path.exists(new_path):
                QMessageBox.warning(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr(
                        "dialog.error.already_exists",
                        "Файл или папка с таким именем уже существует.",
                    ),
                )
                return

            try:
                # Переименовываем
                os.rename(path, new_path)

                # Обновляем дерево
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr("dialog.error.rename", f"Не удалось переименовать: {str(e)}"),
                )

    def _delete_item(self, path):
        """Удаляет файл или директорию."""
        is_dir = os.path.isdir(path)

        # Подтверждение удаления
        msg = (
            tr(
                "dialog.delete_dir.confirm",
                "Вы уверены, что хотите удалить папку и все её содержимое?",
            )
            if is_dir
            else tr(
                "dialog.delete_file.confirm", "Вы уверены, что хотите удалить файл?"
            )
        )

        reply = QMessageBox.question(
            self,
            tr("dialog.delete.title", "Подтверждение удаления"),
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if is_dir:
                    # Рекурсивное удаление директории
                    import shutil

                    shutil.rmtree(path)
                else:
                    # Удаление файла
                    os.remove(path)

                # Обновляем дерево
                self._refresh_tree()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr("dialog.error.title", "Ошибка"),
                    tr("dialog.error.delete", f"Не удалось удалить: {str(e)}"),
                )

    def dragEnterEvent(self, event):
        """Обработка начала drag & drop."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Обработка движения при drag & drop."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Обработка завершения drag & drop."""
        if event.mimeData().hasUrls():
            # Получаем URL'ы файлов
            urls = event.mimeData().urls()

            # Получаем текущую директорию
            current_dir = self.fs_model.rootPath()

            for url in urls:
                # Получаем локальный путь
                file_path = url.toLocalFile()

                if os.path.exists(file_path):
                    # Получаем имя файла
                    file_name = os.path.basename(file_path)

                    # Создаем путь назначения
                    dest_path = os.path.join(current_dir, file_name)

                    # Проверяем, существует ли файл/директория с таким именем
                    if os.path.exists(dest_path) and dest_path != file_path:
                        reply = QMessageBox.question(
                            self,
                            tr("dialog.copy.title", "Копирование файла"),
                            tr(
                                "dialog.copy.exists",
                                f"Файл {file_name} уже существует. Заменить?",
                            ),
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No,
                        )

                        if reply == QMessageBox.StandardButton.No:
                            continue

                    try:
                        # Копируем файл или директорию
                        if os.path.isdir(file_path):
                            import shutil

                            shutil.copytree(file_path, dest_path, dirs_exist_ok=True)
                        else:
                            import shutil

                            shutil.copy2(file_path, dest_path)
                    except Exception as e:
                        QMessageBox.critical(
                            self,
                            tr("dialog.error.title", "Ошибка"),
                            tr(
                                "dialog.error.copy", f"Не удалось скопировать: {str(e)}"
                            ),
                        )

            # Обновляем дерево
            self._refresh_tree()

            event.acceptProposedAction()

    def mousePressEvent(self, event):
        """Обработка нажатия мыши для drag & drop."""
        super().mousePressEvent(event)

    def _on_refresh_label_clicked(self, event):
        """Обрабатывает клик на кнопке обновления."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._refresh_tree()
        # Вызываем стандартный обработчик для QLabel (не ProjectExplorer)
        QLabel.mousePressEvent(self.refresh_label, event)

    def set_current_directory(self, path):
        """Устанавливает текущую директорию."""
        if os.path.isdir(path):
            self._set_current_path(path)
        elif os.path.isfile(path):
            # Если это файл, устанавливаем его директорию
            self._set_current_path(os.path.dirname(path))

    def get_current_directory(self):
        """Возвращает текущую директорию."""
        return self.fs_model.rootPath()

    def update_theme(self, theme_data=None):
        """
        Обновляет внешний вид компонента при изменении темы.

        Args:
            theme_data: Словарь с данными темы (если None, используется текущая палитра приложения)
        """
        logger.debug("Обновление темы ProjectExplorer")

        try:
            app = QApplication.instance()
            if not app or not isinstance(app, QApplication):
                logger.error("Не найден экземпляр QApplication")
                return

            # Получаем цвета из текущей палитры приложения
            palette = app.palette()
            base_color = palette.color(QPalette.ColorRole.Base)
            text_color = palette.color(QPalette.ColorRole.Text)
            highlight_color = palette.color(QPalette.ColorRole.Highlight)

            # Устанавливаем стили для tree_view
            self.tree_view.setStyleSheet(f"""
                QTreeView {{
                    background-color: {base_color.name()};
                    color: {text_color.name()};
                }}
                QTreeView::branch:selected {{
                    background-color: {highlight_color.name()};
                }}
                QTreeView::item:selected {{
                    background-color: {highlight_color.name()};
                }}
            """)

            # Обновляем стиль для выпадающего списка путей
            self.path_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {base_color.name()};
                    color: {text_color.name()};
                }}
            """)

            # Обновляем иконку обновления с учетом текущей палитры
            self.refresh_label.setPixmap(
                self.icon_manager.get_icon("refresh").pixmap(16, 16)
            )

            logger.debug("Тема ProjectExplorer успешно обновлена")
        except Exception as e:
            logger.error(f"Ошибка при обновлении темы ProjectExplorer: {e}")
