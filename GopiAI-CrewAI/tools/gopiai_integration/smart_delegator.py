# --- START OF FILE smart_delegator.py (ВОССТАНОВЛЕННАЯ ЛОГИКА) ---

import logging
import json
import time
import traceback
from typing import Dict, List, Any, Optional

# Импортируем наш модуль системных промптов
from .system_prompts import get_system_prompts

# Инициализируем логгер перед использованием
logger = logging.getLogger(__name__)

# Используем локальную заглушку litellm вместо реального модуля
try:
    import litellm
except ImportError:
    from .base import litellm_stub as litellm
    logger.warning("WARNING: Using litellm stub instead of actual litellm module")
from rag_system import get_rag_system, RAGSystem

class SmartDelegator:
    
    def __init__(self, rag_system: Optional[RAGSystem] = None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.rag_system = rag_system
        self.rag_available = self.rag_system is not None and self.rag_system.embeddings is not None
        
        if self.rag_available:
            logger.info(f"[OK] RAG system passed to SmartDelegator. Records: {self.rag_system.embeddings.count()}")
        else:
            logger.warning("[WARNING] RAG system not passed or not initialized.")

    def process_request(self, message: str, metadata: Dict) -> Dict:
        """
        Главный метод обработки. Анализирует, получает контекст и вызывает LLM.
        """
        start_time = time.time()
        
        # 1. Анализ (пока заглушка, можно вернуть старую логику позже)
        analysis = {"type": "general", "complexity": 1, "requires_crewai": False}
        
        # 2. Получение RAG-контекста
        rag_context = self.rag_system.get_context_for_prompt(message) if self.rag_available else None
        
        # 3. Формирование промпта
        messages = self._format_prompt(message, rag_context, metadata.get("chat_history", []))
        
        # 4. Вызов LLM
        response_text = self._call_llm(messages)
        
        elapsed = time.time() - start_time
        logger.info(f"[TIMING] Request processed in {elapsed:.2f} sec")
        
        # 5. Возвращаем результат в стандартном формате
        analysis['analysis_time'] = elapsed
        return {
            "response": response_text,
            "processed_with_crewai": False,
            "analysis": analysis
        }

    def _format_prompt(self, user_message: str, rag_context: Optional[str], chat_history: List[Dict]) -> List[Dict]:
        """Формирует итоговый список сообщений для LLM."""
        
        # Получаем системные промпты из модуля system_prompts
        prompts_manager = get_system_prompts()
        
        # Проверяем наличие выбранного инструмента в метаданных
        tool_info = None
        for msg in chat_history[-5:]:  # Ищем в последних 5 сообщениях
            if isinstance(msg, dict) and msg.get('metadata') and msg['metadata'].get('tool'):
                tool_info = msg['metadata']['tool']
                break
        
        # Получаем системный промпт с контекстом из RAG
        system_prompt = prompts_manager.get_assistant_prompt_with_context(rag_context)
        
        # Если есть информация об инструменте, добавляем ее в промпт
        if tool_info and isinstance(tool_info, dict):
            tool_name = tool_info.get('name', '') or tool_info.get('tool_id', '')
            tool_description = tool_info.get('description', '')
            tool_usage = tool_info.get('usage', '')
            
            if tool_name:
                system_prompt += f"\n\n## Выбранный инструмент: {tool_name}"
                if tool_description:
                    system_prompt += f"\n{tool_description}"
                if tool_usage:
                    system_prompt += f"\n\nПримеры использования:\n```\n{tool_usage}\n```"
            
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем краткосрочную память (историю чата)
        # Убираем системные сообщения и берем последние 20 реплик
        # Фильтруем сообщения: отсеиваем системные и служебные сообщения
        filtered_history = []
        for msg in chat_history:
            if msg.get("role") == "system":
                continue  # Пропускаем системные сообщения
                
            # Проверяем содержимое на наличие служебных сообщений
            content = msg.get("content", "")
            if content and isinstance(content, str):
                if "⏳ Обрабатываю запрос" in content:
                    continue  # Пропускаем заглушки запросов
                if "Произошла ошибка" in content:
                    continue  # Пропускаем сообщения об ошибках
            
            filtered_history.append(msg)
            
        # Берем только последние 20 сообщений после фильтрации
        history_to_add = filtered_history[-20:]  # Увеличено с 10 до 20 сообщений
        
        # Добавляем логирование размера окна кратковременной памяти
        logger.info(f"Окно кратковременной памяти: добавлено {len(history_to_add)} сообщений из {len(chat_history)} в истории")
        if len(history_to_add) > 0:
            logger.debug(f"Первое сообщение в окне: {history_to_add[0].get('role')}: {history_to_add[0].get('content')[:30]}...")
        messages.extend(history_to_add)
        
        # Добавляем текущий вопрос пользователя, если его еще нет в истории
        if not messages or messages[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})
            
        logger.debug(f"Итоговый промпт для LLM: {json.dumps(messages, indent=2, ensure_ascii=False)}")
        return messages

    def _call_llm(self, messages: List[Dict]) -> str:
        """Безопасно вызывает LLM через litellm с таймаутом."""
        try:
            # Здесь можно добавить логику выбора модели из llm_rotation_config, если нужно
            selected_model = "gemini/gemini-1.5-flash"
            
            logger.info(f"Calling model {selected_model}...")
            response = litellm.completion(
                model=selected_model,
                messages=messages,
                temperature=0.5,
                max_tokens=2000,
                timeout=30  # Таймаут 30 секунд
            )
            
            result = response.choices[0].message.content
            logger.info("[OK] Response from LLM received.")
            return result.strip()
            
        except Exception as e:
            logger.error(f"[ERROR] Error calling LLM: {e}", exc_info=True)
            # Возвращаем пользователю понятное сообщение об ошибке
            if "Timeout" in str(e):
                return "Sorry, the model server is not responding. Please try again later."
            return f"An internal error occurred when accessing the language model."

# --- END OF FILE smart_delegator.py ---