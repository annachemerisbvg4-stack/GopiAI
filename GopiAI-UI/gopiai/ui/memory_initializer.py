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
        # Проверяем, не запущен ли уже сервер
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if response.status_code == 200:
                if not silent:
                    print(f"✅ RAG сервер уже запущен на порту {port}")
                return True
        except:
            pass  # Сервер не запущен, продолжаем
        
        # Определяем путь к RAG системе
        current_dir = Path(__file__).parent.parent.parent.parent  # Корень проекта
        rag_system_path = current_dir / "rag_memory_system"
        simple_server_path = rag_system_path / "simple_rag_server.py"
        
        if not simple_server_path.exists():
            if not silent:
                print("⚠️ simple_rag_server.py не найден, пропускаем инициализацию")
            return False
        
        if not silent:
            print("🧠 Запуск системы памяти GopiAI...")
        
        # Запускаем сервер в фоновом режиме
        try:
            # Используем python для запуска сервера
            cmd = [
                "python", str(simple_server_path)
            ]
            
            # Запускаем в фоновом режиме (без ожидания завершения)
            process = subprocess.Popen(
                cmd,
                cwd=str(rag_system_path),
                stdout=subprocess.PIPE if silent else None,
                stderr=subprocess.PIPE if silent else None,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Ждем немного чтобы сервер запустился
            time.sleep(2)
            
            # Проверяем что сервер действительно запустился
            for attempt in range(5):
                try:
                    response = requests.get(f"http://127.0.0.1:{port}/health", timeout=1)
                    if response.status_code == 200:
                        if not silent:
                            print(f"✅ Система памяти запущена на http://127.0.0.1:{port}")
                        return True
                except:
                    time.sleep(1)
            
            if not silent:
                print("⚠️ Система памяти не отвечает после запуска")
            return False
            
        except Exception as e:
            if not silent:
                print(f"⚠️ Ошибка запуска RAG сервера: {e}")
            return False
            
    except Exception as e:
        logger.warning(f"Ошибка инициализации системы памяти: {e}")
        if not silent:
            print(f"⚠️ Ошибка инициализации системы памяти: {e}")
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