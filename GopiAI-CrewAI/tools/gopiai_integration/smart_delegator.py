# --- START OF FILE smart_delegator.py (ВОССТАНОВЛЕННАЯ ЛОГИКА) ---

import logging
import json
import time
import traceback
from typing import Dict, List, Any, Optional

import litellm
from rag_system import get_rag_system, RAGSystem

logger = logging.getLogger(__name__)

class SmartDelegator:
    
    def __init__(self, rag_system: Optional[RAGSystem] = None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.rag_system = rag_system
        self.rag_available = self.rag_system is not None and self.rag_system.embeddings is not None
        
        if self.rag_available:
            logger.info(f"✅ RAG-система передана в SmartDelegator. Записей: {self.rag_system.embeddings.count()}")
        else:
            logger.warning("⚠️ RAG-система не передана или не инициализирована.")

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
        logger.info(f"⏱ Запрос обработан за {elapsed:.2f} сек")
        
        # 5. Возвращаем результат в стандартном формате
        analysis['analysis_time'] = elapsed
        return {
            "response": response_text,
            "processed_with_crewai": False,
            "analysis": analysis
        }

    def _format_prompt(self, user_message: str, rag_context: Optional[str], chat_history: List[Dict]) -> List[Dict]:
        """Формирует итоговый список сообщений для LLM."""
        
        system_prompt = (
            "Ты - GopiAI, полезный ассистент. "
            "Твой ответ ДОЛЖЕН СТРОГО ОСНОВЫВАТЬСЯ на информации из блока 'КОНТЕКСТ ИЗ ПАМЯТИ', если он предоставлен. "
            "Если в контексте нет ответа, используй свои общие знания. "
            "Будь краток и точен."
        )
        
        if rag_context and "No relevant context" not in rag_context:
            system_prompt += f"\n\nКОНТЕКСТ ИЗ ПАМЯТИ:\n{rag_context}"
            
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем краткосрочную память (историю чата)
        # Убираем системные сообщения и берем последние 10 реплик
        history_to_add = [msg for msg in chat_history if msg.get("role") != "system"][-10:]
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
            
            logger.info(f"Вызов модели {selected_model}...")
            response = litellm.completion(
                model=selected_model,
                messages=messages,
                temperature=0.5,
                max_tokens=2000,
                timeout=30  # Таймаут 30 секунд
            )
            
            result = response.choices[0].message.content
            logger.info("✅ Ответ от LLM получен.")
            return result.strip()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при вызове LLM: {e}", exc_info=True)
            # Возвращаем пользователю понятное сообщение об ошибке
            if "Timeout" in str(e):
                return "Извините, сервер модели не отвечает. Попробуйте позже."
            return f"Произошла внутренняя ошибка при обращении к языковой модели."

# --- END OF FILE smart_delegator.py ---