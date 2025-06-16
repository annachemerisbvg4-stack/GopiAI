"""
JavaScript Bridge для GopiAI WebView

Обеспечивает двустороннюю связь между Python и JavaScript кодом
через QWebChannel для управления чатом с ИИ.
"""

import json
from typing import List, Dict, Any
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

# Импорт для системы памяти
try:
    from .chat_memory import create_memory_manager
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("⚠️ Chat memory system not available")


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
    
    def __init__(self, parent: QObject = None):
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
            
            # Отладочный вывод для проверки загрузки методов
            print("🔧 JavaScriptBridge initialized with browser automation methods!")
            print(f"   Available methods: {[m for m in dir(self) if 'browser' in m.lower()]}")
            
            # Инициализация системы памяти
            self._memory_manager = None
            if MEMORY_AVAILABLE:
                try:
                    self._memory_manager = create_memory_manager()
                    print("✅ Chat memory system initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize memory system: {e}")
                    self._memory_manager = None

    
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
    
    def receive_message_from_python(self, message: str):
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
                return json.dumps(self._chat_history, ensure_ascii=False, indent=2)
            
            elif format_type == "txt":
                lines = []
                for msg in self._chat_history:
                    role = "User" if msg["role"] == "user" else f"AI ({msg['model']})"
                    timestamp = msg["timestamp"]
                    content = msg["content"]
                    lines.append(f"[{timestamp}] {role}: {content}")
                return "\n".join(lines)
            
            elif format_type == "md":
                lines = ["# Chat History", ""]
                for msg in self._chat_history:
                    role = "**User**" if msg["role"] == "user" else f"**AI ({msg['model']})**"
                    timestamp = msg["timestamp"]
                    content = msg["content"]
                    lines.append(f"## {role} - {timestamp}")
                    lines.append(content)
                    lines.append("")
                return "\n".join(lines)
            
            else:
                return json.dumps(self._chat_history, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.error_occurred.emit(f"Error exporting chat: {str(e)}")
            return ""
    
    # Методы для работы с системой памяти
    
    @Slot(str, result=str)
    def enrich_message(self, message: str) -> str:
        """
        Слот для обогащения сообщения контекстом из памяти.
        Вызывается из JavaScript перед отправкой к ИИ.
        
        Args:
            message: Исходное сообщение пользователя
            
        Returns:
            Обогащенное сообщение с контекстом
        """
        if self._memory_manager:
            try:
                return self._memory_manager.enrich_message(message)
            except Exception as e:
                print(f"Memory enrichment error: {e}")
                return message
        return message
    
    @Slot(str, str, result=str)  
    def save_chat_exchange(self, user_message: str, ai_response: str) -> str:
        """
        Слот для сохранения обмена сообщениями в память.
        Вызывается из JavaScript после получения ответа ИИ.
        
        Args:
            user_message: Сообщение пользователя
            ai_response: Ответ ИИ
            
        Returns:
            Статус сохранения ("OK" или "ERROR")
        """
        if self._memory_manager:
            try:
                success = self._memory_manager.save_chat_exchange(user_message, ai_response)
                return "OK" if success else "ERROR"
            except Exception as e:
                print(f"Memory save error: {e}")
                return "ERROR"
        return "OK"  # Если память не доступна, не блокируем работу
    
    @Slot(result=str)
    def start_new_chat_session(self) -> str:
        """
        Слот для начала новой сессии чата.
        Очищает краткосрочную память и создает новую RAG сессию.
        
        Returns:
            ID новой сессии
        """
        if self._memory_manager:
            try:
                self._memory_manager.start_new_session()
                return self._memory_manager.session_id
            except Exception as e:
                print(f"New session error: {e}")
        return "default_session"
    
    @Slot(result=str)
    def get_memory_stats(self) -> str:
        """
        Слот для получения статистики памяти в формате JSON.
        
        Returns:
            JSON строка со статистикой памяти
        """
        if self._memory_manager:
            try:
                stats = self._memory_manager.get_memory_stats()
                return json.dumps(stats, ensure_ascii=False)
            except Exception as e:
                print(f"Memory stats error: {e}")
        
        return json.dumps({
            "memory_available": False,
            "error": "Memory system not initialized"
        })
    
    @Slot(result=bool)
    def is_memory_available(self) -> bool:
        """
        Проверка доступности системы памяти.
        
        Returns:
            True если память доступна
        """
        return self._memory_manager is not None
    
    # ==============================================
    # BROWSER AUTOMATION METHODS
    # ==============================================
    
    @Slot(str, result=str)
    def browser_automation_result(self, action: str, result: str) -> str:
        """
        Слот для получения результатов browser automation из JavaScript.
        
        Args:
            action: Выполненное действие (navigate, click, type, etc.)
            result: Результат действия в JSON формате
            
        Returns:
            Статус обработки
        """
        try:
            # Уведомляем Python о результате browser automation
            print(f"🤖 Browser automation result: {action} -> {result}")
            return "OK"
        except Exception as e:
            self.error_occurred.emit(f"Error processing browser automation result: {str(e)}")
            return "ERROR"
    
    @Slot(str, result=str)
    def get_browser_page_info(self, tab_name: str = "current") -> str:
        """
        Получение информации о текущей странице в браузере.
        
        Args:
            tab_name: Имя вкладки (по умолчанию текущая)
            
        Returns:
            JSON с информацией о странице
        """
        try:
            # Здесь мы можем получить информацию из browser widget
            # Пока возвращаем заглушку
            page_info = {
                "url": "unknown",
                "title": "unknown", 
                "status": "ready",
                "timestamp": datetime.now().isoformat()
            }
            
            # Попытаемся получить реальную информацию из parent widget
            if hasattr(self.parent(), 'get_current_page_info'):
                real_info = self.parent().get_current_page_info()
                if real_info:
                    page_info.update(real_info)
            
            return json.dumps(page_info, ensure_ascii=False)
            
        except Exception as e:
            self.error_occurred.emit(f"Error getting page info: {str(e)}")
            return json.dumps({"error": str(e)})
    
    @Slot(str, str, result=str)
    def execute_browser_action(self, action: str, params: str) -> str:
        """
        Выполнение browser automation действия.
        
        Args:
            action: Тип действия (navigate, click, type, screenshot, etc.)
            params: Параметры в JSON формате
            
        Returns:
            JSON результат выполнения
        """
        try:
            import json
            params_dict = json.loads(params) if params else {}
            
            # Уведомляем Python о запросе browser automation
            print(f"🔧 Browser automation request: {action} with params {params_dict}")
            
            # Здесь можно добавить логику выполнения действий
            # Пока возвращаем заглушку
            result = {
                "action": action,
                "status": "pending",
                "message": f"Browser action '{action}' received",
                "timestamp": datetime.now().isoformat()
            }
            
            # Попытаемся выполнить действие через parent widget  
            if hasattr(self.parent(), 'execute_browser_automation'):
                real_result = self.parent().execute_browser_automation(action, params_dict)
                if real_result:
                    result.update(real_result)
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            error_result = {
                "action": action,
                "status": "error", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.error_occurred.emit(f"Error executing browser action '{action}': {str(e)}")
            return json.dumps(error_result, ensure_ascii=False)
    
    @Slot(result=str)
    def get_browser_automation_capabilities(self) -> str:
        """
        Получение списка доступных browser automation возможностей.
        
        Returns:
            JSON со списком доступных действий
        """
        try:
            capabilities = {
                "available_actions": [
                    "navigate",        # Переход по URL
                    "click",          # Клик по элементу
                    "type",           # Ввод текста
                    "get_text",       # Получение текста элемента
                    "get_source",     # Получение HTML кода страницы
                    "screenshot",     # Снимок экрана
                    "scroll",         # Прокрутка страницы
                    "wait",           # Ожидание элемента
                    "get_elements",   # Поиск элементов
                    "get_page_info"   # Информация о странице
                ],
                "supported_selectors": [
                    "css",           # CSS селекторы
                    "xpath",         # XPath селекторы
                    "id",            # По ID элемента
                    "class",         # По классу
                    "tag",           # По тегу
                    "text"           # По тексту
                ],
                "browser_engine": "QWebEngineView",
                "javascript_execution": True,
                "screenshot_formats": ["png", "jpg"],
                "status": "available",
                "timestamp": datetime.now().isoformat()
            }
            
            return json.dumps(capabilities, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.error_occurred.emit(f"Error getting browser capabilities: {str(e)}")
            return json.dumps(error_result, ensure_ascii=False)