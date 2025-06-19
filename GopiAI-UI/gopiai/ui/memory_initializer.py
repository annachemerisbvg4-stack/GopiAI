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
    Инициализация системы памяти GopiAI с автозапуском простого RAG сервера
    
    Args:
        silent: Тихий режим (без лишних выводов в консоль)
        port: Порт для RAG сервера
        
    Returns:
        True если система памяти успешно инициализирована
    """
    import subprocess
    import requests
    import time
    import os
    
    try:
        # Проверяем не запущен ли уже сервер
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if response.status_code == 200:
                logger.info("✅ RAG сервер уже запущен")
                return True
        except:
            pass
        
        # Запуск сервера в фоновом режиме
        current_dir = Path(__file__).parent.parent.parent.parent  # Корень проекта
        rag_path = current_dir / "rag_memory_system" / "simple_rag_server.py"
        
        if not rag_path.exists():
            logger.error(f"❌ Файл сервера не найден: {rag_path}")
            if not silent:
                print(f"❌ Файл сервера не найден: {rag_path}")
            return False
        
        # Используем subprocess для запуска в фоне
        global server_process
        
        # Запускаем БЕЗ нового окна терминала, чтобы избежать бесконечного цикла окон
        server_process = subprocess.Popen(
            [sys.executable, str(rag_path)], 
            # creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,  # Отключено!
            stdout=subprocess.PIPE if silent else None,
            stderr=subprocess.PIPE if silent else None
        )
        
        logger.info(f"🚀 Запущен RAG сервер (PID: {server_process.pid})")
        if not silent:
            print(f"🚀 Запущен RAG сервер (PID: {server_process.pid})")
        
        time.sleep(2)  # Даем время на запуск
        
        # Проверяем запустился ли сервер
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if response.status_code == 200:
                logger.info("✅ RAG сервер успешно запущен")
                if not silent:
                    print("✅ RAG сервер успешно запущен")
                return True
            else:
                logger.error(f"❌ RAG сервер вернул код {response.status_code}")
                if not silent:
                    print(f"❌ RAG сервер вернул код {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ RAG сервер не отвечает после запуска: {e}")
            if not silent:
                print(f"❌ RAG сервер не отвечает после запуска: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске RAG сервера: {e}")
        if not silent:
            print(f"❌ Ошибка при запуске RAG сервера: {e}")
        return False


def get_memory_status() -> dict:
    """
    Получение статуса системы памяти
    
    Returns:
        Статус системы памяти
    """
    import requests
    
    try:
        # Проверяем статус через HTTP API
        response = requests.get("http://127.0.0.1:8080/health", timeout=2)
        if response.status_code == 200:
            # Получаем статистику
            stats_response = requests.get("http://127.0.0.1:8080/stats", timeout=2)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                return {
                    "running": True,
                    "port": 8080,
                    "conversations": stats.get("conversations", 0),
                    "chunks": stats.get("chunks", 0),
                    "total_content_size": stats.get("total_content_size", 0)
                }
            else:
                return {
                    "running": True,
                    "port": 8080,
                    "stats_error": "Could not get stats"
                }
        else:
            return {
                "running": False,
                "error": f"Health check failed with status {response.status_code}"
            }
        
    except Exception as e:
        return {
            "running": False,
            "error": f"Не удалось получить статус: {e}"
        }


def stop_memory_system():
    """
    Остановка системы памяти (убивает процесс на порту 8080)
    """
    import subprocess
    
    try:
        # Для Windows используем taskkill для остановки процесса на порту
        if os.name == 'nt':
            # Находим PID процесса на порту 8080
            result = subprocess.run(
                ["netstat", "-ano"], 
                capture_output=True, 
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if ':8080 ' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(["taskkill", "/F", "/PID", pid], check=True)
                            print(f"✅ Остановлен процесс RAG сервера (PID: {pid})")
                            return
                        except:
                            pass
        else:
            # Для Linux/MacOS используем lsof и kill
            result = subprocess.run(
                ["lsof", "-ti:8080"], 
                capture_output=True, 
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(["kill", "-9", pid], check=True)
                print(f"✅ Остановлен процесс RAG сервера (PID: {pid})")
                return
        
        print("⚠️ Процесс RAG сервера не найден")
        
    except Exception as e:
        logger.warning(f"Ошибка остановки системы памяти: {e}")
        print(f"⚠️ Ошибка остановки системы памяти: {e}")


# Автоматическая инициализация при импорте отключена
# ВНИМАНИЕ: Автоинициализация вызывала бесконечный запуск терминалов в VS Code
# _auto_init = os.environ.get("GOPIAI_AUTO_INIT_MEMORY", "").lower() in ("1", "true", "yes")
# if _auto_init:
#     init_memory_system(silent=True)


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