"""
Модуль для автоматической инициализации системы памяти GopiAI
=============================================================

Новая версия - использует embedded txtai вместо RAG сервера!
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def init_memory_system(silent: bool = True) -> bool:
    """
    Инициализация системы памяти GopiAI с embedded txtai
    
    Args:
        silent: Тихий режим (без лишних выводов в консоль)
        
    Returns:
        True если система памяти успешно инициализирована
    """
    
    try:
        # Инициализируем новый txtai менеджер
        from rag_memory_system import get_memory_manager
        
        manager = get_memory_manager()
        
        if not silent:
            stats = manager.get_stats()
            print(f"✅ Система памяти инициализирована")
            print(f"📊 Статистика: {stats}")
        
        logger.info("✅ TxtAI память инициализирована")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации памяти: {e}")
        if not silent:
            print(f"❌ Ошибка инициализации памяти: {e}")
        return False

def get_memory_status() -> dict:
    """
    Получение статуса системы памяти
    
    Returns:
        Статус системы памяти
    """
    
    try:
        from rag_memory_system import get_memory_manager
        manager = get_memory_manager()
        return manager.get_stats()
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса: {e}")
        return {
            "error": str(e),
            "txtai_available": False,
            "total_messages": 0,
            "total_sessions": 0
        }

def stop_memory_system():
    """
    Остановка системы памяти
    (Для txtai ничего не нужно делать - embedded)
    """
    logger.info("📝 TxtAI система остановлена (embedded - автоматически)")

# Автоматическая инициализация отключена
# ВНИМАНИЕ: Автоинициализация может вызывать проблемы в VS Code

if __name__ == "__main__":
    # Тестирование модуля
    print("🧪 Тестирование инициализатора памяти...")
    
    success = init_memory_system(silent=False)
    
    if success:
        print("🎉 Инициализация прошла успешно!")
        status = get_memory_status()
        print(f"📊 Статус: {status}")
    else:
        print("❌ Ошибка инициализации")