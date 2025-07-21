# --- START OF FILE manager.py (УНИФИЦИРОВАННАЯ ВЕРСИЯ) ---

"""
Memory Manager for GopiAI UI

This module provides an interface for managing chat history for the current UI session.
Использует общую конфигурацию памяти с сервером CrewAI API для обеспечения
согласованности данных между клиентом и сервером.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Импортируем локальную конфигурацию памяти
from .memory_config import MEMORY_BASE_DIR, CHATS_FILE_PATH, VECTOR_INDEX_PATH

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified memory management for GopiAI UI.
    Uses shared memory configuration with CrewAI API server.
    """
    
    def __init__(self):
        """Initialize the memory manager with shared configuration."""
        # Используем общую конфигурацию памяти
        logger.info(f"[UNIFIED-MEMORY] Initializing memory manager with shared config. Path: {MEMORY_BASE_DIR}")
        
        # Создаем директорию, если она не существует
        MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем структуры данных
        self.chats: List[Dict[str, Any]] = []
        self.sessions: Dict[str, Any] = {}
        
        # Загружаем историю из общего файла
        self._load_chat_history()
        
    def _load_chat_history(self):
        """
        Loads chat history from the shared chats.json file.
        Uses the same file as the CrewAI API server.
        """
        try:
            if CHATS_FILE_PATH.exists():
                with open(CHATS_FILE_PATH, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
                logger.info(f"[UNIFIED-MEMORY] Loaded {len(self.chats)} messages from shared file: {CHATS_FILE_PATH}")
                
                # Создаем словарь сессий на основе загруженных чатов
                session_ids = set(msg.get('session_id') for msg in self.chats if msg.get('session_id'))
                for session_id in session_ids:
                    session_msgs = [msg for msg in self.chats if msg.get('session_id') == session_id]
                    if session_msgs:
                        first_msg = min(session_msgs, key=lambda x: x.get('timestamp', '0'))
                        self.sessions[session_id] = {
                            'id': session_id,
                            'title': first_msg.get('content', '')[:30],
                            'created_at': first_msg.get('timestamp')
                        }
            else:
                logger.info(f"[UNIFIED-MEMORY] No shared chats file found at {CHATS_FILE_PATH}. Creating a new one.")
                # Создаем пустой файл
                with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f)
        except Exception as e:
            logger.error(f"[UNIFIED-MEMORY] Error loading shared chat history: {e}")

    def add_message(self, session_id: str, role: str, content: str, **metadata) -> str:
        """
        Adds a message to the chat history and saves it to the shared file.
        """
        if not content.strip():
            return ""

        # Управляем сессиями
        if session_id not in self.sessions:
            self.sessions[session_id] = {  # type: ignore[type-arg]
                'id': session_id, 
                'title': content[:30], # Название чата - первые 30 символов
                'created_at': datetime.now().isoformat()
            }
        
        message = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        self.chats.append(message)
        
        # Сохраняем в общий файл
        try:
            with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
            logger.info(f"[UNIFIED-MEMORY] Added message and saved to shared file: {CHATS_FILE_PATH}")
        except Exception as e:
            logger.error(f"[UNIFIED-MEMORY] Error saving to shared file: {e}")
            
        return message['id']

    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Gets chat history for a session from the in-memory list."""
        if session_id:
            # Фильтруем сообщения для текущей сессии
            session_messages = [msg for msg in self.chats if msg.get('session_id') == session_id]
            # Сортируем их по времени
            session_messages.sort(key=lambda x: x.get('timestamp', '0'))
            return session_messages
        return []

    # Дополнительные методы для работы с общей памятью
    def list_sessions(self) -> List[Dict]:
        return list(self.sessions.values())

    def get_session_title(self, session_id: str) -> str:
        return self.sessions.get(session_id, {}).get('title', 'New Chat')

    def update_session_title(self, session_id: str, title: str):
        if session_id in self.sessions:
            self.sessions[session_id]['title'] = title
            self._save_data()

    def delete_session(self, session_id: str):
        if not session_id:
            return
        if session_id in self.sessions:
            del self.sessions[session_id]
        self.chats = [msg for msg in self.chats if msg.get('session_id') != session_id]
        self._save_data()

    def _save_data(self):
        try:
            with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'Error saving data: {e}')

# --- Singleton Instance ---
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    """Returns the singleton instance of the MemoryManager."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance

# --- END OF FILE manager.py (УНИФИЦИРОВАННАЯ ВЕРСИЯ) ---