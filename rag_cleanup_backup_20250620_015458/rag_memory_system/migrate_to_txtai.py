"""
Скрипт миграции от старой RAG системы к txtai
"""
import shutil
from pathlib import Path

def migrate_to_txtai():
    base_dir = Path(__file__).parent
    
    print("🔄 Starting migration to txtai...")
    
    # 1. Создаем backup старой системы
    backup_dir = base_dir / "backup_old_rag"
    if not backup_dir.exists():
        backup_dir.mkdir()
        
        # Копируем важные файлы в backup
        files_to_backup = [
            "memory_manager.py",
            "simple_rag_server.py", 
            "api.py",
            "client.py"
        ]
        
        for file_name in files_to_backup:
            file_path = base_dir / file_name
            if file_path.exists():
                shutil.copy2(file_path, backup_dir / file_name)
                print(f"📦 Backed up {file_name}")
    
    # 2. Удаляем ненужные файлы
    files_to_remove = [
        "simple_rag_server.py",
        "server_manager.py", 
        "run_server.py",
        "start_server.py",
        "client.py",
        "api.py",
        "demo_client.py",
        "simple_test.py",
        "final_test.py",
        "debug_search.py",
        "run_demo.py",
        "migrate_from_chroma.py"
    ]
    
    for file_name in files_to_remove:
        file_path = base_dir / file_name
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Removed {file_name}")
    
    # 3. Удаляем ненужные папки
    dirs_to_remove = [
        "simple_rag_data",
        "project_sync", 
        "__pycache__"
    ]
    
    for dir_name in dirs_to_remove:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"🗑️ Removed directory {dir_name}")
    
    # 4. Обновляем __init__.py
    init_file = base_dir / "__init__.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write('''"""
TxtAI Memory System for GopiAI
Simplified RAG replacement using txtai
"""
from .txtai_memory_manager import TxtAIMemoryManager
from .models import ConversationSession, ConversationMessage, MessageRole, SearchResult

__all__ = ['TxtAIMemoryManager', 'ConversationSession', 'ConversationMessage', 'MessageRole', 'SearchResult']
''')
    
    print("✅ Migration to txtai completed!")
    print("📁 Old files backed up to:", backup_dir)
    print("🚀 You can now use TxtAIMemoryManager instead of the old RAG system")

if __name__ == "__main__":
    migrate_to_txtai()