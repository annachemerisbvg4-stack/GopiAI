"""
Модели данных для RAG Memory системы
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class MessageRole(str, Enum):
    """Роли участников разговора"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ConversationMessage(BaseModel):
    """Модель сообщения в разговоре"""
    id: str = Field(..., description="Уникальный ID сообщения")
    role: MessageRole = Field(..., description="Роль отправителя")
    content: str = Field(..., description="Содержимое сообщения")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время создания")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConversationSession(BaseModel):
    """Модель сессии разговора"""
    session_id: str = Field(..., description="Уникальный ID сессии")
    title: str = Field(..., description="Заголовок разговора")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания")
    updated_at: datetime = Field(default_factory=datetime.now, description="Время последнего обновления")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Сообщения в разговоре")
    tags: List[str] = Field(default_factory=list, description="Теги для категоризации")
    summary: Optional[str] = Field(None, description="Краткое содержание разговора")
    project_context: Optional[str] = Field(None, description="Контекст проекта (например, GopiAI-Core)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_message(self, role: MessageRole, content: str, metadata: Dict[str, Any] = None) -> ConversationMessage:
        """Добавить сообщение в разговор"""
        message_id = f"{self.session_id}_msg_{len(self.messages) + 1}"
        message = ConversationMessage(
            id=message_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_context_string(self) -> str:
        """Получить строковое представление разговора для индексации"""
        context_parts = [
            f"Сессия: {self.title}",
            f"Теги: {', '.join(self.tags)}",
            f"Проект: {self.project_context or 'Общий'}",
            f"Дата: {self.created_at.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        if self.summary:
            context_parts.append(f"Резюме: {self.summary}")
        
        context_parts.append("Сообщения:")
        for msg in self.messages:
            role_ru = {"user": "Пользователь", "assistant": "Ассистент", "system": "Система"}.get(msg.role, msg.role)
            context_parts.append(f"{role_ru}: {msg.content}")
        
        return "\n".join(context_parts)

class SearchResult(BaseModel):
    """Результат поиска в RAG системе"""
    session_id: str = Field(..., description="ID найденной сессии")
    title: str = Field(..., description="Заголовок разговора")
    relevance_score: float = Field(..., description="Оценка релевантности (0-1)")
    matched_content: str = Field(..., description="Найденный фрагмент")
    context_preview: str = Field(..., description="Предварительный просмотр контекста")
    timestamp: datetime = Field(..., description="Время создания разговора")
    tags: List[str] = Field(default_factory=list, description="Теги разговора")

class MemoryStats(BaseModel):
    """Статистика памяти RAG системы"""
    total_sessions: int = Field(..., description="Общее количество сессий")
    total_messages: int = Field(..., description="Общее количество сообщений")
    total_documents: int = Field(..., description="Количество документов в векторной БД")
    oldest_session: Optional[datetime] = Field(None, description="Самая старая сессия")
    newest_session: Optional[datetime] = Field(None, description="Самая новая сессия")
    most_active_tags: List[str] = Field(default_factory=list, description="Самые популярные теги")
    storage_size_mb: float = Field(0.0, description="Размер хранилища в МБ")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
