#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправленной интеграции MCP через Smithery Registry API.
"""

import asyncio
import logging
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'gopiai_integration'))

from mcp_integration_fixed import get_smithery_mcp_manager, get_mcp_tools_info

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_mcp_integration():
    """Тестирует исправленную интеграцию MCP"""
    logger.info("=== Тестирование исправленной MCP интеграции ===")
    
    # Получаем менеджер
    manager = get_smithery_mcp_manager()
    if not manager:
        logger.error("Не удалось создать менеджер MCP")
        return
    
    # Инициализируем менеджер
    await manager.initialize()
    
    # Получаем все инструменты
    logger.info("Получение всех инструментов...")
    tools = await manager.get_all_tools()
    
    if not tools:
        logger.warning("Инструменты не найдены")
        return
    
    logger.info(f"Найдено {len(tools)} инструментов:")
    for tool in tools:
        logger.info(f"  - {tool['name']} (сервер: {tool['server_name']})")
        logger.info(f"    Описание: {tool['description']}")
        logger.info("")
    
    # Тестируем поиск инструмента
    if tools:
        first_tool = tools[0]
        logger.info(f"Тестирование поиска инструмента: {first_tool['name']}")
        found_tool = manager.get_tool_by_name(first_tool['name'])
        
        if found_tool:
            logger.info(f"✅ Инструмент найден: {found_tool['name']}")
        else:
            logger.warning("❌ Инструмент не найден")
    
    # Тестируем выполнение инструмента (если есть подходящий)
    for tool in tools:
        # Ищем простой инструмент для тестирования
        if 'config' in tool['name'].lower() or 'info' in tool['name'].lower():
            logger.info(f"Тестирование выполнения инструмента: {tool['name']}")
            
            try:
                result = await manager.execute_tool_async(tool)
                logger.info(f"✅ Результат выполнения: {result}")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка выполнения: {e}")
                break
    
    logger.info("=== Тестирование завершено ===")

def test_tools_info():
    """Тестирует функцию получения информации об инструментах"""
    logger.info("=== Тестирование get_mcp_tools_info ===")
    
    info = get_mcp_tools_info()
    logger.info(f"Информация об инструментах:\n{info}")

if __name__ == "__main__":
    # Тестируем асинхронную интеграцию
    asyncio.run(test_mcp_integration())
    
    # Тестируем синхронную функцию
    test_tools_info()
