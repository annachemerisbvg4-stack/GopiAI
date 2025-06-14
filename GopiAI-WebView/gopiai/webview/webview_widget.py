"""
WebView Widget для GopiAI

Основной Qt виджет для отображения веб-интерфейса чата с ИИ.
Использует QWebEngineView для рендеринга HTML/CSS/JS интерфейса.
"""

import os
from typing import Optional
from pathlib import Path

from PySide6.QtCore import Signal, QUrl, QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage, QWebEngineProfile
from PySide6.QtWebChannel import QWebChannel

from gopiai.webview.js_bridge import JavaScriptBridge


class PuterWebEnginePage(QWebEnginePage):
    """Кастомная веб-страница для разрешения pop-up окон puter.js"""
    
    def createWindow(self, window_type):
        """Разрешаем создание новых окон (pop-up) для puter.js аутентификации"""
        # Создаем новое окно для pop-up
        new_page = PuterWebEnginePage(self.parent())
        
        # Настраиваем разрешения для нового окна
        settings = new_page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        
        # Возвращаем новую страницу
        return new_page


class WebViewWidget(QWidget):
    """
    Qt виджет для отображения веб-интерфейса чата с ИИ.
    
    Использует QWebEngineView для рендеринга веб-страницы с puter.js
    и QWebChannel для связи между Python и JavaScript.
    """
    
    # Сигналы для взаимодействия с родительским приложением
    message_sent = Signal(str)  # Когда пользователь отправил сообщение
    message_received = Signal(str, str)  # Когда получен ответ (model, message)
    chat_cleared = Signal()  # Когда чат очищен
    model_changed = Signal(str)  # Когда изменена модель ИИ
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Инициализация WebView виджета.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация компонентов
        self._setup_ui()
        self._setup_bridge()
        self._load_chat_interface()
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.setObjectName("WebViewWidget")
        
        # Создание layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создание WebEngineView
        self.web_view = QWebEngineView(self)
        
        # Создание кастомной страницы для разрешения pop-up окон
        page = PuterWebEnginePage(self.web_view)
        self.web_view.setPage(page)
        
        # Настройка безопасности для загрузки внешних ресурсов
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        # КРИТИЧЕСКИ ВАЖНО: Разрешаем pop-up окна для puter.js аутентификации
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        
        # Настройка профиля для разрешения CORS
        profile = self.web_view.page().profile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)
        
        layout.addWidget(self.web_view)
    
    def _setup_bridge(self):
        """Настройка моста для связи Python ↔ JavaScript."""
        # Создание канала для связи с JS
        self.channel = QWebChannel(self)
        
        # Создание моста
        self.bridge = JavaScriptBridge(self)
        
        # Подключение сигналов моста к сигналам виджета
        self.bridge.message_sent.connect(self.message_sent)
        self.bridge.message_received.connect(self.message_received)
        self.bridge.chat_cleared.connect(self.chat_cleared)
        self.bridge.model_changed.connect(self.model_changed)
        
        # Регистрация моста в канале
        self.channel.registerObject("bridge", self.bridge)
        
        # Установка канала в WebEngineView
        self.web_view.page().setWebChannel(self.channel)
    
    def _load_chat_interface(self):
        """Загрузка HTML интерфейса чата."""
        # Получение пути к HTML файлу
        assets_dir = Path(__file__).parent / "assets"
        html_path = assets_dir / "chat.html"
        
        if html_path.exists():
            # Загрузка HTML файла
            url = QUrl.fromLocalFile(str(html_path.absolute()))
            self.web_view.load(url)
        else:
            # Fallback: загрузка простого HTML
            self._load_fallback_html()
    
    def _load_fallback_html(self):
        """Загрузка простого HTML интерфейса в случае отсутствия файлов."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GopiAI Chat</title>
            <script src="https://js.puter.com/v2/"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id="chat-container">
                <h1>GopiAI WebView Chat</h1>
                <p>Chat interface loading...</p>
                <input type="text" id="message-input" placeholder="Type your message...">
                <button onclick="sendMessage()">Send</button>
            </div>
            
            <script>
                let bridge = null;
                
                // Инициализация WebChannel
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    bridge = channel.objects.bridge;
                });
                
                function sendMessage() {
                    const input = document.getElementById('message-input');
                    const message = input.value.trim();
                    if (message && bridge) {
                        bridge.send_message(message);
                        input.value = '';
                    }
                }
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html_content)
    
    def send_message_to_chat(self, message: str):
        """
        Отправка сообщения в чат из Python кода.
        
        Args:
            message: Текст сообщения
        """
        if self.bridge:
            self.bridge.receive_message_from_python(message)
    
    def clear_chat(self):
        """Очистка истории чата."""
        if self.bridge:
            self.bridge.clear_chat()
    
    def set_model(self, model: str):
        """
        Установка модели ИИ.
        
        Args:
            model: Название модели ('claude-sonnet-4' или 'claude-opus-4')
        """
        if self.bridge:
            self.bridge.set_model(model)
    
    def get_chat_history(self) -> list:
        """
        Получение истории чата.
        
        Returns:
            Список сообщений
        """
        if self.bridge:
            return self.bridge.get_chat_history()
        return []
    
    def export_chat(self, format_type: str = "json") -> str:
        """
        Экспорт истории чата.
        
        Args:
            format_type: Формат экспорта ('json', 'txt', 'md')
            
        Returns:
            Экспортированные данные
        """
        if self.bridge:
            return self.bridge.export_chat(format_type)
        return ""