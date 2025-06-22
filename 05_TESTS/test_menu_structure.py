#!/usr/bin/env python3
"""
Тест проверки меню GopiAI - убедиться что "Тема" убрана из "Вид" и добавлено меню "Настройки"
"""

import sys
import os
from pathlib import Path

# Добавляем пути модулей
script_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_modules_root = os.path.dirname(script_dir)

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-Widgets"), 
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
    os.path.join(gopiai_modules_root, "rag_memory_system"),
    gopiai_modules_root,
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

from PySide6.QtWidgets import QApplication
from gopiai.ui.components.menu_bar import StandaloneMenuBar

def test_menu_structure():
    """Тест структуры меню"""
    print("🧪 Тестирование структуры меню...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Создаем меню
    menu_bar = StandaloneMenuBar()
    
    # Получаем все меню
    menus = []
    for action in menu_bar.actions():
        if action.menu():
            menus.append(action.menu().title())
    
    print(f"📋 Найденные меню: {menus}")
    
    # Проверяем, что есть меню "Настройки"
    assert "Настройки" in menus, "❌ Меню 'Настройки' не найдено!"
    print("✅ Меню 'Настройки' найдено")
    
    # Проверяем содержимое меню "Вид"
    view_menu = None
    for action in menu_bar.actions():
        if action.menu() and action.menu().title() == "Вид":
            view_menu = action.menu()
            break
    
    if view_menu:
        view_actions = [action.text() for action in view_menu.actions() 
                       if not action.isSeparator() and not action.menu()]
        print(f"📋 Действия в меню 'Вид': {view_actions}")
        
        # Проверяем, что "Тема" НЕ в меню "Вид"
        assert "Тема" not in view_actions, "❌ Пункт 'Тема' всё ещё в меню 'Вид'!"
        print("✅ Пункт 'Тема' убран из меню 'Вид'")
    else:
        print("⚠️ Меню 'Вид' не найдено")
    
    # Проверяем содержимое меню "Настройки"  
    settings_menu = None
    for action in menu_bar.actions():
        if action.menu() and action.menu().title() == "Настройки":
            settings_menu = action.menu()
            break
    
    if settings_menu:
        settings_actions = [action.text() for action in settings_menu.actions() 
                           if not action.isSeparator()]
        print(f"📋 Действия в меню 'Настройки': {settings_actions}")
        
        # Проверяем, что есть нужные пункты
        assert "Настройки приложения" in settings_actions, "❌ 'Настройки приложения' не найдено!"
        assert "Сменить тему" in settings_actions, "❌ 'Сменить тему' не найдено!"
        print("✅ Пункты меню 'Настройки' корректны")
    else:
        print("❌ Меню 'Настройки' не найдено")
        return False
    
    # Проверяем наличие нужных сигналов
    required_signals = ['openSettingsRequested', 'changeThemeRequested']
    for signal_name in required_signals:
        assert hasattr(menu_bar, signal_name), f"❌ Сигнал '{signal_name}' не найден!"
        print(f"✅ Сигнал '{signal_name}' найден")
    
    print("🎉 Все тесты прошли успешно!")
    return True

if __name__ == "__main__":
    try:
        result = test_menu_structure()
        if result:
            print("✅ Тестирование завершено успешно")
            sys.exit(0)
        else:
            print("❌ Тестирование провалено")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
