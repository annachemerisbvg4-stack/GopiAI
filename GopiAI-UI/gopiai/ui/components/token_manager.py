"""
Token Manager для управления контекстом Claude
==============================================

Утилиты для подсчета токенов и управления контекстным окном
при интеграции памяти с Claude AI.
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class TokenLimits:
    """Конфигурация лимитов токенов для Claude"""
    max_total_context: int = 200000  # Максимальный контекст Claude Sonnet
    reserve_for_response: int = 20000  # Резерв для ответа Claude
    reserve_for_complex_tasks: int = 50000  # Резерв для комплексных задач/кода
    max_memory_tokens: int = 130000  # Доступно для памяти (200k - 20k - 50k)
    max_recent_messages_tokens: int = 30000  # Для последних сообщений
    max_rag_search_tokens: int = 100000  # Для RAG поиска


class TokenManager:
    """
    Менеджер токенов для оптимального управления контекстом Claude
    """
    
    def __init__(self, limits: TokenLimits = None):
        self.limits = limits or TokenLimits()
        
    def estimate_tokens(self, text: str) -> int:
        """
        Примерная оценка количества токенов в тексте.
        Используем эвристику: ~4 символа = 1 токен для русского/английского текста.
        """
        if not text:
            return 0
        
        # Базовый подсчет по символам
        char_count = len(text)
        
        # Корректировки для разных типов контента
        if self._is_code_heavy(text):
            # Код обычно более токен-плотный
            estimated_tokens = int(char_count / 3.5)
        elif self._is_russian_heavy(text):
            # Русский текст может быть менее токен-плотный
            estimated_tokens = int(char_count / 4.5)
        else:
            # Английский текст (базовая оценка)
            estimated_tokens = int(char_count / 4.0)
        
        return max(estimated_tokens, 1)  # Минимум 1 токен
    
    def _is_code_heavy(self, text: str) -> bool:
        """Определение текста с большим количеством кода"""
        # Ищем признаки кода
        code_indicators = [
            r'def\s+\w+\(',  # Python функции
            r'class\s+\w+',  # Python классы
            r'import\s+\w+',  # Импорты
            r'function\s+\w+\(',  # JS функции
            r'const\s+\w+\s*=',  # JS константы
            r'{\s*\n.*}',  # Блоки кода
            r'<\w+[^>]*>',  # HTML теги
            r'@\w+\(',  # Декораторы/аннотации
        ]
        
        code_matches = sum(1 for pattern in code_indicators if re.search(pattern, text, re.MULTILINE))
        total_lines = len(text.split('\n'))
        
        return code_matches > 0 and (code_matches / max(total_lines, 1)) > 0.1
    
    def _is_russian_heavy(self, text: str) -> bool:
        """Определение текста с большим количеством русского"""
        # Подсчет русских символов
        russian_chars = len(re.findall(r'[а-яё]', text.lower()))
        total_chars = len(text)
        
        return total_chars > 0 and (russian_chars / total_chars) > 0.3
    
    def optimize_recent_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Оптимизация списка последних сообщений для включения в контекст.
        Возвращает сообщения, которые помещаются в лимит токенов.
        """
        if not messages:
            return []
        
        optimized_messages = []
        total_tokens = 0
        
        # Идем с конца (самые свежие сообщения)
        for message in reversed(messages):
            content = message.get('content', '')
            message_tokens = self.estimate_tokens(content)
            
            # Проверяем, поместится ли сообщение
            if total_tokens + message_tokens <= self.limits.max_recent_messages_tokens:
                optimized_messages.insert(0, message)  # Вставляем в начало
                total_tokens += message_tokens
            else:
                # Если сообщение слишком большое, пытаемся его сократить
                if len(optimized_messages) == 0:  # Если это первое сообщение
                    truncated_content = self._truncate_to_token_limit(
                        content, 
                        self.limits.max_recent_messages_tokens // 2
                    )
                    if truncated_content:
                        truncated_message = message.copy()
                        truncated_message['content'] = truncated_content + "... [сообщение сокращено]"
                        optimized_messages.insert(0, truncated_message)
                break
        
        return optimized_messages
    
    def _truncate_to_token_limit(self, text: str, token_limit: int) -> str:
        """Сокращение текста до указанного лимита токенов"""
        if self.estimate_tokens(text) <= token_limit:
            return text
        
        # Примерная длина в символах
        estimated_char_limit = token_limit * 4
        
        if len(text) <= estimated_char_limit:
            return text
        
        # Обрезаем по предложениям, если возможно
        sentences = re.split(r'[.!?]\s+', text)
        
        result = ""
        for sentence in sentences:
            test_result = result + sentence + ". "
            if self.estimate_tokens(test_result) <= token_limit:
                result = test_result
            else:
                break
        
        if result:
            return result.strip()
        
        # Если не получилось по предложениям, обрезаем по символам
        return text[:estimated_char_limit]
    
    def build_enhanced_context(self, 
                             current_message: str,
                             recent_messages: List[Dict[str, Any]] = None,
                             rag_results: List[Dict[str, Any]] = None) -> str:
        """
        Построение обогащенного контекста для Claude с оптимальным использованием токенов.
        """
        context_parts = []
        total_tokens = 0
        
        # Оценка токенов текущего сообщения
        current_tokens = self.estimate_tokens(current_message)
        
        # 1. Добавляем последние сообщения (если есть место)
        if recent_messages:
            optimized_recent = self.optimize_recent_messages(recent_messages)
            if optimized_recent:
                recent_context = self._format_recent_messages(optimized_recent)
                recent_tokens = self.estimate_tokens(recent_context)
                
                if total_tokens + recent_tokens <= self.limits.max_memory_tokens:
                    context_parts.append("## 📝 Контекст последних сообщений:")
                    context_parts.append(recent_context)
                    total_tokens += recent_tokens
        
        # 2. Добавляем результаты RAG поиска (оставшееся место)
        if rag_results:
            remaining_tokens = self.limits.max_memory_tokens - total_tokens
            rag_context = self._format_rag_results(rag_results, remaining_tokens)
            if rag_context:
                context_parts.append("## 🧠 Релевантная информация из памяти:")
                context_parts.append(rag_context)
        
        # 3. Добавляем текущее сообщение
        context_parts.append("## 💬 Текущий запрос:")
        context_parts.append(current_message)
        
        return "\n\n".join(context_parts)
    
    def _format_recent_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Форматирование последних сообщений для контекста"""
        formatted = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            role_emoji = {
                'user': '👤',
                'assistant': '🤖',
                'system': '⚙️'
            }.get(role, '💬')
            
            if timestamp:
                formatted.append(f"{role_emoji} **{role.title()}** ({timestamp}):")
            else:
                formatted.append(f"{role_emoji} **{role.title()}**:")
            
            formatted.append(content)
            formatted.append("")  # Пустая строка
        
        return "\n".join(formatted)
    
    def _format_rag_results(self, results: List[Dict[str, Any]], token_limit: int) -> str:
        """Форматирование результатов RAG поиска с учетом лимита токенов"""
        if not results:
            return ""
        
        formatted_parts = []
        used_tokens = 0
        
        for i, result in enumerate(results):
            title = result.get('title', f'Результат {i+1}')
            content = result.get('context_preview', result.get('matched_content', ''))
            relevance = result.get('relevance_score', 0.0)
            timestamp = result.get('timestamp', '')
            
            # Форматируем один результат
            result_text = f"### 📋 {title} (релевантность: {relevance:.1%})\n"
            if timestamp:
                result_text += f"*Дата: {timestamp}*\n\n"
            result_text += content + "\n"
            
            # Проверяем, поместится ли результат
            result_tokens = self.estimate_tokens(result_text)
            
            if used_tokens + result_tokens <= token_limit:
                formatted_parts.append(result_text)
                used_tokens += result_tokens
            else:
                # Пытаемся сократить последний результат
                if len(formatted_parts) == 0:  # Если это первый результат
                    available_tokens = token_limit - used_tokens
                    truncated_content = self._truncate_to_token_limit(content, available_tokens - 100)
                    if truncated_content:
                        result_text = f"### 📋 {title} (релевантность: {relevance:.1%})\n"
                        if timestamp:
                            result_text += f"*Дата: {timestamp}*\n\n"
                        result_text += truncated_content + "... [сокращено]"
                        formatted_parts.append(result_text)
                break
        
        return "\n".join(formatted_parts) if formatted_parts else ""
    
    def get_token_usage_stats(self, context: str) -> Dict[str, int]:
        """Получение статистики использования токенов"""
        total_tokens = self.estimate_tokens(context)
        
        return {
            "total_tokens": total_tokens,
            "max_context": self.limits.max_total_context,
            "available_for_response": self.limits.reserve_for_response,
            "available_for_tasks": self.limits.reserve_for_complex_tasks,
            "usage_percentage": round((total_tokens / self.limits.max_total_context) * 100, 1)
        }