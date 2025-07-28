#!/usr/bin/env python3
"""
Скрипт для очистки старых файлов логов GopiAI
=============================================

Этот скрипт удаляет все старые файлы логов из различных компонентов GopiAI,
оставляя только самые последние файлы логов.

Автор: Kiro AI Assistant
Дата: 2025-07-28
"""

import os
import glob
import shutil
from pathlib import Path

def clean_logs():
    """Очищает старые файлы логов"""
    
    print("🧹 Начинаем очистку старых файлов логов...")
    
    # Список директорий и паттернов файлов логов для очистки
    log_patterns = [
        # GopiAI-UI логи
        "GopiAI-UI/logs/*.log",
        "GopiAI-UI/chat_debug.log",
        "GopiAI-UI/chat_widget_debug.log", 
        "GopiAI-UI/crewai_client_debug.log",
        "GopiAI-UI/gopiai/ui/logs/*.log",
        "GopiAI-UI/gopiai/ui/components/logs/*.log",
        
        # GopiAI-CrewAI логи
        "GopiAI-CrewAI/logs/*.log",
        
        # Общие логи
        "logs/*.log",
        "*.log"
    ]
    
    # Файлы которые НЕ нужно удалять (текущие активные логи)
    keep_files = [
        "ui_debug.log",
        "crewai_api_server_debug.log"
    ]
    
    total_deleted = 0
    total_size_freed = 0
    
    for pattern in log_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            file_name = os.path.basename(file_path)
            
            # Пропускаем файлы которые нужно оставить
            if file_name in keep_files:
                continue
                
            try:
                # Получаем размер файла перед удалением
                file_size = os.path.getsize(file_path)
                
                # Удаляем файл
                os.remove(file_path)
                
                total_deleted += 1
                total_size_freed += file_size
                
                print(f"  ✅ Удален: {file_path} ({file_size} байт)")
                
            except PermissionError:
                print(f"  ⚠️ Файл заблокирован (возможно открыт в редакторе): {file_path}")
            except OSError as e:
                print(f"  ❌ Ошибка при удалении {file_path}: {e}")
    
    # Очищаем пустые директории логов
    empty_dirs = [
        "GopiAI-UI/logs",
        "GopiAI-UI/gopiai/ui/logs", 
        "GopiAI-UI/gopiai/ui/components/logs",
        "GopiAI-CrewAI/logs",
        "logs"
    ]
    
    for dir_path in empty_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                # Проверяем, пуста ли директория
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"  🗂️ Удалена пустая директория: {dir_path}")
            except OSError:
                pass  # Игнорируем ошибки
    
    # Форматируем размер освобожденного места
    if total_size_freed < 1024:
        size_str = f"{total_size_freed} байт"
    elif total_size_freed < 1024 * 1024:
        size_str = f"{total_size_freed / 1024:.1f} КБ"
    else:
        size_str = f"{total_size_freed / (1024 * 1024):.1f} МБ"
    
    print(f"\n✅ Очистка завершена!")
    print(f"📊 Удалено файлов: {total_deleted}")
    print(f"💾 Освобождено места: {size_str}")
    
    if total_deleted == 0:
        print("ℹ️ Старые файлы логов не найдены")

def main():
    """Главная функция"""
    print("GopiAI - Утилита очистки логов")
    print("=" * 40)
    
    try:
        clean_logs()
    except KeyboardInterrupt:
        print("\n⚠️ Очистка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()