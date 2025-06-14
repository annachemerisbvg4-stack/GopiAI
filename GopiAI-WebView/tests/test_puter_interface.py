"""
Тесты для PuterChatInterface модуля GopiAI-WebView
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject

from gopiai.webview.puter_interface import PuterChatInterface


@pytest.fixture(scope="session")
def app():
    """Создает экземпляр QApplication для тестов."""
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    finally:
        if app:
            app.quit()


@pytest.fixture
def mock_webview():
    """Создает мок WebView виджета."""
    mock = Mock()
    mock.message_sent = Mock()
    mock.message_received = Mock()
    mock.chat_cleared = Mock()
    mock.model_changed = Mock()
    
    # Мокаем методы с connect
    mock.message_sent.connect = Mock()
    mock.message_received.connect = Mock()
    mock.chat_cleared.connect = Mock()
    mock.model_changed.connect = Mock()
    
    return mock


@pytest.fixture
def chat_interface(app, mock_webview):
    """Создает экземпляр PuterChatInterface для тестов."""
    interface = PuterChatInterface(mock_webview)
    return interface


class TestPuterChatInterface:
    """Тесты для PuterChatInterface класса."""
    
    def test_interface_creation(self, chat_interface):
        """Тестирует создание интерфейса."""
        assert chat_interface is not None
        assert hasattr(chat_interface, '_webview')
        assert hasattr(chat_interface, '_statistics')
        assert hasattr(chat_interface, '_stats_timer')
    
    def test_interface_signals(self, chat_interface):
        """Тестирует наличие сигналов."""
        assert hasattr(chat_interface, 'message_sent')
        assert hasattr(chat_interface, 'message_received')
        assert hasattr(chat_interface, 'chat_cleared')
        assert hasattr(chat_interface, 'model_changed')
        assert hasattr(chat_interface, 'error_occurred')
        assert hasattr(chat_interface, 'statistics_updated')
    
    def test_send_message_success(self, chat_interface, mock_webview):
        """Тестирует успешную отправку сообщения."""
        test_message = "Hello, AI!"
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_webview.send_message_to_chat = Mock()
        
        # Вызываем метод
        result = chat_interface.send_message(test_message)
        
        # Проверяем результат
        assert result is True
        mock_webview.send_message_to_chat.assert_called_once_with(test_message)
    
    def test_send_message_no_webview(self, app):
        """Тестирует отправку сообщения без подключенного WebView."""
        interface = PuterChatInterface()
        test_message = "Hello, AI!"
        
        # Мокаем сигнал error_occurred
        interface.error_occurred = Mock()
        interface.error_occurred.emit = Mock()
        
        # Вызываем метод
        result = interface.send_message(test_message)
        
        # Проверяем результат
        assert result is False
        interface.error_occurred.emit.assert_called_once_with("WebView not connected")
    
    def test_clear_chat_success(self, chat_interface, mock_webview):
        """Тестирует успешную очистку чата."""
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_webview.clear_chat = Mock()
        
        # Устанавливаем некоторую статистику
        chat_interface._statistics["total_messages"] = 10
        chat_interface._statistics["user_messages"] = 5
        
        # Вызываем метод
        result = chat_interface.clear_chat()
        
        # Проверяем результат
        assert result is True
        mock_webview.clear_chat.assert_called_once()
        
        # Проверяем сброс статистики
        assert chat_interface._statistics["total_messages"] == 0
        assert chat_interface._statistics["user_messages"] == 0
    
    def test_set_model_valid(self, chat_interface, mock_webview):
        """Тестирует установку валидной модели."""
        test_model = "claude-sonnet-4"
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_webview.set_model = Mock()
        
        # Вызываем метод
        result = chat_interface.set_model(test_model)
        
        # Проверяем результат
        assert result is True
        mock_webview.set_model.assert_called_once_with(test_model)
    
    def test_set_model_invalid(self, chat_interface, mock_webview):
        """Тестирует установку невалидной модели."""
        test_model = "invalid-model"
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        chat_interface.error_occurred = Mock()
        chat_interface.error_occurred.emit = Mock()
        
        # Вызываем метод
        result = chat_interface.set_model(test_model)
        
        # Проверяем результат
        assert result is False
        chat_interface.error_occurred.emit.assert_called_once_with(f"Unknown model: {test_model}")
    
    def test_get_current_model(self, chat_interface, mock_webview):
        """Тестирует получение текущей модели."""
        expected_model = "claude-opus-4"
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_bridge = Mock()
        mock_bridge.get_current_model.return_value = expected_model
        mock_webview.bridge = mock_bridge
        
        # Вызываем метод
        result = chat_interface.get_current_model()
        
        # Проверяем результат
        assert result == expected_model
        mock_bridge.get_current_model.assert_called_once()
    
    def test_get_chat_history(self, chat_interface, mock_webview):
        """Тестирует получение истории чата."""
        expected_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_webview.get_chat_history.return_value = expected_history
        
        # Вызываем метод
        result = chat_interface.get_chat_history()
        
        # Проверяем результат
        assert result == expected_history
        mock_webview.get_chat_history.assert_called_once()
    
    def test_export_chat_without_file(self, chat_interface, mock_webview):
        """Тестирует экспорт чата без сохранения в файл."""
        format_type = "json"
        expected_data = '{"messages": []}'
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_webview.export_chat.return_value = expected_data
        
        # Вызываем метод
        result = chat_interface.export_chat(format_type)
        
        # Проверяем результат
        assert result == expected_data
        mock_webview.export_chat.assert_called_once_with(format_type)
    
    @patch('gopiai.webview.puter_interface.Path')
    def test_export_chat_with_file(self, mock_path, chat_interface, mock_webview):
        """Тестирует экспорт чата с сохранением в файл."""
        format_type = "json"
        file_path = "/path/to/export.json"
        expected_data = '{"messages": []}'
        
        # Настраиваем мок
        chat_interface._webview = mock_webview
        mock_webview.export_chat.return_value = expected_data
        
        mock_file_path = Mock()
        mock_file_path.parent.mkdir = Mock()
        mock_file_path.write_text = Mock()
        mock_file_path.absolute.return_value = file_path
        mock_path.return_value = mock_file_path
        
        # Вызываем метод
        result = chat_interface.export_chat(format_type, file_path)
        
        # Проверяем результат
        assert result == file_path
        mock_webview.export_chat.assert_called_once_with(format_type)
        mock_file_path.write_text.assert_called_once_with(expected_data, encoding='utf-8')
    
    def test_get_statistics(self, chat_interface):
        """Тестирует получение статистики."""
        # Устанавливаем тестовую статистику
        chat_interface._statistics.update({
            "total_messages": 15,
            "user_messages": 8,
            "ai_messages": 7,
            "models_used": {"claude-sonnet-4", "claude-opus-4"}
        })
        
        # Вызываем метод
        result = chat_interface.get_statistics()
        
        # Проверяем результат
        assert result["total_messages"] == 15
        assert result["user_messages"] == 8
        assert result["ai_messages"] == 7
        assert isinstance(result["models_used"], list)
        assert "claude-sonnet-4" in result["models_used"]
        assert "claude-opus-4" in result["models_used"]
    
    def test_get_available_models(self, chat_interface):
        """Тестирует получение списка доступных моделей."""
        result = chat_interface.get_available_models()
        
        assert isinstance(result, list)
        assert "claude-sonnet-4" in result
        assert "claude-opus-4" in result
        assert len(result) == 2
    
    def test_is_connected(self, chat_interface, mock_webview):
        """Тестирует проверку подключения."""
        # С подключенным WebView
        chat_interface._webview = mock_webview
        assert chat_interface.is_connected() is True
        
        # Без подключенного WebView
        chat_interface._webview = None
        assert chat_interface.is_connected() is False
    
    def test_on_message_sent(self, chat_interface):
        """Тестирует обработку отправленного сообщения."""
        test_message = "Test message"
        initial_count = chat_interface._statistics["user_messages"]
        
        # Мокаем сигнал
        chat_interface.message_sent = Mock()
        chat_interface.message_sent.emit = Mock()
        
        # Вызываем метод
        chat_interface._on_message_sent(test_message)
        
        # Проверяем обновление статистики
        assert chat_interface._statistics["user_messages"] == initial_count + 1
        assert chat_interface._statistics["total_messages"] == initial_count + 1
        assert chat_interface._statistics["last_activity"] is not None
        
        # Проверяем сигнал
        chat_interface.message_sent.emit.assert_called_once_with(test_message)
    
    def test_on_message_received(self, chat_interface):
        """Тестирует обработку полученного ответа ИИ."""
        test_model = "claude-sonnet-4"
        test_message = "AI response"
        initial_count = chat_interface._statistics["ai_messages"]
        
        # Мокаем сигнал
        chat_interface.message_received = Mock()
        chat_interface.message_received.emit = Mock()
        
        # Вызываем метод
        chat_interface._on_message_received(test_model, test_message)
        
        # Проверяем обновление статистики
        assert chat_interface._statistics["ai_messages"] == initial_count + 1
        assert test_model in chat_interface._statistics["models_used"]
        assert chat_interface._statistics["last_activity"] is not None
        
        # Проверяем сигнал
        chat_interface.message_received.emit.assert_called_once_with(test_model, test_message)
    
    def test_setup_callbacks(self, chat_interface):
        """Тестирует установку callback функций."""
        message_callback = Mock()
        response_callback = Mock()
        error_callback = Mock()
        
        # Мокаем сигналы
        chat_interface.message_sent = Mock()
        chat_interface.message_received = Mock()
        chat_interface.error_occurred = Mock()
        
        chat_interface.message_sent.connect = Mock()
        chat_interface.message_received.connect = Mock()
        chat_interface.error_occurred.connect = Mock()
        
        # Устанавливаем callbacks
        chat_interface.setup_message_callback(message_callback)
        chat_interface.setup_response_callback(response_callback)
        chat_interface.setup_error_callback(error_callback)
        
        # Проверяем подключение
        chat_interface.message_sent.connect.assert_called_once_with(message_callback)
        chat_interface.message_received.connect.assert_called_once_with(response_callback)
        chat_interface.error_occurred.connect.assert_called_once_with(error_callback)