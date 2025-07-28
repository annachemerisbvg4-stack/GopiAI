#!/usr/bin/env python3
"""
Утилита для проверки состояния файлов логов GopiAI
================================================

Проверяет доступность файлов логов для записи и показывает их статус.

Автор: Kiro AI Assistant
Дата: 2025-07-28
"""

import os
import sys
from pathlib import Path

def check_file_access(file_path):
    """Проверяет доступность файла для записи"""
    try:
        if os.path.exists(file_path):
            # Пытаемся открыть файл для записи
            with open(file_path, 'a', encoding='utf-8') as f:
                pass
            return "✅ Доступен для записи"
        else:
            return "📄 Файл не существует"
    except PermissionError:
        return "🔒 Заблокирован (возможно открыт в редакторе)"
    except OSError as e:
        return f"❌ Ошибка доступа: {e}"

def main():
    """Главная функция"""
    print("GopiAI - Проверка файлов логов")
    print("=" * 40)
    
    # Список файлов логов для проверки
    log_files = [
        "ui_debug.log",
        "GopiAI-CrewAI/crewai_api_server_debug.log",
        "GopiAI-UI/chat_debug.log",
        "GopiAI-UI/chat_widget_debug.log",
        "GopiAI-UI/crewai_client_debug.log"
    ]
    
    print("📋 Проверка основных файлов логов:")
    print()
    
    for log_file in log_files:
        status = check_file_access(log_file)
        size_info = ""
        
        if os.path.exists(log_file):
            try:
                size = os.path.getsize(log_file)
                if size < 1024:
                    size_info = f" ({size} байт)"
                elif size < 1024 * 1024:
                    size_info = f" ({size / 1024:.1f} КБ)"
                else:
                    size_info = f" ({size / (1024 * 1024):.1f} МБ)"
            except OSError:
                size_info = " (размер неизвестен)"
        
        print(f"  {status} - {log_file}{size_info}")
    
    print()
    print("🔧 Рекомендации:")
    print("  • Если файл заблокирован - закройте его в редакторе")
    print("  • Для очистки старых логов запустите: python clean_logs.py")
    print("  • Для принудительной очистки перезапустите приложения")

if __name__ == "__main__":
    main()