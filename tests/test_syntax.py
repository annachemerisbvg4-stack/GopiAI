#!/usr/bin/env python3
# Простой тест синтаксиса для settings_dialog.py

import sys
import os

# Добавляем путь к GopiAI-UI модулю
sys.path.insert(0, r'C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI')

try:
    print("Тестируем импорт settings_dialog...")
    from gopiai.ui.dialogs.settings_dialog import SettingsCard, GopiAISettingsDialog
    print("✅ Импорт успешен!")
    
    print("Тестируем создание SettingsCard...")
    card = SettingsCard("Тест", "Тестовое описание")
    print("✅ SettingsCard создана успешно!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()