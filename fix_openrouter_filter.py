#!/usr/bin/env python3
"""
Патч-скрипт для исправления фильтрации моделей OpenRouter
Убирает фильтрацию по is_active, так как OpenRouter помечает все модели как неактивные
"""

import os
import re

def fix_openrouter_filter():
    """Исправляет фильтрацию в openrouter_client.py"""
    file_path = r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\tools\gopiai_integration\openrouter_client.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return False
    
    print(f"🔧 Исправляем фильтрацию в: {file_path}")
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Сохраняем бэкап
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📋 Создан бэкап: {backup_path}")
    
    # Исправляем синхронный метод
    pattern1 = r'(\s+)# Фильтруем только активные модели\n(\s+)if model\.is_active:\n(\s+)models\.append\(model\)'
    replacement1 = r'\1# Показываем все модели (убрали фильтрацию is_active)\n\1# if model.is_active:  # OpenRouter помечает все модели как неактивные\n\1models.append(model)'
    
    content = re.sub(pattern1, replacement1, content)
    
    # Исправляем асинхронный метод (если есть)
    pattern2 = r'(\s+)# Фильтруем только активные модели\n(\s+)if model\.is_active:\n(\s+)models\.append\(model\)'
    content = re.sub(pattern2, replacement1, content, count=1)  # Исправляем только первое вхождение, если уже исправили
    
    # Также исправляем строки с логированием
    content = content.replace('активных моделей OpenRouter', 'моделей OpenRouter (все показаны)')
    content = content.replace('Получено {len(models)} активных моделей', 'Получено {len(models)} моделей')
    
    # Записываем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Фильтрация исправлена!")
    print("🔄 Теперь будут показаны все модели OpenRouter")
    return True

if __name__ == "__main__":
    fix_openrouter_filter()
