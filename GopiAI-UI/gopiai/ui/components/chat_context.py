"""
Модуль управления контекстом чата для краткосрочной памяти.
Хранит историю сообщений в рамках текущей сессии чата.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class ChatMessage:
    """Представляет одно сообщение в чате."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # 'user' или 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует сообщение в словарь."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Создает сообщение из словаря."""
        timestamp = datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        return cls(data['role'], data['content'], timestamp)


class ChatContext:
    """Управляет контекстом чата с краткосрочной памятью."""
    
    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        self.messages: List[ChatMessage] = []
        self.max_messages = max_messages  # Максимальное количество сообщений
        self.max_tokens = max_tokens  # Примерный лимит токенов (1 токен ≈ 4 символа)
        
    def add_message(self, role: str, content: str) -> None:
        """Добавляет новое сообщение в контекст."""
        message = ChatMessage(role, content)
        self.messages.append(message)
        self._trim_context()
        
    def add_user_message(self, content: str) -> None:
        """Добавляет сообщение пользователя."""
        self.add_message('user', content)
        
    def add_assistant_message(self, content: str) -> None:
        """Добавляет ответ ассистента."""
        self.add_message('assistant', content)
        
    def get_context_for_api(self) -> List[Dict[str, str]]:
        """Возвращает контекст в формате для API (без timestamp)."""
        return [{'role': msg.role, 'content': msg.content} for msg in self.messages]
        
    def get_context_string(self) -> str:
        """Возвращает контекст как строку для передачи в API."""
        if not self.messages:
            return ""
            
        context_parts = []
        for msg in self.messages:
            if msg.role == 'user':
                context_parts.append(f"Пользователь: {msg.content}")
            elif msg.role == 'assistant':
                context_parts.append(f"Ассистент: {msg.content}")
                
        return "\n\n".join(context_parts)
        
    def get_last_messages(self, count: int) -> List[ChatMessage]:
        """Возвращает последние N сообщений."""
        return self.messages[-count:] if count > 0 else []
        
    def clear(self) -> None:
        """Очищает весь контекст."""
        self.messages.clear()
        
    def _trim_context(self) -> None:
        """Обрезает контекст по лимитам сообщений и токенов."""
        # Обрезка по количеству сообщений
        if len(self.messages) > self.max_messages:
            # Удаляем старые сообщения, но стараемся сохранить парность user-assistant
            excess = len(self.messages) - self.max_messages
            self.messages = self.messages[excess:]
            
        # Обрезка по примерному количеству токенов
        total_chars = sum(len(msg.content) for msg in self.messages)
        estimated_tokens = total_chars // 4  # Грубая оценка: 1 токен ≈ 4 символа
        
        if estimated_tokens > self.max_tokens:
            while len(self.messages) > 2 and estimated_tokens > self.max_tokens:
                removed_msg = self.messages.pop(0)
                estimated_tokens -= len(removed_msg.content) // 4
                
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику контекста."""
        total_chars = sum(len(msg.content) for msg in self.messages)
        estimated_tokens = total_chars // 4
        
        return {
            'message_count': len(self.messages),
            'total_characters': total_chars,
            'estimated_tokens': estimated_tokens,
            'max_messages': self.max_messages,
            'max_tokens': self.max_tokens
        }
        
    def to_json(self) -> str:
        """Сериализует контекст в JSON."""
        data = {
            'messages': [msg.to_dict() for msg in self.messages],
            'max_messages': self.max_messages,
            'max_tokens': self.max_tokens
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'ChatContext':
        """Создает контекст из JSON."""
        data = json.loads(json_str)
        context = cls(data.get('max_messages', 20), data.get('max_tokens', 4000))
        
        for msg_data in data.get('messages', []):
            context.messages.append(ChatMessage.from_dict(msg_data))
            
        return context
