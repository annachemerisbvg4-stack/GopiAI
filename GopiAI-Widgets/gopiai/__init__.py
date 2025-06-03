"""
🚀 GopiAI Widgets - UI компоненты для GopiAI
==========================================
Коллекция виджетов и UI компонентов для построения приложений GopiAI
"""

# Версия проекта
__version__ = "0.2.0"

# Импорт виджетов
import warnings

try:
    from . import widgets
except ImportError as e:
    warnings.warn(f"Не удалось импортировать widgets: {e}")
    widgets = None

# Список доступных модулей
available_modules = []
if widgets: 
    available_modules.append('widgets')

# Логирование статуса загрузки  
if available_modules:
    print(f"🎨 GopiAI Widgets v{__version__} загружен!")
    print(f"📦 Доступные модули: {', '.join(available_modules)}")
else:
    print("⚠️ GopiAI Widgets: Ошибка загрузки модулей")

__all__ = ['widgets', 'available_modules']