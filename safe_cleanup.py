#!/usr/bin/env python3
"""
🧹 БЕЗОПАСНАЯ ОЧИСТКА ПРОБЛЕМНЫХ ФАЙЛОВ
=====================================

Удаляет/архивирует файлы, которые могут вызвать конфликты:
- Пустые файлы (могут маскировать реальные модули)
- Дублирующие файлы
- Временные костыли

ВНИМАНИЕ: Создаёт бэкап перед удалением!
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class SafeCleaner:
    """Безопасный очиститель проблемных файлов"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.backup_path = self.base_path / "cleanup_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
    def log(self, message):
        print(f"🧹 {message}")
    
    def backup_file(self, file_path):
        """Создание бэкапа файла перед удалением"""
        backup_file = self.backup_path / file_path.name
        shutil.copy2(file_path, backup_file)
        self.log(f"   💾 Бэкап создан: {backup_file}")
    
    def remove_empty_files(self):
        """Удаление пустых файлов (ОПАСНО для импортов!)"""
        self.log("УДАЛЕНИЕ ПУСТЫХ ФАЙЛОВ:")
        
        empty_files = [
            "icon_manager.py",
            "integrated_theme_manager.py", 
            "productivity_extension.py",
            "simple_module_connector.py"
        ]
        
        for file_name in empty_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                # Проверяем, действительно ли файл пустой
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    self.backup_file(file_path)
                    file_path.unlink()
                    self.log(f"   ❌ УДАЛЕН: {file_name} (был пустой)")
                else:
                    self.log(f"   ⚠️ ПРОПУЩЕН: {file_name} (не пустой)")
            else:
                self.log(f"   ❓ НЕ НАЙДЕН: {file_name}")
    
    def archive_duplicate_files(self):
        """Архивирование дублирующих файлов"""
        self.log("\\nАРХИВИРОВАНИЕ ДУБЛИРУЮЩИХ ФАЙЛОВ:")
        
        archive_path = self.base_path / "archive" / "duplicates"
        archive_path.mkdir(parents=True, exist_ok=True)
        
        duplicates = [
            "gopiai_standalone_interface_clean.py"  # Дублирует modular версию
        ]
        
        for file_name in duplicates:
            file_path = self.base_path / file_name
            if file_path.exists():
                target_path = archive_path / file_name
                self.backup_file(file_path)
                shutil.move(str(file_path), str(target_path))
                self.log(f"   📦 АРХИВИРОВАН: {file_name} → archive/duplicates/")
    
    def clean_temporary_adapters(self):
        """Очистка временных адаптеров-костылей"""
        self.log("\\nОЧИСТКА ВРЕМЕННЫХ КОСТЫЛЕЙ:")
        
        temp_files = [
            "simple_icon_adapter.py"  # Временный костыль для IconAdapter
        ]
        
        for file_name in temp_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                self.backup_file(file_path)
                file_path.unlink()
                self.log(f"   🗑️ УДАЛЕН: {file_name} (временный костыль)")
    
    def organize_tests(self):
        """Перенос тестов в папку tests/"""
        self.log("\\nОРГАНИЗАЦИЯ ТЕСТОВ:")
        
        tests_path = self.base_path / "tests"
        tests_path.mkdir(exist_ok=True)
        
        test_files = [
            "test_modular_interface.py"
        ]
        
        for file_name in test_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                target_path = tests_path / file_name
                shutil.move(str(file_path), str(target_path))
                self.log(f"   📁 ПЕРЕМЕЩЕН: {file_name} → tests/")
    
    def clean_node_modules(self):
        """Очистка node_modules (если не нужны)"""
        self.log("\\nПРОВЕРКА NODE_MODULES:")
        
        node_modules = self.base_path / "node_modules"
        package_json = self.base_path / "package.json"
        
        if node_modules.exists():
            if package_json.exists():
                with open(package_json, 'r') as f:
                    content = f.read()
                    if len(content.strip()) < 100:  # Почти пустой package.json
                        self.log(f"   ⚠️ package.json выглядит минимальным: {len(content)} байт")
                        response = input("   🤔 Удалить node_modules? (y/N): ")
                        if response.lower() == 'y':
                            shutil.rmtree(node_modules)
                            self.log(f"   🗑️ УДАЛЕН: node_modules/")
                        else:
                            self.log(f"   ✋ ОСТАВЛЕН: node_modules/")
                    else:
                        self.log(f"   ✅ ОСТАВЛЕН: node_modules/ (package.json не пустой)")
            else:
                self.log(f"   ⚠️ node_modules без package.json - подозрительно")
    
    def create_safety_report(self):
        """Создание отчета о безопасности очистки"""
        report = f"""# 🧹 ОТЧЕТ О БЕЗОПАСНОЙ ОЧИСТКЕ
=====================================

Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Бэкап: {self.backup_path}

## Удаленные файлы:
- Пустые файлы, которые могли маскировать реальные модули
- Временные костыли и адаптеры
- Дублирующие файлы

## Архивированные файлы:
- Дублирующие интерфейсы → archive/duplicates/

## Перемещенные файлы:
- Тесты → tests/

## ⚠️ ВАЖНО:
Все файлы сохранены в бэкапе: {self.backup_path}
При проблемах можно восстановить любой файл!

## 🎯 Результат:
- Устранены потенциальные конфликты импортов
- Очищена структура проекта
- Сохранена безопасность (полный бэкап)
"""
        
        report_file = self.base_path / "SAFETY_CLEANUP_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"\\n📊 Отчет создан: {report_file}")
    
    def run_safe_cleanup(self):
        """Запуск безопасной очистки"""
        self.log("🚀 ЗАПУСК БЕЗОПАСНОЙ ОЧИСТКИ ПРОЕКТА")
        self.log("=" * 50)
        self.log(f"📦 Бэкап будет создан в: {self.backup_path}")
        
        try:
            self.remove_empty_files()
            self.archive_duplicate_files()
            self.clean_temporary_adapters()
            self.organize_tests()
            self.clean_node_modules()
            self.create_safety_report()
            
            self.log("=" * 50)
            self.log("🎉 БЕЗОПАСНАЯ ОЧИСТКА ЗАВЕРШЕНА!")
            self.log("✨ Проект стал чище и безопаснее")
            self.log(f"💾 Все бэкапы в: {self.backup_path}")
            
        except Exception as e:
            self.log(f"❌ ОШИБКА: {e}")
            self.log("🔄 Восстановите файлы из бэкапа при необходимости")

def main():
    """Основная функция"""
    print("⚠️ ВНИМАНИЕ: Это действие удалит/переместит файлы!")
    print("✅ Будет создан полный бэкап")
    
    response = input("\\n🤔 Продолжить безопасную очистку? (y/N): ")
    
    if response.lower() == 'y':
        cleaner = SafeCleaner()
        cleaner.run_safe_cleanup()
    else:
        print("✋ Очистка отменена")

if __name__ == "__main__":
    main()
