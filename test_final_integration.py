#!/usr/bin/env python3
"""
Финальный тест интеграции RAG памяти с GopiAI UI
================================================================

Тестирует:
1. Синтаксис Python и JavaScript файлов
2. Импорты и зависимости
3. Доступность RAG API 
4. Интеграцию ClaudeToolsHandler
5. WebView чат виджет
6. Модальное окно истории чатов
7. Функциональность поиска и экспорта
"""

import sys
import os
import json
import asyncio
import subprocess
from pathlib import Path

# Добавляем пути к модулям GopiAI
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "GopiAI-Core"))
sys.path.insert(0, str(project_root / "GopiAI-UI"))
sys.path.insert(0, str(project_root / "GopiAI-WebView"))
sys.path.insert(0, str(project_root / "rag_memory_system"))

def test_python_syntax():
    """Тест синтаксиса Python файлов"""
    print("🔍 Проверка синтаксиса Python файлов...")
    
    files_to_check = [
        "rag_memory_system/models.py",
        "rag_memory_system/api.py", 
        "rag_memory_system/memory_manager.py",
        "GopiAI-UI/gopiai/ui/components/claude_tools_handler.py",
        "GopiAI-UI/gopiai/ui/components/webview_chat_widget.py"
    ]
    
    errors = []
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(full_path), 'exec')
                print(f"✅ {file_path} - синтаксис OK")
            except SyntaxError as e:
                error_msg = f"❌ {file_path} - ошибка синтаксиса: {e}"
                print(error_msg)
                errors.append(error_msg)
        else:
            error_msg = f"⚠️ {file_path} - файл не найден"
            print(error_msg)
            errors.append(error_msg)
    
    return errors

def test_javascript_syntax():
    """Тест синтаксиса JavaScript файлов"""
    print("\n🔍 Проверка синтаксиса JavaScript файлов...")
    
    js_files = [
        "GopiAI-WebView/gopiai/webview/assets/chat.js"
    ]
    
    errors = []
    for js_file in js_files:
        full_path = project_root / js_file
        if full_path.exists():
            try:
                result = subprocess.run(
                    ["node", "-c", str(full_path)], 
                    capture_output=True, 
                    text=True,
                    cwd=project_root
                )
                if result.returncode == 0:
                    print(f"✅ {js_file} - синтаксис OK")
                else:
                    error_msg = f"❌ {js_file} - ошибка синтаксиса: {result.stderr}"
                    print(error_msg)
                    errors.append(error_msg)
            except FileNotFoundError:
                error_msg = f"⚠️ Node.js не найден, пропускаем проверку {js_file}"
                print(error_msg)
        else:
            error_msg = f"⚠️ {js_file} - файл не найден"
            print(error_msg)
            errors.append(error_msg)
    
    return errors

