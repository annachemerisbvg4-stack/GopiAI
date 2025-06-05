#!/usr/bin/env python3
"""
UI Registry - Автоматическая регистрация окон и меню
================================================

Система для автоматического обнаружения и регистрации окон и пунктов меню
на основе метаданных классов.

Автор: Crazy Coder
Версия: 1.0.0
Дата: 2025-01-27
"""

import os
import sys
import importlib
import importlib.util
import inspect
from typing import Dict, List, Optional, Type, Any, Union
from pathlib import Path
import traceback

from .base_window import BaseWindow


class WindowRegistry:
    """Реестр окон для автоматической регистрации и управления меню."""
    
    def __init__(self):
        self.windows: Dict[str, Type[BaseWindow]] = {}
        self.menu_structure: Dict[str, List[Dict[str, Any]]] = {}
        self.discovered_modules: List[str] = []
        
    def discover_windows(self, search_paths: Optional[List[str]] = None) -> None:
        """
        Автоматически обнаруживает все окна в указанных папках.
        
        Args:
            search_paths: Список путей для поиска. По умолчанию - UI/windows и UI/dialogs
        """
        if search_paths is None:
            ui_root = Path(__file__).parent.parent
            search_paths = [
                str(ui_root / "windows"),
                str(ui_root / "dialogs"),
                str(ui_root / "components")  # На случай, если там тоже есть окна
            ]
            
        print(f"🔍 Поиск окон в папках: {search_paths}")
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                print(f"⚠️ Папка не найдена: {search_path}")
                continue
                
            self._scan_directory(search_path)
            
        print(f"✅ Обнаружено окон: {len(self.windows)}")
        print(f"📋 Структура меню: {len(self.menu_structure)} категорий")
        
    def _scan_directory(self, directory: str) -> None:
        """Сканирует директорию на предмет Python-файлов с окнами."""
        for root, dirs, files in os.walk(directory):
            # Пропускаем папки с __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    self._scan_file(file_path)
                    
    def _scan_file(self, file_path: str) -> None:
        """Сканирует Python-файл на предмет классов окон."""
        try:
            # Преобразуем путь к файлу в модуль
            relative_path = os.path.relpath(file_path, os.path.dirname(__file__))
            module_path = relative_path.replace(os.sep, '.').replace('.py', '')
            
            # Убираем '..' из пути и добавляем UI.
            if module_path.startswith('..'):
                module_path = 'UI' + module_path[2:]
            
            print(f"🔍 Сканирую модуль: {module_path}")
            
            # Импортируем модуль
            spec = importlib.util.spec_from_file_location(module_path, file_path)
            if spec is None or spec.loader is None:
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Ищем классы, наследующие от BaseWindow
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (obj != BaseWindow and 
                    issubclass(obj, BaseWindow) and 
                    hasattr(obj, 'window_metadata')):
                    
                    self._register_window(obj)
                    self.discovered_modules.append(module_path)
                    
        except Exception as e:
            print(f"❌ Ошибка при сканировании {file_path}: {e}")
            traceback.print_exc()
            
    def _register_window(self, window_class: Type[BaseWindow]) -> None:
        """Регистрирует класс окна в реестре."""
        metadata = getattr(window_class, 'window_metadata', {})
        window_name = metadata.get('window_name', window_class.__name__)
        
        print(f"📝 Регистрирую окно: {window_name} ({window_class.__name__})")
        
        # Добавляем окно в реестр
        self.windows[window_name] = window_class
        
        # Добавляем в структуру меню (если нужно)
        menu_title = metadata.get('menu_title')
        if menu_title:
            category = metadata.get('menu_category', 'Прочее')
            if category not in self.menu_structure:
                self.menu_structure[category] = []
                
            menu_item = {
                'title': menu_title,
                'window_name': window_name,
                'window_class': window_class,
                'icon': metadata.get('menu_icon'),
                'shortcut': metadata.get('menu_shortcut'),
                'order': metadata.get('menu_order', 999),
                'enabled': metadata.get('menu_enabled', True),
                'tooltip': metadata.get('tooltip', '')
            }
            
            self.menu_structure[category].append(menu_item)
            
    def get_window_class(self, window_name: str) -> Optional[Type[BaseWindow]]:
        """Возвращает класс окна по имени."""
        return self.windows.get(window_name)
        
    def get_menu_structure(self) -> Dict[str, List[Dict[str, Any]]]:
        """Возвращает структуру меню, отсортированную по порядку."""
        sorted_structure = {}
        
        for category, items in self.menu_structure.items():
            sorted_items = sorted(items, key=lambda x: x['order'])
            sorted_structure[category] = sorted_items
            
        return sorted_structure
        
    def get_all_windows(self) -> Dict[str, Type[BaseWindow]]:
        """Возвращает все зарегистрированные окна."""
        return self.windows.copy()
        
    def create_window(self, window_name: str, parent=None, **kwargs) -> Optional[BaseWindow]:
        """Создает экземпляр окна по имени."""
        window_class = self.get_window_class(window_name)
        if window_class:
            try:
                return window_class(parent=parent, **kwargs)
            except Exception as e:
                print(f"❌ Ошибка при создании окна {window_name}: {e}")
                traceback.print_exc()
                return None
        else:
            print(f"❌ Окно {window_name} не найдено в реестре")
            return None
            
    def print_registry(self) -> None:
        """Выводит информацию о зарегистрированных окнах."""
        print("\n" + "="*50)
        print("📋 РЕЕСТР ОКОН")
        print("="*50)
        
        print(f"\n🔍 Обнаружено модулей: {len(self.discovered_modules)}")
        for module in sorted(self.discovered_modules):
            print(f"  - {module}")
            
        print(f"\n📝 Зарегистрировано окон: {len(self.windows)}")
        for name, cls in sorted(self.windows.items()):
            metadata = getattr(cls, 'window_metadata', {})
            print(f"  - {name} ({cls.__name__})")
            print(f"    Описание: {metadata.get('description', 'Не указано')}")
            if metadata.get('menu_title'):
                print(f"    Меню: {metadata.get('menu_category', 'Прочее')} -> {metadata['menu_title']}")
                
        print(f"\n📋 Структура меню: {len(self.menu_structure)} категорий")
        for category, items in sorted(self.menu_structure.items()):
            print(f"\n  📁 {category}:")
            for item in sorted(items, key=lambda x: x['order']):
                print(f"    - {item['title']} ({item['window_name']})")
                if item.get('shortcut'):
                    print(f"      Сочетание: {item['shortcut']}")
                    
        print("="*50)


# Глобальный экземпляр реестра
registry = WindowRegistry()


def get_registry() -> WindowRegistry:
    """Возвращает глобальный экземпляр реестра."""
    return registry


def auto_discover_windows(search_paths: Optional[List[str]] = None) -> WindowRegistry:
    """
    Автоматически обнаруживает все окна и возвращает реестр.
    
    Args:
        search_paths: Список путей для поиска
        
    Returns:
        Заполненный реестр окон
    """
    registry.discover_windows(search_paths)
    return registry


if __name__ == "__main__":
    # Тестирование системы регистрации
    print("🧪 Тестирование системы регистрации окон...")
    
    # Обнаруживаем окна
    test_registry = auto_discover_windows()
    
    # Выводим результаты
    test_registry.print_registry()
