"""
Тестирование встроенной системы памяти GopiAI (embedded txtai)

Этот скрипт проверяет работу встроенной системы памяти на основе txtai.
"""

import sys
import os
from pathlib import Path
import json

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.extend([
    str(project_root),
    str(project_root / "gopiai"),
    str(project_root / "gopiai" / "ui"),
])

class SimpleMemoryManager:
    """Упрощенный менеджер памяти для тестирования"""
    
    def __init__(self, data_dir: str = "conversations"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.chats_file = self.data_dir / "chats.json"
        self.chats = []
        self.sessions = {}
        
        # Инициализация txtai
        try:
            from txtai.embeddings import Embeddings
            self.embeddings = Embeddings({"path": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"})
            print("✅ txtai embeddings инициализированы")
        except ImportError:
            self.embeddings = None
            print("❌ txtai не установлен. Установите: pip install txtai sentence-transformers")
        
        # Инициализация упрощенного эмоционального классификатора
        try:
            from simple_emotion_classifier import get_emotion_classifier
            self.emotion_classifier = get_emotion_classifier()
            print("✅ Упрощенный эмоциональный классификатор инициализирован")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить упрощенный эмоциональный классификатор: {e}")
            self.emotion_classifier = None
        
        self._load_data()
        
    def _load_data(self):
        """Загрузка данных из файла"""
        if self.chats_file.exists():
            try:
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chats = data.get('chats', [])
                    self.sessions = data.get('sessions', {})
                print(f"📂 Загружено {len(self.chats)} сообщений из {len(self.sessions)} сессий")
            except Exception as e:
                print(f"❌ Ошибка загрузки данных: {e}")
    
    def create_session(self, title: str = "Новый чат") -> str:
        """Создание новой сессии чата"""
        import uuid
        from datetime import datetime
        
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'message_count': 0
        }
        print(f"✅ Создана сессия: {title} (ID: {session_id})")
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str) -> str:
        """Добавление сообщения в сессию с эмоциональным анализом"""
        import uuid
        from datetime import datetime
        
        if session_id not in self.sessions:
            self.create_session(f"Автосессия {len(self.sessions) + 1}")
        
        # Анализ эмоциональной окраски сообщения
        emotion_data = {}
        if self.emotion_classifier and role == 'user':
            try:
                emotion_data = self.emotion_classifier.analyze_emotion(content)
                print(f"🎭 Эмоциональный анализ: {emotion_data.get('emotion', 'не определено')} (уверенность: {emotion_data.get('confidence', 0):.2f})")
            except Exception as e:
                print(f"⚠️ Ошибка эмоционального анализа: {e}")
        
        message = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion_data.get('emotion', 'neutral'),
            'emotion_confidence': emotion_data.get('confidence', 0.0),
            'sentiment': emotion_data.get('sentiment', 'neutral')
        }
        
        self.chats.append(message)
        self.sessions[session_id]['message_count'] += 1
        
        # Обновляем индексы txtai
        if self.embeddings:
            self._update_embeddings()
        
        print(f"📝 Добавлено сообщение в сессию {session_id}")
        return message['id']
    
    def _update_embeddings(self):
        """Обновление эмбеддингов для поиска"""
        if not self.embeddings or not self.chats:
            return
        
        try:
            # Создаем индексы для всех сообщений
            texts = [msg['content'] for msg in self.chats]
            
            # Удаляем старые индексы, если они есть
            if hasattr(self.embeddings, 'unindex'):
                self.embeddings.unindex(range(len(texts)))
                
            # Создаем новые индексы
            self.embeddings.index([(i, text, None) for i, text in enumerate(texts)])
        except Exception as e:
            print(f"⚠️ Ошибка обновления эмбеддингов: {e}")
    
    def search_memory(self, query: str, limit: int = 5) -> list:
        """Семантический поиск по сообщениям"""
        if not self.embeddings or not self.chats:
            print("⚠️ Поиск недоступен: txtai не инициализирован")
            return []
        
        try:
            # Выполняем поиск и преобразуем результаты в нужный формат
            search_results = []
            results = self.embeddings.search(query, limit)
            
            # Обрабатываем результаты поиска
            for result in results:
                # Получаем индекс и оценку
                if isinstance(result, (list, tuple)) and len(result) >= 2:
                    score, idx = result[0], int(result[1])  # Преобразуем индекс в int
                if idx < len(self.chats):
                    msg = self.chats[idx]
                    search_results.append({
                        'content': msg['content'],
                        'score': float(score),
                        'session_id': msg['session_id'],
                        'role': msg['role'],
                        'timestamp': msg['timestamp']
                    })
            
            print(f"🔍 Найдено {len(search_results)} результатов для запроса")
            return search_results
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []
    
    def get_emotional_stats(self) -> dict:
        """Получение статистики по эмоциональной окраске сообщений"""
        if not self.chats:
            return {}
            
        emotions = {}
        sentiments = {}
        
        for msg in self.chats:
            if 'emotion' in msg:
                emotion = msg['emotion']
                emotions[emotion] = emotions.get(emotion, 0) + 1
                
            if 'sentiment' in msg:
                sentiment = msg['sentiment']
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                
        return {
            'emotion_distribution': emotions,
            'sentiment_distribution': sentiments,
            'emotion_analyzer_available': self.emotion_classifier is not None
        }
        
    def get_stats(self) -> dict:
        """Получение общей статистики"""
        return {
            'total_messages': len(self.chats),
            'total_sessions': len(self.sessions),
            'txtai_available': self.embeddings is not None,
            'emotion_analyzer_available': self.emotion_classifier is not None,
            'data_dir': str(self.data_dir.absolute())
        }

