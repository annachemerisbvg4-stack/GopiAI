"""
Менеджер RAG сервера для автоматического запуска в фоне
Интегрируется с GopiAI для обеспечения системы памяти
"""

import os
import sys
import time
import atexit
import logging
import threading
import subprocess
from pathlib import Path
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class RAGServerManager:
    """
    Менеджер для автоматического запуска и остановки RAG сервера
    в фоновом режиме для обеспечения системы памяти GopiAI
    """
    
    def __init__(self, 
                 port: int = 8080,
                 host: str = "127.0.0.1",
                 auto_start: bool = True,
                 silent: bool = False):
        """
        Инициализация менеджера сервера
        
        Args:
            port: Порт для RAG сервера
            host: Хост для RAG сервера  
            auto_start: Автоматически запускать сервер
            silent: Тихий режим (меньше логов)
        """
        self.port = port
        self.host = host
        self.auto_start = auto_start
        self.silent = silent
        self.server_process: Optional[subprocess.Popen] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.base_url = f"http://{host}:{port}"
        
        # Определяем пути
        self.current_dir = Path(__file__).parent
        self.python_executable = sys.executable
        
        # Регистрируем функцию остановки при выходе
        atexit.register(self.stop_server)
        
        if self.auto_start:
            self.start_server()
    
    def is_server_running(self, timeout: float = 2.0) -> bool:
        """
        Проверка запущен ли RAG сервер
        
        Args:
            timeout: Таймаут для проверки
            
        Returns:
            True если сервер отвечает
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_server(self) -> bool:
        """
        Запуск RAG сервера в фоновом режиме
        
        Returns:
            True если сервер успешно запущен
        """
        if self.is_server_running():
            if not self.silent:
                print(f"🧠 RAG сервер уже запущен на {self.base_url}")
            self.is_running = True
            return True
        
        try:
            if not self.silent:
                print(f"🚀 Запуск RAG сервера на {self.base_url}...")
            
            # Определяем команду для запуска сервера
            server_script = self.current_dir / "run_server.py"
            
            if not server_script.exists():
                # Если run_server.py не существует, используем api.py напрямую
                server_script = self.current_dir / "api.py"
            
            if not server_script.exists():
                logger.error("❌ Не найден файл для запуска RAG сервера")
                return False
            
            # Запускаем сервер в отдельном процессе
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.current_dir.parent)  # Добавляем родительскую директорию в PYTHONPATH
            
            # Подавляем вывод сервера если включен silent режим
            stdout = subprocess.DEVNULL if self.silent else None
            stderr = subprocess.DEVNULL if self.silent else None
            
            self.server_process = subprocess.Popen(
                [self.python_executable, str(server_script), "--port", str(self.port), "--host", self.host],
                cwd=str(self.current_dir),
                env=env,
                stdout=stdout,
                stderr=stderr
            )
            
            # Ждем пока сервер запустится
            max_attempts = 15  # 15 секунд максимум
            for attempt in range(max_attempts):
                time.sleep(1)
                if self.is_server_running():
                    self.is_running = True
                    if not self.silent:
                        print(f"✅ RAG сервер успешно запущен на {self.base_url}")
                    return True
                
                # Проверяем что процесс еще жив
                if self.server_process.poll() is not None:
                    logger.error(f"❌ RAG сервер завершился с кодом {self.server_process.returncode}")
                    return False
            
            logger.warning(f"⚠️ RAG сервер запущен, но не отвечает на {self.base_url}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска RAG сервера: {e}")
            return False
    
    def stop_server(self):
        """Остановка RAG сервера"""
        if self.server_process and self.server_process.poll() is None:
            try:
                if not self.silent:
                    print("🛑 Остановка RAG сервера...")
                self.server_process.terminate()
                
                # Даем время на корректное завершение
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Принудительное завершение если не завершился корректно
                    self.server_process.kill()
                    self.server_process.wait()
                
                if not self.silent:
                    print("✅ RAG сервер остановлен")
                    
            except Exception as e:
                logger.error(f"Ошибка остановки RAG сервера: {e}")
            finally:
                self.server_process = None
                self.is_running = False
    
    def restart_server(self) -> bool:
        """
        Перезапуск RAG сервера
        
        Returns:
            True если сервер успешно перезапущен
        """
        if not self.silent:
            print("🔄 Перезапуск RAG сервера...")
        self.stop_server()
        time.sleep(2)  # Небольшая пауза
        return self.start_server()
    
    def get_server_status(self) -> dict:
        """
        Получение статуса RAG сервера
        
        Returns:
            Словарь со статусом сервера
        """
        status = {
            "running": self.is_running,
            "url": self.base_url,
            "process_alive": self.server_process.poll() is None if self.server_process else False,
            "responding": self.is_server_running(timeout=1.0)
        }
        
        if status["responding"]:
            try:
                response = requests.get(f"{self.base_url}/stats", timeout=2)
                if response.status_code == 200:
                    status["stats"] = response.json()
            except Exception:
                pass
        
        return status


# Глобальный экземпляр менеджера сервера
_global_server_manager: Optional[RAGServerManager] = None


def start_rag_server(port: int = 8080, host: str = "127.0.0.1", silent: bool = True) -> RAGServerManager:
    """
    Запуск RAG сервера (глобальная функция для импорта в main.py)
    
    Args:
        port: Порт сервера
        host: Хост сервера
        silent: Тихий режим
        
    Returns:
        Экземпляр RAGServerManager
    """
    global _global_server_manager
    
    if _global_server_manager is None:
        _global_server_manager = RAGServerManager(port=port, host=host, silent=silent)
    
    return _global_server_manager


def stop_rag_server():
    """Остановка RAG сервера (глобальная функция)"""
    global _global_server_manager
    
    if _global_server_manager:
        _global_server_manager.stop_server()
        _global_server_manager = None


def get_rag_server_status() -> dict:
    """
    Получение статуса RAG сервера
    
    Returns:
        Статус сервера или информация что сервер не запущен
    """
    global _global_server_manager
    
    if _global_server_manager:
        return _global_server_manager.get_server_status()
    
    return {
        "running": False,
        "error": "RAG server manager not initialized"
    }


# Автоматическая очистка при импорте модуля
def _cleanup():
    """Функция очистки для atexit"""
    stop_rag_server()


atexit.register(_cleanup)


if __name__ == "__main__":
    # Тестирование менеджера сервера
    print("🧪 Тестирование RAG Server Manager...")
    
    manager = RAGServerManager(silent=False)
    
    print("\n📊 Статус сервера:")
    status = manager.get_server_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n⏳ Ожидание 5 секунд...")
    time.sleep(5)
    
    print("\n🛑 Остановка сервера...")
    manager.stop_server()
    
    print("✅ Тест завершен")