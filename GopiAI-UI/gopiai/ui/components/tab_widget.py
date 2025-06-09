"""
Tab Widget Component для GopiAI Standalone Interface
================================================

Центральная область с вкладками документов.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

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
        
        # Виджет вкладок с улучшенными настройками
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        
        # Дополнительные настройки для удобства
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setUsesScrollButtons(True)  # Кнопки прокрутки при множестве вкладок
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)  # Обрезаем длинные названия
        
        # Добавляем стартовую вкладку
        welcome_tab = QTextEdit()
        welcome_tab.setPlainText("🚀 Добро пожаловать в GopiAI v0.3.0!")
        welcome_tab.setReadOnly(True)
        
        self.tab_widget.addTab(welcome_tab, "🏠 Добро пожаловать")
        layout.addWidget(self.tab_widget)

    def add_new_tab(self, title="Новый документ", content=""):
        """Добавление новой вкладки с текстовым редактором"""
        editor = QTextEdit()
        editor.setPlainText(content)
        index = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(index)
        return editor

    def add_browser_tab(self, url="about:blank", title="🌐 Браузер"):
        """Добавление новой вкладки с браузером"""
        print(f"🔍 Создаем встроенный браузер...")
        
        try:
            # Создаем простейший браузер прямо тут
            browser_widget = QWidget()
            browser_layout = QVBoxLayout(browser_widget)
            browser_layout.setContentsMargins(0, 0, 0, 0)
            
            # Создаем сам браузер
            web_view = QWebEngineView()
            
            # Устанавливаем стили и размеры
            web_view.setMinimumSize(800, 600)
            
            # Принудительно показываем
            web_view.show()
            web_view.setVisible(True)
            
            # Добавляем в лейаут
            browser_layout.addWidget(web_view)
            
            # Добавляем вкладку
            index = self.tab_widget.addTab(browser_widget, title)
            self.tab_widget.setCurrentIndex(index)
            
            # Загружаем URL
            if url and url != "about:blank":
                print(f"📡 Загружаем URL: {url}")
            else:
                # Загрузка Google
                url = "https://google.com"
                print(f"📡 Загружаем Google")
                
            web_view.load(QUrl(url))
            
            print(f"✅ Веб-страница загружена: {url}")
            return browser_widget
            
        except Exception as e:
            print(f"❌ Ошибка при создании браузера: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_browser_tab(f"Ошибка: {str(e)}")

    def _create_fallback_browser_tab(self, error_msg):
        """Создает резервную вкладку с информацией об ошибке"""
        fallback_tab = QTextEdit()
        fallback_tab.setPlainText(f"""❌ Браузер недоступен

{error_msg}

🔧 Возможные решения:
• Проверьте установку QWebEngineView
• Убедитесь, что Qt модуль WebEngine включен
• Попробуйте переустановить PySide6 с WebEngine: pip install PySide6[webengine]
""")
        fallback_tab.setReadOnly(True)
        index = self.tab_widget.addTab(fallback_tab, "❌ Браузер недоступен")
        self.tab_widget.setCurrentIndex(index)
        return fallback_tab

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

    def get_current_text(self):
        """Получение текста из текущей вкладки"""
        editor = self.get_current_editor()
        if editor:
            return editor.toPlainText()
        return ""

    def set_current_text(self, text):
        """Установка текста в текущую вкладку"""
        editor = self.get_current_editor()
        if editor:
            editor.setPlainText(text)
