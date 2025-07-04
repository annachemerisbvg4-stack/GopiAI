"""
🧠 Простой менеджер памяти для GopiAI на основе txtai
Адаптировано из similarity.py - никакого оверинжиниринга!
"""

import json
import os
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

# Проверяем доступность FAISS
try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
    print("FAISS доступен")
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS не установлен. Работаем в txtai-only режиме")

class SimpleMemoryManager:
    """Простой менеджер памяти на основе txtai"""
    
    def __init__(self, data_dir: str = "conversations"):
        """Инициализация"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Файл для хранения чатов
        self.chats_file = self.data_dir / "chats.json"
        
        # Данные в памяти
        self.chats = []  # Список всех сообщений
        self.sessions = {}  # Словарь сессий
        
        # Проверяем флаг отключения векторизации
        disable_embeddings = os.getenv('GOPI_DISABLE_EMBEDDINGS', 'false').lower() == 'true'
        
        # txtai embeddings (инициализируем только если не отключено)
        if TXTAI_AVAILABLE and not disable_embeddings:
            try:
                print("🔄 Инициализация txtai embeddings...")
                # Используем ту же модель что в примере
                self.embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2"})
                print("✅ txtai инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации txtai: {e}")
                print("⚠️ Работаем без векторного поиска")
                self.embeddings = None
        else:
            self.embeddings = None
            if disable_embeddings:
                print("⚠️ Векторизация отключена через GOPI_DISABLE_EMBEDDINGS")
            else:
                print("⚠️ txtai недоступен - работаем без поиска")
        
        # Инициализация FAISS-индекса и структур хранения
        self.dim = 768  # размерность векторов для nli-mpnet-base-v2
        
        if FAISS_AVAILABLE and self.embeddings:
            # Создаем FAISS индекс для косинусной близости (Inner Product)
            self.index = faiss.IndexFlatIP(self.dim)
            self.vector_ids = []  # список для соответствия позиция ↔ id сообщения
            print("✅ FAISS индекс инициализирован")
        else:
            self.index = None
            self.vector_ids = []
            if not FAISS_AVAILABLE:
                print("⚠️ FAISS недоступен - работаем только с txtai")
        
        # Пути к файлам для хранения векторов
        self.vectors_file = self.data_dir / "vectors.npy"
        self.idmap_file = self.data_dir / "vector_ids.json"
        self.migration_done_file = self.data_dir / "migration_complete.flag"  # Флаг завершения миграции
        
        # Загружаем сохраненные данные
        self._load_data()
        
        # Загружаем векторы FAISS (если файл отсутствует, будет ленивое перестроение)
        if self.embeddings:
            self._load_embeddings()
            
            # Миграция существующих сообщений в FAISS индекс (только если нужно и не было выполнено)
            self._rebuild_embeddings_if_needed()
        
        # Добавляем атрибут для совместимости
        self.session_id = "default_session"  # Текущая сессия

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

    def _compute_embedding(self, text: str) -> np.ndarray:
        """
        Получить единично-нормированный вектор через self.embeddings.transform([text])[0]
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Единично-нормированный numpy массив размерности self.dim
        """
        if not self.embeddings:
            raise RuntimeError("Embeddings не инициализированы")
        
        try:
            # Получаем вектор через transform (как указано в задаче)
            vector = self.embeddings.transform([text])[0]
            
            # Конвертируем в numpy array если это не так
            if not isinstance(vector, np.ndarray):
                vector = np.array(vector)
            
            # Нормализуем вектор до единичной длины
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            else:
                # В случае нулевого вектора возвращаем нули
                vector = np.zeros_like(vector)
            
            return vector.astype(np.float32)
        
        except Exception as e:
            print(f"❌ Ошибка вычисления эмбеддинга: {e}")
            # Возвращаем нулевой вектор в случае ошибки
            return np.zeros(self.dim, dtype=np.float32)
    
    def _save_embeddings(self):
        """
        Сохранять faiss индекс (через faiss.write_index) ИЛИ np.save матрицу + json id-mapping
        
        Используем второй вариант (np.save + json) так как он более универсален
        и не требует дополнительных зависимостей для сохранения faiss индексов
        """
        if not FAISS_AVAILABLE or self.index is None:
            print("⚠️ FAISS недоступен - сохранение векторов пропущено")
            return
        
        try:
            # Получаем все векторы из FAISS индекса
            if self.index.ntotal > 0:
                # Извлекаем векторы из индекса
                vectors = self.index.reconstruct_n(0, self.index.ntotal)
                
                # Сохраняем векторы в numpy файл
                np.save(self.vectors_file, vectors)
                print(f"✅ Сохранено {len(vectors)} векторов в {self.vectors_file}")
                
                # Сохраняем маппинг ID в JSON
                with open(self.idmap_file, 'w', encoding='utf-8') as f:
                    json.dump(self.vector_ids, f, ensure_ascii=False, indent=2)
                print(f"✅ Сохранен маппинг ID в {self.idmap_file}")
            else:
                print("📁 Нет векторов для сохранения")
                
        except Exception as e:
            print(f"❌ Ошибка сохранения векторов: {e}")

    def _load_embeddings(self):
        """
        При наличии файлов восстанавливать индекс и self.vector_ids.
        Если файлов нет — оставить пустыми, чтобы их можно было построить позже.
        """
        if not FAISS_AVAILABLE or self.index is None:
            print("⚠️ FAISS недоступен - инициализация пустого индекса")
            return
        
        try:
            # Проверяем наличие сохраненных файлов
            if self.vectors_file.exists() and self.idmap_file.exists():
                # Загружаем векторы
                vectors = np.load(self.vectors_file)
                
                # Загружаем маппинг ID
                with open(self.idmap_file, 'r', encoding='utf-8') as f:
                    self.vector_ids = json.load(f)
                
                # Добавляем векторы в FAISS индекс
                if len(vectors) > 0:
                    # Нормализуем векторы для косинусной близости
                    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
                    vectors_normalized = vectors / (norms + 1e-8)  # избегаем деления на ноль
                    
                    self.index.add(vectors_normalized.astype(np.float32))
                    print(f"✅ Загружено {len(vectors)} векторов в FAISS индекс")
                else:
                    print("📁 Файл векторов пуст - оставляем индекс пустым")
            else:
                print("📁 Файлы векторов не найдены - оставляем индекс пустым для построения позже")
                # Инициализируем пустые структуры
                self.vector_ids = []
        
        except Exception as e:
            print(f"❌ Ошибка загрузки векторов: {e}")
            # В случае ошибки инициализируем пустые структуры
            self.index = faiss.IndexFlatIP(self.dim)
            self.vector_ids = []

    def _rebuild_embeddings_if_needed(self):
        """
        Миграция существующих сообщений: если FAISS доступен и индекс пуст,
        пройти по всем self.chats, вычислить embedding, добавить в индекс, пополнить self.vector_ids.
        
        Вызывается автоматически при инициализации после загрузки чатов.
        Теперь с проверкой флага завершения миграции.
        """
        if not FAISS_AVAILABLE or self.index is None:
            print("⚠️ FAISS недоступен - миграция эмбеддингов пропущена")
            return
            
        # Проверяем флаг завершения миграции
        if self.migration_done_file.exists():
            print("✅ Миграция уже завершена ранее (найден флаг)")
            return
            
        if self.index.ntotal > 0:
            print(f"📊 FAISS индекс уже содержит {self.index.ntotal} векторов - создаем флаг миграции")
            # Создаем флаг, чтобы не повторять миграцию
            self.migration_done_file.touch()
            return
            
        if not self.chats:
            print("📝 Нет сообщений для миграции - создаем флаг")
            # Создаем флаг, чтобы не пытаться мигрировать пустые данные
            self.migration_done_file.touch()
            return
            
        if not self.embeddings:
            print("⚠️ Embeddings модель недоступна - миграция пропущена")
            return
            
        print(f"🔄 Начинаем ЕДИНОКРАТНУЮ миграцию {len(self.chats)} существующих сообщений в FAISS индекс...")
        
        try:
            migrated_count = 0
            failed_count = 0
            
            for chat in self.chats:
                try:
                    # Извлекаем текст сообщения
                    content = chat.get('content', '')
                    if not content.strip():
                        continue
                        
                    # Вычисляем эмбеддинг
                    embedding = self._compute_embedding(content)
                    
                    # Добавляем в FAISS индекс
                    # embedding должен быть 2D массивом для faiss
                    embedding_2d = embedding.reshape(1, -1)
                    self.index.add(embedding_2d)
                    
                    # Добавляем соответствие позиция -> id сообщения
                    chat_id = chat.get('id', str(len(self.vector_ids)))
                    self.vector_ids.append(chat_id)
                    
                    migrated_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    # Убираем подробное логирование ошибок - слишком много спама
                    if failed_count <= 5:  # Показываем только первые 5 ошибок
                        print(f"⚠️ Ошибка при миграции сообщения {chat.get('id', 'unknown')}: {e}")
                    elif failed_count == 6:
                        print("⚠️ ... (скрываем дальнейшие ошибки миграции)")
                    continue
                    
            print(f"✅ Миграция завершена: {migrated_count} успешно, {failed_count} ошибок")
            
            # Сохраняем результат
            if migrated_count > 0:
                self._save_embeddings()
                print(f"💾 Эмбеддинги сохранены в файлы")
            
            # Создаем флаг завершения миграции независимо от результата
            self.migration_done_file.touch()
            print(f"🏁 Флаг завершения миграции создан: {self.migration_done_file}")
            
        except Exception as e:
            print(f"❌ Критическая ошибка при миграции эмбеддингов: {e}")
            # В случае ошибки очищаем поврежденные данные
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatIP(self.dim)
                self.vector_ids = []
            # Все равно создаем флаг, чтобы не повторять попытки
            self.migration_done_file.touch()
    
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
        Семантический поиск по памяти с векторным поиском через FAISS
        
        Новая логика:
        1. Если FAISS_AVAILABLE и self.index.ntotal > 0 — векторный поиск
        2. Fallback: старая txtai или «нет поиска»
        3. Возвращаем результаты в прежнем формате
        """
        if not self.chats:
            print("⚠️ Поиск недоступен - нет сообщений")
            return []
        
        # 1. Если FAISS доступен и в индексе есть векторы - используем векторный поиск
        if FAISS_AVAILABLE and self.index.ntotal > 0:
            try:
                # Вычисляем embedding запроса
                query_vector = self._compute_embedding(query)
                
                # Преобразуем в нужный формат для FAISS (добавляем размерность batch)
                query_vector = query_vector.reshape(1, -1)
                
                # Выполняем поиск: D - расстояния, I - индексы
                D, I = self.index.search(query_vector, limit)
                
                # Формируем список результатов
                results = []
                for k in range(len(I[0])):
                    idx = I[0][k]
                    if idx != -1 and idx < len(self.vector_ids):  # Проверяем валидность индекса
                        real_id = self.vector_ids[idx]  # Получаем real-id сообщения
                        score = float(D[0][k])  # Получаем score
                        
                        # Ищем сообщение по real_id в self.chats
                        chat = None
                        for chat_item in self.chats:
                            if chat_item.get('id') == real_id:
                                chat = chat_item
                                break
                        
                        if chat:
                            results.append({
                                'content': chat['content'],
                                'score': score,
                                'session_id': chat['session_id'],
                                'role': chat['role'],
                                'timestamp': chat['timestamp']
                            })
                
                print(f"🔍 FAISS поиск: найдено {len(results)} результатов для '{query}'")
                return results
                
            except Exception as e:
                print(f"❌ Ошибка FAISS поиска: {e}")
                # Падаем на fallback
        
        # 2. Fallback: старая txtai или «нет поиска»
        if self.embeddings:
            try:
                # Готовим данные для поиска (как в старой версии)
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
                
                print(f"🔍 txtai поиск: найдено {len(results)} результатов для '{query}'")
                return results
                
            except Exception as e:
                print(f"❌ Ошибка txtai поиска: {e}")
                return []
        else:
            print("⚠️ Поиск недоступен - ни FAISS, ни txtai не инициализированы")
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
            'vector_messages': self.index.ntotal if self.index is not None else 0,
            'faiss_available': FAISS_AVAILABLE,
            'data_dir': str(self.data_dir)
        }
    
    # Методы совместимости с существующим API GopiAI
    
    def enrich_message(self, message: str) -> str:
        """
        Обогащает сообщение пользователя контекстом из памяти.
        
        Добавляет:
        1. Недавние сообщения из текущей сессии (контекст разговора)
        2. Релевантные воспоминания из памяти по запросу
        
        Args:
            message: Исходное сообщение пользователя
            
        Returns:
            Обогащенное сообщение с контекстом
        """
        try:
            # Получаем недавние сообщения текущей сессии (до 5)
            recent_messages = self._format_recent_messages(self.session_id, 5)
            
            # Поиск релевантных воспоминаний по запросу (до 3 результатов)
            memory_results = self.search_memory(message, limit=3)
            memory_context = self._format_memory_results(memory_results)
            
            # Собираем все вместе
            parts = []
            
            # Добавляем оригинальное сообщение
            parts.append(message)
            
            # Добавляем контекстную информацию только если она есть
            context_parts = []
            
            if recent_messages:
                context_parts.append(f"Контекст разговора:\n{recent_messages}")
            
            if memory_context:
                context_parts.append(f"Релевантная информация из памяти:\n{memory_context}")
            
            # Добавляем контекст только если он есть
            if context_parts:
                parts.append("\n\n--- Дополнительный контекст ---\n" + "\n\n".join(context_parts))
                
                # Добавляем мягкую инструкцию, как использовать контекст
                parts.append("Используй приведенный выше контекст при необходимости, но не упоминай его напрямую в ответе.")
            
            # Формируем итоговое обогащенное сообщение
            enriched_message = "\n\n".join(parts)
            
            # Логгируем результат (для отладки)
            enrichment_stats = {
                "original_length": len(message),
                "enriched_length": len(enriched_message),
                "memory_results": len(memory_results) if memory_results else 0,
                "has_recent_context": bool(recent_messages)
            }
            print(f"🧠 Message enriched: {enrichment_stats}")
            
            return enriched_message
            
        except Exception as e:
            # В случае любой ошибки возвращаем исходное сообщение
            print(f"❌ Error enriching message: {e}")
            return message

    def _format_recent_messages(self, session_id: str, limit: int = 5) -> str:
        """
        Форматирует последние сообщения из указанной сессии.
        
        Args:
            session_id: ID сессии
            limit: Максимальное количество сообщений
            
        Returns:
            Отформатированный текст сообщений
        """
        messages = self.get_session_messages(session_id, limit=limit)
        if not messages:
            return ""
        
        formatted = []
        for msg in messages:
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            formatted.append(f"{role_emoji} {msg['content']}")
        
        return "\n\n".join(formatted)

    def _format_memory_results(self, results: List[Dict]) -> str:
        """
        Форматирует результаты поиска в памяти.
        
        Args:
            results: Список результатов поиска
            
        Returns:
            Отформатированный текст результатов
        """
        if not results:
            return ""
        
        formatted = []
        for result in results:
            content = result.get('content', '')
            formatted.append(content)
        
        return "\n\n---\n\n".join(formatted)

    def start_new_session(self, title: str = "Новый чат") -> str:
        """Начать новую сессию (для совместимости с js_bridge)"""
        self.session_id = self.create_session(title)
        return self.session_id

    def get_memory_stats(self) -> Dict[str, Any]:
        """Получить статистику памяти (алиас для get_stats)"""
        stats = self.get_stats()
        # Добавляем дополнительные поля для совместимости
        stats.update({
            'current_session': self.session_id,
            'memory_available': True,
            'recent_messages': len(self.get_session_messages(self.session_id, limit=10))
        })
        return stats

    def save_chat_exchange(self, user_msg_or_session: str, ai_response_or_user: str, ai_response: Optional[str] = None) -> bool:
        """
        Сохранение обмена сообщениями (с поддержкой двух сигнатур для совместимости)
        
        Если 3 параметра: save_chat_exchange(session_id, user_msg, ai_response) - новый API
        Если 2 параметра: save_chat_exchange(user_msg, ai_response) - старый API для js_bridge
        """
        try:
            if ai_response is None:
                # Старая сигнатура: save_chat_exchange(user_msg, ai_response)
                user_message = user_msg_or_session
                ai_message = ai_response_or_user
                session_id = self.session_id  # Используем текущую сессию
            else:
                # Новая сигнатура: save_chat_exchange(session_id, user_msg, ai_response)  
                session_id = user_msg_or_session
                user_message = ai_response_or_user
                ai_message = ai_response
            
            self.add_message(session_id, "user", user_message)
            self.add_message(session_id, "assistant", ai_message)
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


""" if __name__ == "__main__":
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
    
print("🎉 Всё работает!") """