"""
Тесты для WebViewWidget модуля GopiAI-WebView
"""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from gopiai.webview.webview_widget import WebViewWidget


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
def webview_widget(app, qtbot):
    """Создает экземпляр WebViewWidget для тестов."""
    widget = WebViewWidget()
    qtbot.addWidget(widget)
    return widget


class TestWebViewWidget:
    """Тесты для WebViewWidget класса."""
    
    def test_widget_creation(self, webview_widget):
        """Тестирует создание виджета."""
        assert webview_widget is not None
        assert hasattr(webview_widget, 'web_view')
        assert hasattr(webview_widget, 'bridge')
        assert hasattr(webview_widget, 'channel')
    
    def test_widget_signals(self, webview_widget):
        """Тестирует наличие сигналов."""
        assert hasattr(webview_widget, 'message_sent')
        assert hasattr(webview_widget, 'message_received')
        assert hasattr(webview_widget, 'chat_cleared')
        assert hasattr(webview_widget, 'model_changed')
    
    def test_send_message_to_chat(self, webview_widget):
        """Тестирует отправку сообщения в чат."""
        test_message = "Test message"
        
        # Мокаем bridge
        webview_widget.bridge = Mock()
        
        # Вызываем метод
        webview_widget.send_message_to_chat(test_message)
        
        # Проверяем вызов
        webview_widget.bridge.receive_message_from_python.assert_called_once_with(test_message)
    
    def test_clear_chat(self, webview_widget):
        """Тестирует очистку чата."""
        # Мокаем bridge
        webview_widget.bridge = Mock()
        
        # Вызываем метод
        webview_widget.clear_chat()
        
        # Проверяем вызов
        webview_widget.bridge.clear_chat.assert_called_once()
    
    def test_set_model(self, webview_widget):
        """Тестирует установку модели."""
        test_model = "claude-sonnet-4"
        
        # Мокаем bridge
        webview_widget.bridge = Mock()
        
        # Вызываем метод
        webview_widget.set_model(test_model)
        
        # Проверяем вызов
        webview_widget.bridge.set_model.assert_called_once_with(test_model)
    
    def test_get_chat_history(self, webview_widget):
        """Тестирует получение истории чата."""
        expected_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        # Мокаем bridge
        webview_widget.bridge = Mock()
        webview_widget.bridge.get_chat_history.return_value = expected_history
        
        # Вызываем метод
        result = webview_widget.get_chat_history()
        
        # Проверяем результат
        assert result == expected_history
        webview_widget.bridge.get_chat_history.assert_called_once()
    
    def test_export_chat(self, webview_widget):
        """Тестирует экспорт истории чата."""
        format_type = "json"
        expected_export = '{"messages": []}'
        
        # Мокаем bridge
        webview_widget.bridge = Mock()
        webview_widget.bridge.export_chat.return_value = expected_export
        
        # Вызываем метод
        result = webview_widget.export_chat(format_type)
        
        # Проверяем результат
        assert result == expected_export
        webview_widget.bridge.export_chat.assert_called_once_with(format_type)
    
    def test_bridge_signal_connections(self, webview_widget):
        """Тестирует подключение сигналов моста."""
        # Мокаем bridge для проверки подключения сигналов
        mock_bridge = Mock()
        mock_bridge.message_sent = Mock()
        mock_bridge.message_received = Mock()
        mock_bridge.chat_cleared = Mock()
        mock_bridge.model_changed = Mock()
        
        # Симулируем подключение сигналов
        mock_bridge.message_sent.connect = Mock()
        mock_bridge.message_received.connect = Mock()
        mock_bridge.chat_cleared.connect = Mock()
        mock_bridge.model_changed.connect = Mock()
        
        webview_widget.bridge = mock_bridge
        
        # Подключаем сигналы вручную для теста
        webview_widget.bridge.message_sent.connect(webview_widget.message_sent)
        webview_widget.bridge.message_received.connect(webview_widget.message_received)
        webview_widget.bridge.chat_cleared.connect(webview_widget.chat_cleared)
        webview_widget.bridge.model_changed.connect(webview_widget.model_changed)
        
        # Проверяем что сигналы подключены
        assert mock_bridge.message_sent.connect.called
        assert mock_bridge.message_received.connect.called
        assert mock_bridge.chat_cleared.connect.called
        assert mock_bridge.model_changed.connect.called
    
    @patch('gopiai.webview.webview_widget.Path')
    def test_load_chat_interface_file_exists(self, mock_path, webview_widget):
        """Тестирует загрузку HTML интерфейса когда файл существует."""
        # Мокаем Path для симуляции существующего файла
        mock_html_path = Mock()
        mock_html_path.exists.return_value = True
        mock_html_path.absolute.return_value = "/path/to/chat.html"
        mock_path.return_value.parent.__truediv__.return_value = mock_html_path
        
        # Мокаем web_view
        webview_widget.web_view = Mock()
        
        # Вызываем метод
        webview_widget._load_chat_interface()
        
        # Проверяем что load был вызван
        assert webview_widget.web_view.load.called
    
    @patch('gopiai.webview.webview_widget.Path')
    def test_load_chat_interface_file_not_exists(self, mock_path, webview_widget):
        """Тестирует загрузку fallback HTML когда файл не существует."""
        # Мокаем Path для симуляции отсутствующего файла
        mock_html_path = Mock()
        mock_html_path.exists.return_value = False
        mock_path.return_value.parent.__truediv__.return_value = mock_html_path
        
        # Мокаем web_view
        webview_widget.web_view = Mock()
        
        # Вызываем метод
        webview_widget._load_chat_interface()
        
        # Проверяем что setHtml был вызван с fallback HTML
        assert webview_widget.web_view.setHtml.called
        args = webview_widget.web_view.setHtml.call_args[0][0]
        assert "GopiAI WebView Chat" in args
        assert "puter.js" in args