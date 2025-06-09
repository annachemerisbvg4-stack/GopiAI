import sys
import os
import chardet
from PySide6.QtCore import Qt, QSettings, QRect, QSize, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QTextFormat
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QFileDialog, QMessageBox, QPlainTextEdit, QInputDialog, QTabWidget
from gopiai.ui.utils.simple_theme_manager import load_theme # Исправленный импорт

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class NumberedTextEdit(QPlainTextEdit):
    def __init__(self, highlight_color=None, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self._highlight_color = highlight_color or QColor(127, 127, 127)  # fallback: средний серый
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(lambda rect, dy: self.update_line_number_area(rect, dy))
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(245,245,245))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(150,150,150))
                painter.drawText(0, top, self.line_number_area.width()-2, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1
    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = self._highlight_color
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.line_number_area.update()

class TextEditorWidget(QWidget):
    """Виджет для текстового редактора с нумерацией строк."""
    file_name_changed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.current_encoding = "utf-8"
        self.settings = QSettings("GopiAI", "MinimalVersion")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        theme = load_theme() or {}
        highlight_color = theme.get("border_color")
        if highlight_color:
            highlight_color = QColor(highlight_color)
        else:
            highlight_color = QColor(127, 127, 127)  # fallback: средний серый
        self.text_editor = NumberedTextEdit(highlight_color=highlight_color)
        layout.addWidget(self.text_editor)

    def open_file(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    raw = f.read()
                    import chardet
                    enc = chardet.detect(raw)['encoding']
                    tried = []
                    text = None
                    errors = []
                    # 1. chardet
                    if enc:
                        tried.append(enc)
                        try:
                            text = raw.decode(enc)
                            self.current_encoding = enc
                        except Exception as e:
                            errors.append(f"{enc}: {e}")
                            text = None
                    # 2. utf-8
                    if text is None:
                        tried.append('utf-8')
                        try:
                            text = raw.decode('utf-8')
                            self.current_encoding = 'utf-8'
                        except Exception as e:
                            errors.append(f"utf-8: {e}")
                            text = None
                    # 3. cp1251
                    if text is None:
                        tried.append('cp1251')
                        try:
                            text = raw.decode('cp1251')
                            self.current_encoding = 'cp1251'
                        except Exception as e:
                            errors.append(f"cp1251: {e}")
                            text = None
                    # 4. latin1
                    if text is None:
                        tried.append('latin1')
                        try:
                            text = raw.decode('latin1')
                            self.current_encoding = 'latin1'
                        except Exception as e:
                            errors.append(f"latin1: {e}")
                            text = None
                    # 5. Если всё не удалось — спросить у пользователя
                    if text is None:
                        encodings = ['utf-8', 'cp1251', 'latin1', 'koi8-r', 'windows-1252', 'iso8859-5']
                        enc, ok = QInputDialog.getItem(self, "Выбор кодировки", "Не удалось определить кодировку файла. Выберите кодировку:", encodings, 0, False)
                        if ok:
                            try:
                                text = raw.decode(enc)
                                self.current_encoding = enc
                            except Exception as e:
                                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл даже с выбранной кодировкой {enc}: {e}\n\nОшибки попыток: {'; '.join(errors)}")
                                return
                        else:
                            return
                    self.text_editor.setPlainText(text)
                    self.current_file = file_path
                    self.file_name_changed.emit(os.path.basename(file_path))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        try:
            text = self.text_editor.toPlainText()
            with open(self.current_file, 'w', encoding=self.current_encoding) as f:
                f.write(text)
            self.file_name_changed.emit(os.path.basename(self.current_file))
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

def save_file_as(self):
    from PySide6.QtWidgets import QFileDialog
    file_path, selected_filter = QFileDialog.getSaveFileName(
        self,
        "Сохранить файл как",
        "",
        "Текстовые файлы (*.txt);;Все файлы (*.*)"
    )
    if file_path:
        # Если выбран фильтр txt и нет расширения, добавляем .txt
        if selected_filter.startswith("Текстовые файлы") and not file_path.lower().endswith(".txt"):
            file_path += ".txt"
        self.current_file = file_path
        self.current_encoding = 'utf-8'
        self.save_file()
        self.file_name_changed.emit(os.path.basename(file_path))

    def undo(self):
        self.text_editor.undo()
    def redo(self):
        self.text_editor.redo()
    def cut(self):
        self.text_editor.cut()
    def copy(self):
        self.text_editor.copy()
    def paste(self):
        self.text_editor.paste()
    def delete(self):
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        else:
            cursor.deleteChar()
    def select_all(self):
        self.text_editor.selectAll()
