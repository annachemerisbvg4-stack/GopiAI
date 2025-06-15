"""
Модуль для автоматической инициализации системы памяти GopiAI
=============================================================

Этот модуль обеспечивает автоматический запуск RAG сервера для системы памяти
при старте приложения GopiAI. Предназначен для импорта из main.py одной строкой.

Использование:
    from gopiai.ui.memory_initializer import init_memory_system

Автор: Crazy Coder
Дата: 2025-01-27
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Настройка логирования
logger = logging.getLogger(__name__)


def init_memory_system(silent: bool = True, port: int = 8080) -> bool:
    """
    Инициализация системы памяти GopiAI с автозапуском RAG сервера
    
    Args:
        silent: Тихий режим (без лишних выводов в консоль)
        port: Порт для RAG сервера
        
    Returns:
        True если система памяти успешно инициализирована
    """
    try:
        # Определяем путь к RAG системе относительно текущего файла
        current_dir = Path(__file__).parent.parent.parent.parent  # GopiAI-UI/gopiai/ui/ -> корень проекта
        rag_system_path = current_dir / "rag_memory_system"
        
        if not rag_system_path.exists():
            if not silent:
                print("⚠️ RAG система памяти не найдена, пропускаем инициализацию")
            return False
        
        # Добавляем путь к RAG системе в sys.path если его там нет
        rag_system_str = str(rag_system_path)
        if rag_system_str not in sys.path:
            sys.path.insert(0, rag_system_str)
        
        # Импортируем и запускаем RAG сервер
        try:
            from server_manager import start_rag_server
            
            if not silent:
                print("🧠 Инициализация системы памяти GopiAI...")
            
            # Запускаем RAG сервер в тихом режиме
            server_manager = start_rag_server(port=port, silent=silent)
            
            if server_manager and server_manager.is_running:
                if not silent:
                    print(f"✅ Система памяти запущена на http://127.0.0.1:{port}")
                return True
            else:
                if not silent:
                    print("⚠️ Система памяти не смогла запуститься")
                return False
                
        except ImportError as e:
            if not silent:
                print(f"⚠️ Не удалось импортировать RAG сервер: {e}")
            return False
            
    except Exception as e:
        logger.warning(f"Ошибка инициализации системы памяти: {e}")
        if not silent:
            print(f"⚠️ Ошибка инициализации системы памяти: {e}")
        return False


def get_memory_status() -> dict:
    """
    Получение статуса системы памяти
    
    Returns:
        Статус системы памяти
    """
    try:
        # Пытаемся получить статус через server_manager
        current_dir = Path(__file__).parent.parent.parent.parent
        rag_system_path = current_dir / "rag_memory_system"
        rag_system_str = str(rag_system_path)
        
        if rag_system_str not in sys.path:
            sys.path.insert(0, rag_system_str)
        
        from server_manager import get_rag_server_status
        return get_rag_server_status()
        
    except Exception as e:
        return {
            "running": False,
            "error": f"Не удалось получить статус: {e}"
        }


def stop_memory_system():
    """
    Остановка системы памяти
    """
    try:
        current_dir = Path(__file__).parent.parent.parent.parent
        rag_system_path = current_dir / "rag_memory_system"
        rag_system_str = str(rag_system_path)
        
        if rag_system_str not in sys.path:
            sys.path.insert(0, rag_system_str)
        
        from server_manager import stop_rag_server
        stop_rag_server()
        
    except Exception as e:
        logger.warning(f"Ошибка остановки системы памяти: {e}")


# Автоматическая инициализация при импорте (опционально)
_auto_init = os.environ.get("GOPIAI_AUTO_INIT_MEMORY", "").lower() in ("1", "true", "yes")

if _auto_init:
    init_memory_system(silent=True)


if __name__ == "__main__":
    # Тестирование модуля
    print("🧪 Тестирование инициализатора памяти...")
    
    # Инициализация в не-тихом режиме для демонстрации
    success = init_memory_system(silent=False)
    
    if success:
        print("\n📊 Статус системы памяти:")
        status = get_memory_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n⏳ Система работает... (нажмите Ctrl+C для остановки)")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Остановка системы памяти...")
            stop_memory_system()
            print("✅ Система остановлена")
    else:
        print("❌ Не удалось инициализировать систему памяти")