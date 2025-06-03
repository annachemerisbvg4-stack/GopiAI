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
    
    base_path = Path(__file__).parent
    rag_path = base_path / "rag_memory_system" / "project_sync"
    
    # Создаем папку для синхронизации, если её нет
    rag_path.mkdir(exist_ok=True)
    
    print("🔄 Синхронизация проекта с RAG системой...")
    print("=" * 50)
    
    # Файлы для синхронизации
    files_to_sync = [
        "project_map.json",
        "gopiai_standalone_interface.py",
        "CLEAN_MODULAR.md",
        "CLEANUP_REPORT.md"
    ]
    
    # Папки для синхронизации (только ключевые файлы)
    folders_to_sync = {
        "GopiAI-Extensions/gopiai/extensions": ["*.py"],
        "GopiAI-Core/gopiai": ["*.py"],
        "GopiAI-Widgets/gopiai": ["*.py"]
    }
    
    synced_files = []
    
    # Синхронизируем основные файлы
    for file_name in files_to_sync:
        source_file = base_path / file_name
        if source_file.exists():
            target_file = rag_path / file_name
            try:
                shutil.copy2(source_file, target_file)
                synced_files.append(file_name)
                print(f"📄 Синхронизирован: {file_name}")
            except Exception as e:
                print(f"⚠️  Ошибка при синхронизации {file_name}: {e}")
        else:
            print(f"❌ Файл не найден: {file_name}")
    
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
        import sys
        sys.path.append(str(Path(__file__).parent))
        from rag_memory_system.memory_manager import MemoryManager
        
        print("\\n🧠 Создание RAG индекса...")
        
        # Инициализируем менеджер памяти
        memory = MemoryManager()
        
        # Добавляем project_map.json в индекс
        project_map_path = Path(__file__).parent / "project_map.json"
        if project_map_path.exists():
            with open(project_map_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Создаем запись для project_map
            memory.save_conversation({
                "type": "project_structure",
                "content": json.dumps(project_data, indent=2, ensure_ascii=False),
                "metadata": {
                    "file_type": "project_map",
                    "total_files": project_data.get("total_files", 0),
                    "modules": list(project_data.get("modules", {}).keys())
                }
            })
            
            print("📊 Project map добавлен в RAG индекс")
        
        print("✅ RAG индекс создан!")
        
    except ImportError:
        print("⚠️  RAG система недоступна, пропускаем индексацию")
    except Exception as e:
        print(f"⚠️  Ошибка создания RAG индекса: {e}")

if __name__ == "__main__":
    # Синхронизируем файлы
    rag_path = sync_project_to_rag()
    
    # Создаем RAG индекс
    create_rag_index()
    
    print(f"\\n💡 Теперь AI сможет лучше ориентироваться в проекте!")
    print(f"🔍 Используйте RAG поиск для поиска компонентов и кода")
