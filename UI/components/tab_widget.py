"""
Tab Widget Component для GopiAI Standalone Interface
================================================

Центральная область с вкладками документов.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit


class TabDocumentWidget(QWidget):
    """Центральная область с вкладками документов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabDocument")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса вкладок"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Виджет вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        
        # Добавляем стартовую вкладку
        welcome_tab = QTextEdit()
        welcome_tab.setPlainText("""
🚀 Добро пожаловать в GopiAI v0.2.0!

Это модульный интерфейс для работы с ИИ ассистентом.

Основные возможности:
• 📁 Проводник файлов (левая панель)
• 📝 Редактор кода с вкладками (центральная область)
• 🤖 ИИ чат ассистент (правая панель)  
• 💻 Встроенный терминал (нижняя панель)
• 🎨 Современный дизайн с темной темой

Используйте меню "Файл" для открытия документов или "Вид" для управления панелями.

Создано с ❤️ командой GopiAI
        """)
        welcome_tab.setReadOnly(True)
        
        self.tab_widget.addTab(welcome_tab, "🏠 Добро пожаловать")
        layout.addWidget(self.tab_widget)

    def add_new_tab(self, title="Новый документ", content=""):
        """Добавление новой вкладки"""
        editor = QTextEdit()
        editor.setPlainText(content)
        index = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(index)
        return editor

    def close_current_tab(self):
        """Закрытие текущей вкладки"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0 and self.tab_widget.count() > 1:
            self.tab_widget.removeTab(current_index)

    def get_current_editor(self):
        """Получение текущего редактора"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, QTextEdit):
            return current_widget
        return None

    def get_current_text(self) -> str:
        """Получение текста из текущей вкладки"""
        editor = self.get_current_editor()
        if editor:
            return editor.toPlainText()
        return ""

    def set_current_text(self, text: str):
        """Установка текста в текущую вкладку"""
        editor = self.get_current_editor()
        if editor:
            editor.setPlainText(text)
