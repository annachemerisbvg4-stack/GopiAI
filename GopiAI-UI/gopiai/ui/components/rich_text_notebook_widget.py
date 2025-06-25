"""
RichTextNotebookWidget
=====================

Блокнот с форматированием на основе PySide6 QTextEdit и тулбара форматирования.
Интеграция расширенного движка из rich_text_notebook_extension.wordprocessor.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
import chardet

# Импортируем расширенный движок блокнота из расширения
try:
    from gopiai.extensions.rich_text_notebook_extension.wordprocessor import MegasolidEditor
    WORDPROCESSOR_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Не удалось импортировать MegasolidEditor: {e}")
    MegasolidEditor = None
    WORDPROCESSOR_AVAILABLE = False

class RichTextNotebookWidget(QWidget):
    """
    Виджет блокнота с форматированием, использует MegasolidEditor из расширения,
    либо fallback на QTextEdit (минимальный режим).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RichTextNotebookWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if WORDPROCESSOR_AVAILABLE:
            self.editor = MegasolidEditor()
            self.editor.reset(
                x=0, y=0, width=800, height=600,
                use_icons=False, use_menu=False, use_monospace=False, allow_inline_tables=True
            )
            # Встраиваем центральный виджет редактора в layout
            layout.addWidget(self.editor.centralWidget())
        else:
            from PySide6.QtWidgets import QTextEdit, QToolBar
            self.editor = QTextEdit(self)
            self.editor.setAcceptRichText(True)
            self.editor.setPlaceholderText("Введите заметку...")
            layout.addWidget(self.editor)

    def setHtml(self, html):
        if WORDPROCESSOR_AVAILABLE:
            self.editor.editor.setHtml(html)
        else:
            self.editor.setHtml(html)

    def toHtml(self):
        if WORDPROCESSOR_AVAILABLE:
            return self.editor.editor.toHtml()
        else:
            return self.editor.toHtml()

    def setPlainText(self, text):
        if WORDPROCESSOR_AVAILABLE:
            self.editor.editor.setPlainText(text)
        else:
            self.editor.setPlainText(text)

    def toPlainText(self):
        if WORDPROCESSOR_AVAILABLE:
            return self.editor.editor.toPlainText()
        else:
            return self.editor.toPlainText()

    # Методы для открытия/сохранения файлов с autodetect кодировки
    def open_file(self, path):
        with open(path, 'rb') as f:
            raw = f.read()
        encoding = chardet.detect(raw)['encoding'] or 'utf-8'
        html = raw.decode(encoding, errors='replace')
        self.setHtml(html)

    def save_file(self, path):
        html = self.toHtml()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
