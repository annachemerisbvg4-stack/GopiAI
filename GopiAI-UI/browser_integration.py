"""
Интеграция SmartBrowserAgent с существующим enhanced_browser_widget
"""

import sys
import os
import importlib.util
from typing import Optional, Dict, Any
from SmartBrowserAgent import SmartBrowserAgent

class BrowserIntegration:
    """Класс для интеграции SmartBrowserAgent с UI"""
    
    def __init__(self, brave_api_key: str):
        self.smart_agent = SmartBrowserAgent(brave_api_key)
        self.browser_widget = None
        
    def connect_browser_widget(self, browser_widget):
        """Подключает существующий browser widget"""
        self.browser_widget = browser_widget
        
    def smart_navigate(self, command: str) -> Dict[str, Any]:
        """Умная навигация с автоматическим определением URL"""
        
        # Обрабатываем команду через SmartAgent
        result = self.smart_agent.process_command(command)
        
        if result['success'] and result['url']:
            # Если есть подключенный browser widget, используем его
            if self.browser_widget:
                try:
                    # Предполагаем, что у browser_widget есть метод navigate
                    if hasattr(self.browser_widget, 'navigate'):
                        self.browser_widget.navigate(result['url'])
                    elif hasattr(self.browser_widget, 'load'):
                        self.browser_widget.load(result['url'])
                    elif hasattr(self.browser_widget, 'setUrl'):
                        self.browser_widget.setUrl(result['url'])
                    
                    result['message'] = f"✅ Успешно перешёл на {result['url']}"
                    
                except Exception as e:
                    result['success'] = False
                    result['message'] = f"❌ Ошибка навигации в браузере: {str(e)}"
        
        return result
    
    def add_smart_commands_to_widget(self, browser_widget):
        """Добавляет умные команды к существующему browser widget"""
        
        # Создаём обёртку для метода navigate
        original_navigate = getattr(browser_widget, 'navigate', None)
        
        def smart_navigate_wrapper(url_or_command: str):
            """Обёртка для умной навигации"""
            
            # Если это уже валидный URL, используем оригинальный метод
            if url_or_command.startswith(('http://', 'https://')):
                if original_navigate:
                    return original_navigate(url_or_command)
                return
            
            # Иначе обрабатываем как команду
            result = self.smart_navigate(url_or_command)
            
            if not result['success']:
                print(f"⚠️ {result['message']}")
                
            return result
        
        # Заменяем метод navigate на умную версию
        setattr(browser_widget, 'smart_navigate', smart_navigate_wrapper)
        
        # Добавляем alias для обратной совместимости
        if not original_navigate:
            setattr(browser_widget, 'navigate', smart_navigate_wrapper)


# Функция для быстрой интеграции
def enhance_browser_widget_with_smart_navigation(browser_widget, brave_api_key: str):
    """
    Быстрая функция для добавления умной навигации к существующему browser widget
    
    Usage:
        from browser_integration import enhance_browser_widget_with_smart_navigation
        
        # Где-то в коде UI
        enhance_browser_widget_with_smart_navigation(your_browser_widget, "your_brave_api_key")
        
        # Теперь можно использовать:
        your_browser_widget.smart_navigate("зайди на сайт leonardo ai")
    """
    
    integration = BrowserIntegration(brave_api_key)
    integration.connect_browser_widget(browser_widget)
    integration.add_smart_commands_to_widget(browser_widget)
    
    return integration


# Пример использования для enhanced_browser_widget.py
def patch_enhanced_browser_widget():
    """
    Патч для enhanced_browser_widget.py
    Добавляет умную навигацию к существующему виджету
    """
    
    try:
        # Пытаемся импортировать существующий модуль
        from gopiai.ui.components.enhanced_browser_widget import EnhancedBrowserWidget
        
        # Brave API ключ - в продакшене лучше вынести в конфиг
        BRAVE_API_KEY = "BSAEcqmI0ZUDsktUV1FKYYYq7HaQlnt"
        
        # Сохраняем оригинальный __init__
        original_init = EnhancedBrowserWidget.__init__
        
        def enhanced_init(self, *args, **kwargs):
            # Вызываем оригинальный инициализатор
            original_init(self, *args, **kwargs)
            
            # Добавляем умную навигацию
            enhance_browser_widget_with_smart_navigation(self, BRAVE_API_KEY)
        
        # Заменяем __init__
        EnhancedBrowserWidget.__init__ = enhanced_init
        
        print("✅ Enhanced browser widget successfully patched with smart navigation!")
        
    except ImportError as e:
        print(f"⚠️ Could not import enhanced_browser_widget: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🔧 Browser Integration Module")
    print("Этот модуль добавляет умную навигацию к существующим browser widgets")
    
    # Тестируем патч
    patch_enhanced_browser_widget()
