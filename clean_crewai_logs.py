#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки логов CrewAI от нечитаемых символов
"""

import re
import os

def clean_log_content(content):
    """Очищает содержимое лога от нечитаемых символов"""
    
    # Создаем новую строку только из читаемых символов
    clean_chars = []
    for char in content:
        code = ord(char)
        
        # Разрешенные диапазоны:
        # 32-126: основные ASCII символы (пробел, буквы, цифры, знаки)
        # 1040-1103: кириллица (А-я)
        # 1025, 1105: Ё, ё
        # 10, 13: переносы строк (\n, \r)
        # 9: табуляция (\t)
        if (32 <= code <= 126 or          # ASCII
            1040 <= code <= 1103 or       # Кириллица А-я
            code == 1025 or code == 1105 or  # Ё, ё
            code in [9, 10, 13]           # \t, \n, \r
            ):
            clean_chars.append(char)
        else:
            # Заменяем нечитаемые символы на пробел
            clean_chars.append(' ')
    
    content = ''.join(clean_chars)
    
    # Убираем множественные пробелы
    content = re.sub(r' +', ' ', content)
    
    # Убираем пробелы в начале и конце строк
    lines = content.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    content = '\n'.join(cleaned_lines)
    
    return content

def clean_crewai_log():
    """Очищает лог файл CrewAI"""
    log_file = 'GopiAI-CrewAI/crewai_api_server_debug.log'
    
    if not os.path.exists(log_file):
        print(f"[ERROR] Файл {log_file} не найден")
        return
    
    print(f"[INFO] Читаем файл {log_file}...")
    
    try:
        # Читаем исходный файл
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()
        
        print(f"[INFO] Исходный размер: {len(original_content)} символов")
        
        # Очищаем содержимое
        cleaned_content = clean_log_content(original_content)
        
        print(f"[INFO] Очищенный размер: {len(cleaned_content)} символов")
        
        # Создаем резервную копию
        backup_file = log_file + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"[INFO] Создана резервная копия: {backup_file}")
        
        # Записываем очищенное содержимое в новый файл
        clean_file = log_file.replace('.log', '_clean.log')
        with open(clean_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"[SUCCESS] Создан очищенный файл: {clean_file}")
        print("[INFO] Теперь все символы должны быть читаемыми")
        
    except Exception as e:
        print(f"[ERROR] Ошибка при обработке файла: {e}")

if __name__ == "__main__":
    clean_crewai_log()