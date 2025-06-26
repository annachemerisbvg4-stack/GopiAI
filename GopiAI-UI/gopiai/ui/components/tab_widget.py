"""
Tab Widget Component для GopiAI Standalone Interface
================================================

Центральная область с вкладками документов.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

import chardet

# Импортируем продвинутый текстовый редактор
import sys
import os
# Добавляем путь к модулю GopiAI-Widgets
widgets_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'GopiAI-Widgets')
widgets_path = os.path.abspath(widgets_path)
if widgets_path not in sys.path:
    sys.path.insert(0, widgets_path)

from gopiai.widgets.core.text_editor import TextEditorWidget
from gopiai.ui.components.rich_text_notebook_widget import NotebookEditorWidget
TEXT_EDITOR_AVAILABLE = True

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

    def add_notebook_tab(self, title="Новый блокнот", content="", menu_bar=None):
        """Добавление новой вкладки-блокнота с форматированием (чистый rich text notebook)"""
        from gopiai.ui.components.rich_text_notebook_widget import NotebookEditorWidget
        notebook = NotebookEditorWidget()
        if content:
            notebook.setPlainText(content)
        index = self.tab_widget.addTab(notebook, title)
        self.tab_widget.setCurrentIndex(index)
        # Подключаем сигналы меню к QTextEdit, если menu_bar передан
        if menu_bar is not None:
            try:
                menu_bar.undoRequested.connect(notebook.editor.undo)
                menu_bar.redoRequested.connect(notebook.editor.redo)
                menu_bar.cutRequested.connect(notebook.editor.cut)
                menu_bar.copyRequested.connect(notebook.editor.copy)
                menu_bar.pasteRequested.connect(notebook.editor.paste)
                menu_bar.deleteRequested.connect(notebook.editor.clear)
                menu_bar.selectAllRequested.connect(notebook.editor.selectAll)
            except Exception as e:
                print(f"[WARNING] Не удалось подключить сигналы меню к NotebookEditorWidget: {e}")
        return notebook

    def open_file_in_tab(self, file_path):
        """Открытие файла в новой вкладке"""
        try:
            if TEXT_EDITOR_AVAILABLE:
                # Создаем текстовый редактор
                editor = TextEditorWidget()
                editor.current_file = file_path
                with open(file_path, 'rb') as f:
                    raw = f.read()
                encoding = chardet.detect(raw)['encoding'] or 'utf-8'
                text = raw.decode(encoding, errors='replace')
                editor.current_encoding = encoding
                editor.text_editor.setPlainText(text)
                import os
                tab_title = os.path.basename(file_path)
                editor.file_name_changed.connect(
                    lambda name: self._update_tab_title(editor, name)
                )
                print(f"Файл открыт в TextEditorWidget: {file_path}")
            else:
                # Fallback к обычному редактору
                editor = QTextEdit()
                with open(file_path, 'rb') as f:
                    raw = f.read()
                encoding = chardet.detect(raw)['encoding'] or 'utf-8'
                content = raw.decode(encoding, errors='replace')
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
        if self.tab_widget.count() > 0:  
            self.tab_widget.removeTab(index)

    def add_browser_tab(self, url="about:blank", title="Браузер"):
        """Добавление новой вкладки с браузером"""
        print(f"Создаем встроенный браузер...")
        try:
            from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLineEdit
            from PySide6.QtCore import QUrl
            
            # Создаем главный виджет браузера
            browser_widget = QWidget()
            browser_layout = QVBoxLayout(browser_widget)
            browser_layout.setContentsMargins(5, 5, 5, 5)
            browser_layout.setSpacing(2)
            
            # ==============================================
            # Панель навигации с адресной строкой
            # ==============================================
            nav_layout = QHBoxLayout()
            nav_layout.setContentsMargins(0, 0, 0, 0)
            nav_layout.setSpacing(5)
            
            # Кнопка "Назад"
            back_btn = QPushButton("←")
            back_btn.setFixedSize(30, 30)
            back_btn.setToolTip("Назад")
            back_btn.setObjectName("browserBackBtn")
            
            # Кнопка "Вперед"  
            forward_btn = QPushButton("→")
            forward_btn.setFixedSize(30, 30)
            forward_btn.setToolTip("Вперед")
            forward_btn.setObjectName("browserForwardBtn")
            
            # Кнопка "Обновить"
            refresh_btn = QPushButton("↻")
            refresh_btn.setFixedSize(30, 30)
            refresh_btn.setToolTip("Обновить")
            refresh_btn.setObjectName("browserRefreshBtn")
            
            # Адресная строка
            address_bar = QLineEdit()
            address_bar.setPlaceholderText("Введите URL или поисковый запрос...")
            address_bar.setObjectName("browserAddressBar")
            
            # Кнопка "Перейти"
            go_btn = QPushButton("➤")
            go_btn.setFixedSize(30, 30)
            go_btn.setToolTip("Перейти")
            go_btn.setObjectName("browserGoBtn")
            
            # Добавляем элементы в панель навигации
            nav_layout.addWidget(back_btn)
            nav_layout.addWidget(forward_btn)
            nav_layout.addWidget(refresh_btn)
            nav_layout.addWidget(address_bar)
            nav_layout.addWidget(go_btn)
            
            # ==============================================
            # Веб-браузер
            # ==============================================
            web_view = QWebEngineView()
            web_view.setMinimumSize(800, 600)
            
            # Принудительно показываем
            web_view.show()
            web_view.setVisible(True)
            
            # ==============================================
            # Подключение сигналов навигации
            # ==============================================
            def navigate_back():
                if web_view.history().canGoBack():
                    web_view.back()
                    
            def navigate_forward():
                if web_view.history().canGoForward():
                    web_view.forward()
                    
            def refresh_page():
                web_view.reload()
                
            def navigate_to_url():
                url_text = address_bar.text().strip()
                if not url_text:
                    return
                    
                # Если не содержит протокол, добавляем https://
                if not url_text.startswith(('http://', 'https://', 'file://', 'about:')):
                    # Проверяем, выглядит ли это как URL
                    if '.' in url_text and ' ' not in url_text:
                        url_text = 'https://' + url_text
                    else:
                        # Выглядит как поисковый запрос
                        url_text = f'https://google.com/search?q={url_text}'
                
                print(f"📡 Переходим к URL: {url_text}")
                web_view.load(QUrl(url_text))
                
            def update_address_bar(qurl):
                """Обновление адресной строки при изменении URL"""
                address_bar.setText(qurl.toString())
                
            def update_navigation_buttons():
                """Обновление состояния кнопок навигации"""
                back_btn.setEnabled(web_view.history().canGoBack())
                forward_btn.setEnabled(web_view.history().canGoForward())
            
            # Подключаем сигналы
            back_btn.clicked.connect(navigate_back)
            forward_btn.clicked.connect(navigate_forward)
            refresh_btn.clicked.connect(refresh_page)
            go_btn.clicked.connect(navigate_to_url)
            address_bar.returnPressed.connect(navigate_to_url)
            
            # Обновляем адресную строку при изменении URL
            web_view.urlChanged.connect(update_address_bar)
            web_view.loadFinished.connect(lambda: update_navigation_buttons())
            
            # ==============================================
            # Сборка интерфейса
            # ==============================================
            browser_layout.addLayout(nav_layout)
            browser_layout.addWidget(web_view)
            
            # Сохраняем ссылки на компоненты для доступа извне
            browser_widget.setProperty("_web_view", web_view)
            browser_widget.setProperty("_address_bar", address_bar)
            browser_widget.setProperty("_back_btn", back_btn)
            browser_widget.setProperty("_forward_btn", forward_btn)
            browser_widget.setProperty("_refresh_btn", refresh_btn)
            
            # Добавляем вкладку
            index = self.tab_widget.addTab(browser_widget, title)
            self.tab_widget.setCurrentIndex(index)
            
            # Загружаем URL
            if url and url != "about:blank":
                print(f"📡 Загружаем URL: {url}")
                address_bar.setText(url)
            else:
                # Загрузка Google
                url = "https://google.com"
                print(f"📡 Загружаем Google")
                address_bar.setText(url)
                
            web_view.load(QUrl(url))
            
            print(f"Веб-страница с навигацией загружена: {url}")
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

    def save_current_file(self, parent=None):
        """Сохраняет текущую вкладку в файл (если уже был путь) или вызывает save as"""
        current_widget = self.tab_widget.currentWidget()
        file_path = getattr(current_widget, 'current_file', None)
        if not file_path:
            return self.save_current_file_as(parent)
        return self._save_widget_to_file(current_widget, file_path, parent)

    def save_current_file_as(self, parent=None):
        """Сохраняет текущую вкладку в новый файл с выбором формата и расширения"""
        from PySide6.QtWidgets import QFileDialog
        current_widget = self.tab_widget.currentWidget()
        if current_widget is None:
            return False
        # Расширенный список форматов
        filters = (
            "Python (*.py);;JavaScript (*.js);;TypeScript (*.ts);;C++ (*.cpp *.h);;C (*.c *.h);;C# (*.cs);;Java (*.java);;Go (*.go);;Rust (*.rs);;Kotlin (*.kt);;Swift (*.swift);;PHP (*.php);;Ruby (*.rb);;Perl (*.pl);;Shell Script (*.sh);;Batch (*.bat);;PowerShell (*.ps1);;HTML (*.html *.htm);;CSS (*.css);;JSON (*.json);;YAML (*.yaml *.yml);;Markdown (*.md);;INI (*.ini);;XML (*.xml);;SQL (*.sql);;Текстовый файл (*.txt);;Rich Text (*.rtf);;Все файлы (*.*)"
        )
        file_path, selected_filter = QFileDialog.getSaveFileName(parent, "Сохранить как", "", filters)
        if not file_path:
            return False
        # Автоматически подставлять расширение, если не указано
        ext_map = {
            'Python': '.py', 'JavaScript': '.js', 'TypeScript': '.ts', 'C++': '.cpp', 'C#': '.cs', 'C ': '.c',
            'Java': '.java', 'Go': '.go', 'Rust': '.rs', 'Kotlin': '.kt', 'Swift': '.swift', 'PHP': '.php',
            'Ruby': '.rb', 'Perl': '.pl', 'Shell Script': '.sh', 'Batch': '.bat', 'PowerShell': '.ps1',
            'HTML': '.html', 'CSS': '.css', 'JSON': '.json', 'YAML': '.yaml', 'Markdown': '.md', 'INI': '.ini',
            'XML': '.xml', 'SQL': '.sql', 'Rich Text': '.rtf', 'Текстовый файл': '.txt'
        }
        if '.' not in file_path.split(os.sep)[-1]:
            for key, ext in ext_map.items():
                if key in selected_filter:
                    file_path += ext
                    break
        # Сохраняем
        result = self._save_widget_to_file(current_widget, file_path, parent, selected_filter)
        if result:
            setattr(current_widget, 'current_file', file_path)
        return result

    def _save_widget_to_file(self, widget, file_path, parent=None, selected_filter=None):
        """Сохраняет содержимое виджета в файл с учетом формата"""
        try:
            # Определяем тип редактора
            if isinstance(widget, NotebookEditorWidget):
                # Для блокнота поддерживаем txt, md, rtf, html
                if selected_filter and 'Markdown' in selected_filter:
                    text = widget.editor.toPlainText()
                elif selected_filter and 'Rich Text' in selected_filter:
                    text = widget.editor.toHtml()  # QTextEdit не поддерживает RTF напрямую, но можно сохранить HTML
                elif selected_filter and 'HTML' in selected_filter:
                    text = widget.editor.toHtml()
                else:
                    text = widget.editor.toPlainText()
            elif hasattr(widget, 'text_editor'):
                text = widget.text_editor.toPlainText()
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText()
            else:
                text = str(widget)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "Ошибка", f"Не удалось сохранить файл: {e}")
            return False
