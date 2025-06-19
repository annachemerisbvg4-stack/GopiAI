"""
Простой клиент для тестирования RAG Memory системы
"""
import requests
import json
from datetime import datetime
from typing import List, Optional

class RAGMemoryClient:
    """Клиент для взаимодействия с RAG Memory API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def create_conversation(self, title: str, project_context: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """Создать новый разговор"""
        data = {"title": title}
        if project_context:
            data["project_context"] = project_context
        if tags:
            data["tags"] = tags
        
        response = self.session.post(f"{self.base_url}/sessions", params=data)
        response.raise_for_status()
        return response.json()["session_id"]
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[dict] = None):
        """Добавить сообщение в разговор"""
        data = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        response = self.session.post(f"{self.base_url}/sessions/{session_id}/messages", json=data)
        response.raise_for_status()
        return response.json()
    
    def search_memory(self, query: str, limit: int = 5) -> List[dict]:
        """Поиск в памяти"""
        params = {"q": query, "limit": limit}
        response = self.session.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_conversation(self, session_id: str) -> dict:
        """Получить разговор"""
        response = self.session.get(f"{self.base_url}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> dict:
        """Получить статистику"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

def demo_conversation():
    """Демонстрация работы с RAG Memory системой"""
    print("🧠 Демонстрация RAG Memory системы")
    print("=" * 50)
    
    client = RAGMemoryClient()
    
    try:
        # Тест здоровья системы
        health = client.session.get("http://127.0.0.1:8080/health").json()
        print(f"✅ Система работает: {health['status']}")
        print()
        
        # Создаем тестовый разговор
        session_id = client.create_conversation(
            title="Тестирование RAG системы",
            project_context="GopiAI-Core",
            tags=["тест", "rag", "память"]
        )
        print(f"📝 Создан разговор: {session_id}")
        
        # Добавляем сообщения
        print("💬 Добавление сообщений...")
        
        client.add_message(session_id, "user", 
                          "Привет! Я тестирую новую RAG Memory систему для GopiAI. Как она работает?")
        
        client.add_message(session_id, "assistant", 
                          "Привет! RAG Memory система позволяет сохранять и искать информацию из предыдущих разговоров. "
                          "Она использует векторную базу данных ChromaDB для семантического поиска и может помочь избежать "
                          "повторных объяснений одних и тех же концепций.")
        
        client.add_message(session_id, "user", 
                          "Отлично! Расскажи про архитектуру GopiAI и модульную структуру проекта.")
        
        client.add_message(session_id, "assistant", 
                          "GopiAI имеет модульную архитектуру с несколькими основными компонентами:\n"
                          "- GopiAI-Core: базовые интерфейсы и агенты\n"
                          "- GopiAI-Extensions: расширения для интеграций\n"
                          "- GopiAI-Widgets: UI компоненты\n"
                          "- GopiAI-Assets: ресурсы и медиа\n"
                          "- GopiAI-App: главное приложение")
        
        print("✅ Сообщения добавлены")
        print()
        
        # Создаем второй разговор для демонстрации поиска
        session_id2 = client.create_conversation(
            title="Обсуждение UI/UX улучшений",
            project_context="GopiAI-Widgets",
            tags=["ui", "ux", "дизайн"]
        )
        
        client.add_message(session_id2, "user", 
                          "Нужно улучшить пользовательский интерфейс виджетов GopiAI")
        
        client.add_message(session_id2, "assistant", 
                          "Для улучшения UI виджетов GopiAI рекомендую:\n"
                          "1. Добавить темную тему\n"
                          "2. Улучшить адаптивность для мобильных устройств\n"
                          "3. Добавить анимации переходов\n"
                          "4. Создать единый дизайн-систему")
        
        print("📱 Создан второй разговор про UI/UX")
        print()
        
        # Тестируем поиск
        print("🔍 Тестирование поиска:")
        print("-" * 30)
        
        # Поиск по архитектуре
        results = client.search_memory("модульная архитектура GopiAI")
        print(f"Запрос: 'модульная архитектура GopiAI' -> найдено {len(results)} результатов")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (релевантность: {result['relevance_score']:.2f})")
            print(f"     {result['context_preview'][:100]}...")
        print()
        
        # Поиск по UI
        results = client.search_memory("улучшения интерфейса виджетов")
        print(f"Запрос: 'улучшения интерфейса виджетов' -> найдено {len(results)} результатов")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (релевантность: {result['relevance_score']:.2f})")
            print(f"     {result['context_preview'][:100]}...")
        print()
        
        # Статистика
        stats = client.get_stats()
        print("📊 Статистика системы:")
        print(f"  - Всего разговоров: {stats['total_sessions']}")
        print(f"  - Всего сообщений: {stats['total_messages']}")
        print(f"  - Документов в БД: {stats['total_documents']}")
        print(f"  - Размер хранилища: {stats['storage_size_mb']:.2f} МБ")
        print(f"  - Популярные теги: {', '.join(stats['most_active_tags'][:5])}")
        print()
        
        print("🎉 Демонстрация завершена успешно!")
        print(f"🌐 Откройте браузер по адресу: http://127.0.0.1:8080 для веб-интерфейса")
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу")
        print("Запустите сервер командой: python -m rag_memory_system.api")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    demo_conversation()
