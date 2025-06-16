#!/usr/bin/env python3
"""
Тест интеграции RAG с Claude Tools
"""
import json
import urllib.request
import urllib.parse
import urllib.error

def test_search_memory_function(query: str, limit: int = 5):
    """
    Тест функции search_memory из ClaudeToolsHandler
    """
    try:
        # Валидация входных данных
        if not query or not query.strip():
            raise ValueError("Empty search query")
        
        if limit < 1 or limit > 20:
            limit = 5  # Безопасное значение по умолчанию
        
        # Подготовка URL для RAG API
        rag_api_url = "http://127.0.0.1:8080"
        search_endpoint = f"{rag_api_url}/search"
        
        # Кодирование параметров
        params = urllib.parse.urlencode({
            'q': query.strip(),
            'limit': limit
        })
        
        full_url = f"{search_endpoint}?{params}"
        
        print(f"🔍 Searching RAG memory: {query} (limit: {limit})")
        print(f"🌐 URL: {full_url}")
        
        # HTTP запрос к RAG API
        try:
            request = urllib.request.Request(full_url)
            request.add_header('Content-Type', 'application/json')
            request.add_header('User-Agent', 'GopiAI-ClaudeTools/1.0')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    search_results = json.loads(response.read().decode('utf-8'))
                    print(f"✅ API Response: {response.status}")
                else:
                    raise Exception(f"RAG API returned status {response.status}")
                    
        except urllib.error.URLError as e:
            if "Connection refused" in str(e) or "[Errno 10061]" in str(e):
                raise Exception("RAG server not running on port 8080. Start with: python start_rag_server.py")
            else:
                raise Exception(f"RAG API connection error: {e}")
        
        # Обработка результатов поиска
        if not search_results:
            result = {
                "success": True,
                "query": query,
                "results": [],
                "total_found": 0,
                "message": "No results found in memory"
            }
        else:
            # Форматирование результатов для Claude
            formatted_results = []
            for item in search_results:
                formatted_item = {
                    "session_id": item.get("session_id", ""),
                    "title": item.get("title", "Untitled"),
                    "relevance_score": item.get("relevance_score", 0.0),
                    "matched_content": item.get("matched_content", ""),
                    "context_preview": item.get("context_preview", ""),
                    "timestamp": item.get("timestamp", ""),
                    "tags": item.get("tags", [])
                }
                formatted_results.append(formatted_item)
            
            result = {
                "success": True,
                "query": query,
                "results": formatted_results,
                "total_found": len(formatted_results),
                "rag_api_url": rag_api_url
            }
        
        print(f"🎯 RAG search completed: {len(search_results)} results for '{query}'")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ RAG search error: {error_msg}")
        
        error_result = {
            "success": False,
            "error": error_msg,
            "query": query,
            "rag_status": "error"
        }
        
        return json.dumps(error_result, ensure_ascii=False, indent=2)

def test_health_check():
    """Проверка здоровья RAG API"""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5)
        data = json.loads(response.read().decode())
        print("✅ RAG Health Check:", data)
        return True
    except Exception as e:
        print("❌ RAG Health Check failed:", e)
        return False

def test_stats_check():
    """Проверка статистики RAG API"""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8080/stats", timeout=5)
        data = json.loads(response.read().decode())
        print("📊 RAG Stats:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print("❌ RAG Stats Check failed:", e)
        return False

if __name__ == "__main__":
    print("🧠 Testing RAG Integration with Claude Tools")
    print("=" * 50)
    
    # Тест 1: Health Check
    print("\n1. Health Check:")
    health_ok = test_health_check()
    
    # Тест 2: Stats Check
    print("\n2. Stats Check:")
    stats_ok = test_stats_check()
    
    # Тест 3: Search Memory Function
    print("\n3. Search Memory Function Test:")
    if health_ok:
        result = test_search_memory_function("Claude tools", 3)
        print("Search Result:")
        print(result)
    else:
        print("❌ Skipping search test - RAG server not available")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")