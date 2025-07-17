#!/usr/bin/env python3
"""
Тестовый скрипт для проверки локальных MCP инструментов
"""

import os
import sys
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

def test_local_mcp_tools():
    """Тест локальных MCP инструментов"""
    try:
        logger.info("=== Тест локальных MCP инструментов ===")
        
        # Импортируем локальные инструменты
        from tools.gopiai_integration.local_mcp_tools import get_local_mcp_tools
        
        local_tools = get_local_mcp_tools()
        logger.info("Локальные MCP инструменты инициализированы")
        
        # Получаем список доступных инструментов
        tools = local_tools.get_available_tools()
        logger.info(f"Доступно инструментов: {len(tools)}")
        
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool['description']}")
        
        # Тестируем каждый инструмент
        test_results = {}
        
        # Тест 1: Системная информация
        logger.info("\n--- Тест 1: Системная информация ---")
        result = local_tools.call_tool("system_info", {})
        test_results["system_info"] = result
        logger.info(f"Результат: {result}")
        
        # Тест 2: Время
        logger.info("\n--- Тест 2: Текущее время ---")
        result = local_tools.call_tool("time_helper", {"operation": "current_time"})
        test_results["time_helper"] = result
        logger.info(f"Результат: {result}")
        
        # Тест 3: Статус проекта
        logger.info("\n--- Тест 3: Статус проекта ---")
        result = local_tools.call_tool("project_helper", {"action": "health_check"})
        test_results["project_helper"] = result
        logger.info(f"Результат: {result}")
        
        # Тест 4: Операции с файлами
        logger.info("\n--- Тест 4: Операции с файлами ---")
        result = local_tools.call_tool("file_operations", {
            "operation": "list",
            "path": "."
        })
        test_results["file_operations"] = result
        logger.info(f"Результат: {str(result)[:200]}...")
        
        # Проверяем результаты
        success_count = 0
        for tool_name, result in test_results.items():
            if result and not result.get("error"):
                success_count += 1
                logger.info(f"✅ {tool_name}: УСПЕШНО")
            else:
                logger.error(f"❌ {tool_name}: ОШИБКА - {result.get('error', 'неизвестная ошибка')}")
        
        logger.info(f"\n=== Результаты тестирования ===")
        logger.info(f"Успешно: {success_count}/{len(test_results)}")
        
        return success_count == len(test_results)
        
    except Exception as e:
        logger.error(f"[ERROR] Ошибка при тестировании локальных MCP инструментов: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_delegator_with_local_tools():
    """Тест SmartDelegator с локальными инструментами"""
    try:
        logger.info("\n=== Тест SmartDelegator с локальными инструментами ===")
        
        # Инициализация RAG системы
        from rag_system import get_rag_system
        rag_system = get_rag_system()
        
        # Инициализация SmartDelegator
        from tools.gopiai_integration.smart_delegator import SmartDelegator
        smart_delegator = SmartDelegator(rag_system=rag_system)
        
        # Тестовые запросы
        test_requests = [
            "Покажи системную информацию",
            "Какое сейчас время?",
            "Статус проекта",
            "Здоровье системы"
        ]
        
        for i, request in enumerate(test_requests, 1):
            logger.info(f"\n--- Тест {i}: {request} ---")
            
            result = smart_delegator.process_request(request, {"session_id": "test_session"})
            
            if result and result.get("response"):
                logger.info(f"✅ Ответ получен: {result['response'][:100]}...")
            else:
                logger.error(f"❌ Не удалось получить ответ")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Ошибка при тестировании SmartDelegator: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=== Тестирование локальных MCP инструментов ===")
    
    # Тест 1: Локальные инструменты
    tools_ok = test_local_mcp_tools()
    
    # Тест 2: SmartDelegator с локальными инструментами
    delegator_ok = test_smart_delegator_with_local_tools()
    
    if tools_ok and delegator_ok:
        logger.info("\n🎉 Все тесты пройдены успешно!")
        sys.exit(0)
    else:
        logger.error("\n❌ Некоторые тесты провалились")
        sys.exit(1)
