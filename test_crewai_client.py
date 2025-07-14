#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки работы CrewAIClient после исправления формата запроса
"""

import sys
import os
import time
import json
import logging
from pathlib import Path

# Настраиваем пути для импорта
current_dir = Path(__file__).parent
ui_dir = current_dir / "GopiAI-UI"
sys.path.append(str(ui_dir))

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_crewai_client.log")
    ]
)
logger = logging.getLogger(__name__)

# Импортируем CrewAIClient
try:
    from gopiai.ui.components.crewai_client import CrewAIClient
    logger.info("CrewAIClient успешно импортирован")
except ImportError as e:
    logger.error(f"Ошибка импорта CrewAIClient: {e}")
    sys.exit(1)

def test_simple_request():
    """Тестирование простого запроса к CrewAI API"""
    client = CrewAIClient()
    
    # Проверяем доступность сервера
    if not client.is_available():
        logger.error("Сервер CrewAI недоступен")
        return False
    
    logger.info("Отправка простого запроса...")
    response = client.process_request("Привет, это тестовое сообщение")
    
    logger.info(f"Получен ответ: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # Проверяем наличие task_id в ответе
    if 'task_id' in response:
        logger.info(f"Получен task_id: {response['task_id']}")
        
        # Ждем и проверяем статус задачи
        for _ in range(10):  # Максимум 10 попыток
            time.sleep(2)  # Пауза 2 секунды между запросами
            
            status_response = client.check_task_status(response['task_id'])
            logger.info(f"Статус задачи: {json.dumps(status_response, ensure_ascii=False, indent=2)}")
            
            if status_response.get('status') == 'completed':
                logger.info("Задача успешно выполнена!")
                return True
            
            if status_response.get('status') == 'failed':
                logger.error(f"Задача завершилась с ошибкой: {status_response.get('error')}")
                return False
        
        logger.warning("Превышено время ожидания выполнения задачи")
        return False
    else:
        logger.error("В ответе отсутствует task_id")
        return False

def test_complex_request():
    """Тестирование сложного запроса с дополнительными полями"""
    client = CrewAIClient()
    
    # Проверяем доступность сервера
    if not client.is_available():
        logger.error("Сервер CrewAI недоступен")
        return False
    
    # Формируем сложный запрос с дополнительными полями
    request = {
        "message": "Расскажи о возможностях CrewAI",
        "system_prompt": "Ты - эксперт по CrewAI. Отвечай кратко и по существу.",
        "metadata": {
            "chat_history": [
                {"role": "user", "content": "Привет"},
                {"role": "assistant", "content": "Здравствуйте! Чем могу помочь?"}
            ]
        }
    }
    
    logger.info("Отправка сложного запроса...")
    response = client.process_request(request)
    
    logger.info(f"Получен ответ: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # Проверяем наличие task_id в ответе
    if 'task_id' in response:
        logger.info(f"Получен task_id: {response['task_id']}")
        
        # Ждем и проверяем статус задачи
        for _ in range(10):  # Максимум 10 попыток
            time.sleep(2)  # Пауза 2 секунды между запросами
            
            status_response = client.check_task_status(response['task_id'])
            logger.info(f"Статус задачи: {json.dumps(status_response, ensure_ascii=False, indent=2)}")
            
            if status_response.get('status') == 'completed':
                logger.info("Задача успешно выполнена!")
                return True
            
            if status_response.get('status') == 'failed':
                logger.error(f"Задача завершилась с ошибкой: {status_response.get('error')}")
                return False
        
        logger.warning("Превышено время ожидания выполнения задачи")
        return False
    else:
        logger.error("В ответе отсутствует task_id")
        return False

if __name__ == "__main__":
    logger.info("=== Начало тестирования CrewAIClient ===")
    
    # Тестируем простой запрос
    logger.info("--- Тестирование простого запроса ---")
    simple_result = test_simple_request()
    
    # Тестируем сложный запрос
    logger.info("--- Тестирование сложного запроса ---")
    complex_result = test_complex_request()
    
    # Выводим итоговый результат
    logger.info("=== Результаты тестирования ===")
    logger.info(f"Простой запрос: {'УСПЕШНО' if simple_result else 'ОШИБКА'}")
    logger.info(f"Сложный запрос: {'УСПЕШНО' if complex_result else 'ОШИБКА'}")
    
    if simple_result and complex_result:
        logger.info("Все тесты пройдены успешно!")
    else:
        logger.error("Некоторые тесты завершились с ошибкой.")
