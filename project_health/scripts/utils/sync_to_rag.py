#!/usr/bin/env python3
"""
Синхронизация проекта с RAG системой
===================================

Автоматическая синхронизация project_map.json и ключевых файлов
проекта с RAG системой для улучшения навигации и поиска

Автор: Crazy Coder
Дата: 2025-06-02
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def sync_project_to_rag():
    """Синхронизация проекта с RAG системой"""
    
    # Получаем базовый путь к проекту (GOPI_AI_MODULES)
    base_path = Path(__file__).parent.parent.parent.parent
    reports_path = base_path / "project_health" / "reports"
    rag_path = base_path / "rag_memory_system" / "project_sync"
    
    # Создаем папку для синхронизации, если её нет
    rag_path.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Синхронизация проекта с RAG системой...")
    print("=" * 50)
    
    # Файлы для синхронизации (обновленные пути)
    files_to_sync = [
        ("project_health/reports/project_map.json", "project_map.json"),
        ("UI/main.py", "main_ui.py"),
        ("gopiai_standalone_interface.py", "standalone_interface.py"),
        ("README.md", "README.md")
    ]
    
    # Ключевые папки для синхронизации
    folders_to_sync = {
        "UI/utils": ["*.py"],
        "UI/components": ["*.py"],
        "GopiAI-Core/gopiai": ["*.py"],
        "GopiAI-Extensions/gopiai": ["*.py"]
    }
    
    synced_files = []
    
    # Синхронизируем основные файлы
    for source_path, target_name in files_to_sync:
        source_file = base_path / source_path
        if source_file.exists():
            target_file = rag_path / target_name
            try:
                shutil.copy2(source_file, target_file)
                synced_files.append(target_name)
                print(f"📄 Синхронизирован: {source_path} -> {target_name}")
            except Exception as e:
                print(f"⚠️  Ошибка при синхронизации {source_path}: {e}")
        else:
            print(f"❌ Файл не найден: {source_path}")
    
    # Синхронизируем папки
    for folder_path, patterns in folders_to_sync.items():
        source_folder = base_path / folder_path
        if source_folder.exists():
            target_folder = rag_path / folder_path
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Копируем файлы по паттернам
            for pattern in patterns:
                for file_path in source_folder.glob(pattern):
                    if file_path.is_file():
                        target_file = target_folder / file_path.name
                        try:
                            shutil.copy2(file_path, target_file)
                            print(f"📁 Синхронизирован: {folder_path}/{file_path.name}")
                        except Exception as e:
                            print(f"⚠️  Ошибка: {e}")
    
    # Создаем метаданные синхронизации
    metadata = {
        "sync_time": datetime.now().isoformat(),
        "synced_files": synced_files,
        "total_files": len(synced_files),
        "source_path": str(base_path),
        "rag_path": str(rag_path)
    }
    
    metadata_file = rag_path / "sync_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("=" * 50)
    print(f"✅ Синхронизация завершена!")
    print(f"📄 Синхронизировано файлов: {len(synced_files)}")
    print(f"📁 Путь RAG: {rag_path}")
    print(f"🕒 Время: {datetime.now().strftime('%H:%M:%S')}")
    
    return rag_path

def create_rag_index():
    """Создание индекса RAG для быстрого поиска"""
    try:
        # Проверяем наличие project_map.json в reports
        base_path = Path(__file__).parent.parent.parent.parent
        project_map_path = base_path / "project_health" / "reports" / "project_map.json"
        
        print("\n🧠 Создание RAG индекса...")
        
        if project_map_path.exists():
            with open(project_map_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Создаем упрощённый индекс для поиска
            index_data = {
                "project_overview": {
                    "name": project_data.get("project_name", "GopiAI"),
                    "total_files": project_data.get("summary", {}).get("total_files", 0),
                    "total_modules": project_data.get("summary", {}).get("total_modules", 0),
                    "modules": list(project_data.get("modules", {}).keys())
                },
                "modules_detail": project_data.get("modules", {}),
                "generated_at": project_data.get("generated_at"),
                "quick_access": {
                    "ui_files": [f for f in project_data.get("modules", {}).get("UI", {}).get("files", [])],
                    "core_files": [f for f in project_data.get("modules", {}).get("GopiAI-Core", {}).get("files", [])],
                    "extension_files": [f for f in project_data.get("modules", {}).get("GopiAI-Extensions", {}).get("files", [])]
                }
            }
            
            # Сохраняем упрощённый индекс
            rag_path = base_path / "rag_memory_system" / "project_sync"
            rag_path.mkdir(parents=True, exist_ok=True)
            
            index_file = rag_path / "project_index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            print("📊 Project index создан для RAG системы")
            print(f"📁 Сохранён в: {index_file}")
        else:
            print(f"⚠️  Project map не найден: {project_map_path}")
        
        print("✅ RAG индекс готов!")
        
    except Exception as e:
        print(f"⚠️  Ошибка создания RAG индекса: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    # Синхронизируем файлы
    rag_path = sync_project_to_rag()
    
    # Создаем RAG индекс
    create_rag_index()
    
    print(f"\\n💡 Теперь AI сможет лучше ориентироваться в проекте!")
    print(f"🔍 Используйте RAG поиск для поиска компонентов и кода")
