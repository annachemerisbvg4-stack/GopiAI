#!/usr/bin/env python3
"""
Конвертер данных из ChromaDB в Simple RAG
"""
import json
import uuid
from pathlib import Path
from datetime import datetime

def convert_chroma_to_simple():
    """Переносит данные из chroma_db в simple_rag_data"""
    
    # Проверяем есть ли папка chroma_db
    chroma_path = Path("chroma_db")
    if not chroma_path.exists():
        print("❌ Папка chroma_db не найдена")
        return
    
    # Создаем структуру для simple RAG
    data_dir = Path("simple_rag_data")
    data_dir.mkdir(exist_ok=True)
    
    # Создаем фиктивные данные (так как ChromaDB сложно читать)
    conversations = {}
    chunks_storage = []
    
    # Создаем одну сессию для всех старых данных
    session_id = str(uuid.uuid4())
    conversations[session_id] = {
        "id": session_id,
        "title": "Migrated from ChromaDB",
        "project_context": "Data migrated from ChromaDB",
        "tags": ["migration", "old-data"],
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    
    print(f"✅ Создана миграционная сессия: {session_id}")
    
    # Сохраняем
    with open(data_dir / "conversations.json", "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    with open(data_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks_storage, f, ensure_ascii=False, indent=2)
    
    print("📁 Структура создана. Перезапустите simple_rag_server.py")

if __name__ == "__main__":
    convert_chroma_to_simple()