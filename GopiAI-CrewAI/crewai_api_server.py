# --- START OF FILE crewai_api_server.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import sys
import json
import time
import traceback
import uuid
import threading
import signal
import atexit
from pathlib import Path
from datetime import datetime, timedelta

# Исправляем конфликт OpenMP библиотек
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
# Загружаем .env из корневой директории проекта
load_dotenv(dotenv_path="../.env")

from flask import Flask, request, jsonify

# --- Настройка путей и импортов ---
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# ### ИЗМЕНЕНО: Импортируем правильные фабричные функции ###
from rag_system import get_rag_system
from tools.gopiai_integration.smart_delegator import SmartDelegator

# --- Настройки сервера ---
HOST = "0.0.0.0"  # Слушаем на всех интерфейсах
PORT = 5051  # Стандартный порт для CrewAI API сервера
DEBUG = False
TASK_CLEANUP_INTERVAL = 300

# --- Глобальное хранилище задач ---
TASKS = {}
TASKS_LOCK = threading.Lock()

class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id, message, metadata):
        self.task_id = task_id
        self.message = message
        self.metadata = metadata
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.lock = threading.Lock()

    def start_processing(self):
        with self.lock:
            self.status = TaskStatus.PROCESSING
            self.started_at = datetime.now()

    def complete(self, result):
        with self.lock:
            self.status = TaskStatus.COMPLETED
            self.result = result
            self.completed_at = datetime.now()

    def fail(self, error):
        with self.lock:
            self.status = TaskStatus.FAILED
            self.error = str(error)
            self.completed_at = datetime.now()

    def to_dict(self):
        return {
            "task_id": self.task_id, "status": self.status, "message": self.message,
            "result": self.result, "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

def cleanup_old_tasks():
    while True:
        time.sleep(TASK_CLEANUP_INTERVAL)
        now = datetime.now()
        with TASKS_LOCK:
            for task_id in list(TASKS.keys()):
                if TASKS[task_id].completed_at and (now - TASKS[task_id].completed_at) > timedelta(hours=1):
                    del TASKS[task_id]

cleanup_thread = threading.Thread(target=cleanup_old_tasks, daemon=True)
cleanup_thread.start()

app = Flask(__name__)

# --- Инициализация всех систем при старте ---
try:
    print("[ДИАГНОСТИКА] Начало инициализации систем")
    logger.info("--- ИНИЦИАЛИЗАЦИЯ СИСТЕМ ---")
    
    # 1. Получаем единственный экземпляр RAGSystem
    print("[ДИАГНОСТИКА] Вызов get_rag_system()")
    rag_system_instance = get_rag_system()
    print(f"[ДИАГНОСТИКА] RAGSystem получен: {rag_system_instance is not None}")
    
    # 2. Создаем SmartDelegator, передавая ему наш единственный экземпляр RAG
    print("[ДИАГНОСТИКА] Создание SmartDelegator")
    smart_delegator_instance = SmartDelegator(rag_system=rag_system_instance)
    print(f"[ДИАГНОСТИКА] SmartDelegator создан: {smart_delegator_instance is not None}")
    
    logger.info("✅ Smart Delegator и RAG System успешно инициализированы.")
    SERVER_IS_READY = True
    print("[ДИАГНОСТИКА] SERVER_IS_READY = True")
except Exception as e:
    print(f"[DIAGNOSTIC] CRITICAL ERROR: {e}")
    logger.error(f"CRITICAL ERROR DURING SERVER STARTUP: {e}", exc_info=True)
    rag_system_instance = None
    smart_delegator_instance = None
    SERVER_IS_READY = False
    print("[DIAGNOSTIC] SERVER_IS_READY = False, server will not be started")

# --- Flask routes ---

@app.route('/api/health', methods=['GET'])
def health_check():
    rag_status = "OK" if rag_system_instance and rag_system_instance.embeddings else "NOT INITIALIZED"
    return jsonify({
        "status": "online" if SERVER_IS_READY else "limited_mode",
        "rag_status": rag_status,
        "indexed_documents": rag_system_instance.embeddings.count() if rag_status == "OK" else 0
    })

def process_task(task_id: str):
    """Processes a task in a separate thread."""
    task = TASKS.get(task_id)
    if not task:
        logger.error(f"[TASK-ERROR] Task {task_id} not found in TASKS")
        return
        
    if not smart_delegator_instance:
        error_msg = "Smart Delegator not initialized."
        logger.error(f"[TASK-ERROR] {error_msg}")
        task.fail(error_msg)
        return

    try:
        task.start_processing()
        logger.info(f"[TASK-START] Starting task {task_id} for message: '{task.message}'")
        
        # Добавляем дополнительную проверку
        if not hasattr(smart_delegator_instance, 'process_request'):
            error_msg = "Smart Delegator missing process_request method"
            logger.error(f"[TASK-ERROR] {error_msg}")
            task.fail(error_msg)
            return
            
        response_data = smart_delegator_instance.process_request(
            message=task.message,
            metadata=task.metadata
        )
        
        logger.info(f"[TASK-SUCCESS] Task {task_id} processed successfully.")
        task.complete(response_data)
        
    except Exception as e:
        error_msg = f"Error processing task {task_id}: {str(e)}"
        logger.error(f"[TASK-ERROR] {error_msg}", exc_info=True)
        task.fail(error_msg)

@app.route('/api/process', methods=['POST'])
def process_request():
    if not SERVER_IS_READY:
        return jsonify({"error": "Server started in limited mode due to initialization error."}), 503

    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data.get('message')
    metadata = data.get('metadata', {})

    task_id = str(uuid.uuid4())
    task = Task(task_id, message, metadata)

    with TASKS_LOCK:
        TASKS[task_id] = task

    thread = threading.Thread(target=process_task, args=(task_id,), daemon=True)
    thread.start()

    return jsonify({
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "message": "Task queued for processing",
        "created_at": task.created_at.isoformat()
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())

@app.route('/api/debug', methods=['GET'])
def debug_status():
    """Debug endpoint for system status"""
    return jsonify({
        "server_ready": SERVER_IS_READY,
        "smart_delegator_ready": smart_delegator_instance is not None,
        "rag_system_ready": rag_system_instance is not None,
        "active_tasks": len(TASKS),
        "task_ids": list(TASKS.keys())
    })

# Обработка сигналов для корректного завершения
def signal_handler(signum, frame):
    print(f"\n[SHUTDOWN] Received signal {signum}. Shutting down gracefully...")
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def cleanup_on_exit():
    print("[SHUTDOWN] Cleaning up resources...")
    logger.info("Cleaning up resources...")

if __name__ == '__main__':
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_on_exit)
    
    print(f"[DIAGNOSTIC] __main__ block, SERVER_IS_READY = {SERVER_IS_READY}")
    if SERVER_IS_READY:
        print(f"[DIAGNOSTIC] Starting server on http://{HOST}:{PORT}")
        logger.info(f"[STARTUP] Server starting on http://{HOST}:{PORT}")
        try:
            print("[DIAGNOSTIC] Calling app.run()")
            app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True, use_reloader=False)
            print("[DIAGNOSTIC] After app.run() - this message should not appear")
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received KeyboardInterrupt. Shutting down gracefully...")
            logger.info("Received KeyboardInterrupt. Shutting down gracefully...")
        except Exception as e:
            print(f"[DIAGNOSTIC] Error starting server: {e}")
            logger.error(f"Error starting server: {e}")
    else:
        print("[DIAGNOSTIC] Server not started due to initialization errors")
        logger.error("Server not started due to initialization errors.")
        print("CRITICAL ERROR: Server cannot be started due to initialization errors.")
        sys.exit(1)

# --- END OF FILE crewai_api_server.py ---