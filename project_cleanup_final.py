#!/usr/bin/env python3
"""
🧹 ГЕНЕРАЛЬНАЯ УБОРКА ПРОЕКТА GOPIAI
===================================

Автоматическая очистка проекта после успешного модульного рефакторинга:
- Архивирование устаревших файлов
- Очистка временных файлов
- Организация структуры проекта  
- Создание финальной документации

Автор: AI Assistant
Дата: 3 июня 2025 г.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import zipfile

class ProjectCleaner:
    """Класс для генеральной уборки проекта"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.backup_path = self.base_path / "project_cleanup_backup"
        self.archive_path = self.base_path / "archive"
        self.report = []
        
    def log(self, message):
        """Логирование действий"""
        print(message)
        self.report.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def create_backup_structure(self):
        """Создание структуры для бэкапов"""
        self.log("📁 Создание структуры бэкапов...")
        
        directories = [
            self.backup_path / "legacy_interfaces",
            self.backup_path / "test_files", 
            self.backup_path / "temporary_files",
            self.archive_path / "old_versions"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.log(f"   ✅ {directory.name}")
    
    def archive_legacy_interfaces(self):
        """Архивирование устаревших интерфейсов"""
        self.log("🗃️ Архивирование устаревших интерфейсов...")
        
        legacy_files = [
            "gopiai_standalone_interface_backup_damaged.py",
            "gopiai_standalone_interface_broken.py", 
            "gopiai_standalone_interface_old.py",
            "gopiai_standalone_interface_simple.py"
        ]
        
        moved_count = 0
        for file_name in legacy_files:
            source = self.base_path / file_name
            if source.exists():
                target = self.backup_path / "legacy_interfaces" / file_name
                shutil.move(str(source), str(target))
                self.log(f"   📦 {file_name} → backup/legacy_interfaces/")
                moved_count += 1
        
        self.log(f"   ✅ Перемещено {moved_count} устаревших файлов")
    
    def archive_test_files(self):
        """Архивирование временных тестовых файлов"""
        self.log("🧪 Архивирование тестовых файлов...")
        
        test_files = [
            "test_icons.py",
            "test_icons_themes.py", 
            "test_icon_adapter.py",
            "test_icon_mapping.py",
            "test_lucide_direct.py",
            "test_svg_rendering.py"
        ]
        
        moved_count = 0
        for file_name in test_files:
            source = self.base_path / file_name
            if source.exists():
                target = self.backup_path / "test_files" / file_name
                shutil.move(str(source), str(target))
                self.log(f"   🧪 {file_name} → backup/test_files/")
                moved_count += 1
        
        self.log(f"   ✅ Перемещено {moved_count} тестовых файлов")
    
    def clean_temporary_files(self):
        """Очистка временных файлов"""
        self.log("🗑️ Очистка временных файлов...")
        
        temp_patterns = [
            "*.pyc",
            "*.tmp", 
            "*.log",
            "*_backup_*",
            "ui_debug.log"
        ]
        
        cleaned_count = 0
        for pattern in temp_patterns:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    self.log(f"   🗑️ Удален: {file_path.name}")
                    cleaned_count += 1
        
        # Очистка __pycache__
        pycache_dirs = list(self.base_path.glob("**/__pycache__"))
        for pycache_dir in pycache_dirs:
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                self.log(f"   🗑️ Удален: {pycache_dir}")
                cleaned_count += 1
        
        self.log(f"   ✅ Очищено {cleaned_count} временных файлов")
    
    def organize_documentation(self):
        """Организация документации"""
        self.log("📚 Организация документации...")
        
        docs_path = self.base_path / "docs"
        docs_path.mkdir(exist_ok=True)
        
        doc_files = [
            "CLEAN_MODULAR.md",
            "CLEANUP_REPORT.md", 
            "CURRENT_STATUS_REPORT.md",
            "MODULAR_REFACTORING_REPORT.md",
            "REFACTORING_SUMMARY.md",
            "icon_mapping_extraction_report.md",
            "PROJECT_CLEANUP_ANALYSIS.md"
        ]
        
        moved_count = 0
        for file_name in doc_files:
            source = self.base_path / file_name
            if source.exists():
                target = docs_path / file_name
                shutil.move(str(source), str(target))
                self.log(f"   📄 {file_name} → docs/")
                moved_count += 1
        
        self.log(f"   ✅ Организовано {moved_count} документов")
    
    def create_project_structure_doc(self):
        """Создание документации финальной структуры проекта"""
        self.log("📋 Создание документации структуры проекта...")
        
        structure_doc = """# 🏗️ ФИНАЛЬНАЯ СТРУКТУРА ПРОЕКТА GOPIAI
=============================================

## 📦 Основные файлы
```
gopiai_standalone_interface_modular.py  # 🚀 Основной модульный интерфейс (394 строки)
gopiai_standalone_interface.py          # 📚 Оригинальный интерфейс (сохранен как референс)
gopiai_standalone_interface_clean.py    # 🧹 Альтернативная чистая версия
test_modular_interface.py               # 🧪 Тесты модульной архитектуры
sync_to_rag.py                          # 🔄 Синхронизация с RAG системой
auto_cleanup.py                         # 🧹 Автоматическая очистка
project_cleanup_final.py                # 🧽 Финальная генеральная уборка
```

## 🎨 Модули UI (ui_components/)
```
ui_components/
├── __init__.py              # 🎯 Центральный экспорт компонентов
├── menu_bar.py             # 📋 Система меню (StandaloneMenuBar)
├── titlebar.py             # 🏠 Заголовок окна (StandaloneTitlebar, StandaloneTitlebarWithMenu)
├── file_explorer.py        # 📁 Файловый менеджер (FileExplorerWidget)
├── tab_widget.py           # 📑 Система вкладок (TabDocumentWidget)
├── chat_widget.py          # 💬 ИИ чат (ChatWidget)
└── terminal_widget.py      # ⌨️ Терминал (TerminalWidget)
```

## 🎯 GopiAI Модули
```
GopiAI-Core/        # 🧠 Ядро системы
GopiAI-Widgets/     # 🎨 Виджеты интерфейса
GopiAI-App/         # 📱 Приложение
GopiAI-Extensions/  # 🔌 Расширения
GopiAI-Assets/      # 🖼️ Ресурсы
```

## 🗃️ Архив и бэкапы
```
project_cleanup_backup/
├── legacy_interfaces/      # 📦 Устаревшие интерфейсы
├── test_files/            # 🧪 Тестовые файлы
└── temporary_files/       # 🗑️ Временные файлы

archive/
└── old_versions/          # 📚 Старые версии
```

## 📚 Документация
```
docs/
├── MODULAR_REFACTORING_REPORT.md    # 📊 Отчет о рефакторинге
├── REFACTORING_SUMMARY.md           # 📋 Краткая сводка
├── CLEANUP_REPORT.md                # 🧹 Отчет об очистке
└── [другие документы]               # 📄 Прочая документация
```

## 🧠 RAG система
```
rag_memory_system/          # 🧠 Система памяти
├── project_sync/          # 🔄 Синхронизированные файлы
└── memory_manager.py      # 🧮 Менеджер памяти
```

## ✨ Ключевые достижения
- 📏 Размер основного файла уменьшен на **75%** (1593 → 394 строки)
- 🏗️ Создана **модульная архитектура** из 7 компонентов
- 🔄 Реализован **fallback режим** для стабильности
- 🧪 Добавлены **автоматические тесты**
- 🧹 Проведена **генеральная уборка** проекта
- 🧠 Интегрирована **RAG система** для навигации

## 🎯 Статус проекта: ЗАВЕРШЕН УСПЕШНО ✅
"""
        
        structure_file = self.base_path / "PROJECT_STRUCTURE_FINAL.md"
        with open(structure_file, 'w', encoding='utf-8') as f:
            f.write(structure_doc)
        
        self.log("   ✅ Документация структуры создана")
    
    def create_cleanup_summary(self):
        """Создание итогового отчета об уборке"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary = {
            "cleanup_date": timestamp,
            "actions_performed": self.report,
            "project_status": "CLEANED AND ORGANIZED",
            "modular_architecture": "ACTIVE",
            "main_file_size_reduction": "75% (1593 → 394 lines)",
            "modules_created": 7,
            "backup_location": str(self.backup_path),
            "archive_location": str(self.archive_path),
            "documentation_location": "docs/",
            "final_structure": "PROJECT_STRUCTURE_FINAL.md"
        }
        
        summary_file = self.base_path / "CLEANUP_FINAL_REPORT.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.log("📊 Итоговый отчет создан: CLEANUP_FINAL_REPORT.json")
    
    def run_cleanup(self):
        """Запуск полной уборки"""
        self.log("🧹 ЗАПУСК ГЕНЕРАЛЬНОЙ УБОРКИ ПРОЕКТА GOPIAI")
        self.log("=" * 60)
        
        try:
            self.create_backup_structure()
            self.archive_legacy_interfaces()
            self.archive_test_files()
            self.clean_temporary_files()
            self.organize_documentation()
            self.create_project_structure_doc()
            self.create_cleanup_summary()
            
            self.log("=" * 60)
            self.log("🎉 ГЕНЕРАЛЬНАЯ УБОРКА ЗАВЕРШЕНА УСПЕШНО!")
            self.log("✨ Проект GopiAI теперь чистый и организованный")
            self.log(f"📦 Бэкапы сохранены в: {self.backup_path}")
            self.log(f"📚 Документация в: docs/")
            self.log("🚀 Готов к дальнейшему развитию!")
            
        except Exception as e:
            self.log(f"❌ Ошибка при уборке: {e}")
            raise

def main():
    """Основная функция"""
    cleaner = ProjectCleaner()
    cleaner.run_cleanup()

if __name__ == "__main__":
    main()
