"""
🚀 GopiAI - Универсальная ИИ платформа
====================================
Единая точка входа для всех модулей GopiAI
"""

# Версия проекта
__version__ = "0.2.0"

# Автоматический импорт всех доступных модулей
import warnings

def _safe_import(module_name, package_name):
    """Безопасный импорт модуля"""
    try:
        module = __import__(module_name, fromlist=[package_name])
        return getattr(module, package_name, None)
    except ImportError:
        warnings.warn(f"Модуль {module_name}.{package_name} недоступен")
        return None

# Попытка импорта всех основных модулей
core = _safe_import('gopiai', 'core')
app = _safe_import('gopiai', 'app') 
widgets = _safe_import('gopiai', 'widgets')
extensions = _safe_import('gopiai', 'extensions')
assets = _safe_import('gopiai', 'assets')

# Список доступных модулей
available_modules = []
if core: available_modules.append('core')
if app: available_modules.append('app')
if widgets: available_modules.append('widgets')
if extensions: available_modules.append('extensions')
if assets: available_modules.append('assets')

print(f"🚀 GopiAI v{__version__} загружен!")
print(f"📦 Доступные модули: {', '.join(available_modules)}")

__all__ = ['core', 'app', 'widgets', 'extensions', 'assets', 'available_modules']
