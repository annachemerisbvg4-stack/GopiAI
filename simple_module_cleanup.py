#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🧹 SIMPLE MODULE CLEANUP 
🎯 Простая очистка модульных папок от stub-файлов
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def load_analysis():
    """Загружает результаты анализа"""
    analysis_file = Path(__file__).parent / 'MODULE_FOLDERS_ANALYSIS.json'
    
    if not analysis_file.exists():
        print(f"❌ Файл анализа не найден: {analysis_file}")
        return None
        
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_backup_dir():
    """Создает директорию для резервных копий"""
    base_path = Path(__file__).parent
    backup_dir = base_path / 'cleanup_backup_modules' / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def cleanup_stub_files(stub_files, backup_dir):
    """Удаляет stub-файлы с резервным копированием"""
    print("\n🧹 Удаление stub-файлов...")
    
    removed_count = 0
    base_path = Path(__file__).parent
    
    for file_path_str in stub_files:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"⚠️ Файл не найден: {file_path}")
            continue
            
        try:
            # Создаем бэкап
            relative_path = file_path.relative_to(base_path)
            backup_path = backup_dir / 'stubs' / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Удаляем оригинал
            file_path.unlink()
            print(f"✅ Удален: {file_path.name}")
            removed_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при удалении {file_path}: {e}")
            
    print(f"✅ Удалено stub-файлов: {removed_count}")
    return removed_count

def archive_deprecated_files(deprecated_files, backup_dir):
    """Архивирует устаревшие файлы"""
    print("\n📦 Архивирование устаревших файлов...")
    
    base_path = Path(__file__).parent
    archive_dir = base_path / 'archive' / 'modules' / 'deprecated'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archived_count = 0
    
    for file_path_str in deprecated_files:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"⚠️ Файл не найден: {file_path}")
            continue
            
        try:
            # Определяем путь в архиве
            relative_path = file_path.relative_to(base_path)
            archive_path = archive_dir / relative_path
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Создаем бэкап
            backup_path = backup_dir / 'deprecated' / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Перемещаем в архив
            shutil.move(str(file_path), str(archive_path))
            print(f"✅ Архивирован: {file_path.name}")
            archived_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при архивировании {file_path}: {e}")
            
    print(f"✅ Архивировано файлов: {archived_count}")
    return archived_count

def remove_empty_directories():
    """Удаляет пустые директории"""
    print("\n🗂️ Удаление пустых директорий...")
    
    base_path = Path(__file__).parent
    removed_count = 0
    
    # Проходим по всем модульным папкам
    for module_name in ['GopiAI-Core', 'GopiAI-Widgets', 'GopiAI-Extensions', 'GopiAI-App', 'GopiAI-Assets']:
        module_path = base_path / module_name
        
        if not module_path.exists():
            continue
            
        # Ищем пустые директории (снизу вверх)
        for root, dirs, files in os.walk(module_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                
                try:
                    # Проверяем, пустая ли директория
                    if not any(dir_path.iterdir()):
                        # Пропускаем системные директории
                        if dir_name in ['__pycache__', '.pytest_cache', '.idea', 'venv', '.git']:
                            continue
                            
                        print(f"🗑️ Удаляем пустую директорию: {dir_path.relative_to(base_path)}")
                        dir_path.rmdir()
                        removed_count += 1
                        
                except OSError:
                    # Директория не пустая или другая ошибка
                    pass
                except Exception as e:
                    print(f"❌ Ошибка при удалении директории {dir_path}: {e}")
                    
    print(f"✅ Удалено пустых директорий: {removed_count}")
    return removed_count

def main():
    """Главная функция"""
    print("🧹 ПРОСТАЯ ОЧИСТКА МОДУЛЬНЫХ ПАПОК GopiAI")
    print("="*50)
    
    # Загружаем анализ
    analysis = load_analysis()
    if not analysis:
        return 1
        
    # Создаем директорию для резервных копий
    backup_dir = create_backup_dir()
    print(f"💾 Резервные копии будут сохранены в: {backup_dir}")
    
    # Получаем рекомендации
    recommendations = analysis.get('recommendations', [])
    
    total_removed = 0
    total_archived = 0
    
    # Выполняем очистку
    for rec in recommendations:
        if rec['action'] == 'REMOVE' and rec['category'] == 'Stub Files':
            total_removed = cleanup_stub_files(rec['files'], backup_dir)
            
        elif rec['action'] == 'ARCHIVE' and rec['category'] == 'Deprecated Files':
            total_archived = archive_deprecated_files(rec['files'], backup_dir)
    
    # Удаляем пустые директории
    empty_dirs_removed = remove_empty_directories()
    
    # Выводим сводку
    print("\n" + "="*50)
    print("✅ ОЧИСТКА ЗАВЕРШЕНА")
    print("="*50)
    print(f"🗑️ Удалено stub-файлов: {total_removed}")
    print(f"📦 Архивировано устаревших файлов: {total_archived}")
    print(f"🗂️ Удалено пустых директорий: {empty_dirs_removed}")
    print(f"💾 Резервные копии: {backup_dir}")
    
    return 0

if __name__ == "__main__":
    exit(main())
