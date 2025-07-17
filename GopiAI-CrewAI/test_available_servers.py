#!/usr/bin/env python3
"""
Тестовый скрипт для проверки доступных серверов и способов подключения.
"""

import asyncio
import logging
import sys
import os
import httpx
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_available_servers():
    """Тестирует доступные серверы и способы подключения"""
    logger.info("=== Проверка доступных серверов ===")
    
    # Загружаем переменные окружения
    load_dotenv(r"C:\Users\crazy\GOPI_AI_MODULES\.env")
    api_key = os.environ.get("SMITHERY_API_KEY")
    
    if not api_key:
        logger.error("SMITHERY_API_KEY не найден")
        return
    
    registry_url = "https://registry.smithery.ai"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Получаем все серверы
        response = await client.get(
            f"{registry_url}/servers?pageSize=20",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Ошибка получения серверов: {response.status_code}")
            return
        
        data = response.json()
        servers = data.get('servers', [])
        
        logger.info(f"Найдено {len(servers)} серверов:")
        
        http_servers = []
        deployed_servers = []
        
        for server in servers:
            qualified_name = server.get('qualifiedName', 'Unknown')
            display_name = server.get('displayName', 'No name')
            is_deployed = server.get('isDeployed', False)
            is_remote = server.get('remote', False)
            
            logger.info(f"  - {qualified_name}: {display_name}")
            logger.info(f"    Развернут: {is_deployed}, Удаленный: {is_remote}")
            
            if is_deployed:
                deployed_servers.append(qualified_name)
            
            # Получаем детальную информацию о сервере
            try:
                server_response = await client.get(
                    f"{registry_url}/servers/{qualified_name}",
                    headers=headers
                )
                
                if server_response.status_code == 200:
                    server_info = server_response.json()
                    connections = server_info.get('connections', [])
                    tools = server_info.get('tools', [])
                    deployment_url = server_info.get('deploymentUrl')
                    
                    logger.info(f"    Deployment URL: {deployment_url}")
                    logger.info(f"    Инструментов: {len(tools)}")
                    
                    if connections:
                        logger.info(f"    Способы подключения:")
                        for conn in connections:
                            conn_type = conn.get('type', 'Unknown')
                            conn_url = conn.get('url', 'No URL')
                            logger.info(f"      - {conn_type}: {conn_url}")
                            
                            if conn_type == 'http' and conn_url != 'No URL':
                                http_servers.append({
                                    'name': qualified_name,
                                    'url': conn_url,
                                    'tools': tools,
                                    'deployment_url': deployment_url
                                })
                    
                    if tools:
                        logger.info(f"    Инструменты:")
                        for tool in tools[:3]:  # Показываем первые 3 инструмента
                            logger.info(f"      - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                
                logger.info("")
            except Exception as e:
                logger.error(f"    Ошибка получения информации о сервере: {e}")
                logger.info("")
        
        logger.info(f"Развернутых серверов: {len(deployed_servers)}")
        logger.info(f"Серверов с HTTP подключением: {len(http_servers)}")
        
        # Тестируем подключение к HTTP серверам
        if http_servers:
            logger.info("\n=== Тестирование подключения к HTTP серверам ===")
            
            for server in http_servers[:3]:  # Тестируем первые 3 сервера
                logger.info(f"Тестирование сервера: {server['name']}")
                
                try:
                    # Пробуем подключиться к серверу
                    url = server.get('deployment_url') or server.get('url')
                    if url:
                        # Тестируем JSON-RPC запрос на получение инструментов
                        request_data = {
                            "jsonrpc": "2.0",
                            "id": "test_tools_list",
                            "method": "tools/list",
                            "params": {}
                        }
                        
                        test_response = await client.post(
                            url,
                            json=request_data,
                            headers=headers
                        )
                        
                        logger.info(f"  Статус подключения: {test_response.status_code}")
                        
                        if test_response.status_code == 200:
                            try:
                                response_data = test_response.json()
                                logger.info(f"  Ответ: {response_data}")
                            except:
                                logger.info(f"  Ответ (текст): {test_response.text}")
                        else:
                            logger.info(f"  Ошибка: {test_response.text}")
                    else:
                        logger.info("  Нет URL для подключения")
                        
                except Exception as e:
                    logger.error(f"  Ошибка подключения: {e}")
                
                logger.info("")

if __name__ == "__main__":
    asyncio.run(test_available_servers())
