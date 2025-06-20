"""
JavaScript Bridge для GopiAI WebView

Обеспечивает двустороннюю связь между Python и JavaScript кодом
через QWebChannel для управления чатом с ИИ.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

# Импорт НОВОГО txtai менеджера памяти
try:
    import sys
    from pathlib import Path
    # Добавляем путь к rag_memory_system
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from rag_memory_system import get_memory_manager
    MEMORY_AVAILABLE = True
    print("✅ TxtAI memory system imported successfully")
except ImportError as e:
    MEMORY_AVAILABLE = False
    print(f"⚠️ TxtAI memory system not available: {e}")


class JavaScriptBridge(QObject):
    """
    Мост для связи между Python и JavaScript кодом.
    
    Предоставляет слоты для вызова из JavaScript и сигналы
    для уведомления Python кода о событиях в веб-интерфейсе.
    """
    
    # Сигналы для уведомления Python кода
    message_sent = Signal(str)  # Сообщение отправлено пользователем
    message_received = Signal(str, str)  # Получен ответ ИИ (model, message)
    chat_cleared = Signal()  # Чат очищен
    model_changed = Signal(str)  # Изменена модель ИИ
    error_occurred = Signal(str)  # Произошла ошибка
    browser_action_completed = Signal(str, str, str)  # Browser automation завершен (action_id, action, result)
    def __init__(self, parent: Optional[QObject] = None):
            """
            Инициализация моста.
            
            Args:
                parent: Родительский объект
            """
            super().__init__(parent)
            
            # История чата
            self._chat_history: List[Dict[str, Any]] = []
            
            # Текущая модель
            self._current_model = "claude-sonnet-4"
            
            # Родительский виджет для browser automation
            self._parent_widget = parent
            
            # Отладочный вывод для проверки загрузки методов
            print("🔧 JavaScriptBridge initialized with browser automation methods!")
            print(f"   Available methods: {[m for m in dir(self) if 'browser' in m.lower()]}")
            
            # Инициализация НОВОЙ системы памяти
            self._memory_manager = None
            if MEMORY_AVAILABLE:
                try:
                    self._memory_manager = get_memory_manager()
                    # Создаем новую сессию
                    session = self._memory_manager.create_session("GopiAI Chat Session")
                    self._current_session_id = session
                    print("✅ TxtAI memory system initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize TxtAI memory: {e}")
                    self._memory_manager = None
            
            # Инициализация Claude Tools Handler
            self._claude_tools_handler = None
            print("🔧 Claude Tools Handler initialized (placeholder)")

    
    @Slot(result=str)
    def test_new_method(self) -> str:
        """ТЕСТОВЫЙ МЕТОД - если он появится в bridge, значит код обновился!"""
        return "NEW_CODE_LOADED"
    
    @Slot(str)
    def send_message(self, message: str):
        """
        Слот для отправки сообщения из JavaScript.
        
        Args:
            message: Текст сообщения от пользователя
        """
        try:
            # Добавление сообщения в историю
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "model": self._current_model
            }
            self._chat_history.append(user_message)
            
            # Уведомление Python кода
            self.message_sent.emit(message)
            
        except Exception as e:
            self.error_occurred.emit(f"Error sending message: {str(e)}")
    
    @Slot(str, str)
    def receive_ai_message(self, model: str, message: str):
        """
        Слот для получения ответа ИИ из JavaScript.
        
        Args:
            model: Название модели ИИ
            message: Текст ответа ИИ
        """
        try:
            # Добавление ответа в историю
            ai_message = {
                "role": "assistant",
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "model": model
            }
            self._chat_history.append(ai_message)
            
            # Уведомление Python кода
            self.message_received.emit(model, message)
            
        except Exception as e:
            self.error_occurred.emit(f"Error receiving AI message: {str(e)}")
    
    @Slot()
    def clear_chat(self):
        """Слот для очистки чата из JavaScript."""
        try:
            self._chat_history.clear()
            
            # Создаем новую сессию памяти
            if self._memory_manager:
                session = self._memory_manager.create_session("New GopiAI Chat")
                self._current_session_id = session
                print("🔄 New memory session created")
            
            self.chat_cleared.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Error clearing chat: {str(e)}")
    
    @Slot(str)
    def change_model(self, model: str):
        """
        Слот для изменения модели ИИ из JavaScript.
        
        Args:
            model: Название новой модели
        """
        try:
            if model in ["claude-sonnet-4", "claude-opus-4"]:
                self._current_model = model
                self.model_changed.emit(model)
            else:
                self.error_occurred.emit(f"Unknown model: {model}")
        except Exception as e:
            self.error_occurred.emit(f"Error changing model: {str(e)}")
    
    @Slot(str)
    def log_error(self, error_message: str):
        """
        Слот для логирования ошибок из JavaScript.
        
        Args:
            error_message: Сообщение об ошибке
        """
        self.error_occurred.emit(f"JS Error: {error_message}")
    
    @Slot(result=str)
    def get_chat_history_json(self) -> str:
        """
        Слот для получения истории чата в формате JSON.
        
        Returns:
            История чата в формате JSON
        """
        try:
            return json.dumps(self._chat_history, ensure_ascii=False, indent=2)
        except Exception as e:
            self.error_occurred.emit(f"Error getting chat history: {str(e)}")
            return "[]"
    
    @Slot(result=str)
    def get_current_model(self) -> str:
        """
        Слот для получения текущей модели ИИ.
        
        Returns:
            Название текущей модели
        """
        return self._current_model
    
    # Методы для вызова из Python кода
    
    def send_message_to_chat(self, message: str):
        """
        Отправка сообщения в чат из Python кода.
        
        Args:
            message: Текст сообщения
        """
        # Этот метод может быть использован для отправки сообщений
        # в веб-интерфейс из Python кода
        pass
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Получение истории чата.
        
        Returns:
            Список сообщений
        """
        return self._chat_history.copy()
    
    def set_model(self, model: str):
        """
        Установка модели ИИ из Python кода.
        
        Args:
            model: Название модели
        """
        if model in ["claude-sonnet-4", "claude-opus-4"]:
            self._current_model = model
            self.model_changed.emit(model)
    
    def export_chat(self, format_type: str = "json") -> str:
        """
        Экспорт истории чата в различных форматах.
        
        Args:
            format_type: Формат экспорта ('json', 'txt', 'md')
            
        Returns:
            Экспортированные данные
        """
        try:
            if format_type == "json":
                return json.dumps(self._chat_history, ensure_ascii=False, indent=2, default=str)
            
            elif format_type == "txt":
                lines = []
                for msg in self._chat_history:
                    role = "User" if msg["role"] == "user" else f"AI ({msg['model']})"
                    timestamp = msg.get("timestamp", "")
                    content = msg.get("content", "")
                    lines.append(f"[{timestamp}] {role}: {content}")
                return "\n".join(lines)
            
            elif format_type == "md":
                lines = ["# Chat History", ""]
                for msg in self._chat_history:
                    role = "**User**" if msg["role"] == "user" else f"**AI ({msg['model']})**"
                    timestamp = msg.get("timestamp", "")
                    content = msg.get("content", "")
                    lines.append(f"## {role} - {timestamp}")
                    lines.append(content)
                    lines.append("")
                return "\n".join(lines)
            
            else:
                return json.dumps(self._chat_history, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            self.error_occurred.emit(f"Error exporting chat: {str(e)}")
            return ""
    
    # ==============================================
    # МЕТОДЫ РАБОТЫ С ПАМЯТЬЮ (TXTAI)
    # ==============================================
    
    @Slot(str, result=str)
    def enrich_message(self, message: str) -> str:
        """
        Обогащение сообщения контекстом из памяти
        
        Args:
            message: Исходное сообщение пользователя
            
        Returns:
            Обогащенное сообщение с контекстом
        """
        if not self._memory_manager:
            return message
        
        try:
            enriched = self._memory_manager.enrich_message(message)
            print(f"🧠 Memory: enriched message ({len(enriched)} chars)")
            return enriched
        except Exception as e:
            print(f"❌ Memory enrichment error: {e}")
            return message
    
    @Slot(str, str, result=str)
    def save_chat_exchange(self, user_message: str, ai_response: str) -> str:
        """
        Сохранение обмена сообщениями в память
        
        Args:
            user_message: Сообщение пользователя
            ai_response: Ответ ИИ
            
        Returns:
            Статус сохранения (JSON)
        """
        if not self._memory_manager or not self._current_session_id:
            return json.dumps({"status": "error", "message": "Memory not available"})
        
        try:
            success = self._memory_manager.save_chat_exchange(
                self._current_session_id, 
                user_message, 
                ai_response
            )
            
            status = "success" if success else "error"
            print(f"💾 Memory: saved exchange ({status})")
            
            return json.dumps({
                "status": status,
                "session_id": self._current_session_id,
                "saved": success
            })
            
        except Exception as e:
            print(f"❌ Memory save error: {e}")
            return json.dumps({"status": "error", "message": str(e)})
    
    @Slot(result=str)
    def start_new_chat_session(self) -> str:
        """Начало новой сессии чата"""
        if not self._memory_manager:
            return json.dumps({"status": "error", "message": "Memory not available"})
        
        try:
            session = self._memory_manager.create_session("New GopiAI Chat")
            self._current_session_id = session
            
            return json.dumps({
                "status": "success",
                "session_id": self._current_session_id
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
    
    @Slot(result=str)
    def get_memory_stats(self) -> str:
        """Получение статистики памяти"""
        if not self._memory_manager:
            return json.dumps({"available": False})
        
        try:
            stats = self._memory_manager.get_stats()
            stats["available"] = True
            stats["current_session"] = self._current_session_id
            return json.dumps(stats)
            
        except Exception as e:
            return json.dumps({"available": False, "error": str(e)})
    
    @Slot(result=str) 
    def is_memory_available(self) -> str:
        """Проверка доступности памяти"""
        return json.dumps({"available": self._memory_manager is not None})
    
    # Методы для вызова из Python кода
    
    def process_python_message(self, message: str):
        """Получение сообщения из Python кода для отправки в JavaScript"""
        try:
            # Можно добавить логику для отправки сообщения в JavaScript
            pass
        except Exception as e:
            self.error_occurred.emit(f"Error processing Python message: {str(e)}")
    
    
    # ==============================================
    # BROWSER AUTOMATION METHODS
    # ==============================================

    @Slot(str, result=str)
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
            
            web_view = getattr(widget, 'web_view', None)
            if not web_view:
                raise Exception("WebView attribute not found")
            
            # Выполняем действие в зависимости от типа
            if action == "navigate":
                url = params_dict.get("url", "")
                if url:
                    web_view.setUrl(url)
                    result_data = {"message": f"Navigated to {url}"}
                else:
                    raise Exception("URL parameter required for navigate action")
                    
            elif action == "get_url":
                current_url = web_view.page().url().toString()
                result_data = {"url": current_url}
                
            elif action == "get_title":
                title = web_view.page().title()
                result_data = {"title": title}
                
            elif action == "reload":
                web_view.reload()
                result_data = {"message": "Page reloaded"}
                
            elif action == "back":
                web_view.back()
                result_data = {"message": "Navigated back"}
                
            elif action == "forward":
                web_view.forward()
                result_data = {"message": "Navigated forward"}
                
            elif action == "execute_script":
                script = params_dict.get("script", "")
                if script:
                    # Выполняем JavaScript в WebView с callback согласно Qt документации
                    def script_callback(result):
                        print(f"📜 JavaScript result: {result}")
                        # Результат будет обработан асинхронно
                        
                    web_view.page().runJavaScript(script, script_callback)
                    result_data = {"message": f"Script executed: {script[:50]}...", "note": "Result will be available asynchronously"}
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
            
            if widget and hasattr(widget, 'web_view'):
                web_view = getattr(widget, 'web_view', None)
                if web_view and web_view.page():
                    # Получаем актуальную информацию о странице
                    page = web_view.page()
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
            else:
                # Если widget недоступен, возвращаем базовую информацию
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

    @Slot(str, str)
    def execute_script_async(self, action_id: str, script: str) -> None:
        """
        Асинхронное выполнение JavaScript с правильной обработкой результата
        согласно официальной документации Qt
        """
        try:
            widget = self._parent_widget
            
            if not widget or not hasattr(widget, 'web_view'):
                raise Exception("WebView not available")
            
            web_view = getattr(widget, 'web_view', None)
            if not web_view:
                raise Exception("WebView attribute not found")
            
            print(f"🚀 Bridge: executing async script with ID {action_id}")
            print(f"📜 Script: {script[:100]}...")
            
            # Создаем callback функцию согласно Qt документации
            def script_result_callback(result):
                """
                Callback функция для получения результата JavaScript
                Вызывается асинхронно согласно Qt runJavaScript документации
                """
                try:
                    print(f"📨 Script callback for {action_id}: {result}")
                    
                    # Формируем результат согласно Qt документации:
                    # Поддерживаются: JSON types, Date, ArrayBuffer
                    # НЕ поддерживаются: Function, Promise
                    result_data = {
                        "success": True,
                        "action_id": action_id,
                        "result": result,
                        "type": type(result).__name__,
                        "timestamp": "2025-01-16T12:00:00Z"
                    }
                    
                    # Передаем результат через signal (НЕ блокируем callback)
                    result_json = json.dumps(result_data, ensure_ascii=False)
                    self.browser_action_completed.emit(action_id, "execute_script", result_json)
                    
                except Exception as e:
                    print(f"❌ Script callback error for {action_id}: {e}")
                    error_data = {
                        "success": False,
                        "action_id": action_id,
                        "error": str(e),
                        "timestamp": "2025-01-16T12:00:00Z"
                    }
                    error_json = json.dumps(error_data, ensure_ascii=False)
                    self.browser_action_completed.emit(action_id, "execute_script", error_json)
            
            # Выполняем JavaScript с callback согласно Qt документации
            # Пример из документации: page.runJavaScript("document.title", [](const QVariant &v) { qDebug() << v.toString(); });
            web_view.page().runJavaScript(script, script_result_callback)
            
            print(f"✅ Bridge: script {action_id} submitted for async execution")
            
        except Exception as e:
            print(f"❌ Bridge: execute_script_async error: {e}")
            error_data = {
                "success": False,
                "action_id": action_id,
                "error": str(e),
                "timestamp": "2025-01-16T12:00:00Z"
            }
            error_json = json.dumps(error_data, ensure_ascii=False)
            self.browser_action_completed.emit(action_id, "execute_script", error_json)

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
        
    # ==============================================
    # CLAUDE TOOLS INTEGRATION METHODS
    # ==============================================
    
    @Slot(str, str, result=str)
    def execute_claude_tool(self, tool_name: str, params: str) -> str:
        """Выполнение Claude tool через ClaudeToolsHandler"""
        if self._claude_tools_handler:
            try:
                # Генерируем request_id
                request_id = self._claude_tools_handler._generate_request_id()
                
                # Парсим параметры
                params_dict = json.loads(params) if params else {}
                
                print(f"🔧 Bridge: executing Claude tool '{tool_name}' with params: {params_dict}")
                
                # Выполняем инструмент в зависимости от типа
                if tool_name == "navigate_to_url":
                    return self._claude_tools_handler.navigate_to_url(params_dict.get('url', ''), request_id)
                elif tool_name == "get_current_url":
                    return self._claude_tools_handler.get_current_url()
                elif tool_name == "get_page_title":
                    return self._claude_tools_handler.get_page_title()
                elif tool_name == "execute_javascript":
                    return self._claude_tools_handler.execute_javascript(params_dict.get('script', ''), request_id)
                elif tool_name == "get_page_source":
                    return self._claude_tools_handler.get_page_source(request_id)
                elif tool_name == "wait_for_element":
                    return self._claude_tools_handler.wait_for_element(
                        params_dict.get('selector', ''), 
                        params_dict.get('timeout', 5000), 
                        request_id
                    )
                elif tool_name == "read_file":
                    return self._claude_tools_handler.read_file(params_dict.get('file_path', ''))
                elif tool_name == "write_file":
                    return self._claude_tools_handler.write_file(
                        params_dict.get('file_path', ''), 
                        params_dict.get('content', '')
                    )
                elif tool_name == "run_script":
                    return self._claude_tools_handler.run_script(params_dict.get('command', ''))
                elif tool_name == "search_memory":
                    return self._claude_tools_handler.search_memory(
                        params_dict.get('query', ''), 
                        params_dict.get('limit', 5)
                    )
                else:
                    error_result = {
                        "success": False,
                        "error": f"Unknown Claude tool: {tool_name}",
                        "available_tools": ["navigate_to_url", "get_current_url", "get_page_title", 
                                        "execute_javascript", "get_page_source", "wait_for_element",
                                        "read_file", "write_file", "run_script", "search_memory"]
                    }
                    return json.dumps(error_result)
                    
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "tool_name": tool_name
                }
                print(f"❌ Bridge: Claude tool execution error: {e}")
                return json.dumps(error_result)
        else:
            error_result = {
                "success": False,
                "error": "ClaudeToolsHandler not available"
            }
            return json.dumps(error_result)
    
    @Slot(result=str)
    def get_claude_tools_list(self) -> str:
        """Получение списка доступных Claude tools"""
        if self._claude_tools_handler:
            return self._claude_tools_handler.get_available_tools()
        else:
            result = {
                "success": False,
                "error": "ClaudeToolsHandler not available"
            }
            return json.dumps(result)
    
    @Slot(result=str)
    def get_pending_claude_requests(self) -> str:
        """Получение информации о ожидающих Claude запросах"""
        if self._claude_tools_handler:
            return self._claude_tools_handler.get_pending_requests()
        else:
            result = {
                "success": False,
                "error": "ClaudeToolsHandler not available"
            }
            return json.dumps(result)