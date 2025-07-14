#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки логирования CrewAIClient и ChatAsyncHandler
"""

import os
import sys
import time

# Добавляем путь к модулям GopiAI-UI
sys.path.append(os.path.join(os.path.dirname(__file__), 'GopiAI-UI'))

# Импортируем необходимые модули
from gopiai.ui.components.crewai_client import CrewAIClient
from gopiai.ui.components.chat_async_handler import ChatAsyncHandler

def main():
    """Основная функция для тестирования логирования"""
    print("Запуск тестирования логирования CrewAIClient и ChatAsyncHandler...")
    
    # Инициализируем CrewAIClient
    print("Инициализация CrewAIClient...")
    crewai_client = CrewAIClient(base_url="http://localhost:8000")
    
    # Логируем тестовое сообщение
    print("Логирование тестового сообщения в CrewAIClient...")
    # Используем глобальный логгер из модуля crewai_client
    from gopiai.ui.components.crewai_client import logger as crewai_logger
    crewai_logger.info("Тестовое сообщение CrewAIClient")
    crewai_logger.debug("Тестовое отладочное сообщение CrewAIClient")
    
    # Инициализируем ChatAsyncHandler
    print("Инициализация ChatAsyncHandler...")
    chat_handler = ChatAsyncHandler(crewai_client)
    
    # Логируем тестовое сообщение
    print("Логирование тестового сообщения в ChatAsyncHandler...")
    # Используем глобальный логгер из модуля chat_async_handler
    from gopiai.ui.components.chat_async_handler import logger as async_logger
    async_logger.info("Тестовое сообщение ChatAsyncHandler")
    async_logger.debug("Тестовое отладочное сообщение ChatAsyncHandler")
    
    # Тестируем отправку сообщения
    print("Тестирование отправки сообщения...")
    
    # Создаем словарь с данными сообщения
    message_data = {
        "message": "Тестовое сообщение для CrewAI",
        "metadata": {
            "system_prompt": "Вы помощник", 
            "user_id": "test_user"
        }
    }
    
    # Отправляем сообщение асинхронно
    chat_handler.process_message(message_data)
    
    # Ждем немного, чтобы асинхронный обработчик успел выполниться
    print("Ожидание завершения асинхронной обработки...")
    time.sleep(5)
    
    print("Тестирование завершено!")
    print("Проверьте наличие лог-файлов:")
    print("1. crewai_client.log")
    print("2. chat_async_handler.log")

if __name__ == "__main__":
    main()
