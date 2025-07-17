#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к MCP серверам
"""

import os
import sys
import asyncio
import logging
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

def check_smithery_api_key():
    """Проверяем API ключ Smithery"""
    api_key = os.environ.get("SMITHERY_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        logger.info(f"[OK] SMITHERY_API_KEY найден: {masked_key}")
        return True
    else:
        logger.error("[ERROR] SMITHERY_API_KEY не найден в переменных окружения")
        return False

async def test_mcp_manager():
    """Тест MCP менеджера"""
    try:
        logger.info("=== Тест MCP Manager ===")
        
        # Импортируем MCP менеджер
        from tools.gopiai_integration.mcp_integration import MCPToolsManager, get_mcp_tools_manager
        
        # Получаем экземпляр менеджера
        mcp_manager = get_mcp_tools_manager()
        logger.info("MCP менеджер инициализирован")
        
        # Проверяем доступные серверы
        logger.info("Доступные MCP серверы:")
        for server in mcp_manager.MCP_SERVERS:
            logger.info(f"  - {server['name']}: {server['url']}")
        
        # Пробуем получить инструменты
        logger.info("Пытаемся получить инструменты...")
        tools = await mcp_manager.get_all_tools()
        
        if tools:
            logger.info(f"[SUCCESS] Получено {len(tools)} инструментов MCP")
            for tool in tools[:5]:  # Показываем первые 5
                logger.info(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        else:
            logger.warning("[WARNING] Не удалось получить инструменты MCP")
            
        return len(tools) if tools else 0
        
    except Exception as e:
        logger.error(f"[ERROR] Ошибка при тестировании MCP: {e}")
        import traceback
        traceback.print_exc()
        return 0

async def test_single_server():
    """Тест подключения к одному серверу"""
    try:
        logger.info("=== Тест подключения к одному серверу ===")
        
        import httpx
        
        # Тестируем подключение к toolbox серверу
        url = "https://server.smithery.ai/@smithery/toolbox/mcp"
        headers = {
            "Authorization": f"Bearer {os.environ.get('SMITHERY_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # Пробуем простой POST запрос
        async with httpx.AsyncClient() as client:
            response = await client.post(url, 
                                       json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
                                       headers=headers,
                                       timeout=10.0)
            
            logger.info(f"Ответ от сервера: {response.status_code}")
            if response.status_code == 200:
                logger.info("[SUCCESS] Подключение к серверу успешно")
                return True
            else:
                logger.error(f"[ERROR] Ошибка подключения: {response.status_code}")
                logger.error(f"Ответ: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"[ERROR] Ошибка при тестировании сервера: {e}")
        return False

async def main():
    """Основная функция"""
    logger.info("=== Диагностика MCP подключения ===")
    
    # Проверяем API ключ
    if not check_smithery_api_key():
        logger.error("Не удается продолжить без API ключа")
        return False
    
    # Тестируем подключение к одному серверу
    single_server_ok = await test_single_server()
    
    # Тестируем MCP менеджер
    tools_count = await test_mcp_manager()
    
    logger.info(f"\n=== Результаты ===")
    logger.info(f"Подключение к серверу: {'OK' if single_server_ok else 'FAIL'}")
    logger.info(f"Количество инструментов: {tools_count}")
    
    if single_server_ok and tools_count > 0:
        logger.info("[SUCCESS] MCP подключение работает!")
        return True
    else:
        logger.error("[FAIL] Проблемы с MCP подключением")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
