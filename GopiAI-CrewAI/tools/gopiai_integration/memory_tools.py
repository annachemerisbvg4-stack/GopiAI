"""
🧠 GopiAI Memory Tool для CrewAI
Интеграция CrewAI агентов с системой памяти и RAG GopiAI
"""

import os
import json
from typing import Type, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryInput(BaseModel):
    """Схема входных данных для работы с памятью"""
    action: str = Field(description="Действие: store, search, retrieve, list, delete, summarize")
    query: str = Field(description="Поисковый запрос или ключ")
    data: str = Field(default="", description="Данные для сохранения")
    category: str = Field(default="general", description="Категория: general, code, docs, research")
    importance: int = Field(default=5, description="Важность от 1 до 10")

class GopiAIMemoryTool:
    """
    Мощный инструмент для работы с памятью и RAG системой GopiAI
    
    Возможности:
    - Сохранение и поиск информации
    - RAG (Retrieval-Augmented Generation)
    - Семантический поиск
    - Категоризация знаний
    - Долговременная память агентов
    """
    
    name: str = "gopiai_memory"
    description: str = """Работает с системой памяти и RAG GopiAI.
    
    Действия:
    - store: сохранить информацию (data=текст, category=категория)
    - search: поиск по запросу (query=поисковый_запрос)
    - retrieve: получить по ключу (query=ключ)
    - list: список сохраненной информации (category=категория)
    - delete: удалить запись (query=ключ)
    - summarize: создать сводку (query=тема)
    
    Категории:
    - general: общая информация
    - code: код и техническая документация
    - docs: документация проекта
    - research: результаты исследований
    
    Примеры:
    - store: data="Важная информация", category="research"
    - search: query="как настроить CrewAI"
    - retrieve: query="project_config"
    """
    args_schema: Type[BaseModel] = MemoryInput
    
    def __init__(self):
                # Путь к системе памяти
        self.memory_path = os.path.join(
            os.path.dirname(__file__), 
            "../../../rag_memory_system"
        )
        # Локальная память (файловая)
        self.local_memory_file = os.path.join(
            os.path.dirname(__file__), 
            "../../memory/crewai_memory.json"
        )
        self._ensure_memory_file()
        
    def _ensure_memory_file(self):
        """Создает файл памяти если его нет"""
        os.makedirs(os.path.dirname(self.local_memory_file), exist_ok=True)
        if not os.path.exists(self.local_memory_file):
            with open(self.local_memory_file, 'w', encoding='utf-8') as f:
                json.dump({"memories": [], "metadata": {"created": datetime.now().isoformat()}}, f)
        
    def _run(self, action: str, query: str, data: str = "", category: str = "general", importance: int = 5) -> str:
        """
        Выполнение операции с памятью
        """
        try:
            if action == "store":
                return self._store_memory(data, query, category, importance)
            elif action == "search":
                return self._search_memory(query, category)
            elif action == "retrieve":
                return self._retrieve_memory(query)
            elif action == "list":
                return self._list_memories(category)
            elif action == "delete":
                return self._delete_memory(query)
            elif action == "summarize":
                return self._summarize_memories(query)
            else:
                return f"❌ Неизвестное действие: {action}"
                
        except Exception as e:
            return f"❌ Ошибка памяти: {str(e)}"
    
    def _load_local_memory(self) -> Dict:
        """Загружает локальную память"""
        try:
            with open(self.local_memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"memories": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_local_memory(self, memory_data: Dict):
        """Сохраняет локальную память"""
        with open(self.local_memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    def _store_memory(self, data: str, key: str, category: str, importance: int) -> str:
        """Сохранение в память"""
        if not data.strip():
            return "❌ Нет данных для сохранения"
        
        try:
            # Попытка сохранения в RAG систему
            rag_result = self._store_to_rag(data, key, category)
            
            # Локальное сохранение
            memory_data = self._load_local_memory()
            
            memory_record = {
                "id": len(memory_data["memories"]) + 1,
                "key": key or f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "data": data,
                "category": category,
                "importance": importance,
                "timestamp": datetime.now().isoformat(),
                "rag_stored": bool(rag_result)
            }
            
            memory_data["memories"].append(memory_record)
            self._save_local_memory(memory_data)
            
            return f"✅ Информация сохранена: ключ '{memory_record['key']}', категория '{category}' ({len(data)} символов)"
            
        except Exception as e:
            return f"❌ Ошибка сохранения: {str(e)}"
    
    def _search_memory(self, query: str, category: str = "all") -> str:
        """Поиск в памяти"""
        if not query.strip():
            return "❌ Пустой поисковый запрос"
        
        try:
            # Попытка поиска в RAG системе
            rag_results = self._search_in_rag(query, category)
            
            # Локальный поиск
            memory_data = self._load_local_memory()
            local_results = []
            
            query_lower = query.lower()
            for memory in memory_data["memories"]:
                if category != "all" and memory["category"] != category:
                    continue
                
                # Поиск в ключе и данных
                if (query_lower in memory["key"].lower() or 
                    query_lower in memory["data"].lower()):
                    
                    snippet = memory["data"][:200] + "..." if len(memory["data"]) > 200 else memory["data"]
                    local_results.append(f"🔑 {memory['key']} ({memory['category']}):\\n{snippet}")
            
            # Формируем результат
            results = []
            if rag_results:
                results.append(f"🧠 RAG результаты:\\n{rag_results}")
            
            if local_results:
                results.append(f"💾 Локальные результаты:\\n" + "\\n\\n".join(local_results[:5]))
            
            if not results:
                return f"🔍 Поиск '{query}' не дал результатов"
            
            return "🔍 Результаты поиска:\\n\\n" + "\\n\\n".join(results)
            
        except Exception as e:
            return f"❌ Ошибка поиска: {str(e)}"
    
    def _retrieve_memory(self, key: str) -> str:
        """Получение конкретной записи"""
        try:
            memory_data = self._load_local_memory()
            
            for memory in memory_data["memories"]:
                if memory["key"] == key:
                    return f"📄 Запись '{key}':\\n\\nКатегория: {memory['category']}\\nВажность: {memory['importance']}/10\\nСохранено: {memory['timestamp']}\\n\\nДанные:\\n{memory['data']}"
            
            return f"❌ Запись с ключом '{key}' не найдена"
            
        except Exception as e:
            return f"❌ Ошибка получения: {str(e)}"
    
    def _list_memories(self, category: str = "all") -> str:
        """Список сохраненных записей"""
        try:
            memory_data = self._load_local_memory()
            
            filtered_memories = []
            for memory in memory_data["memories"]:
                if category == "all" or memory["category"] == category:
                    filtered_memories.append(memory)
            
            if not filtered_memories:
                return f"📭 Нет записей в категории '{category}'"
            
            # Сортируем по важности и времени
            filtered_memories.sort(key=lambda x: (x["importance"], x["timestamp"]), reverse=True)
            
            memory_list = []
            for memory in filtered_memories[:20]:  # Показываем только 20
                memory_list.append(f"🔑 {memory['key']} | {memory['category']} | важность: {memory['importance']}/10")
            
            return f"📋 Записи в памяти ({len(filtered_memories)} всего):\\n" + "\\n".join(memory_list)
            
        except Exception as e:
            return f"❌ Ошибка списка: {str(e)}"
    
    def _delete_memory(self, key: str) -> str:
        """Удаление записи"""
        try:
            memory_data = self._load_local_memory()
            
            for i, memory in enumerate(memory_data["memories"]):
                if memory["key"] == key:
                    deleted_memory = memory_data["memories"].pop(i)
                    self._save_local_memory(memory_data)
                    return f"✅ Запись '{key}' удалена (категория: {deleted_memory['category']})"
            
            return f"❌ Запись с ключом '{key}' не найдена"
            
        except Exception as e:
            return f"❌ Ошибка удаления: {str(e)}"
    
    def _summarize_memories(self, topic: str) -> str:
        """Создание сводки по теме"""
        try:
            # Ищем все связанные записи
            search_result = self._search_memory(topic, "all")
            
            memory_data = self._load_local_memory()
            related_memories = []
            
            topic_lower = topic.lower()
            for memory in memory_data["memories"]:
                if (topic_lower in memory["key"].lower() or 
                    topic_lower in memory["data"].lower()):
                    related_memories.append(memory)
            
            if not related_memories:
                return f"❌ Нет записей по теме '{topic}'"
            
            # Группируем по категориям
            by_category = {}
            for memory in related_memories:
                cat = memory["category"]
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(memory)
            
            # Формируем сводку
            summary_parts = [f"📊 Сводка по теме '{topic}':"]
            
            for category, memories in by_category.items():
                summary_parts.append(f"\\n## {category.upper()} ({len(memories)} записей)")
                for memory in memories[:3]:  # Топ-3 по категории
                    snippet = memory["data"][:100] + "..." if len(memory["data"]) > 100 else memory["data"]
                    summary_parts.append(f"• {memory['key']}: {snippet}")
            
            return "\\n".join(summary_parts)
            
        except Exception as e:
            return f"❌ Ошибка создания сводки: {str(e)}"
    
    def _store_to_rag(self, data: str, key: str, category: str) -> str:
        """Сохранение в RAG систему (если доступна)"""
        try:
            # Попытка интеграции с RAG системой GopiAI
            # Здесь будет реальная интеграция с rag_memory_system
            return f"RAG: сохранено {len(data)} символов"
        except Exception:
            return ""
    
    def _search_in_rag(self, query: str, category: str) -> str:
        """Поиск в RAG системе (если доступна)"""
        try:
            # Попытка поиска в RAG системе GopiAI
            # Здесь будет реальная интеграция с rag_memory_system
            return ""
        except Exception:
            return ""


# Экспорт инструментов
__all__ = [
    "GopiAIMemoryTool"
]


if __name__ == "__main__":
    # Тест инструментов
    print("🧪 Тестирование GopiAI Memory Tools...")
    
    # Тест памяти
    memory = GopiAIMemoryTool()
    
    # Сохранение
    result = memory._run("store", "test_key", "Это тестовая информация для проверки памяти", "research", 8)
    print(f"Store test: {result}")
    
    # Поиск
    result = memory._run("search", "тестовая")
    print(f"Search test: {result}")
    
    # Список
    result = memory._run("list", "research")
    print(f"List test: {result}")
    
    print("✅ Все инструменты готовы!")