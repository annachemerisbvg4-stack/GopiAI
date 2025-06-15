"""
Tab Widget Component для GopiAI Standalone Interface
================================================

Центральная область с вкладками документов.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

# Импортируем продвинутый текстовый редактор
try:
    import sys
    import os
    # Добавляем путь к модулю GopiAI-Widgets
    widgets_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'GopiAI-Widgets')
    widgets_path = os.path.abspath(widgets_path)
    if widgets_path not in sys.path:
        sys.path.insert(0, widgets_path)
    
    from gopiai.widgets.core.text_editor import TextEditorWidget
    TEXT_EDITOR_AVAILABLE = True
    print("TextEditorWidget импортирован успешно")
except ImportError as e:
    print(f"Не удалось импортировать TextEditorWidget: {e}")
    TEXT_EDITOR_AVAILABLE = False

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
        welcome_tab.setPlainText("Добро пожаловать в GopiAI v0.3.0!")
        welcome_tab.setReadOnly(True)
        
        self.tab_widget.addTab(welcome_tab, "Добро пожаловать")
        
        # Подключаем сигнал закрытия вкладок
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        
        layout.addWidget(self.tab_widget)

    def add_new_tab(self, title="Новый документ", content=""):
        """Добавление новой вкладки с текстовым редактором"""
        if TEXT_EDITOR_AVAILABLE:
            # Используем продвинутый текстовый редактор с нумерацией строк
            editor = TextEditorWidget()
            editor.text_editor.setPlainText(content)
            print(f"Создана вкладка с TextEditorWidget: {title}")
        else:
            # Fallback к обычному QTextEdit
            editor = QTextEdit()
            editor.setPlainText(content)
            print(f"Создана вкладка с QTextEdit (fallback): {title}")

        index = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(index)
        return editor

    def open_file_in_tab(self, file_path):
        """Открытие файла в новой вкладке"""
        try:
            if TEXT_EDITOR_AVAILABLE:
                # Создаем текстовый редактор
                editor = TextEditorWidget()
                
                # Открываем файл через методы редактора (он сам обработает кодировку)
                editor.current_file = file_path
                with open(file_path, 'rb') as f:
                    raw = f.read()
                    
                # Определяем кодировку как в оригинальном коде
                import chardet
                try:
                    encoding = chardet.detect(raw)['encoding'] or 'utf-8'
                    text = raw.decode(encoding)
                    editor.current_encoding = encoding
                except:
                    text = raw.decode('utf-8', errors='replace')
                    editor.current_encoding = 'utf-8'
                
                editor.text_editor.setPlainText(text)
                
                # Подключаем сигнал изменения имени файла для обновления заголовка вкладки
                import os
                tab_title = os.path.basename(file_path)
                editor.file_name_changed.connect(
                    lambda name: self._update_tab_title(editor, name)
                )
                
                print(f"Файл открыт в TextEditorWidget: {file_path}")
            else:
                # Fallback к обычному редактору
                editor = QTextEdit()
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.setPlainText(content)
                import os
                tab_title = os.path.basename(file_path)
                print(f"Файл открыт в QTextEdit (fallback): {file_path}")
            
            # Добавляем вкладку
            index = self.tab_widget.addTab(editor, tab_title)
            self.tab_widget.setCurrentIndex(index)
            return editor
            
        except Exception as e:
            print(f"Ошибка открытия файла {file_path}: {e}")
            # Создаем вкладку с сообщением об ошибке
            error_tab = QTextEdit()
            error_tab.setPlainText(f"Ошибка открытия файла:\n{file_path}\n\n{str(e)}")
            error_tab.setReadOnly(True)
            index = self.tab_widget.addTab(error_tab, "Ошибка")
            self.tab_widget.setCurrentIndex(index)
            return error_tab

    def _update_tab_title(self, editor_widget, new_title):
        """Обновление заголовка вкладки"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == editor_widget:
                self.tab_widget.setTabText(i, new_title)
                break

    def _close_tab(self, index):
        """Закрытие вкладки по индексу"""
        if self.tab_widget.count() > 1:  # Оставляем хотя бы одну вкладку
            self.tab_widget.removeTab(index)

    def add_browser_tab(self, url="about:blank", title="Браузер"):
        """Добавление новой вкладки с браузером"""
        print(f"Создаем встроенный браузер...")
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
            
            print(f"Веб-страница загружена: {url}")
            return browser_widget
            
        except Exception as e:
            print(f"Ошибка при создании браузера: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_browser_tab(f"Ошибка: {str(e)}")

    def _create_fallback_browser_tab(self, error_msg):
        """Создает резервную вкладку с информацией об ошибке"""
        fallback_tab = QTextEdit()
        fallback_tab.setPlainText(f"""Браузер недоступен

{error_msg}

🔧 Возможные решения:
• Проверьте установку QWebEngineView
• Убедитесь, что Qt модуль WebEngine включен
• Попробуйте переустановить PySide6 с WebEngine: pip install PySide6[webengine]
""")
        fallback_tab.setReadOnly(True)
        index = self.tab_widget.addTab(fallback_tab, "Браузер недоступен")
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
        
        # Проверяем, является ли это TextEditorWidget
        if TEXT_EDITOR_AVAILABLE and type(current_widget).__name__ == "TextEditorWidget":
            return getattr(current_widget, "text_editor", None)  # Безопасно получаем внутренний редактор
        elif isinstance(current_widget, QTextEdit):
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
