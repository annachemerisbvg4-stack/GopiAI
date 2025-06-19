"""
🧠 Простой менеджер памяти для GopiAI на основе txtai
Адаптировано из similarity.py - никакого оверинжиниринга!
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Проверяем доступность txtai
try:
    from txtai.embeddings import Embeddings
    TXTAI_AVAILABLE = True
except ImportError:
    TXTAI_AVAILABLE = False
    print("⚠️ txtai не установлен. Установите: pip install txtai sentence-transformers")

class SimpleMemoryManager:
    """
    Простейший менеджер памяти на txtai
    По мотивам similarity.py - работает из коробки!
    """
    
    def __init__(self, data_dir: str = "conversations"):
        """Инициализация"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Файл для хранения чатов
        self.chats_file = self.data_dir / "chats.json"
        
        # Данные в памяти
        self.chats = []  # Список всех сообщений
        self.sessions = {}  # Словарь сессий
        
        # txtai embeddings (как в similarity.py)
        if TXTAI_AVAILABLE:
            # Используем ту же модель что в примере
            self.embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2"})
            print("✅ txtai инициализирован")
        else:
            self.embeddings = None
            print("⚠️ txtai недоступен - работаем без поиска")
        
        # Загружаем сохраненные данные
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из JSON"""
        if self.chats_file.exists():
            try:
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chats = data.get('chats', [])
                    self.sessions = data.get('sessions', {})
                print(f"📂 Загружено {len(self.chats)} сообщений")
            except Exception as e:
                print(f"❌ Ошибка загрузки: {e}")
    
    def _save_data(self):
        """Сохранение данных в JSON"""
        try:
            data = {
                'chats': self.chats,
                'sessions': self.sessions
            }
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
    
    def create_session(self, title: str = "Новый чат") -> str:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'message_count': 0
        }
        self._save_data()
        print(f"✅ Создана сессия: {title}")
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str) -> str:
        """Добавление сообщения"""
        if session_id not in self.sessions:
            # Автосоздаем сессию
            self.sessions[session_id] = {
                'id': session_id,
                'title': 'Auto Session',
                'created_at': datetime.now().isoformat(),
                'message_count': 0
            }
        
        message_id = str(uuid.uuid4())
        message = {
            'id': message_id,
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.chats.append(message)
        self.sessions[session_id]['message_count'] += 1
        self._save_data()
        
        print(f"📝 Добавлено сообщение в сессию {session_id}")
        return message_id
    
    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Семантический поиск по памяти
        Точно как в similarity.py!
        """
        if not self.embeddings or not self.chats:
            print("⚠️ Поиск недоступен")
            return []
        
        try:
            # Готовим данные для поиска (как в similarity.py)
            data = [chat['content'] for chat in self.chats]
            
            if not data:
                return []
            
            # Выполняем поиск (метод из similarity.py)
            similarities = self.embeddings.similarity(query, data)
            
            # Формируем результаты
            results = []
            for idx, score in similarities[:limit]:
                chat = self.chats[idx]
                results.append({
                    'content': chat['content'],
                    'score': score,
                    'session_id': chat['session_id'],
                    'role': chat['role'],
                    'timestamp': chat['timestamp']
                })
            
            print(f"🔍 Найдено {len(results)} результатов для '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []
    
    def get_session_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Получение сообщений сессии"""
        messages = [chat for chat in self.chats if chat['session_id'] == session_id]
        return messages[-limit:] if limit else messages
    
    def get_all_sessions(self) -> List[Dict]:
        """Получение всех сессий"""
        return list(self.sessions.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            'total_messages': len(self.chats),
            'total_sessions': len(self.sessions),
            'txtai_available': self.embeddings is not None,
            'data_dir': str(self.data_dir)
        }
    
    # Методы совместимости с существующим API GopiAI
    
    def enrich_message(self, message: str) -> str:
        """Обогащение сообщения контекстом"""
        try:
            results = self.search_memory(message, limit=2)
            if results:
                context = "\n".join([f"• {r['content'][:100]}..." for r in results])
                return f"{message}\n\n📋 Контекст:\n{context}"
            return message
        except:
            return message
    
    def save_chat_exchange(self, session_id: str, user_msg: str, ai_response: str) -> bool:
        """Сохранение обмена сообщениями"""
        try:
            self.add_message(session_id, "user", user_msg)
            self.add_message(session_id, "assistant", ai_response)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения обмена: {e}")
            return False


# Глобальный экземпляр
_memory_manager = None

def get_memory_manager() -> SimpleMemoryManager:
    """Получить менеджер памяти (синглтон)"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = SimpleMemoryManager()
    return _memory_manager


# Для совместимости
class TxtAIMemoryManager(SimpleMemoryManager):
    """Алиас для совместимости с существующим кодом"""
    pass


if __name__ == "__main__":
    # Быстрый тест
    print("🧪 Тестируем Simple Memory Manager...")
    
    manager = SimpleMemoryManager()
    
    # Создаем сессию
    session_id = manager.create_session("Тест txtai")
    
    # Добавляем сообщения
    manager.add_message(session_id, "user", "Привет! Как дела с txtai интеграцией?")
    manager.add_message(session_id, "assistant", "Отлично! txtai работает прекрасно для семантического поиска в GopiAI")
    manager.add_message(session_id, "user", "Расскажи про архитектуру системы памяти")
    
    # Тестируем поиск
    results = manager.search_memory("txtai поиск")
    print(f"✅ Найдено результатов: {len(results)}")
    
    # Статистика
    stats = manager.get_stats()
    print(f"📊 Статистика: {stats}")
    
    print("🎉 Всё работает!")