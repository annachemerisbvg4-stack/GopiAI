"""
Puter Chat Interface для GopiAI WebView

Python API для управления чатом с ИИ через puter.js.
Предоставляет высокоуровневый интерфейс для работы с чатом.
"""

import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QTimer


class PuterChatInterface(QObject):
    """
    Высокоуровневый Python интерфейс для управления чатом с ИИ.
    
    Предоставляет API для отправки сообщений, управления моделями,
    экспорта истории и получения статистики чата.
    """
    
    # Сигналы для уведомлений
    message_sent = Signal(str)  # Отправлено сообщение
    message_received = Signal(str, str)  # Получен ответ (model, message)
    chat_cleared = Signal()  # Чат очищен
    model_changed = Signal(str)  # Изменена модель
    error_occurred = Signal(str)  # Произошла ошибка
    statistics_updated = Signal(dict)  # Обновлена статистика
    
    def __init__(self, webview_widget=None, parent: QObject = None):
        """
        Инициализация интерфейса чата.
        
        Args:
            webview_widget: Экземпляр WebViewWidget
            parent: Родительский объект
        """
        super().__init__(parent)
        
        self._webview = webview_widget
        self._statistics = {
            "total_messages": 0,
            "user_messages": 0,
            "ai_messages": 0,
            "models_used": set(),
            "session_start": datetime.now().isoformat(),
            "last_activity": None
        }
        
        # Таймер для обновления статистики
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._update_statistics)
        self._stats_timer.start(5000)  # Обновление каждые 5 секунд
        
        # Подключение к сигналам WebView, если он предоставлен
        if self._webview:
            self._connect_webview_signals()
    
    def set_webview(self, webview_widget):
        """
        Установка WebView виджета.
        
        Args:
            webview_widget: Экземпляр WebViewWidget
        """
        self._webview = webview_widget
        self._connect_webview_signals()
    
    def _connect_webview_signals(self):
        """Подключение к сигналам WebView виджета."""
        if self._webview:
            self._webview.message_sent.connect(self._on_message_sent)
            self._webview.message_received.connect(self._on_message_received)
            self._webview.chat_cleared.connect(self._on_chat_cleared)
            self._webview.model_changed.connect(self._on_model_changed)
    
    def _on_message_sent(self, message: str):
        """Обработка отправленного сообщения."""
        self._statistics["user_messages"] += 1
        self._statistics["total_messages"] += 1
        self._statistics["last_activity"] = datetime.now().isoformat()
        self.message_sent.emit(message)
    
    def _on_message_received(self, model: str, message: str):
        """Обработка полученного ответа ИИ."""
        self._statistics["ai_messages"] += 1
        self._statistics["total_messages"] += 1
        self._statistics["models_used"].add(model)
        self._statistics["last_activity"] = datetime.now().isoformat()
        self.message_received.emit(model, message)
    
    def _on_chat_cleared(self):
        """Обработка очистки чата."""
        self.chat_cleared.emit()
    
    def _on_model_changed(self, model: str):
        """Обработка изменения модели."""
        self._statistics["models_used"].add(model)
        self.model_changed.emit(model)
    
    def _update_statistics(self):
        """Обновление статистики."""
        stats = self._statistics.copy()
        stats["models_used"] = list(stats["models_used"])
        self.statistics_updated.emit(stats)
    
    # Основные методы API
    
    def send_message(self, message: str) -> bool:
        """
        Отправка сообщения в чат.
        
        Args:
            message: Текст сообщения
            
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            if self._webview:
                self._webview.send_message_to_chat(message)
                return True
            else:
                self.error_occurred.emit("WebView not connected")
                return False
        except Exception as e:
            self.error_occurred.emit(f"Error sending message: {str(e)}")
            return False
    
    def clear_chat(self) -> bool:
        """
        Очистка истории чата.
        
        Returns:
            True если чат очищен успешно
        """
        try:
            if self._webview:
                self._webview.clear_chat()
                # Сброс статистики
                self._statistics.update({
                    "total_messages": 0,
                    "user_messages": 0,
                    "ai_messages": 0,
                    "models_used": set(),
                    "last_activity": None
                })
                return True
            else:
                self.error_occurred.emit("WebView not connected")
                return False
        except Exception as e:
            self.error_occurred.emit(f"Error clearing chat: {str(e)}")
            return False
    
    def set_model(self, model: str) -> bool:
        """
        Установка модели ИИ.
        
        Args:
            model: Название модели ('claude-sonnet-4' или 'claude-opus-4')
            
        Returns:
            True если модель установлена успешно
        """
        try:
            if model not in ["claude-sonnet-4", "claude-opus-4"]:
                self.error_occurred.emit(f"Unknown model: {model}")
                return False
            
            if self._webview:
                self._webview.set_model(model)
                return True
            else:
                self.error_occurred.emit("WebView not connected")
                return False
        except Exception as e:
            self.error_occurred.emit(f"Error setting model: {str(e)}")
            return False
    
    def get_current_model(self) -> Optional[str]:
        """
        Получение текущей модели ИИ.
        
        Returns:
            Название текущей модели или None
        """
        try:
            if self._webview and self._webview.bridge:
                return self._webview.bridge.get_current_model()
            return None
        except Exception as e:
            self.error_occurred.emit(f"Error getting current model: {str(e)}")
            return None
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Получение истории чата.
        
        Returns:
            Список сообщений
        """
        try:
            if self._webview:
                return self._webview.get_chat_history()
            return []
        except Exception as e:
            self.error_occurred.emit(f"Error getting chat history: {str(e)}")
            return []
    
    def export_chat(self, format_type: str = "json", file_path: Optional[str] = None) -> str:
        """
        Экспорт истории чата.
        
        Args:
            format_type: Формат экспорта ('json', 'txt', 'md')
            file_path: Путь для сохранения файла (опционально)
            
        Returns:
            Экспортированные данные или путь к файлу
        """
        try:
            if not self._webview:
                self.error_occurred.emit("WebView not connected")
                return ""
            
            exported_data = self._webview.export_chat(format_type)
            
            if file_path:
                # Сохранение в файл
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(exported_data, encoding='utf-8')
                return str(path.absolute())
            else:
                return exported_data
                
        except Exception as e:
            self.error_occurred.emit(f"Error exporting chat: {str(e)}")
            return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики чата.
        
        Returns:
            Словарь со статистикой
        """
        stats = self._statistics.copy()
        stats["models_used"] = list(stats["models_used"])
        return stats
    
    def get_available_models(self) -> List[str]:
        """
        Получение списка доступных моделей.
        
        Returns:
            Список названий моделей
        """
        return ["claude-sonnet-4", "claude-opus-4"]
    
    def is_connected(self) -> bool:
        """
        Проверка подключения к WebView.
        
        Returns:
            True если WebView подключен
        """
        return self._webview is not None
    
    # Вспомогательные методы
    
    def setup_message_callback(self, callback: Callable[[str], None]):
        """
        Установка callback для обработки сообщений.
        
        Args:
            callback: Функция для обработки сообщений
        """
        self.message_sent.connect(callback)
    
    def setup_response_callback(self, callback: Callable[[str, str], None]):
        """
        Установка callback для обработки ответов ИИ.
        
        Args:
            callback: Функция для обработки ответов (model, message)
        """
        self.message_received.connect(callback)
    
    def setup_error_callback(self, callback: Callable[[str], None]):
        """
        Установка callback для обработки ошибок.
        
        Args:
            callback: Функция для обработки ошибок
        """
        self.error_occurred.connect(callback)