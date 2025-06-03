#!/usr/bin/env python3
"""
🧹 АВТОМАТИЧЕСКАЯ ОЧИСТКА УСТАРЕВШИХ ФАЙЛОВ GopiAI
==================================================

Скрипт удаляет устаревшие, дублирующие и ненужные файлы.
Основан на анализе от 3 июня 2025 г.

ВНИМАНИЕ: Перед запуском сделайте бэкап проекта!
"""

import os
import shutil
import sys
from datetime import datetime

# Корневая директория проекта
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Список файлов и каталогов для удаления
CLEANUP_LIST = [
    # Пустые интерфейсы
    "gopiai_mockup_interface.py",
    "gopiai_interface_with_stubs.py", 
    "gopiai_integrated_interface.py",
    
    # Устаревшие тесты
    "test_svg_rendering.py",
    "test_lucide_direct.py",
    "test_icon_adapter.py",
    "test_icons_themes.py",
    "simple_icon_test.py",
    
    # Устаревшие менеджеры
    "icon_manager.py",
    "simple_icon_manager.py",
    "simple_icon_adapter.py",
    "integrated_theme_manager.py",
    "local_titlebar_with_menu.py",
    "module_connector.py",
    "simple_module_connector.py",
    
    # Отладочные файлы
    "diagnose_icons_themes.py",
    "cleanup_old_files.py",
    "ui_debug.log",
    
    # Node.js артефакты
    "package-lock.json",
    "package.json",
    "node_modules",
    
    # Каталоги с устаревшими данными
    "imports_reports",
    "marked_code_reports", 
    "logs",
    "__pycache__",
    
    # Дублирующие файлы в RAG системе
    "rag_memory_system/project_sync",
]

# Файлы для сохранения (проверка безопасности)
KEEP_LIST = [
    "gopiai_standalone_interface.py",
    "icon_mapping.py",
    "icon_mapping_extraction_report.md",
    "test_icon_mapping.py",
    "productivity_extension.py",
    "sync_to_rag.py",
    "PROJECT_CLEANUP_ANALYSIS.md",
    "CLEANUP_REPORT.md",
    "CLEAN_MODULAR.md",
]

def log_action(message, level="INFO"):
    """Логирование действий"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_safety():
    """Проверка безопасности - все важные файлы на месте"""
    log_action("🔍 Проверка безопасности...")
    
    missing_files = []
    for file in KEEP_LIST:
        file_path = os.path.join(ROOT_DIR, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        log_action(f"❌ ОШИБКА: Отсутствуют важные файлы: {missing_files}", "ERROR")
        return False
    
    log_action("✅ Все важные файлы на месте")
    return True

def get_file_size(path):
    """Получить размер файла/каталога"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
        return total
    return 0

def format_size(size_bytes):
    """Форматирование размера в читаемый вид"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"

def cleanup_files(dry_run=True):
    """Основная функция очистки"""
    log_action("🧹 Начинаем очистку устаревших файлов...")
    
    if dry_run:
        log_action("🔍 РЕЖИМ СИМУЛЯЦИИ - файлы НЕ будут удалены")
    
    deleted_count = 0
    total_size_freed = 0
    errors = []
    
    for item in CLEANUP_LIST:
        item_path = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(item_path):
            try:
                size = get_file_size(item_path)
                size_str = format_size(size)
                
                if dry_run:
                    if os.path.isdir(item_path):
                        log_action(f"🗑️ [СИМУЛЯЦИЯ] Каталог: {item} ({size_str})")
                    else:
                        log_action(f"🗑️ [СИМУЛЯЦИЯ] Файл: {item} ({size_str})")
                else:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        log_action(f"🗑️ Удален каталог: {item} ({size_str})")
                    else:
                        os.remove(item_path)
                        log_action(f"🗑️ Удален файл: {item} ({size_str})")
                
                deleted_count += 1
                total_size_freed += size
                
            except Exception as e:
                error_msg = f"Ошибка при удалении {item}: {e}"
                errors.append(error_msg)
                log_action(error_msg, "ERROR")
        else:
            log_action(f"⚠️ Не найден: {item}", "WARN")
    
    # Итоговая статистика
    log_action("=" * 50)
    if dry_run:
        log_action(f"📊 СИМУЛЯЦИЯ ЗАВЕРШЕНА:")
    else:
        log_action(f"📊 ОЧИСТКА ЗАВЕРШЕНА:")
    
    log_action(f"   Обработано элементов: {deleted_count}")
    log_action(f"   Освобождено места: {format_size(total_size_freed)}")
    
    if errors:
        log_action(f"   Ошибок: {len(errors)}")
        for error in errors:
            log_action(f"     - {error}")
    
    return deleted_count, total_size_freed, errors

def create_backup_list():
    """Создание списка файлов для бэкапа"""
    backup_file = os.path.join(ROOT_DIR, f"cleanup_backup_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write("# Список файлов, подлежащих удалению\n")
        f.write(f"# Создан: {datetime.now()}\n\n")
        
        for item in CLEANUP_LIST:
            item_path = os.path.join(ROOT_DIR, item)
            if os.path.exists(item_path):
                size = get_file_size(item_path)
                f.write(f"{item} ({format_size(size)})\n")
    
    log_action(f"📝 Создан список для бэкапа: {backup_file}")

def main():
    """Главная функция"""
    print("🧹 GopiAI Project Cleanup Tool")
    print("=" * 40)
    
    # Проверка безопасности
    if not check_safety():
        log_action("❌ Очистка прервана из-за проблем безопасности", "ERROR")
        sys.exit(1)
    
    # Создание списка для бэкапа
    create_backup_list()
    
    # Запрос подтверждения
    mode = input("\n🤔 Выберите режим:\n1 - Симуляция (показать что будет удалено)\n2 - Реальное удаление\n\nВаш выбор (1/2): ").strip()
    
    if mode == "1":
        cleanup_files(dry_run=True)
        print("\n💡 Для реального удаления запустите скрипт еще раз и выберите режим 2")
    elif mode == "2":
        print("\n⚠️ ВНИМАНИЕ: Файлы будут удалены БЕЗВОЗВРАТНО!")
        confirm = input("Продолжить? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y', 'да', 'д']:
            cleanup_files(dry_run=False)
            log_action("✅ Очистка завершена!")
        else:
            log_action("❌ Очистка отменена пользователем")
    else:
        log_action("❌ Неверный выбор. Выход.", "ERROR")

if __name__ == "__main__":
    main()