def test_memory_system():
    """Основная функция тестирования"""
    print("\n🧪 Тестирование системы памяти GopiAI (embedded txtai)")
    print("=" * 60 + "\n")
    
    try:
        # 1. Инициализация
        print("1. Инициализация менеджера памяти...")
        manager = SimpleMemoryManager()
        
        if not manager.embeddings:
            print("❌ Не удалось инициализировать txtai. Тестирование прервано.")
            return False
        
        # 2. Создаем тестовую сессию
        print("\n2. Создание тестовой сессии...")
        session_id = manager.create_session("Тестовая сессия")
        
        # 3. Добавляем тестовые сообщения
        print("\n3. Добавление тестовых сообщений...")
        test_messages = [
            ("user", "Привет! Это тестовое сообщение."),
            ("assistant", "Здравствуйте! Я ваш ассистент."),
            ("user", "Как настроена система памяти в GopiAI?"),
            ("assistant", "GopiAI использует txtai для семантического поиска и хранения контекста."),
            ("user", "Какие технологии используются для обработки естественного языка?"),
            ("assistant", "Для обработки естественного языка используются трансформеры и эмбеддинги.")
        ]
        
        for role, content in test_messages:
            manager.add_message(session_id, role, content)
        
        # 4. Тестируем поиск
        print("\n4. Тестирование семантического поиска...")
        test_queries = [
            "Как работает память?",
            "Что такое txtai?",
            "Какие технологии используются?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Поиск: '{query}'")
            results = manager.search_memory(query, limit=2)
            
            if not results:
                print("   ❌ Результаты не найдены")
                continue
                
            for i, result in enumerate(results, 1):
                print(f"   {i}. Скоринг: {result.get('score', 0):.3f}")
                print(f"      {result.get('content', '')[:100]}...")
        
        # 5. Выводим статистику
        print("\n5. Общая статистика:")
        stats = manager.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # 6. Выводим эмоциональную статистику
        print("\n6. Эмоциональная статистика:")
        emotion_stats = manager.get_emotional_stats()
        
        if emotion_stats.get('emotion_analyzer_available'):
            print("   Распределение эмоций:")
            for emotion, count in emotion_stats.get('emotion_distribution', {}).items():
                print(f"      {emotion}: {count} сообщений")
                
            print("\n   Распределение настроений:")
            for sentiment, count in emotion_stats.get('sentiment_distribution', {}).items():
                print(f"      {sentiment}: {count} сообщений")
        else:
            print("   Эмоциональный анализатор недоступен")
        
        print("\n✅ Все тесты успешно завершены!")
        return True
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_memory_system()
