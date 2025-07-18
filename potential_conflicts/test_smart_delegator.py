#!/usr/bin/env python3
"""
Тестовый скрипт для проверки SmartDelegator без сервера
"""

import logging
import sys
import os
from pathlib import Path

# Исправляем конфликт OpenMP библиотек
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

# Добавляем пути
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_smart_delegator():
    """Тест SmartDelegator"""
    try:
        logger.info("=== Тест SmartDelegator ===")
        
        # Инициализация RAG системы
        logger.info("Инициализация RAG системы...")
        from rag_system import get_rag_system
        rag_system = get_rag_system()
        logger.info(f"RAG система инициализирована: {rag_system.embeddings.count()} документов")
        
        # Инициализация SmartDelegator
        logger.info("Инициализация SmartDelegator...")
        from tools.gopiai_integration.smart_delegator import SmartDelegator
        smart_delegator = SmartDelegator(rag_system=rag_system)
        logger.info("SmartDelegator инициализирован")
        
        # Тестовый запрос
        test_message = "Привет! Как дела?"
        test_metadata = {"session_id": "test_session"}
        
        logger.info(f"Отправляем тестовое сообщение: {test_message}")
        result = smart_delegator.process_request(test_message, test_metadata)
        
        logger.info("Результат обработки:")
        logger.info(f"Ответ: {result.get('response', 'Нет ответа')}")
        logger.info(f"Статус: {result.get('processed_with_crewai', 'Неизвестно')}")
        
        print("[SUCCESS] SmartDelegator работает корректно!")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Ошибка при тестировании SmartDelegator: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_smart_delegator()
    sys.exit(0 if success else 1)
