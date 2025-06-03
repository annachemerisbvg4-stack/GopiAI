#!/usr/bin/env python3
"""
Тест модульного интерфейса GopiAI
=================================

Проверяет загрузку всех модулей и их основные функции.
"""

import sys
import os

def test_imports():
    """Тест импорта всех модулей"""
    print("🧪 Тестирование импортов модулей...")
    
    try:
        from ui_components import (
            StandaloneMenuBar,
            StandaloneTitlebar,
            StandaloneTitlebarWithMenu,
            CustomGrip,
            FileExplorerWidget,
            TabDocumentWidget,
            ChatWidget,
            TerminalWidget
        )
        print("✅ Все основные модули UI успешно импортированы")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        return False

def test_fallback_mode():
    """Тест fallback режима"""
    print("🧪 Тестирование fallback режима...")
    
    # Временно переименуем папку ui_components
    import shutil
    ui_components_path = "ui_components"
    ui_components_backup = "ui_components_backup_test"
    
    try:
        if os.path.exists(ui_components_path):
            shutil.move(ui_components_path, ui_components_backup)
            print("📁 ui_components временно перемещена")
          # Попробуем импортировать модуль в fallback режиме
        if 'gopiai_standalone_interface_modular' in sys.modules:
            del sys.modules['gopiai_standalone_interface_modular']
            
        try:
            with open('gopiai_standalone_interface_modular.py', 'r', encoding='utf-8') as f:
                code = f.read()
            exec(code)
            print("✅ Fallback режим работает корректно")
            fallback_success = True
        except Exception as e:
            print(f"❌ Ошибка в fallback режиме: {e}")
            fallback_success = False
            
    finally:
        # Восстанавливаем папку
        if os.path.exists(ui_components_backup):
            if os.path.exists(ui_components_path):
                shutil.rmtree(ui_components_path)
            shutil.move(ui_components_backup, ui_components_path)
            print("📁 ui_components восстановлена")
    
    return fallback_success

def test_module_structure():
    """Проверка структуры модулей"""
    print("🧪 Проверка структуры модулей...")
    
    modules_to_check = [
        "ui_components/__init__.py",
        "ui_components/menu_bar.py",
        "ui_components/titlebar.py", 
        "ui_components/file_explorer.py",
        "ui_components/tab_widget.py",
        "ui_components/chat_widget.py",
        "ui_components/terminal_widget.py"
    ]
    
    all_exist = True
    for module_path in modules_to_check:
        if os.path.exists(module_path):
            print(f"✅ {module_path}")
        else:
            print(f"❌ {module_path} - НЕ НАЙДЕН")
            all_exist = False
    
    return all_exist

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов модульного интерфейса GopiAI")
    print("=" * 50)
    
    tests = [
        ("Импорт модулей", test_imports),
        ("Структура модулей", test_module_structure),
        ("Fallback режим", test_fallback_mode)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} - ПРОЙДЕН")
                passed += 1
            else:
                print(f"❌ {test_name} - ПРОВАЛЕН")
        except Exception as e:
            print(f"💥 {test_name} - ОШИБКА: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Результаты тестирования: {passed}/{total} тестов пройдены")
    
    if passed == total:
        print("🎉 Все тесты успешно пройдены!")
        print("✅ Модульная архитектура GopiAI работает корректно")
    else:
        print("⚠️ Некоторые тесты провалены, требуется доработка")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
