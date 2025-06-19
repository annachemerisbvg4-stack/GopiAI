#!/usr/bin/env python3
"""
Простой тест импорта модуля GopiAI-WebView
"""

try:
    from gopiai.webview import WebViewWidget, PuterChatInterface
    print("✅ Модуль GopiAI-WebView успешно импортирован!")
    print("✅ WebViewWidget доступен")
    print("✅ PuterChatInterface доступен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что модуль установлен: pip install -e GopiAI-WebView/")

try:
    from PySide6.QtWidgets import QApplication
    print("✅ PySide6 доступен")
except ImportError:
    print("❌ PySide6 не установлен")

print("\nТест завершен!")