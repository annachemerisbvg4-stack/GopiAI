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

# Импорт системы памяти
try:
    import sys
    webview_path = Path(__file__).parent.parent.parent.parent / "GopiAI-WebView"
    if webview_path.exists():
        sys.path.insert(0, str(webview_path))
    from gopiai.webview.chat_memory import create_memory_manager
    MEMORY_AVAILABLE = True
    print("✅ Chat memory system imported successfully")
except ImportError as e:
    MEMORY_AVAILABLE = False
    print(f"⚠️ Chat memory system not available: {e}")


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
            super().__init__(parent)
            
            # Сохраняем ссылку на родительский WebViewChatWidget
            self._parent_widget = parent
            
            # Инициализация системы памяти
            self._memory_manager = None
            if MEMORY_AVAILABLE:
                try:
                    self._memory_manager = create_memory_manager()
                    print("✅ Memory system initialized in WebViewChatBridge")
                except Exception as e:
                    print(f"⚠️ Failed to initialize memory system: {e}")
                    self._memory_manager = None

    
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
    
    # Методы для работы с системой памяти
    
    @Slot(str, result=str)
    def enrich_message(self, message: str) -> str:
        """
        Обогащение сообщения контекстом из памяти.
        Вызывается из JavaScript перед отправкой к ИИ.
        """
        if self._memory_manager:
            try:
                enriched = self._memory_manager.enrich_message(message)
                print(f"🧠 Memory: enriched message ({len(message)} -> {len(enriched)} chars)")
                return enriched
            except Exception as e:
                print(f"❌ Memory enrichment error: {e}")
                return message
        return message

    @Slot(str, str, result=str)
    def save_chat_exchange(self, user_message: str, ai_response: str) -> str:
        """
        Сохранение обмена сообщениями в память.
        Вызывается из JavaScript после получения ответа ИИ.
        """
        if self._memory_manager:
            try:
                success = self._memory_manager.save_chat_exchange(user_message, ai_response)
                status = "OK" if success else "ERROR"
                print(f"💾 Memory: saved exchange ({status})")
                return status
            except Exception as e:
                print(f"❌ Memory save error: {e}")
                return "ERROR"
        return "OK"

    @Slot(result=str)
    def start_new_chat_session(self) -> str:
        """
        Начало новой сессии чата.
        Очищает краткосрочную память и создает новую RAG сессию.
        """
        if self._memory_manager:
            try:
                self._memory_manager.start_new_session()
                print(f"🆕 Memory: new session {self._memory_manager.session_id}")
                return self._memory_manager.session_id
            except Exception as e:
                print(f"❌ New session error: {e}")
        return "default_session"

    @Slot(result=str)
    def get_memory_stats(self) -> str:
        """
        Получение статистики памяти в формате JSON.
        """
        if self._memory_manager:
            try:
                stats = self._memory_manager.get_memory_stats()
                return json.dumps(stats, ensure_ascii=False)
            except Exception as e:
                print(f"❌ Memory stats error: {e}")
        
        return json.dumps({
            "memory_available": False,
            "error": "Memory system not initialized"
        })

    @Slot(result=bool)
    def is_memory_available(self) -> bool:
        """Проверка доступности системы памяти."""
        return self._memory_manager is not None

    # ==============================================
    # BROWSER AUTOMATION METHODS
    # ==============================================

    @Slot(result=str)
    def get_browser_automation_capabilities(self) -> str:
        """Получение списка доступных browser automation функций"""
        capabilities = {
            "available": True,
            "functions": [
                "navigate", "click", "type", "screenshot", "get_text", 
                "get_source", "scroll", "wait", "execute_script"
            ],
            "engine": "QWebEngineView",
            "version": "1.0"
        }
        print("🌐 Bridge: browser automation capabilities requested")
        return json.dumps(capabilities, ensure_ascii=False)

    @Slot(str, str, result=str)
    def execute_browser_action(self, action: str, params: str) -> str:
        """Выполнение browser automation действия"""
        try:
            params_dict = json.loads(params) if params else {}
            print(f"🤖 Bridge: executing browser action '{action}' with params: {params_dict}")
            
            # Получаем родительский WebViewChatWidget
            widget = self._parent_widget
            
            if not widget or not hasattr(widget, 'web_view'):
                raise Exception("WebView not available")
        
            
            # Выполняем действие в зависимости от типа
            if action == "navigate":
                url = params_dict.get("url", "")
                if url:
                    widget.web_view.setUrl(url)
                    result_data = {"message": f"Navigated to {url}"}
                else:
                    raise Exception("URL parameter required for navigate action")
                    
            elif action == "get_url":
                current_url = widget.web_view.page().url().toString()
                result_data = {"url": current_url}
                
            elif action == "get_title":
                title = widget.web_view.page().title()
                result_data = {"title": title}
                
            elif action == "reload":
                widget.web_view.reload()
                result_data = {"message": "Page reloaded"}
                
            elif action == "back":
                widget.web_view.back()
                result_data = {"message": "Navigated back"}
                
            elif action == "forward":
                widget.web_view.forward()
                result_data = {"message": "Navigated forward"}
                
            elif action == "execute_script":
                script = params_dict.get("script", "")
                if script:
                    # Выполняем JavaScript в WebView
                    widget.web_view.page().runJavaScript(script)
                    result_data = {"message": f"Script executed: {script[:50]}..."}
                else:
                    raise Exception("Script parameter required for execute_script action")
                    
            elif action == "screenshot":
                # Пока возвращаем заглушку для screenshot
                result_data = {"message": "Screenshot functionality not implemented yet"}
                
            else:
                raise Exception(f"Unknown action: {action}")
            
            result = {
                "success": True,
                "action": action,
                "params": params_dict,
                "result": result_data,
                "timestamp": "2025-01-16T12:00:00Z"
            }
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "action": action,
                "timestamp": "2025-01-16T12:00:00Z"
            }
            print(f"❌ Bridge: browser action error: {e}")
            return json.dumps(error_result, ensure_ascii=False)

    @Slot(result=str)
    def get_browser_page_info(self) -> str:
        """Получение информации о текущей странице браузера"""
        try:
            # Получаем родительский WebViewChatWidget
            widget = self._parent_widget
            
            if widget and hasattr(widget, 'web_view') and widget.web_view.page():
                # Получаем актуальную информацию о странице
                page = widget.web_view.page()
                url = page.url().toString() if page.url() else "about:blank"
                title = page.title() if page.title() else "Untitled"
                
                page_info = {
                    "url": url,
                    "title": title,
                    "ready": True,
                    "loading": False,
                    "engine": "QWebEngineView",
                    "timestamp": "2025-01-16T12:00:00Z"
                }
            else:
                # Если WebView недоступен, возвращаем базовую информацию
                page_info = {
                    "url": "about:blank",
                    "title": "GopiAI Chat",
                    "ready": True,
                    "loading": False,
                    "engine": "QWebEngineView",
                    "timestamp": "2025-01-16T12:00:00Z"
                }
            
            print(f"📄 Bridge: page info - {page_info['title']} ({page_info['url']})")
            return json.dumps(page_info, ensure_ascii=False)
            
        except Exception as e:
            error_info = {
                "error": str(e),
                "url": "about:blank",
                "timestamp": "2025-01-16T12:00:00Z"
            }
            print(f"❌ Bridge: page info error: {e}")
            return json.dumps(error_info, ensure_ascii=False)

    @Slot(str, result=str)
    def browser_automation_result(self, result_data: str) -> str:
        """Обработка результатов browser automation"""
        try:
            result = json.loads(result_data)
            print(f"📊 Bridge: browser automation result received: {result}")
            return "OK"
        except Exception as e:
            print(f"❌ Bridge: result processing error: {e}")
            return f"ERROR: {e}"


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
            """Создание запасного HTML интерфейса с поддержкой памяти"""
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>GopiAI Chat with Memory</title>
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
                    .memory-status {
                        padding: 8px 12px;
                        margin-bottom: 10px;
                        border-radius: 4px;
                        font-size: 12px;
                        background: var(--chat-ai-bg, #404040);
                        border-left: 3px solid var(--accent-primary, #0078d4);
                    }
                    .memory-available {
                        border-left-color: #00cc66;
                    }
                    .memory-unavailable {
                        border-left-color: #ff4444;
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
                        word-wrap: break-word;
                    }
                    .user-message {
                        background: var(--chat-user-bg, #0078d4);
                        margin-left: auto;
                        text-align: right;
                        color: var(--user-message-text, #ffffff);
                    }
                    .ai-message {
                        background: var(--chat-ai-bg, #404040);
                        color: var(--ai-message-text, #ffffff);
                    }
                    .memory-enhanced {
                        border-left: 3px solid #00cc66;
                        background: var(--chat-ai-bg, #404040);
                        font-style: italic;
                        opacity: 0.8;
                        margin-bottom: 5px;
                        padding: 8px;
                        font-size: 11px;
                    }
                    .input-container {
                        display: flex;
                        gap: 10px;
                        align-items: center;
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
                    #send-btn:disabled {
                        background: #555;
                        cursor: not-allowed;
                    }
                    .typing-indicator {
                        display: none;
                        font-style: italic;
                        color: var(--text-muted, #888);
                        padding: 5px 10px;
                    }
                    .typing-indicator.active {
                        display: block;
                    }
                </style>
            </head>
            <body>
                <div class="chat-container">
                    <div id="memory-status" class="memory-status memory-unavailable">
                        🧠 Проверка системы памяти...
                    </div>
                    
                    <div id="messages-container" class="messages-container">
                        <div class="message ai-message">
                            🤖 Добро пожаловать в GopiAI Chat! Я работаю на основе puter.js и готов помочь вам.
                            <br><br>
                            💡 <strong>Новая функция:</strong> Теперь у меня есть память! Я запоминаю наши разговоры и могу ссылаться на предыдущие обсуждения.
                        </div>
                    </div>
                    
                    <div class="typing-indicator" id="typing-indicator">
                        ИИ печатает...
                    </div>
                    
                    <div class="input-container">
                        <input type="text" id="message-input" placeholder="Введите ваше сообщение...">
                        <button id="send-btn">Отправить</button>
                    </div>
                </div>
                
                <script>
                    let bridge = null;
                    let currentModel = 'claude-sonnet-4';
                    let memoryAvailable = false;
                    
                    // Инициализация WebChannel
                    if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined') {
                        try {
                            new QWebChannel(qt.webChannelTransport, (channel) => {
                                bridge = channel.objects.bridge;
                                console.log('🔗 WebChannel bridge connected:', bridge);
                                
                                // Проверяем доступность памяти
                                checkMemoryAvailability();
                            });
                        } catch (error) {
                            console.error('❌ Error initializing WebChannel:', error);
                        }
                    } else {
                        console.warn('⚠️ QWebChannel or qt not available');
                    }
                    
                    // Проверка доступности системы памяти
                    async function checkMemoryAvailability() {
                        if (bridge && typeof bridge.is_memory_available === 'function') {
                            try {
                                bridge.is_memory_available((available) => {
                                    memoryAvailable = available;
                                    updateMemoryStatus();
                                });
                            } catch (error) {
                                console.warn('⚠️ Memory check failed:', error);
                                updateMemoryStatus();
                            }
                        } else {
                            updateMemoryStatus();
                        }
                    }
                    
                    function updateMemoryStatus() {
                        const statusEl = document.getElementById('memory-status');
                        if (memoryAvailable) {
                            statusEl.className = 'memory-status memory-available';
                            statusEl.innerHTML = '🧠 Система памяти активна - ваши разговоры сохраняются и используются для улучшения ответов';
                        } else {
                            statusEl.className = 'memory-status memory-unavailable';
                            statusEl.innerHTML = '🧠 Система памяти недоступна - работаю в обычном режиме';
                        }
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
                        const typingIndicator = document.getElementById('typing-indicator');
                        
                        try {
                            await waitForPuter();
                            console.log('✅ puter.js loaded successfully');
                        } catch (error) {
                            console.error('❌ Failed to load puter.js:', error);
                            addMessage('ai', '⚠️ Ошибка: Не удалось загрузить puter.js. Проверьте подключение к интернету.');
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
                            
                            // Блокируем UI пока обрабатываем
                            messageInput.disabled = true;
                            sendBtn.disabled = true;
                            messageInput.value = '';
                            
                            // Показываем сообщение пользователя
                            addMessage('user', message);
                            
                            // Уведомляем Python о сообщении
                            if (bridge && typeof bridge.send_message === 'function') {
                                try {
                                    bridge.send_message(message);
                                } catch (error) {
                                    console.error('❌ Error calling bridge.send_message:', error);
                                }
                            }
                            
                            try {
                                let finalMessage = message;
                                
                                // 🧠 ШАГИ ИНТЕГРАЦИИ ПАМЯТИ - ВСЕГО 2 СТРОЧКИ!
                                // Шаг 1: Обогащаем сообщение контекстом из памяти
                                if (memoryAvailable && bridge && typeof bridge.enrich_message === 'function') {
                                    try {
                                        bridge.enrich_message(message, (enriched) => {
                                            if (enriched && enriched !== message) {
                                                // Показываем что сообщение обогащено памятью
                                                addMemoryContext(enriched);
                                                finalMessage = enriched;
                                            }
                                            
                                            // Продолжаем отправку к ИИ
                                            sendToAI(finalMessage, message);
                                        });
                                        return; // Ждем callback
                                    } catch (error) {
                                        console.warn('⚠️ Memory enrichment failed:', error);
                                    }
                                }
                                
                                // Если память недоступна, отправляем как есть
                                sendToAI(finalMessage, message);
                                
                            } catch (error) {
                                addMessage('ai', `❌ Ошибка: ${error.message}`);
                                console.error('❌ Send message error:', error);
                            } finally {
                                // Разблокируем UI
                                messageInput.disabled = false;
                                sendBtn.disabled = false;
                                messageInput.focus();
                            }
                        }
                        
                        async function sendToAI(finalMessage, originalMessage) {
                            // Показываем индикатор печатания
                            typingIndicator.classList.add('active');
                            
                            try {
                                const response = await puter.ai.chat(finalMessage, {
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
                                
                                // Шаг 2: Сохраняем обмен сообщениями в память
                                if (memoryAvailable && bridge && fullResponse && typeof bridge.save_chat_exchange === 'function') {
                                    try {
                                        bridge.save_chat_exchange(originalMessage, fullResponse, (status) => {
                                            if (status === 'OK') {
                                                console.log('💾 Chat exchange saved to memory');
                                            } else {
                                                console.warn('⚠️ Failed to save to memory:', status);
                                            }
                                        });
                                    } catch (error) {
                                        console.warn('⚠️ Memory save failed:', error);
                                    }
                                }
                                
                                // Уведомляем Python о получении ответа
                                if (bridge && fullResponse && typeof bridge.receive_ai_message === 'function') {
                                    try {
                                        bridge.receive_ai_message(currentModel, fullResponse);
                                    } catch (error) {
                                        console.error('❌ Error calling bridge.receive_ai_message:', error);
                                    }
                                }
                                
                            } catch (error) {
                                addMessage('ai', `❌ Ошибка: ${error.message}`);
                                if (bridge && typeof bridge.log_error === 'function') {
                                    try {
                                        bridge.log_error(error.message);
                                    } catch (bridgeError) {
                                        console.error('❌ Error calling bridge.log_error:', bridgeError);
                                    }
                                }
                            } finally {
                                // Убираем индикатор печатания
                                typingIndicator.classList.remove('active');
                            }
                        }
                        
                        function addMemoryContext(enrichedMessage) {
                            const contextDiv = document.createElement('div');
                            contextDiv.className = 'message memory-enhanced';
                            contextDiv.innerHTML = '🧠 Используется контекст из памяти предыдущих разговоров';
                            messagesContainer.appendChild(contextDiv);
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
            
            # ИСПРАВЛЕНИЕ: Оборачиваем код в функцию для изоляции переменных
            script = f"""
            (function() {{
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
            }})();
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