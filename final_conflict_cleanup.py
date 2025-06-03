#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🔧 FINAL CONFLICT CLEANUP 
🎯 Удаление оставшихся конфликтующих файлов из старых модулей
"""

import shutil
from pathlib import Path
from datetime import datetime

def main():
    """Главная функция"""
    print("🔧 ФИНАЛЬНАЯ ОЧИСТКА КОНФЛИКТУЮЩИХ ФАЙЛОВ")
    print("="*50)
    
    base_path = Path(__file__).parent
    backup_dir = base_path / 'cleanup_backup_modules' / datetime.now().strftime('%Y%m%d_%H%M%S_conflicts')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Список конфликтующих файлов для удаления
    conflicting_files = [
        # Старые виджеты чата и терминала в корне GopiAI-Widgets
        'GopiAI-Widgets/simple_chat_widget.py',
        'GopiAI-Widgets/terminal_widget.py',
        
        # Старый titlebar в компонентах
        'GopiAI-Widgets/gopiai/widgets/components/titlebar.py',
        
        # Старые виджеты в корне GopiAI-Widgets, которые дублируют функциональность
        'GopiAI-Widgets/thought_tree_widget.py',
    ]
    
    removed_count = 0
    
    for file_rel_path in conflicting_files:
        file_path = base_path / file_rel_path
        
        if not file_path.exists():
            print(f"⚠️ Файл не найден: {file_rel_path}")
            continue
            
        try:
            # Создаем бэкап
            backup_path = backup_dir / file_rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Удаляем оригинал
            file_path.unlink()
            print(f"✅ Удален конфликтующий файл: {file_path.name}")
            removed_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при удалении {file_path}: {e}")
    
    # Удаляем пустые директории после удаления файлов
    print("\n🗂️ Проверка пустых директорий...")
    empty_dirs_removed = 0
    
    for module_name in ['GopiAI-Widgets', 'GopiAI-Core', 'GopiAI-Extensions', 'GopiAI-App']:
        module_path = base_path / module_name
        
        if not module_path.exists():
            continue
            
        # Ищем пустые директории (снизу вверх)
        import os
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
                        empty_dirs_removed += 1
                        
                except OSError:
                    # Директория не пустая или другая ошибка
                    pass
                except Exception as e:
                    print(f"❌ Ошибка при удалении директории {dir_path}: {e}")
    
    # Выводим сводку
    print("\n" + "="*50)
    print("✅ ФИНАЛЬНАЯ ОЧИСТКА ЗАВЕРШЕНА")
    print("="*50)
    print(f"🗑️ Удалено конфликтующих файлов: {removed_count}")
    print(f"🗂️ Удалено пустых директорий: {empty_dirs_removed}")
    print(f"💾 Резервные копии: {backup_dir}")
    
    print("\n✨ Теперь проект использует только новый модульный интерфейс!")
    print("🎯 Все старые заглушки, дубли и конфликтующие файлы удалены")
    
    return 0

if __name__ == "__main__":
    exit(main())
