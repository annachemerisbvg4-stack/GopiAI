"""
WebView Chat Widget для GopiAI UI
===============================

Интегрированный чат виджет с puter.js для главного интерфейса GopiAI.
Заменяет стандартный chat_widget.py и обеспечивает бесшовную интеграцию
с глобальной системой тем.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, QObject, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PySide6.QtWebChannel import QWebChannel
from pathlib import Path
import json


class PuterWebEnginePage(QWebEnginePage):
    """Кастомная веб-страница для разрешения pop-up окон puter.js"""
    
    def createWindow(self, window_type):
        """Разрешаем создание новых окон (pop-up) для puter.js аутентификации"""
        new_page = PuterWebEnginePage(self.parent())
        
        # Настраиваем разрешения для нового окна
        settings = new_page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        
        return new_page


class WebViewChatBridge(QObject):
    """Bridge для связи между Python и JavaScript"""
    
    # Сигналы для главного интерфейса
    message_sent = Signal(str)
    ai_response_received = Signal(str, str)  # model, response
    model_changed = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__()
    
    @Slot(str)
    def send_message(self, message: str):
        """Получение сообщения от JavaScript"""
        print(f"🔄 Bridge: received message from JS: {message[:50]}...")
        self.message_sent.emit(message)
    
    @Slot(str, str)
    def receive_ai_message(self, model: str, response: str):
        """Получение ответа ИИ от JavaScript"""
        print(f"🤖 Bridge: received AI response from {model}: {response[:50]}...")
        self.ai_response_received.emit(model, response)
    
    @Slot(str)
    def change_model(self, model: str):
        """Изменение модели ИИ"""
        print(f"🔧 Bridge: model changed to {model}")
        self.model_changed.emit(model)
    
    @Slot(str)
    def log_error(self, error: str):
        """Логирование ошибок"""
        print(f"❌ Bridge: error from JS: {error}")
        self.error_occurred.emit(error)
    
    @Slot()
    def clear_chat(self):
        """Очистка чата"""
        print("🧹 Bridge: chat cleared")
    
    @Slot(result=str)
    def get_chat_history_json(self) -> str:
        """Получение истории чата в JSON формате"""
        print("📜 Bridge: chat history requested")
        return json.dumps([])



class WebViewChatWidget(QWidget):
    """
    Основной чат виджет с интеграцией puter.js для GopiAI UI
    """
    
    # Сигналы для интеграции с главным интерфейсом
    message_sent = Signal(str)
    response_received = Signal(str, str)  # model, response
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = WebViewChatBridge(self)
        self.theme_manager = None  # Будет установлен извне
        
        self._setup_ui()
        self._setup_web_engine()
        self._setup_connections()
        self._load_chat_interface()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # WebView для чата
        self.web_view = QWebEngineView(self)
        
        # Добавляем компоненты в layout
        layout.addWidget(self.web_view)
    
    def _setup_web_engine(self):
        """Настройка WebEngine"""
        # Создание кастомной страницы для разрешения pop-up окон
        page = PuterWebEnginePage(self.web_view)
        self.web_view.setPage(page)
        
        # Настройки веб-движка
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        # КРИТИЧЕСКИ ВАЖНО: Разрешаем pop-up окна для puter.js аутентификации
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        
        # Настройка WebChannel для связи с JavaScript
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        page.setWebChannel(self.channel)
    
    def _setup_connections(self):
        """Настройка соединений сигналов"""
        # Пробрасываем сигналы от bridge
        self.bridge.message_sent.connect(self.message_sent.emit)
        self.bridge.ai_response_received.connect(self.response_received.emit)
    
    def _load_chat_interface(self):
            """Загрузка HTML интерфейса чата"""
            # Найдем корень проекта (где находятся GopiAI-UI и GopiAI-WebView)
            current_file = Path(__file__).resolve()
            root_path = current_file
            
            # Поднимаемся по дереву папок пока не найдем GopiAI-WebView
            while root_path.parent != root_path:
                if (root_path / 'GopiAI-WebView').exists():
                    break
                root_path = root_path.parent
            
            assets_path = root_path / "GopiAI-WebView" / "gopiai" / "webview" / "assets"
            html_path = assets_path / "chat.html"
            
            print(f"🔍 Checking HTML path: {html_path}")
            print(f"🔍 HTML exists: {html_path.exists()}")
            
            if html_path.exists():
                # Загружаем HTML файл
                file_url = html_path.as_uri()
                print(f"📁 Loading main HTML from: {file_url}")
                self.web_view.load(file_url)
                
                # Ждем загрузки страницы и применяем тему
                self.web_view.loadFinished.connect(self._on_page_loaded)
            else:
                # Если файл не найден, создаем базовый HTML
                print("⚠️ Main HTML not found, using fallback")
                self._create_fallback_html()


    
    def _on_page_loaded(self, success):
        """Обработчик завершения загрузки страницы"""
        if success:
            print("WebView page loaded successfully")
            # Применяем тему после загрузки страницы
            if self.theme_manager:
                self._apply_theme_to_webview()
        else:
            print("WebView page failed to load")
    
    def _create_fallback_html(self):
        """Создание запасного HTML интерфейса"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>GopiAI Chat</title>
            <script src="https://js.puter.com/v2/"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: var(--chat-bg, #1e1e1e);
                    color: var(--chat-text, #ffffff);
                }
                .chat-container {
                    max-width: 800px;
                    margin: 0 auto;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                .messages-container {
                    flex: 1;
                    overflow-y: auto;
                    padding: 10px;
                    margin-bottom: 10px;
                    border: 1px solid var(--chat-border, #333);
                    border-radius: 8px;
                    background: var(--chat-messages-bg, #2d2d2d);
                }
                .message {
                    margin-bottom: 15px;
                    padding: 10px;
                    border-radius: 8px;
                    max-width: 80%;
                }
                .user-message {
                    background: var(--chat-user-bg, #0078d4);
                    margin-left: auto;
                    text-align: right;
                }
                .ai-message {
                    background: var(--chat-ai-bg, #404040);
                }
                .input-container {
                    display: flex;
                    gap: 10px;
                }
                #message-input {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid var(--chat-border, #333);
                    border-radius: 4px;
                    background: var(--chat-input-bg, #2d2d2d);
                    color: var(--chat-text, #ffffff);
                }
                #send-btn {
                    padding: 10px 20px;
                    background: var(--chat-btn-bg, #0078d4);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                #send-btn:hover {
                    background: var(--chat-btn-hover, #106ebe);
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div id="messages-container" class="messages-container">
                    <div class="message ai-message">
                        Welcome to GopiAI Chat! I'm powered by puter.js and ready to help you.
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" id="message-input" placeholder="Type your message here...">
                    <button id="send-btn">Send</button>
                </div>
            </div>
            
            <script>
                let bridge = null;
                let currentModel = 'claude-sonnet-4';
                
                // Инициализация WebChannel
                if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined') {
                    try {
                        new QWebChannel(qt.webChannelTransport, (channel) => {
                            bridge = channel.objects.bridge;
                            console.log('WebChannel bridge connected:', bridge);
                            console.log('Available bridge methods:', Object.getOwnPropertyNames(bridge));
                        });
                    } catch (error) {
                        console.error('Error initializing WebChannel:', error);
                    }
                } else {
                    console.warn('QWebChannel or qt not available');
                }
                
                // Ожидание загрузки puter.js
                async function waitForPuter() {
                    return new Promise((resolve, reject) => {
                        if (typeof puter !== 'undefined') {
                            resolve();
                        } else {
                            let attempts = 0;
                            const maxAttempts = 50;
                            const checkInterval = setInterval(() => {
                                attempts++;
                                if (typeof puter !== 'undefined') {
                                    clearInterval(checkInterval);
                                    resolve();
                                } else if (attempts >= maxAttempts) {
                                    clearInterval(checkInterval);
                                    reject(new Error('puter.js failed to load'));
                                }
                            }, 100);
                        }
                    });
                }
                
                // Инициализация после загрузки DOM
                document.addEventListener('DOMContentLoaded', async () => {
                    const messageInput = document.getElementById('message-input');
                    const sendBtn = document.getElementById('send-btn');
                    const messagesContainer = document.getElementById('messages-container');
                    
                    try {
                        await waitForPuter();
                        console.log('puter.js loaded successfully');
                    } catch (error) {
                        console.error('Failed to load puter.js:', error);
                        addMessage('ai', '⚠️ Error: Failed to load puter.js. Please check your internet connection.');
                    }
                    
                    // Обработчики событий
                    sendBtn.addEventListener('click', sendMessage);
                    messageInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            sendMessage();
                        }
                    });
                    
                    async function sendMessage() {
                        const message = messageInput.value.trim();
                        if (!message) return;
                        
                        messageInput.value = '';
                        addMessage('user', message);
                        
                        // Уведомляем Python
                        if (bridge && typeof bridge.send_message === 'function') {
                            try {
                                bridge.send_message(message);
                            } catch (error) {
                                console.error('Error calling bridge.send_message:', error);
                            }
                        } else {
                            console.warn('Bridge not available or send_message method not found');
                        }
                        
                        try {
                            const response = await puter.ai.chat(message, {
                                model: currentModel,
                                stream: true
                            });
                            
                            const messageElement = addMessage('ai', '', true);
                            let fullResponse = '';
                            
                            for await (const part of response) {
                                if (part?.text) {
                                    fullResponse += part.text;
                                    updateMessage(messageElement, fullResponse);
                                }
                            }
                            
                            // Уведомляем Python о полном ответе
                            if (bridge && fullResponse && typeof bridge.receive_ai_message === 'function') {
                                try {
                                    bridge.receive_ai_message(currentModel, fullResponse);
                                } catch (error) {
                                    console.error('Error calling bridge.receive_ai_message:', error);
                                }
                            }
                            
                        } catch (error) {
                            addMessage('ai', `❌ Error: ${error.message}`);
                            if (bridge && typeof bridge.log_error === 'function') {
                                try {
                                    bridge.log_error(error.message);
                                } catch (bridgeError) {
                                    console.error('Error calling bridge.log_error:', bridgeError);
                                }
                            }
                        }
                    }
                    
                    function addMessage(type, content, isStreaming = false) {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `message ${type}-message`;
                        messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
                        
                        if (isStreaming) {
                            messageDiv.classList.add('streaming');
                        }
                        
                        messagesContainer.appendChild(messageDiv);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        return messageDiv;
                    }
                    
                    function updateMessage(messageElement, content) {
                        messageElement.innerHTML = content.replace(/\\n/g, '<br>');
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                });
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content)
    
    def set_theme_manager(self, theme_manager):
        """Установка менеджера тем для интеграции с глобальной темой"""
        print(f"🎨 WebView chat: Установка theme_manager: {theme_manager}")
        self.theme_manager = theme_manager
        
        # Подключаемся к сигналу смены темы если он есть
        if hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)
            print("🎨 WebView chat: Подключен к сигналу theme_changed")
        
        # Применяем текущую тему
        print("🎨 WebView chat: Применяем текущую тему...")
        self._apply_theme_to_webview()
    
    def _on_theme_changed(self):
        """Обработчик смены темы"""
        print("Theme changed, updating WebView chat...")
        self._apply_theme_to_webview()
    
    def _apply_theme_to_webview(self):
        """Применение глобальной темы к WebView с полным переопределением стилей"""
        print("🎨 WebView chat: Начинаем применение темы...")
        if not self.theme_manager:
            print("⚠️ WebView chat: theme_manager не установлен")
            return
        
        # Проверяем, что WebView загружен
        if not hasattr(self, 'web_view') or not self.web_view.page():
            print("⚠️ WebView chat: страница еще не загружена, откладываем применение темы")
            # Устанавливаем флаг для применения темы после загрузки
            self._theme_pending = True
            return
        
        # Получаем цвета текущей темы
        theme_colors = self._get_theme_colors()
        
        # Создаем более подробные CSS переменные для полной интеграции
        css_variables = self._generate_css_variables(theme_colors)
        
        # Инъекция CSS переменных в WebView
        css_injection = f"""
        :root {{
            {css_variables}
        }}
        
        /* Применяем плавные переходы при смене темы */
        *, *::before, *::after {{
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }}
        """
        
        # Применяем CSS через JavaScript
        script = f"""
        // Удаляем предыдущие темы если есть
        const existingThemeStyles = document.querySelectorAll('[data-gopiai-theme]');
        existingThemeStyles.forEach(style => style.remove());
        
        // Создаем новый элемент стилей
        const style = document.createElement('style');
        style.setAttribute('data-gopiai-theme', 'true');
        style.textContent = `{css_injection}`;
        document.head.appendChild(style);
        
        // Уведомляем об обновлении темы если есть соответствующий обработчик
        if (window.gopiaiChat && window.gopiaiChat.onThemeUpdated) {{
            window.gopiaiChat.onThemeUpdated();
        }}
        
        console.log('GopiAI theme applied to WebView chat');
        """
        
        self.web_view.page().runJavaScript(script)
    
    def _generate_css_variables(self, theme_colors: dict) -> str:
        """Генерация CSS переменных из цветов темы"""
        variables = []
        
        # Основные цвета
        variables.append(f"--bg-primary: {theme_colors.get('background', '#1e1e1e')};")
        variables.append(f"--bg-secondary: {theme_colors.get('header_bg', '#2d2d2d')};")
        variables.append(f"--bg-tertiary: {theme_colors.get('input_bg', '#2a2a2a')};")
        
        # Цвета текста
        variables.append(f"--text-primary: {theme_colors.get('text', '#ffffff')};")
        variables.append(f"--text-secondary: {theme_colors.get('text_secondary', theme_colors.get('text', '#ffffff'))};")
        variables.append(f"--text-muted: {self._adjust_opacity(theme_colors.get('text', '#ffffff'), 0.6)};")
        
        # Акцентные цвета
        variables.append(f"--accent-primary: {theme_colors.get('accent_color', '#0078d4')};")
        variables.append(f"--accent-secondary: {self._darken_color(theme_colors.get('accent_color', '#0078d4'), 0.1)};")
        
        # Границы и рамки
        variables.append(f"--border-color: {theme_colors.get('border', '#333333')};")
        
        # Сообщения
        variables.append(f"--user-message-bg: {theme_colors.get('user_message', theme_colors.get('accent_color', '#0078d4'))};")
        variables.append(f"--user-message-text: {theme_colors.get('user_message_text', '#ffffff')};")
        variables.append(f"--ai-message-bg: {theme_colors.get('ai_message', theme_colors.get('messages_bg', '#2d2d2d'))};")
        variables.append(f"--ai-message-text: {theme_colors.get('ai_message_text', theme_colors.get('text', '#ffffff'))};")
        
        # Поля ввода
        variables.append(f"--input-bg: {theme_colors.get('input_bg', theme_colors.get('background', '#1e1e1e'))};")
        variables.append(f"--input-text: {theme_colors.get('text', '#ffffff')};")
        
        # Кнопки
        variables.append(f"--button-bg: {theme_colors.get('button', theme_colors.get('control_color', '#0078d4'))};")
        variables.append(f"--button-hover-bg: {theme_colors.get('button_hover', self._lighten_color(theme_colors.get('control_color', '#0078d4'), 0.1))};")
        variables.append(f"--button-active-bg: {theme_colors.get('button_active', self._darken_color(theme_colors.get('control_color', '#0078d4'), 0.1))};")
        variables.append(f"--button-text: {theme_colors.get('button_text', '#ffffff')};")
        
        # Заголовок
        variables.append(f"--header-bg: {theme_colors.get('header_bg', theme_colors.get('header_color', '#2d2d2d'))};")
        variables.append(f"--header-text: {theme_colors.get('header_text', theme_colors.get('text', '#ffffff'))};")
        
        # Системные цвета
        variables.append(f"--error-color: #ff4444;")
        variables.append(f"--success-color: #00cc66;")
        variables.append(f"--warning-color: #ffaa00;")
        
        # Индикатор набора
        variables.append(f"--typing-indicator-color: {theme_colors.get('accent_color', '#0078d4')};")
        
        # Модальные окна
        variables.append(f"--modal-overlay: rgba(0, 0, 0, 0.5);")
        variables.append(f"--modal-bg: {theme_colors.get('background', '#1e1e1e')};")
        
        # Скроллбар
        variables.append(f"--scrollbar-track: {theme_colors.get('header_bg', '#2d2d2d')};")
        variables.append(f"--scrollbar-thumb: {theme_colors.get('border', '#333333')};")
        variables.append(f"--scrollbar-thumb-hover: {self._lighten_color(theme_colors.get('border', '#333333'), 0.2)};")
        
        # Тени
        shadow_color = "0, 0, 0" if self._is_dark_theme(theme_colors.get('background', '#1e1e1e')) else "0, 0, 0"
        variables.append(f"--shadow-light: 0 2px 8px rgba({shadow_color}, 0.1);")
        variables.append(f"--shadow-medium: 0 4px 16px rgba({shadow_color}, 0.2);")
        
        return '\n            '.join(variables)
    
    def _adjust_opacity(self, hex_color: str, opacity: float) -> str:
        """Корректировка прозрачности цвета"""
        try:
            # Убираем # если есть
            hex_color = hex_color.lstrip('#')
            
            # Конвертируем в RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Возвращаем RGBA
            return f"rgba({r}, {g}, {b}, {opacity})"
        except:
            return f"rgba(255, 255, 255, {opacity})"
    
    def _is_dark_theme(self, bg_color: str) -> bool:
        """Определение темной ли темы"""
        try:
            # Убираем # если есть
            hex_color = bg_color.lstrip('#')
            
            # Конвертируем в RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Вычисляем яркость (luminance)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            return luminance < 0.5
        except:
            return True  # По умолчанию считаем темной
    
    def _get_theme_colors(self) -> dict:
        """Получение цветов из текущей темы GopiAI-UI с более точным маппингом"""
        if not self.theme_manager:
            return self._get_fallback_colors()
        
        try:
            # Получаем данные текущей темы
            theme_data = None
            if hasattr(self.theme_manager, 'get_current_theme_data'):
                theme_data = self.theme_manager.get_current_theme_data()
            elif hasattr(self.theme_manager, 'load_theme'):
                theme_data = self.theme_manager.load_theme()
            
            if not theme_data:
                return self._get_fallback_colors()
            
            # Извлекаем основные цвета из темы GopiAI
            main_color = theme_data.get('main_color', '#1e1e1e')
            text_color = theme_data.get('text_color', '#ffffff')
            header_color = theme_data.get('header_color', '#2d2d2d')
            control_color = theme_data.get('control_color', '#0078d4')
            accent_color = theme_data.get('accent_color', '#7a4c8f')
            button_color = theme_data.get('button_color', '#3d6281')
            button_hover_color = theme_data.get('button_hover_color', '#4d6d88')
            button_active_color = theme_data.get('button_active_color', control_color)
            border_color = theme_data.get('border_color', '#75777b')
            titlebar_background = theme_data.get('titlebar_background', header_color)
            titlebar_text = theme_data.get('titlebar_text', text_color)
            
            # Генерируем производные цвета для чата
            chat_colors = {
                'background': main_color,
                'text': text_color,
                'text_secondary': self._adjust_brightness(text_color, -0.2),
                'border': border_color,
                'header_bg': header_color,
                'header_color': header_color,  # Для совместимости
                'header_text': titlebar_text,
                
                # Цвета сообщений - используем существующие цвета темы
                'messages_bg': self._lighten_color(main_color, 0.03),
                'user_message': control_color,  # Используем основной control_color для сообщений пользователя
                'ai_message': self._lighten_color(main_color, 0.08),
                
                # Поля ввода
                'input_bg': self._lighten_color(main_color, 0.05),
                
                # Кнопки - точное соответствие теме GopiAI
                'button': control_color,
                'control_color': control_color,  # Для совместимости
                'button_hover': button_hover_color,
                'button_active': button_active_color,
                
                # Акцентные цвета
                'accent_color': accent_color,
                
                # Контрастные цвета текста
                'user_message_text': self._get_contrast_text(control_color),
                'ai_message_text': text_color,
                'button_text': self._get_contrast_text(control_color),
                'header_text': titlebar_text,
                
                # Системные сообщения
                'system_message': self._lighten_color(button_color, 0.2),
                
                # Статус-бары и дополнительные элементы
                'scrollbar_track': self._lighten_color(main_color, 0.1),
                'scrollbar_thumb': border_color,
            }
            
            return chat_colors
            
        except Exception as e:
            print(f"Error getting theme colors: {e}")
            return self._get_fallback_colors()
    
    def _adjust_brightness(self, hex_color: str, factor: float) -> str:
        """Корректировка яркости цвета (положительный factor = светлее, отрицательный = темнее)"""
        try:
            # Убираем # если есть
            hex_color = hex_color.lstrip('#')
            
            # Конвертируем в RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            if factor > 0:
                # Осветляем
                r = min(255, int(r + (255 - r) * factor))
                g = min(255, int(g + (255 - g) * factor))
                b = min(255, int(b + (255 - b) * factor))
            else:
                # Затемняем
                factor = abs(factor)
                r = max(0, int(r * (1 - factor)))
                g = max(0, int(g * (1 - factor)))
                b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def _get_fallback_colors(self) -> dict:
        """Запасные цвета если тема недоступна"""
        return {
            'background': '#1e1e1e',
            'text': '#ffffff',
            'border': '#333333',
            'header_bg': '#2d2d2d',
            'messages_bg': '#252525',
            'user_message': '#0078d4',
            'ai_message': '#2d2d2d',
            'input_bg': '#2a2a2a',
            'button': '#0078d4',
            'button_hover': '#106ebe',
            'button_active': '#005a9e',
            'system_message': '#505050',
            'user_message_text': '#ffffff',
            'ai_message_text': '#ffffff',
            'button_text': '#ffffff'
        }
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Осветление цвета на заданный коэффициент"""
        try:
            # Убираем # если есть
            hex_color = hex_color.lstrip('#')
            
            # Конвертируем в RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Осветляем
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Затемнение цвета на заданный коэффициент"""
        try:
            # Убираем # если есть
            hex_color = hex_color.lstrip('#')
            
            # Конвертируем в RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Затемняем
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def _get_contrast_text(self, bg_color: str) -> str:
        """Определение контрастного цвета текста для фона"""
        try:
            # Убираем # если есть
            hex_color = bg_color.lstrip('#')
            
            # Конвертируем в RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Вычисляем яркость (luminance)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Возвращаем черный или белый в зависимости от яркости
            return '#000000' if luminance > 0.5 else '#ffffff'
        except:
            return '#ffffff'
    
    def send_message_to_ai(self, message: str):
        """Программная отправка сообщения в чат"""
        script = f"""
        if (window.gopiaiChat) {{
            window.gopiaiChat.messageInput.value = `{message}`;
            window.gopiaiChat.sendMessage();
        }}
        """
        self.web_view.page().runJavaScript(script)
    
    def clear_chat(self):
        """Очистка чата"""
        script = """
        if (window.gopiaiChat) {
            window.gopiaiChat.clearChat();
        }
        """
        self.web_view.page().runJavaScript(script)
    
    def change_model(self, model: str):
        """Смена модели ИИ"""
        script = f"""
        if (window.gopiaiChat) {{
            window.gopiaiChat.changeModel('{model}');
        }}
        """
        self.web_view.page().runJavaScript(script)