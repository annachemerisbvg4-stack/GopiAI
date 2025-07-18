#!/usr/bin/env python3
"""
Скрипт для тестирования исправлений GopiAI-CrewAI
"""

import sys
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_txtai_import():
    """Тестирует импорт txtai"""
    try:
        from txtai.embeddings import Embeddings
        logger.info("✅ txtai успешно импортирован")
        return True
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта txtai: {e}")
        return False

def test_crewai_import():
    """Тестирует импорт CrewAI"""
    try:
        from crewai import Agent, Task, Crew, Process
        logger.info("✅ CrewAI успешно импортирован")
        return True
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта CrewAI: {e}")
        return False

def test_mcp_import():
    """Тестирует импорт MCP"""
    try:
        from mcp.client.streamable_http import streamablehttp_client
        from mcp.types import JSONRPCRequest, JSONRPCResponse
        logger.info("✅ MCP модули успешно импортированы")
        return True
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта MCP: {e}")
        return False

def test_rag_system():
    """Тестирует RAG систему"""
    try:
        from rag_system import get_rag_system
        rag = get_rag_system()
        logger.info(f"✅ RAG система инициализирована: {rag is not None}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации RAG системы: {e}")
        return False

def test_smart_delegator():
    """Тестирует SmartDelegator"""
    try:
        from tools.gopiai_integration.smart_delegator import SmartDelegator
        from rag_system import get_rag_system
        
        rag = get_rag_system()
        delegator = SmartDelegator(rag_system=rag)
        logger.info(f"✅ SmartDelegator инициализирован: {delegator is not None}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации SmartDelegator: {e}")
        return False

def test_mcp_integration():
    """Тестирует MCP интеграцию"""
    try:
        from tools.gopiai_integration.mcp_integration import get_mcp_tools_manager
        manager = get_mcp_tools_manager()
        logger.info(f"✅ MCP менеджер инициализирован: {manager is not None}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации MCP менеджера: {e}")
        return False

def main():
    """Основная функция тестирования"""
    logger.info("🚀 Начинаем тестирование исправлений GopiAI-CrewAI")
    logger.info("=" * 60)
    
    tests = [
        ("txtai импорт", test_txtai_import),
        ("CrewAI импорт", test_crewai_import),
        ("MCP импорт", test_mcp_import),
        ("RAG система", test_rag_system),
        ("SmartDelegator", test_smart_delegator),
        ("MCP интеграция", test_mcp_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"🧪 Тестируем: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
        logger.info("-" * 40)
    
    # Итоговый отчет
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ:")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛЕН"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("-" * 40)
    logger.info(f"Всего тестов: {len(results)}")
    logger.info(f"Прошло: {passed}")
    logger.info(f"Провалено: {failed}")
    
    if failed == 0:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return 0
    else:
        logger.error(f"⚠️  {failed} тестов провалено. Требуется дополнительная настройка.")
        return 1

if __name__ == "__main__":
    sys.exit(main())