#!/usr/bin/env python3
import sys
import os

# Добавляем путь к GopiAI-UI модулю
sys.path.insert(0, r'C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI')

try:
    print("Тестируем импорт settings_dialog...")
    
    # Импорт по частям для точного определения проблемы
    from PySide6.QtWidgets import QApplication
    print("✅ PySide6 импортирован")
    
    # Создаем минимальное приложение
    app = QApplication.instance() or QApplication([])
    print("✅ QApplication создан")
    
    from gopiai.ui.dialogs.settings_dialog import SettingsCard
    print("✅ SettingsCard импортирован!")
    
    from gopiai.ui.dialogs.settings_dialog import GopiAISettingsDialog
    print("✅ GopiAISettingsDialog импортирован!")
    
    print("🎉 Все работает!")
    
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка в строке {e.lineno}: {e.text}")
    print(f"   {e.msg}")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("Тест завершен.")