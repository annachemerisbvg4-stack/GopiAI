#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Smithery API ключа и интеграции с MCP серверами.
"""

import os
import sys
import asyncio
import httpx
import logging
from urllib.parse import quote
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmitheryAPITester:
    """Тестер для Smithery Registry API"""
    
    def __init__(self):
        # Загружаем переменные окружения из .env файла
        load_dotenv(r"C:\Users\crazy\GOPI_AI_MODULES\.env")
        self.api_key = os.environ.get("SMITHERY_API_KEY")
        if not self.api_key:
            logger.error("SMITHERY_API_KEY не найден в переменных окружения")
            sys.exit(1)
        
        self.base_url = "https://registry.smithery.ai"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        
        logger.info(f"Инициализация с API ключом: {self.api_key[:8]}...{self.api_key[-4:]}")
    
    async def test_api_key(self):
        """Тестирует валидность API ключа"""
        logger.info("Проверка валидности API ключа...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/servers",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info("✅ API ключ валидный")
                    return True
                elif response.status_code == 401:
                    logger.error("❌ API ключ недействителен")
                    logger.error(f"Ответ: {response.text}")
                    return False
                else:
                    logger.error(f"❌ Неожиданный статус: {response.status_code}")
                    logger.error(f"Ответ: {response.text}")
                    return False
            except Exception as e:
                logger.error(f"❌ Ошибка при проверке API ключа: {e}")
                return False
    
    async def list_servers(self, limit=5):
        """Получает список доступных серверов"""
        logger.info("Получение списка серверов...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/servers?pageSize={limit}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    servers = data.get('servers', [])
                    
                    logger.info(f"✅ Найдено {len(servers)} серверов:")
                    for server in servers:
                        logger.info(f"  - {server.get('qualifiedName', 'Unknown')}: {server.get('displayName', 'No name')}")
                        logger.info(f"    Описание: {server.get('description', 'No description')}")
                        logger.info(f"    Развернут: {server.get('isDeployed', False)}")
                        logger.info(f"    Удаленный: {server.get('remote', False)}")
                        logger.info("")
                    
                    return servers
                else:
                    logger.error(f"❌ Ошибка получения списка серверов: {response.status_code}")
                    logger.error(f"Ответ: {response.text}")
                    return []
            except Exception as e:
                logger.error(f"❌ Ошибка при получении списка серверов: {e}")
                return []
    
    async def get_server_info(self, qualified_name):
        """Получает информацию о конкретном сервере"""
        logger.info(f"Получение информации о сервере: {qualified_name}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/servers/{qualified_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Информация о сервере {qualified_name}:")
                    logger.info(f"  Название: {data.get('displayName', 'No name')}")
                    logger.info(f"  Описание: {data.get('description', 'No description')}")
                    logger.info(f"  Развернут: {data.get('deploymentUrl', 'No deployment URL')}")
                    logger.info(f"  Удаленный: {data.get('remote', False)}")
                    
                    # Показываем инструменты
                    tools = data.get('tools', [])
                    if tools:
                        logger.info(f"  Инструменты ({len(tools)}):")
                        for tool in tools:
                            logger.info(f"    - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    else:
                        logger.info("  Инструменты: не найдены")
                    
                    # Показываем способы подключения
                    connections = data.get('connections', [])
                    if connections:
                        logger.info(f"  Способы подключения ({len(connections)}):")
                        for conn in connections:
                            logger.info(f"    - Тип: {conn.get('type', 'Unknown')}")
                            if conn.get('url'):
                                logger.info(f"      URL: {conn.get('url')}")
                    
                    return data
                else:
                    logger.error(f"❌ Ошибка получения информации о сервере: {response.status_code}")
                    logger.error(f"Ответ: {response.text}")
                    return None
            except Exception as e:
                logger.error(f"❌ Ошибка при получении информации о сервере: {e}")
                return None
    
    async def test_deployed_servers(self):
        """Тестирует развернутые серверы"""
        logger.info("Поиск развернутых серверов...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/servers?q=is:deployed&pageSize=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    servers = data.get('servers', [])
                    deployed_servers = [s for s in servers if s.get('isDeployed', False)]
                    
                    logger.info(f"✅ Найдено {len(deployed_servers)} развернутых серверов:")
                    for server in deployed_servers:
                        logger.info(f"  - {server.get('qualifiedName', 'Unknown')}: {server.get('displayName', 'No name')}")
                    
                    return deployed_servers
                else:
                    logger.error(f"❌ Ошибка поиска развернутых серверов: {response.status_code}")
                    logger.error(f"Ответ: {response.text}")
                    return []
            except Exception as e:
                logger.error(f"❌ Ошибка при поиске развернутых серверов: {e}")
                return []

async def main():
    """Основная функция тестирования"""
    logger.info("=== Тестирование Smithery API ===")
    
    tester = SmitheryAPITester()
    
    # 1. Проверяем API ключ
    if not await tester.test_api_key():
        logger.error("Тестирование прервано из-за недействительного API ключа")
        return
    
    # 2. Получаем список серверов
    servers = await tester.list_servers(limit=3)
    
    # 3. Тестируем информацию о первом сервере
    if servers:
        first_server = servers[0]
        qualified_name = first_server.get('qualifiedName')
        if qualified_name:
            await tester.get_server_info(qualified_name)
    
    # 4. Тестируем развернутые серверы
    deployed_servers = await tester.test_deployed_servers()
    
    # 5. Тестируем информацию о первом развернутом сервере
    if deployed_servers:
        first_deployed = deployed_servers[0]
        qualified_name = first_deployed.get('qualifiedName')
        if qualified_name:
            logger.info(f"\n=== Детальная информация о развернутом сервере ===")
            await tester.get_server_info(qualified_name)
    
    logger.info("=== Тестирование завершено ===")

if __name__ == "__main__":
    asyncio.run(main())
