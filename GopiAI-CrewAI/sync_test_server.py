#!/usr/bin/env python3
"""
Синхронный тестовый сервер для проверки SmartDelegator
"""

import logging
import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

# Добавляем пути
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Импортируем необходимые модули
from rag_system import get_rag_system
from tools.gopiai_integration.smart_delegator import SmartDelegator

app = Flask(__name__)

# Инициализация системы
rag_system = None
smart_delegator = None

def init_systems():
    """Инициализация RAG и SmartDelegator"""
    global rag_system, smart_delegator
    
    try:
        logger.info("Инициализация RAG системы...")
        rag_system = get_rag_system()
        logger.info(f"RAG система инициализирована: {rag_system.embeddings.count()} документов")
        
        logger.info("Инициализация SmartDelegator...")
        smart_delegator = SmartDelegator(rag_system=rag_system)
        logger.info("SmartDelegator инициализирован")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "rag_ready": rag_system is not None,
        "smart_delegator_ready": smart_delegator is not None
    })

@app.route('/api/sync_process', methods=['POST'])
def sync_process():
    """Синхронная обработка запроса"""
    if not smart_delegator:
        return jsonify({"error": "SmartDelegator not initialized"}), 500
    
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field"}), 400
    
    message = data.get('message')
    metadata = data.get('metadata', {})
    
    logger.info(f"[SYNC] Обрабатываем сообщение: {message}")
    
    try:
        # Синхронная обработка
        result = smart_delegator.process_request(message, metadata)
        logger.info(f"[SYNC] Обработка завершена успешно")
        return jsonify({
            "status": "completed",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"[SYNC] Ошибка при обработке: {e}")
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=== Синхронный тестовый сервер ===")
    
    if init_systems():
        print("Системы инициализированы успешно")
        print("Запуск на http://127.0.0.1:5053")
        app.run(host='127.0.0.1', port=5053, debug=False, threaded=True)
    else:
        print("Ошибка инициализации систем")
        sys.exit(1)
