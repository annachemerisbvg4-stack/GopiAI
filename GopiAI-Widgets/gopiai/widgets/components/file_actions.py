"""
File Actions Mixin for MainWindow.

This module contains methods related to file operations in the MainWindow class.
"""

# Robust logger import with fallback to avoid Pyright import errors
try:
    from gopiai.core.logging import get_logger  # type: ignore[reportMissingImports]
except Exception:
    import logging
    def get_logger():  # type: ignore[misc]
        class _Wrap:
            logger = logging.getLogger("gopiai.widgets.file_actions")
        return _Wrap()

logger = get_logger().logger

import os

from typing import Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget
from gopiai.widgets.i18n.translator import tr  # type: ignore[reportMissingImports]


from typing import Protocol, runtime_checkable, Any

@runtime_checkable
class _HasCentralTabs(Protocol):
    central_tabs: Any  # QWidget-like tab container

@runtime_checkable
class _HasCentralWidgetEditor(Protocol):
    central_widget: Any  # object with 'editor' attribute

class FileActionsMixin:
    """Provides file operations functionality for MainWindow."""

    def _new_file(self):
        """Создает новый файл."""
        logger.info("Action: New File - creating new file")

        try:
            # Если есть центральные табы, добавляем новую вкладку
            if isinstance(self, _HasCentralTabs) or hasattr(self, "central_tabs"):
                try:
                    from gopiai.widgets.editor import CodeEditor  # type: ignore[reportMissingImports]
                except Exception:
                    CodeEditor = None  # type: ignore[misc,assignment]

                logger.info("Creating new CodeEditor instance")

                if CodeEditor is None:
                    raise ImportError("gopiai.widgets.editor.CodeEditor not available")

                editor = CodeEditor(self)  # type: ignore[operator]

                # Используем метод set_new_file
                logger.info("Calling set_new_file on editor")
                editor.set_new_file()

                logger.info("Adding new tab to central_tabs")
                tab_index = self.central_tabs.addTab(editor, "Untitled")  # type: ignore[reportAttributeAccessIssue]
                self.central_tabs.setCurrentWidget(editor)  # type: ignore[reportAttributeAccessIssue]
                logger.info(f"New file tab created at index {tab_index}")

                # Активируем новый редактор
                editor.setFocus()
                logger.info("Focus set to new editor")

                return editor
            else:
                logger.error("Cannot create new file: central_tabs not found")
                QMessageBox.warning(
                    getattr(self, "parent", None),  # type: ignore[arg-type]
                    tr("dialog.error", "Error"),
                    tr(
                        "dialog.central_tabs_not_found",
                        "Cannot create new file: tab container not found",
                    ),
                )
        except Exception as e:
            logger.error(f"Error creating new file: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.error", "Error"),
                tr(
                    "dialog.error_creating_file", "Error creating new file: {error}"
                ).format(error=str(e)),
            )

    def _open_file(self, file_path=None):
        """Открывает файл."""
        logger.info(f"Action: Open File {file_path}")

        # Если путь к файлу не указан, показываем диалог выбора файла
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.open_file", "Open File"),
                "",
                tr(
                    "dialog.file_filter",
                    "All Files (*);;Text Files (*.txt);;Python Files (*.py)",
                ),
            )
            logger.info(f"User selected file: {file_path}")

        if not file_path:
            logger.info("No file path provided or user cancelled the dialog")
            return

        if not os.path.isfile(file_path):
            logger.error(
                f"Cannot open {file_path}: file does not exist or is not a file"
            )
            QMessageBox.warning(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.error", "Error"),
                tr("dialog.file_not_found", "File not found: {path}").format(
                    path=file_path
                ),
            )
            return

        # Проверяем, есть ли у нас виджет MultiEditorWidget для открытия файла
        multi_editor = None  # type: ignore[assignment]
        if isinstance(self, _HasCentralWidgetEditor) or (hasattr(self, "central_widget") and hasattr(self.central_widget, "editor")):  # type: ignore[attr-defined]
            multi_editor = self.central_widget.editor  # type: ignore[assignment,attr-defined]
            logger.info("Using MultiEditorWidget for file opening")

        # Если есть многоредакторный виджет, используем его
        if multi_editor and hasattr(multi_editor, "add_new_tab"):
            # Проверяем, может файл уже открыт
            if (
                hasattr(multi_editor, "open_files")
                and file_path in multi_editor.open_files
            ):
                # Переключаемся на вкладку с уже открытым файлом
                editor = multi_editor.open_files[file_path]
                index = multi_editor.tabs.indexOf(editor)
                if index >= 0:
                    multi_editor.tabs.setCurrentIndex(index)
                    logger.info(
                        f"File already open in MultiEditorWidget, switching to tab {index}"
                    )
                    return
                else:
                    logger.warning(
                        f"File {file_path} marked as open but tab not found in MultiEditorWidget"
                    )

            # Открываем новую вкладку в MultiEditorWidget
            logger.info(f"Opening file in MultiEditorWidget: {file_path}")
            multi_editor.add_new_tab(file_path)
            return

        # Если у нас нет MultiEditorWidget, используем обычные табы
        if isinstance(self, _HasCentralTabs) or hasattr(self, "central_tabs"):
            # Попробуем найти, открыт ли уже этот файл
            tabs = getattr(self, "central_tabs", None)  # type: ignore[assignment]
            if tabs is not None:
                for i in range(tabs.count()):  # type: ignore[reportAttributeAccessIssue]
                    widget = tabs.widget(i)  # type: ignore[reportAttributeAccessIssue]
                    if hasattr(widget, "file_path") and getattr(widget, "file_path") == file_path:
                        tabs.setCurrentIndex(i)  # type: ignore[reportAttributeAccessIssue]
                        logger.info(
                            f"File already open in central_tabs, switching to tab {i}"
                        )
                        return

            # Файл не открыт, создаем новую вкладку
            try:
                try:
                    from gopiai.widgets.editor import CodeEditor  # type: ignore[reportMissingImports]
                except Exception:
                    CodeEditor = None  # type: ignore[misc,assignment]

                if CodeEditor is None:
                    raise ImportError("gopiai.widgets.editor.CodeEditor not available")

                editor = CodeEditor(self)  # type: ignore[operator]
                editor.open_file(file_path)
                filename = os.path.basename(file_path)
                index = self.central_tabs.addTab(editor, filename)  # type: ignore[reportAttributeAccessIssue]
                self.central_tabs.setCurrentWidget(editor)  # type: ignore[reportAttributeAccessIssue]
                logger.info(f"File opened in a new tab: {file_path}")
                return
            except Exception as e:
                logger.error(f"Error creating editor for file: {e}")
                import traceback

                logger.debug(traceback.format_exc())
                QMessageBox.critical(
                    getattr(self, "parent", None),  # type: ignore[arg-type]
                    tr("dialog.error", "Error"),
                    tr(
                        "dialog.error_opening_file", "Error opening file: {error}"
                    ).format(error=str(e)),
                )
                return

        logger.error(
            "Cannot open file: no suitable editor found (neither MultiEditorWidget nor central_tabs)"
        )
        QMessageBox.critical(
            getattr(self, "parent", None),  # type: ignore[arg-type]
            tr("dialog.error", "Error"),
            tr("dialog.error_no_editor", "Cannot open file: no suitable editor found"),
        )

    def _save_file(self):
        """Сохраняет текущий файл."""
        logger.info("Action: Save File")

        if isinstance(self, _HasCentralTabs) or hasattr(self, "central_tabs"):
            current_widget = self.central_tabs.currentWidget()  # type: ignore[reportAttributeAccessIssue]
            if current_widget and hasattr(current_widget, "save_file"):
                current_widget.save_file()
                logger.info("File saved")
            else:
                logger.warning("Current widget does not support saving")
        else:
            logger.error("Cannot save file: central_tabs not found")

    def _save_file_as(self):
        """Сохраняет файл под новым именем."""
        logger.info("Action: Save File As")

        if isinstance(self, _HasCentralTabs) or hasattr(self, "central_tabs"):
            current_widget = self.central_tabs.currentWidget()  # type: ignore[reportAttributeAccessIssue]
            if current_widget and hasattr(current_widget, "save_file_as"):
                current_widget.save_file_as()
                # Обновляем заголовок вкладки, если имя файла изменилось
                if hasattr(current_widget, "file_path"):
                    filename = os.path.basename(current_widget.file_path)
                    self.central_tabs.setTabText(  # type: ignore[reportAttributeAccessIssue]
                        self.central_tabs.currentIndex(), filename  # type: ignore[reportAttributeAccessIssue]
                    )
                logger.info("File saved as new name")
            else:
                logger.warning("Current widget does not support 'save as'")
        else:
            logger.error("Cannot save file: central_tabs not found")
