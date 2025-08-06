"""
Edit Actions Mixin for MainWindow.

This module contains methods related to editing operations in the MainWindow class.
"""

from typing import Optional, Callable, Any, Protocol, runtime_checkable

try:
    # Local logging helper (may be vendored in this repo)
    from gopiai.core.logging import get_logger  # type: ignore[reportMissingImports]
except Exception:  # Fallback if import path differs in this package layout
    # Fallback to a minimal logger if package path differs or unavailable
    import logging
    def get_logger():  # type: ignore[misc]
        class _Wrap:
            logger = logging.getLogger("gopiai.widgets.edit_actions")
        return _Wrap()

logger = get_logger().logger

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from PySide6.QtGui import QCursor
from PySide6.QtCore import QPoint
from gopiai.widgets.i18n.translator import tr  # type: ignore[reportMissingImports]

# remove duplicate reassignment that confused type checker
# logger = get_logger().logger


@runtime_checkable
class _HasSimpleEdit(Protocol):
    def cut(self) -> None: ...
    def copy(self) -> None: ...
    def paste(self) -> None: ...
    def undo(self) -> None: ...
    def redo(self) -> None: ...
    def selectAll(self) -> None: ...


class EditActionsMixin:
    """Provides editing operations functionality for MainWindow."""

    def _on_cut(self):
        """Вырезает выделенный текст."""
        logger.info("Action: Cut")

        # Находим активный виджет, который может поддерживать вырезание
        focused_widget: Optional[QWidget] = QApplication.focusWidget()
        if focused_widget is not None:
            method = getattr(focused_widget, "cut", None)
            if callable(method):
                method()
                logger.info("Cut performed on focused widget")
            else:
                logger.warning("No widget with cut() method is focused")
        else:
            logger.warning("No widget is focused")

    def _on_copy(self):
        """Копирует выделенный текст."""
        logger.info("Action: Copy")

        # Находим активный виджет, который может поддерживать копирование
        focused_widget: Optional[QWidget] = QApplication.focusWidget()
        if focused_widget is not None:
            method = getattr(focused_widget, "copy", None)
            if callable(method):
                method()
                logger.info("Copy performed on focused widget")
            else:
                logger.warning("No widget with copy() method is focused")
        else:
            logger.warning("No widget is focused")

    def _on_paste(self):
        """Вставляет текст из буфера обмена."""
        logger.info("Action: Paste")

        # Находим активный виджет, который может поддерживать вставку
        focused_widget: Optional[QWidget] = QApplication.focusWidget()
        if focused_widget is not None:
            method = getattr(focused_widget, "paste", None)
            if callable(method):
                method()
                logger.info("Paste performed on focused widget")
            else:
                logger.warning("No widget with paste() method is focused")
        else:
            logger.warning("No widget is focused")

    def _on_undo(self):
        """Отменяет последнее действие."""
        logger.info("Action: Undo")

        # Находим активный виджет, который может поддерживать отмену
        focused_widget: Optional[QWidget] = QApplication.focusWidget()
        if focused_widget is not None:
            method = getattr(focused_widget, "undo", None)
            if callable(method):
                method()
                logger.info("Undo performed on focused widget")
            else:
                logger.warning("No widget with undo() method is focused")
        else:
            logger.warning("No widget is focused")

    def _on_redo(self):
        """Повторяет отмененное действие."""
        logger.info("Action: Redo")

        # Находим активный виджет, который может поддерживать повтор
        focused_widget: Optional[QWidget] = QApplication.focusWidget()
        if focused_widget is not None:
            method = getattr(focused_widget, "redo", None)
            if callable(method):
                method()
                logger.info("Redo performed on focused widget")
            else:
                logger.warning("No widget with redo() method is focused")
        else:
            logger.warning("No widget is focused")

    def _on_select_all(self):
        """Выделяет весь текст."""
        logger.info("Action: Select All")

        # Находим активный виджет, который может поддерживать выделение всего
        focused_widget: Optional[QWidget] = QApplication.focusWidget()
        if focused_widget is not None:
            method = getattr(focused_widget, "selectAll", None)
            if callable(method):
                method()
                logger.info("Select All performed on focused widget")
            else:
                logger.warning("No widget with selectAll() method is focused")
        else:
            logger.warning("No widget is focused")

    def _show_emoji_dialog(self, position=None):
        """Показывает диалог выбора эмодзи.

        Args:
            position (QPoint, optional): Позиция для отображения диалога. Если None,
                                         используется текущая позиция курсора.
        """
        logger.info("Action: Show Emoji Dialog")

        try:
            from gopiai.widgets.emoji_dialog import EmojiDialog  # type: ignore[reportMissingImports]

            # Создаем диалог эмодзи
            dialog = EmojiDialog(self)  # type: ignore[arg-type]

            # Подключаем сигнал для вставки эмодзи
            dialog.emoji_selected.connect(self._insert_emoji)

            # Получаем текущую позицию курсора, если не передана
            if not position:
                position = QCursor.pos()

            # Проверяем тип позиции и преобразуем при необходимости
            if position and not isinstance(position, QPoint):
                logger.warning(f"Converting position {position} to QPoint")
                position = QCursor.pos()

            dialog_size = dialog.sizeHint()
            screen_geometry = QApplication.primaryScreen().geometry()

            # Расчитываем позицию так, чтобы диалог не выходил за пределы экрана
            x = min(position.x(), screen_geometry.width() - dialog_size.width())
            y = min(position.y(), screen_geometry.height() - dialog_size.height())

            dialog.move(x, y)
            logger.info(f"Positioned emoji dialog at {x},{y}")

            # Показываем диалог
            from PySide6.QtWidgets import QDialog

            result = dialog.exec()
            logger.info(f"Emoji dialog result: {result}")

            # PySide6 returns int for exec(); Accepted is an int constant
            return result == int(QDialog.Accepted)  # type: ignore[reportAttributeAccessIssue]
        except ImportError:
            logger.error("Could not import emoji_dialog module.")
            QMessageBox.warning(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.error", "Error"),
                tr("dialog.emoji.import_error", "Could not load emoji dialog."),
            )
            return False
        except Exception as e:
            logger.error(f"Error showing emoji dialog: {e}", exc_info=True)
            QMessageBox.warning(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.error", "Error"),
                tr("dialog.emoji.error", f"Error showing emoji dialog: {str(e)}"),
            )
            return False

    def _insert_emoji(self, emoji):
        """Вставляет эмодзи в текущий активный редактор.

        Args:
            emoji (str): Эмодзи для вставки.
        """
        logger.info(f"Inserting emoji: {emoji}")

        # Получаем активный виджет
        focused_widget: Optional[QWidget] = QApplication.focusWidget()

        # Проверяем, есть ли активный виджет
        if not focused_widget:
            logger.warning("Could not insert emoji: no widget is focused")
            QMessageBox.warning(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.warning", "Warning"),
                tr(
                    "dialog.emoji.no_focus",
                    "No text field is focused. Please click in a text field first.",
                ),
            )
            return False

        # Пытаемся вставить эмодзи в зависимости от типа виджета
        inserted = False

        # Для QLineEdit и подобных виджетов с методами text(), cursorPosition() и setCursorPosition()
        if focused_widget is not None and (
            hasattr(focused_widget, "text")
            and callable(getattr(focused_widget, "text", None))
            and hasattr(focused_widget, "cursorPosition")
            and callable(getattr(focused_widget, "cursorPosition", None))
            and hasattr(focused_widget, "setText")
            and callable(getattr(focused_widget, "setText", None))
            and hasattr(focused_widget, "setCursorPosition")
            and callable(getattr(focused_widget, "setCursorPosition", None))
        ):

            current_text = getattr(focused_widget, "text")()
            current_pos = getattr(focused_widget, "cursorPosition")()

            # Вставляем эмодзи в текущую позицию курсора
            # Guard slicing types for type checker
            try:
                new_text = str(current_text)[: int(current_pos)] + str(emoji) + str(current_text)[int(current_pos) :]
            except Exception:
                new_text = f"{current_text}{emoji}"

            getattr(focused_widget, "setText")(new_text)

            # Перемещаем курсор после вставленного эмодзи
            try:
                getattr(focused_widget, "setCursorPosition")(int(current_pos) + len(str(emoji)))
            except Exception:
                pass

            inserted = True
            logger.info(
                f"Emoji {emoji} inserted into QLineEdit widget at position {current_pos}"
            )

        # Для текстовых редакторов (QTextEdit, QPlainTextEdit)
        elif focused_widget is not None and hasattr(focused_widget, "insertPlainText") and callable(
            getattr(focused_widget, "insertPlainText", None)
        ):
            getattr(focused_widget, "insertPlainText")(str(emoji))
            inserted = True
            logger.info(f"Emoji {emoji} inserted into text editor widget")

        # Если не удалось вставить эмодзи
        if not inserted:
            logger.warning(
                f"Could not insert emoji: unsupported widget type {type(focused_widget).__name__}"
            )
            QMessageBox.warning(
                getattr(self, "parent", None),  # type: ignore[arg-type]
                tr("dialog.warning", "Warning"),
                tr(
                    "dialog.emoji.unsupported",
                    "Could not insert emoji: the focused control does not support text input.",
                ),
            )
            return False

        # Возвращаем фокус на виджет
        focused_widget.setFocus()
        return True
