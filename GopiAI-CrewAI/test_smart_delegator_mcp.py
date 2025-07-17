#!/usr/bin/env python3
"""
Тестовый скрипт для проверки SmartDelegator с исправленной MCP интеграцией.
"""

import os
import sys
import logging
import asyncio

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'gopiai_integration'))

# Добавляем путь к системе RAG
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'GopiAI-CrewAI'))

# Устанавливаем переменную окружения для KMP, чтобы избежать конфликтов
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_smart_delegator_mcp():
    """Тестирует SmartDelegator с MCP интеграцией"""
    logger.info("=== Тестирование SmartDelegator с MCP интеграцией ===")
    
    try:
        # Импортируем SmartDelegator
        from tools.gopiai_integration.smart_delegator import SmartDelegator
        
        # Создаем экземпляр без RAG системы
        delegator = SmartDelegator()
        
        # Проверяем инициализацию
        logger.info(f"Локальные инструменты доступны: {delegator.local_tools_available}")
        logger.info(f"Внешние MCP инструменты доступны: {delegator.mcp_available}")
        
        # Тестируем обработку запроса без MCP инструментов
        logger.info("\n--- Тестирование обычного запроса ---")
        result = delegator.process_request(
            "Привет, как дела?",
            {"chat_history": [], "user_id": "test_user"}
        )
        logger.info(f"Результат: {result.get('response', 'Нет ответа')}")
        
        # Тестируем запрос с использованием локального инструмента
        logger.info("\n--- Тестирование запроса с локальным инструментом ---")
        result = delegator.process_request(
            "Используй system_info для получения информации о системе",
            {"chat_history": [], "user_id": "test_user"}
        )
        logger.info(f"Результат: {result.get('response', 'Нет ответа')}")
        
        # Тестируем запрос с использованием внешнего MCP инструмента
        if delegator.mcp_available:
            logger.info("\n--- Тестирование запроса с внешним MCP инструментом ---")
            result = delegator.process_request(
                "Используй search_engine для поиска информации о Python",
                {"chat_history": [], "user_id": "test_user"}
            )
            logger.info(f"Результат: {result.get('response', 'Нет ответа')}")
        
        logger.info("\n=== Тестирование завершено ===")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_delegator_mcp()
