#!/usr/bin/env python3
"""
Простой RAG сервер без ChromaDB
===============================
FastAPI сервер для приема chunk-ов и сохранения в JSON
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict, Any
import uvicorn
import json
import uuid
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

app = FastAPI(
    title="GopiAI Simple RAG API", 
    description="Упрощенный RAG API без ChromaDB",
    version="1.0.0"
)

# Хранилище в памяти
conversations = {}
chunks_storage = []

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Простая панель"""
    stats = {
        "conversations": len(conversations),
        "chunks": len(chunks_storage)
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Simple RAG Dashboard</title></head>
    <body>
        <h1>🧠 Simple RAG Memory</h1>
        <p>Conversations: {stats['conversations']}</p>
        <p>Chunks: {stats['chunks']}</p>
    </body>
    </html>
    """
    return html

class SessionCreate(BaseModel):
    title: str
    project_context: str = ""
    tags: List[str] = []

@app.post("/sessions")
async def create_session(session_data: SessionCreate):
    """Создать сессию"""
    session_id = str(uuid.uuid4())
    conversations[session_id] = {
        "id": session_id,
        "title": session_data.title,
        "project_context": session_data.project_context,
        "tags": session_data.tags,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    return {"session_id": session_id}

@app.post("/sessions/{session_id}/messages")
async def add_message(session_id: str, message: Dict[str, Any]):
    """Добавить сообщение"""
    if session_id not in conversations:
        raise HTTPException(404, "Session not found")
    
    # Добавляем сообщение
    conversations[session_id]["messages"].append({
        "role": message.get("role", "user"),
        "content": message.get("content", ""),
        "metadata": message.get("metadata", {}),
        "created_at": datetime.now().isoformat()
    })
    
    # Сохраняем chunk для поиска
    chunks_storage.append({
        "session_id": session_id,
        "content": message.get("content", ""),
        "metadata": message.get("metadata", {}),
        "created_at": datetime.now().isoformat()
    })
    
    return {"status": "added"}

@app.get("/search")
async def search_memory(q: str, limit: int = 5):
    """Простой поиск по содержимому"""
    results = []
    query_lower = q.lower()
    
    for chunk in chunks_storage:
        if query_lower in chunk["content"].lower():
            # Формат совместимый с claude_tools_handler.py и chat_memory.py
            results.append({
                "session_id": chunk["session_id"],
                "title": f"Conversation from {chunk['created_at'][:10]}",
                "relevance_score": 0.8,  # Простая метрика - если найдено, то релевантно
                "matched_content": chunk["content"][:300] + "..." if len(chunk["content"]) > 300 else chunk["content"],
                "context_preview": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "timestamp": chunk["created_at"],
                "tags": chunk["metadata"].get("tags", []),
                "content": chunk["content"][:500] + "..." if len(chunk["content"]) > 500 else chunk["content"],
                "metadata": chunk["metadata"]
            })
            
        if len(results) >= limit:
            break
    
    return {"results": results}

@app.get("/sessions")
async def list_sessions():
    """Список сессий"""
    return {"sessions": list(conversations.values())}

@app.get("/health")
async def health_check():
    """Проверка состояния сервера"""
    return {"status": "ok", "message": "Simple RAG server is running"}

@app.get("/stats")
async def get_stats():
    """Статистика"""
    return {
        "conversations": len(conversations),
        "chunks": len(chunks_storage),
        "total_content_size": sum(len(c["content"]) for c in chunks_storage)
    }

def save_to_files():
    """Сохранить данные в файлы"""
    data_dir = Path("simple_rag_data")
    data_dir.mkdir(exist_ok=True)
    
    # Сохраняем conversations
    with open(data_dir / "conversations.json", "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    # Сохраняем chunks
    with open(data_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks_storage, f, ensure_ascii=False, indent=2)

def load_from_files():
    """Загрузить данные из файлов"""
    global conversations, chunks_storage
    data_dir = Path("simple_rag_data")
    
    try:
        if (data_dir / "conversations.json").exists():
            with open(data_dir / "conversations.json", "r", encoding="utf-8") as f:
                conversations = json.load(f)
        
        if (data_dir / "chunks.json").exists():
            with open(data_dir / "chunks.json", "r", encoding="utf-8") as f:
                chunks_storage = json.load(f)
                
        print(f"Загружено: {len(conversations)} сессий, {len(chunks_storage)} chunk-ов")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")

@app.on_event("startup")
async def startup_event():
    """При запуске"""
    load_from_files()

@app.on_event("shutdown") 
async def shutdown_event():
    """При остановке"""
    save_to_files()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    print(f"🚀 Запуск Simple RAG сервера на http://127.0.0.1:{port}")
    print(f"📊 Dashboard: http://127.0.0.1:{port}")
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=port)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
        save_to_files()