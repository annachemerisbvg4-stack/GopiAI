"""
API интерфейс для RAG Memory системы
Простой REST API для интеграции с различными клиентами
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Optional
import uvicorn
from datetime import datetime
import json

from memory_manager import RAGMemoryManager
from models import ConversationSession, MessageRole, SearchResult, MemoryStats, CreateSessionRequest, AddMessageRequest

# Создаем FastAPI приложение
app = FastAPI(
    title="GopiAI RAG Memory API",
    description="API для управления памятью разговоров в GopiAI",
    version="1.0.0"
)

# Глобальный экземпляр менеджера памяти
memory_manager = RAGMemoryManager()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Простая веб-панель для мониторинга системы"""
    stats = memory_manager.get_memory_stats()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GopiAI RAG Memory Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .stat-item {{ text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007acc; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            h1 {{ color: #333; text-align: center; }}
            h2 {{ color: #555; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
            .search-form {{ margin: 20px 0; }}
            .search-input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }}
            .search-button {{ background: #007acc; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }}
            .search-button:hover {{ background: #005999; }}
            .tag {{ background: #e1f5fe; color: #0277bd; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 GopiAI RAG Memory Dashboard</h1>
            
            <div class="card">
                <h2>📊 Статистика памяти</h2>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{stats.total_sessions}</div>
                        <div class="stat-label">Всего разговоров</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats.total_messages}</div>
                        <div class="stat-label">Всего сообщений</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats.total_documents}</div>
                        <div class="stat-label">Документов в БД</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats.storage_size_mb:.1f} МБ</div>
                        <div class="stat-label">Размер хранилища</div>
                    </div>
                </div>
                
                {f'''
                <div style="margin-top: 20px;">
                    <strong>Период:</strong> 
                    {stats.oldest_session.strftime("%d.%m.%Y") if stats.oldest_session else "Нет данных"} - 
                    {stats.newest_session.strftime("%d.%m.%Y") if stats.newest_session else "Нет данных"}
                </div>
                ''' if stats.oldest_session else ''}
                
                {f'''
                <div style="margin-top: 15px;">
                    <strong>Популярные теги:</strong><br>
                    {"".join([f'<span class="tag">{tag}</span>' for tag in stats.most_active_tags[:10]])}
                </div>
                ''' if stats.most_active_tags else ''}
            </div>
            
            <div class="card">
                <h2>🔍 Поиск в памяти</h2>
                <div class="search-form">
                    <input type="text" id="searchQuery" class="search-input" placeholder="Введите запрос для поиска в истории разговоров...">
                    <button onclick="searchMemory()" class="search-button">Поиск</button>
                </div>
                <div id="searchResults"></div>
            </div>
            
            <div class="card">
                <h2>⚡ API Endpoints</h2>
                <ul>
                    <li><strong>GET /stats</strong> - Статистика системы</li>
                    <li><strong>POST /sessions</strong> - Создать новую сессию</li>
                    <li><strong>POST /sessions/{{session_id}}/messages</strong> - Добавить сообщение</li>
                    <li><strong>GET /search?q={{query}}</strong> - Поиск в разговорах</li>
                    <li><strong>GET /sessions/{{session_id}}</strong> - Получить разговор</li>
                </ul>
            </div>
        </div>
        
        <script>
            async function searchMemory() {{
                const query = document.getElementById('searchQuery').value;
                if (!query.trim()) return;
                
                try {{
                    const response = await fetch(`/search?q=${{encodeURIComponent(query)}}`);
                    const results = await response.json();
                    
                    const resultsDiv = document.getElementById('searchResults');
                    if (results.length === 0) {{
                        resultsDiv.innerHTML = '<p>Ничего не найдено</p>';
                        return;
                    }}
                    
                    let html = '<h3>Результаты поиска:</h3>';
                    results.forEach(result => {{
                        html += `
                            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px;">
                                <h4>${{result.title}} <span style="color: #666; font-size: 0.9em;">(релевантность: ${{(result.relevance_score * 100).toFixed(1)}}%)</span></h4>
                                <p>${{result.context_preview}}</p>
                                <small>Дата: ${{new Date(result.timestamp).toLocaleDateString('ru-RU')}} | Теги: ${{result.tags.join(', ')}}</small>
                            </div>
                        `;
                    }});
                    resultsDiv.innerHTML = html;
                }} catch (error) {{
                    console.error('Ошибка поиска:', error);
                    document.getElementById('searchResults').innerHTML = '<p style="color: red;">Ошибка поиска</p>';
                }}
            }}
            
            // Поиск по Enter
            document.getElementById('searchQuery').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    searchMemory();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/stats")
async def get_stats() -> MemoryStats:
    """Получить статистику памяти"""
    return memory_manager.get_memory_stats()

@app.post("/sessions")
async def create_session(request: CreateSessionRequest) -> dict:
    """Создать новую сессию разговора"""
    try:
        session = memory_manager.create_session(request.title, request.project_context, request.tags)
        return {"session_id": session.session_id, "message": "Сессия создана"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions/{session_id}/messages")
async def add_message(session_id: str, request: AddMessageRequest) -> dict:
    """Добавить сообщение в сессию"""
    try:
        message = memory_manager.add_message(session_id, request.role, request.content, request.metadata)
        return {"message_id": message.id, "message": "Сообщение добавлено"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_conversations(q: str, limit: int = 5) -> List[SearchResult]:
    """Поиск в разговорах"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Пустой запрос")
    
    try:
        results = memory_manager.search_conversations(q, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Optional[ConversationSession]:
    """Получить конкретную сессию"""
    session = memory_manager.get_conversation_history(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return session

@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

def start_server(host: str = "127.0.0.1", port: int = 8080):
    """Запустить сервер"""
    print(f"🚀 Запуск RAG Memory API сервера на http://{host}:{port}")
    print(f"📊 Dashboard доступен по адресу: http://{host}:{port}")
    print(f"📚 API документация: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