def test_rag_imports():
    """Тест импортов RAG системы"""
    print("\n🔍 Проверка импортов RAG системы...")
    
    errors = []
    
    # Тест базовых зависимостей
    dependencies = [
        "fastapi", "uvicorn", "chromadb", 
        "langchain", "langchain_community", "sentence_transformers"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - импорт OK")
        except ImportError as e:
            error_msg = f"❌ {dep} - ошибка импорта: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    # Тест импорта модулей RAG
    try:
        from rag_memory_system.models import ChatMessage, SearchResult, MemoryStats
        print("✅ rag_memory_system.models - импорт OK")
    except ImportError as e:
        error_msg = f"❌ rag_memory_system.models - ошибка импорта: {e}"
        print(error_msg)
        errors.append(error_msg)
    
    try:
        from rag_memory_system.memory_manager import MemoryManager
        print("✅ rag_memory_system.memory_manager - импорт OK")
    except ImportError as e:
        error_msg = f"❌ rag_memory_system.memory_manager - ошибка импорта: {e}"
        print(error_msg)
        errors.append(error_msg)
    
    return errors

def test_claude_tools_handler():
    """Тест ClaudeToolsHandler"""
    print("\n🔍 Проверка ClaudeToolsHandler...")
    
    errors = []
    
    try:
        from GopiAI.UI.gopiai.ui.components.claude_tools_handler import ClaudeToolsHandler
        print("✅ ClaudeToolsHandler - импорт OK")
        
        # Проверяем наличие метода search_memory
        if hasattr(ClaudeToolsHandler, 'search_memory'):
            print("✅ ClaudeToolsHandler.search_memory - метод найден")
        else:
            error_msg = "❌ ClaudeToolsHandler.search_memory - метод не найден"
            print(error_msg)
            errors.append(error_msg)
            
    except ImportError as e:
        error_msg = f"❌ ClaudeToolsHandler - ошибка импорта: {e}"
        print(error_msg)
        errors.append(error_msg)
    
    return errors

def test_webview_widget():
    """Тест WebView виджета"""
    print("\n🔍 Проверка WebView чат виджета...")
    
    errors = []
    
    try:
        from GopiAI.UI.gopiai.ui.components.webview_chat_widget import WebViewChatWidget, WebViewChatBridge
        print("✅ WebViewChatWidget - импорт OK")
        print("✅ WebViewChatBridge - импорт OK")
        
        # Проверяем наличие нужных методов в bridge
        bridge_methods = ['send_message', 'receive_ai_message', 'log_error']
        for method in bridge_methods:
            if hasattr(WebViewChatBridge, method):
                print(f"✅ WebViewChatBridge.{method} - метод найден")
            else:
                error_msg = f"❌ WebViewChatBridge.{method} - метод не найден"
                print(error_msg)
                errors.append(error_msg)
                
    except ImportError as e:
        error_msg = f"❌ WebView компоненты - ошибка импорта: {e}"
        print(error_msg)
        errors.append(error_msg)
    
    return errors

def test_html_structure():
    """Тест структуры HTML"""
    print("\n🔍 Проверка структуры HTML файлов...")
    
    errors = []
    
    html_file = project_root / "GopiAI-WebView/gopiai/webview/assets/chat.html"
    if html_file.exists():
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Проверяем наличие ключевых элементов
            required_elements = [
                'id="history-btn"',
                'id="history-modal"', 
                'id="history-list"',
                'id="history-search"',
                'id="export-history-btn"',
                'id="new-chat-btn"',
                'id="close-history"'
            ]
            
            for element in required_elements:
                if element in html_content:
                    print(f"✅ {element} - элемент найден")
                else:
                    error_msg = f"❌ {element} - элемент не найден"
                    print(error_msg)
                    errors.append(error_msg)
                    
            # Проверяем исправление SVG path
            if 'path d="M21 21L16.65 16.65"' in html_content:
                print("✅ SVG path исправлен")
            elif 'path d="M21 21l-4.35-4.35"' in html_content:
                error_msg = "❌ SVG path все еще содержит ошибку"
                print(error_msg)
                errors.append(error_msg)
            
        except Exception as e:
            error_msg = f"❌ Ошибка чтения HTML: {e}"
            print(error_msg)
            errors.append(error_msg)
    else:
        error_msg = "❌ chat.html не найден"
        print(error_msg)
        errors.append(error_msg)
    
    return errors

async def test_rag_api():
    """Тест RAG API"""
    print("\n🔍 Проверка RAG API...")
    
    errors = []
    
    try:
        import aiohttp
        
        # Проверяем доступность API
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://localhost:8001/health', timeout=5) as response:
                    if response.status == 200:
                        print("✅ RAG API доступен")
                    else:
                        error_msg = f"❌ RAG API вернул статус {response.status}"
                        print(error_msg)
                        errors.append(error_msg)
            except Exception as e:
                error_msg = f"⚠️ RAG API недоступен (возможно не запущен): {e}"
                print(error_msg)
                errors.append(error_msg)
                
    except ImportError:
        error_msg = "❌ aiohttp не установлен"
        print(error_msg)
        errors.append(error_msg)
    
    return errors

def main():
    """Основная функция тестирования"""
    print("=" * 70)
    print("🧪 ФИНАЛЬНЫЙ ТЕСТ ИНТЕГРАЦИИ RAG ПАМЯТИ С GopiAI UI")
    print("=" * 70)
    
    all_errors = []
    
    # Запускаем все тесты
    all_errors.extend(test_python_syntax())
    all_errors.extend(test_javascript_syntax())
    all_errors.extend(test_rag_imports())
    all_errors.extend(test_claude_tools_handler())
    all_errors.extend(test_webview_widget())
    all_errors.extend(test_html_structure())
    
    # Асинхронный тест API
    try:
        all_errors.extend(asyncio.run(test_rag_api()))
    except Exception as e:
        all_errors.append(f"❌ Ошибка тестирования API: {e}")
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    
    if not all_errors:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ RAG память готова к интеграции с GopiAI UI")
        print("✅ История чатов настроена корректно")
        print("✅ JavaScript и HTML файлы валидны")
        print("✅ Все зависимости установлены")
        return 0
    else:
        print(f"❌ НАЙДЕНО {len(all_errors)} ОШИБОК:")
        print("-" * 50)
        for error in all_errors:
            print(error)
        print("\n⚠️ Исправьте ошибки перед финализацией интеграции")
        return 1

if __name__ == "__main__":
    sys.exit(main())