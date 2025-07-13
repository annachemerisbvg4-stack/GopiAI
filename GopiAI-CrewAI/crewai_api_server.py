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
from pathlib import Path
from datetime import datetime, timedelta

from flask import Flask, request, jsonify

# --- Настройка путей и импортов ---
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# ### ИЗМЕНЕНО: Импортируем правильные фабричные функции ###
from rag_system import get_rag_system
from tools.gopiai_integration.smart_delegator import SmartDelegator

# --- Настройки сервера ---
HOST = "127.0.0.1"
PORT = 5051  # Изменено с 5050 на 5051 для проверки
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
    print(f"[ДИАГНОСТИКА] КРИТИЧЕСКАЯ ОШИБКА: {e}")
    logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ СЕРВЕРА: {e}", exc_info=True)
    rag_system_instance = None
    smart_delegator_instance = None
    SERVER_IS_READY = False
    print("[ДИАГНОСТИКА] SERVER_IS_READY = False")

# --- Роуты Flask ---

@app.route('/api/health', methods=['GET'])
def health_check():
    rag_status = "OK" if rag_system_instance and rag_system_instance.embeddings else "NOT INITIALIZED"
    return jsonify({
        "status": "online" if SERVER_IS_READY else "limited_mode",
        "rag_status": rag_status,
        "indexed_documents": rag_system_instance.embeddings.count() if rag_status == "OK" else 0
    })

def process_task(task_id: str):
    """Выполняет задачу в отдельном потоке."""
    task = TASKS.get(task_id)
    if not task: return
        
    if not smart_delegator_instance:
        task.fail("Smart Delegator не инициализирован.")
        return

    try:
        task.start_processing()
        logger.info(f"Начинаю обработку задачи {task_id} для сообщения: '{task.message}'")
        
        response_data = smart_delegator_instance.process_request(
            message=task.message,
            metadata=task.metadata
        )
        
        logger.info(f"✅ Задача {task_id} успешно обработана.")
        task.complete(response_data)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке задачи {task_id}: {e}", exc_info=True)
        task.fail(str(e))

@app.route('/api/process', methods=['POST'])
def process_request():
    if not SERVER_IS_READY:
        return jsonify({"error": "Сервер запущен в ограниченном режиме из-за ошибки инициализации."}), 503

    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Отсутствует поле 'message'"}), 400

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
        "message": "Задача поставлена в очередь на обработку",
        "created_at": task.created_at.isoformat()
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    return jsonify(task.to_dict())

if __name__ == '__main__':
    print(f"[ДИАГНОСТИКА] __main__ блок, SERVER_IS_READY = {SERVER_IS_READY}")
    if SERVER_IS_READY:
        print(f"[ДИАГНОСТИКА] Запуск сервера на http://{HOST}:{PORT}")
        logger.info(f"🚀 Сервер запускается на http://{HOST}:{PORT}")
        try:
            print("[ДИАГНОСТИКА] Вызов app.run()")
            app.run(host=HOST, port=PORT, debug=DEBUG)
            print("[ДИАГНОСТИКА] После app.run() - это сообщение не должно появиться")
        except Exception as e:
            print(f"[ДИАГНОСТИКА] Ошибка при запуске Flask: {e}")
    else:
        print("[ДИАГНОСТИКА] Сервер не запущен из-за ошибок инициализации")
        logger.error("❌ Сервер не запущен из-за ошибок инициализации.")
        print("КРИТИЧЕСКАЯ ОШИБКА: Сервер не может быть запущен из-за ошибок инициализации.")
        sys.exit(1)

# --- END OF FILE crewai_api_server.py ---