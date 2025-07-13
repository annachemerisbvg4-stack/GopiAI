# --- START OF FILE manager.py (ФИНАЛЬНАЯ ВЕРСИЯ ДЛЯ ОТЛАДКИ) ---

"""
Memory Manager for GopiAI UI

This module provides an interface for managing chat history for the current UI session.
It operates entirely in-memory and does not create any files or folders on disk,
making it completely isolated from the server-side RAG system.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    In-memory-only memory management for GopiAI UI.
    Does not create or write to any files on disk.
    """
    
    def __init__(self):
        """Initialize the memory manager without disk interaction."""
        # ### ИЗМЕНЕНО ###
        # Больше не создаем папки Path.home() / ".gopiai"
        logger.info("[CLIENT-SIDE MEMORY] Initializing in-memory manager. No files will be created.")
        
        # Данные существуют только в оперативной памяти
        self.chats: List[Dict[str, Any]] = []
        self.sessions: Dict[str, Any] = {}
        
        # Пытаемся загрузить историю из локального файла для удобства отображения,
        # но не падаем, если его нет.
        self._load_local_data_for_display()
        
    def _load_local_data_for_display(self):
        """
        Tries to load a local chats.json for display purposes only.
        This is a convenience for debugging and does not affect the server.
        """
        try:
            # Ищем chats.json рядом с этим файлом
            local_chats_file = Path(__file__).parent / "chats.json"
            if local_chats_file.exists():
                with open(local_chats_file, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
                logger.info(f"[CLIENT-SIDE MEMORY] For display only: Loaded {len(self.chats)} messages from local {local_chats_file}")
            else:
                 logger.info("[CLIENT-SIDE MEMORY] No local chats.json found for display. Starting with a clean slate.")
        except Exception as e:
            logger.error(f"Error loading local chats for display: {e}")

    def add_message(self, session_id: str, role: str, content: str, **metadata) -> str:
        """
        Adds a message to the IN-MEMORY list for the current UI session.
        Does NOT save to disk.
        """
        import uuid
        from datetime import datetime
        
        if not content.strip():
            return ""

        # Управляем сессиями только в памяти
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'id': session_id, 'title': content[:30], # Название чата - первые 30 символов
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
        logger.info("[CLIENT-SIDE MEMORY] Added message to in-memory list. Disk saving is OFF.")
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

    # Остальные методы могут быть упрощены или возвращать пустые значения,
    # так как они больше не управляют персистентностью.
    def list_sessions(self) -> List[Dict]:
        return list(self.sessions.values())
        
# --- Singleton Instance ---
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    """Returns the singleton instance of the MemoryManager."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance

# --- END OF FILE manager.py ---