"""
GopiAI WebView Module

Модуль для интеграции веб-чата с ИИ через puter.js в приложениях GopiAI.
Поддерживает Claude Sonnet 4 и Opus 4 модели с современным веб-интерфейсом.

Основные компоненты:
- WebViewWidget: Qt виджет с QWebEngineView для отображения веб-интерфейса
- JavaScriptBridge: Мост для связи Python ↔ JavaScript
- PuterChatInterface: Python API для управления чатом
"""

from gopiai.webview.webview_widget import WebViewWidget
from gopiai.webview.js_bridge import JavaScriptBridge
from gopiai.webview.puter_interface import PuterChatInterface

__version__ = "0.1.0"
__all__ = ["WebViewWidget", "JavaScriptBridge", "PuterChatInterface"]